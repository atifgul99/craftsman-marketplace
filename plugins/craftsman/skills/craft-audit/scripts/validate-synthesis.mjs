#!/usr/bin/env node
// Read-only synthesis validator for a Craftsman workspace.
// Requires the durable deduplication-map artifact before a master tracker can claim synthesis.

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";

function fail(message) {
  console.error(`FAIL: ${message}`);
  process.exitCode = 1;
}

function usage(message) {
  console.error(`FAIL: ${message}`);
  process.exit(2);
}

function workspaceFrom(input) {
  if (!existsSync(input)) usage(`path does not exist: ${input}`);
  if (!statSync(input).isDirectory()) usage(`not a directory: ${input}`);
  if (existsSync(join(input, "audits"))) return input;
  const nested = join(input, ".craftsman");
  if (existsSync(join(nested, "audits"))) return nested;
  usage(`no .craftsman workspace found at ${input}`);
}

function findingsFiles(workspace) {
  const root = join(workspace, "audits");
  const out = [];
  const walk = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) walk(path);
      else if (entry.isFile() && entry.name === "findings.md") out.push(path);
    }
  };
  walk(root);
  return out;
}

function eligibleOpenFindings(file) {
  const lines = readFileSync(file, "utf8").split("\n");
  const headings = [];
  for (let i = 0; i < lines.length; i++) {
    if (/^## .+ · severity [🔴🟡🟢] · status /u.test(lines[i])) headings.push(i);
  }
  return headings.filter((start, index) => {
    const end = headings[index + 1] ?? lines.length;
    return /^## .+ · severity [🔴🟡🟢] · status (open|regressed)$/u.test(lines[start]) &&
      !lines.slice(start, end).some((line) => line.trim() === "**Confidence:** unverified-from-repo");
  }).length;
}

const input = process.argv[2];
if (!input || process.argv.length !== 3) usage("usage: node validate-synthesis.mjs <path-to-.craftsman-or-project-root>");

const workspace = workspaceFrom(input);
const mapPath = join(workspace, "dedup-map.md");
if (!existsSync(mapPath)) {
  fail("missing dedup-map.md — semantic reconciliation cannot be assumed from findings alone");
  process.exit(process.exitCode ?? 0);
}

const map = readFileSync(mapPath, "utf8");
const summary = map.match(/Raw eligible findings:\s*(\d+)\s*·\s*Exact-key groups:\s*(\d+)\s*·\s*Semantic candidates reviewed:\s*(\d+)\s*·\s*Distinct eligible defects:\s*(\d+)/);
if (!summary) {
  fail("dedup-map.md is missing the required raw/exact/semantic/distinct summary line");
} else {
  const raw = Number(summary[1]);
  const semantic = Number(summary[3]);
  const actualRaw = findingsFiles(workspace).reduce((total, file) => total + eligibleOpenFindings(file), 0);
  if (raw !== actualRaw) fail(`dedup-map raw eligible count ${raw} does not match workspace count ${actualRaw}`);
  if (!map.includes("## Semantic reconciliation")) fail("dedup-map.md is missing the Semantic reconciliation section");
  if (!map.includes("## Attestation")) fail("dedup-map.md is missing the Attestation section");
  if (raw > 1 && semantic === 0 && !/search basis.+0 candidates after review/is.test(map)) {
    fail("zero semantic candidates requires an attestation with search basis and '0 candidates after review'");
  }
  if (semantic > 0) {
    const semanticSection = map.split("## Semantic reconciliation")[1]?.split("## Attestation")[0] ?? "";
    const rows = semanticSection.split("\n").filter((line) => /^\|/.test(line) && !/^\|\s*-/.test(line)).slice(1);
    if (rows.length < semantic) fail(`dedup-map records ${semantic} semantic candidates but only ${rows.length} decision row(s)`);
  }
}

if (process.exitCode) process.exit(process.exitCode);
console.log(`OK: synthesis deduplication evidence validated for ${relative(process.cwd(), workspace) || "."}`);
