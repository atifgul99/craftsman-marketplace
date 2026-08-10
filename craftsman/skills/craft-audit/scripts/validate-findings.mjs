#!/usr/bin/env node
// Mechanical validator for craftsman `.craftsman/audits/<scope>/<domain>/findings.md` files.
//
// Authoritative spec: craftsman/skills/craft-audit/references/workspace.md —
//   - "Canonical findings.md emission format (mandatory)" (heading grammar, required labels,
//     optional Confidence/Fix-attempt trailing labels, forbidden shapes)
//   - "Mechanical validation checklist" (the six checks this script implements)
// This script is read-only: it never rewrites, normalizes, or repairs a findings.md file.
//
// Checks implemented (all six from the spec):
//   1. Every finding heading matches the canonical `## ` heading grammar (severity + status,
//      non-empty wontfix reason / merged-into ID).
//   2. Per finding block: exactly one of each required label, in order — What breaks (plain
//      language), Technical, Fix, Fingerprint, Last-checked. Fingerprint and Last-checked value
//      grammar. Optional trailing Confidence (one value from a fixed set, absent = verified) then
//      optional repeatable Fix-attempt lines, in that order after Last-checked.
//   3. No `###` (or otherwise non-canonical) finding-shaped headings anywhere in the file.
//   4. No body bullets `- **Severity:**` / `- **Status:**` (those live in the heading only).
//   5. An empty findings file (header stamp only, zero findings) is valid if it has the file
//      header stamp and no malformed headings.
//   6. Path binding: for `audits/<scope>/<domain>/findings.md`, every finding's Fingerprint
//      `scope=`/`domain=` match the directory path, and the heading's scopeLabel/DOMAINCODE match
//      too (scopeLabel = scope.replaceAll('/', '-'), DOMAINCODE from the domain-code table below,
//      sourced from workspace.md — not invented here).
//
// Invocation:
//   node validate-findings.mjs <path-to-.craftsman-or-project-root>
// Accepts either the `.craftsman` directory itself or the project root that contains it.
//
// Exit codes: 0 = every file passed. 1 = at least one file failed a check. 2 = usage/IO error
// (no workspace found, unreadable path, etc).

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, relative, sep } from "node:path";

// ---------------------------------------------------------------------------
// Domain-code table — sourced verbatim from workspace.md's ID label table
// ("| ux | `UX` | security | `SEC` | ..." around line 132-138).
// ---------------------------------------------------------------------------
const DOMAIN_CODES = {
  ux: "UX",
  frontend: "FE",
  backend: "BE",
  db: "DB",
  security: "SEC",
  infra: "INFRA",
  observability: "OBS",
  testing: "TEST",
  lint: "LINT",
  ai: "AI",
};
const DOMAIN_CODE_ALTERNATION = Object.values(DOMAIN_CODES).join("|");

// Canonical heading grammar (check 1). Full-line, column-0 `## `.
const HEADING_RE = new RegExp(
  `^## ([A-Za-z0-9][A-Za-z0-9-]*)-(${DOMAIN_CODE_ALTERNATION})-(\\d{3}) · severity ([🔴🟡🟢]) · status (open|fixed|regressed|wontfix \\(.+\\)|fixed \\(merged into .+\\))$`,
  "u",
);

// Finding-shaped heading detector, for rejecting non-canonical Markdown headings (check 3).
// A bare ID-shaped line is ordinary prose unless it has Markdown heading structure; rejecting it
// makes a sentence such as "root-INFRA-002, ..." a false positive.
const FINDING_SHAPED_RE = new RegExp(
  `severity\\s*[🔴🟡🟢]|status\\s+(open|fixed|regressed|wontfix)|-(${DOMAIN_CODE_ALTERNATION})-\\d{3}\\b`,
  "iu",
);

const REQUIRED_LABELS = [
  "**What breaks (plain language):**",
  "**Technical:**",
  "**Fix:**",
  "**Fingerprint:**",
  "**Last-checked:**",
];

const CONFIDENCE_LABEL = "**Confidence:**";
const DEPLOYMENT_STATE_LABEL = "**Deployment-state:**";
const FIX_ATTEMPT_LABEL = "**Fix-attempt:**";
const CONFIDENCE_VALUES = new Set(["verified", "inferred", "unverified-from-repo"]);
const DEPLOYMENT_STATE_RE = /^(active|not-applicable|unverified-from-repo|pending \(.+\))$/;

const FP_RE = /`scope=([^·`]+)\s*·\s*domain=([^·`]+)\s*·\s*class=([^·`]+)\s*·\s*resource=([^`]+)`/;
const LAST_CHECKED_RE = /^\d{4}-\d{2}-\d{2} · ([0-9a-f]{4,40}|none \(no git\))$/;

// File header stamp (check 5): "> Generated: <date> · commit <sha|...> · driven by <domain>-craft · scope: <path>"
const HEADER_STAMP_RE = /^> Generated: .+ · commit .+ · driven by .+ · scope: .+$/m;

const SEVERITY_ORDER = ["🔴", "🟡", "🟢"];
const STATUS_ORDER = ["open", "fixed", "regressed", "wontfix", "fixed (merged)"];

// ---------------------------------------------------------------------------
// Errors are collected as { line, message } and printed as <relative-path>:<line>: <message>
// ---------------------------------------------------------------------------

function usageError(message) {
  console.error(`FAIL: ${message}`);
  process.exit(2);
}

function resolveWorkspaceDir(inputPath) {
  const resolved = inputPath;
  if (!existsSync(resolved)) {
    usageError(`path does not exist: ${resolved}`);
  }
  let st;
  try {
    st = statSync(resolved);
  } catch (err) {
    usageError(`could not stat ${resolved}: ${err.message}`);
  }
  if (!st.isDirectory()) {
    usageError(`not a directory: ${resolved}`);
  }
  // Accept either the `.craftsman` directory itself, or a project root containing it.
  if (existsSync(join(resolved, "audits"))) {
    return resolved;
  }
  const nested = join(resolved, ".craftsman");
  if (existsSync(nested) && existsSync(join(nested, "audits"))) {
    return nested;
  }
  usageError(
    `no .craftsman workspace found at ${resolved} (expected ${resolved}/audits or ${resolved}/.craftsman/audits)`,
  );
}

// Walk `audits/` and find every findings.md, recording its (scope, domain) from the path —
// scope may contain slashes, so we walk the tree rather than assuming a fixed depth.
function findFindingsFiles(workspaceDir) {
  const auditsDir = join(workspaceDir, "audits");
  const results = [];
  if (!existsSync(auditsDir)) return results;

  // Recursively collect every findings.md under audits/, then derive scope/domain from the path
  // relative to auditsDir: <scope...>/<domain>/findings.md.
  // Any readdirSync failure (permission denied, race with deletion, etc.) must surface rather
  // than being silently skipped — a partial scan that reports success is worse than a hard stop.
  const walk = (dir) => {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch (err) {
      throw new Error(`could not read directory ${dir}: ${err.message}`);
    }
    for (const entry of entries) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.isFile() && entry.name === "findings.md") {
        const relParts = relative(auditsDir, full).split(sep);
        // relParts = [...scopeParts, domain, "findings.md"]
        if (relParts.length < 3) continue; // not a valid <scope>/<domain>/findings.md shape
        const domain = relParts[relParts.length - 2];
        const scope = relParts.slice(0, -2).join("/");
        results.push({ path: full, scope, domain });
      }
    }
  };
  walk(auditsDir);
  return results;
}

// Compute the 1-based line number of a given character offset in `content`.
function lineNumberAt(content, offset) {
  let line = 1;
  for (let i = 0; i < offset && i < content.length; i++) {
    if (content[i] === "\n") line++;
  }
  return line;
}

function unwrapMarkdownContainers(line) {
  let s = line;
  for (let guard = 0; guard < 12; guard++) {
    let next = s.replace(/^\s+/, "");
    next = next.replace(/^(?:> ?)+/, "");
    next = next.replace(/^(?:[-*+]|\d+\.)\s+/, "");
    if (next === s) break;
    s = next;
  }
  return s;
}

// Scan for finding-shaped headings that are NOT canonical column-0 `## ` matches — these are
// malformed and must be rejected (check 3, and the "forbidden" shapes in the emission format).
function scanMalformedHeadings(lines) {
  const malformed = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (HEADING_RE.test(line)) continue; // canonical — fine

    const unwrapped = unwrapMarkdownContainers(line);
    if (!unwrapped) continue;

    const atx = unwrapped.match(/^(#{1,6})\s+(\S.*)$/);
    if (atx) {
      if (FINDING_SHAPED_RE.test(atx[2])) {
        malformed.push({ lineIdx: i, text: line.trimEnd() || unwrapped });
      }
      continue;
    }

    // Setext-style heading (title line followed by === or --- underline)
    if (i + 1 < lines.length) {
      const under = unwrapMarkdownContainers(lines[i + 1]);
      if (/^(=+|-+)\s*$/.test(under) && FINDING_SHAPED_RE.test(unwrapped) && unwrapped.trim() !== "") {
        malformed.push({ lineIdx: i, text: `${unwrapped.trim()} / ${under.trim()}` });
      }
    }
  }
  return malformed;
}

// Split content into finding blocks. Only column-0 `## ` lines start a block (canonical form) —
// any other finding-shaped heading is caught separately by scanMalformedHeadings.
function splitFindingBlocks(lines) {
  const blocks = [];
  let current = null;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("## ")) {
      if (current) blocks.push(current);
      current = { headingLineIdx: i, heading: line, bodyLines: [], bodyStartIdx: i + 1 };
    } else if (current) {
      current.bodyLines.push(line);
    }
  }
  if (current) blocks.push(current);
  return blocks;
}

// A label line is one whose content, after optional leading whitespace, STARTS with a
// `**...:**` token — not merely a line that mentions a label somewhere mid-sentence. This keeps
// prose like "this will require a **Fix:** eventually" from being misread as a label line.
const LABEL_LINE_RE = /^\*\*[^*\n]+:\*\*/;

function isLabelLine(line) {
  return LABEL_LINE_RE.test(line.replace(/^\s+/, ""));
}

function lineStartsWithLabel(line, label) {
  return line.replace(/^\s+/, "").startsWith(label);
}

// Positions of lines that START with `label` (not just contain it), within [startIdx, endIdx).
function labelPositions(lines, startIdx, endIdx, label) {
  const positions = [];
  for (let i = startIdx; i < endIdx; i++) {
    if (lineStartsWithLabel(lines[i], label)) positions.push(i);
  }
  return positions;
}

// Validate a single finding block. Pushes errors ({ line, message }) and returns
// { severity, status } on success (used for the per-domain summary), or null on failure.
function validateBlock(block, content, lines, scope, domain, errors, addError) {
  const hm = block.heading.match(HEADING_RE);
  if (!hm) {
    addError(block.headingLineIdx, `heading does not match canonical grammar: ${block.heading}`);
    return null;
  }
  const [, scopeLabel, domainCode, , severity, status] = hm;
  const expectedCode = DOMAIN_CODES[domain];
  const expectedScopeLabel = scope.replaceAll("/", "-");

  let ok = true;

  if (expectedCode && domainCode !== expectedCode) {
    addError(
      block.headingLineIdx,
      `heading DOMAINCODE "${domainCode}" does not match path domain "${domain}" (expected "${expectedCode}")`,
    );
    ok = false;
  }
  if (scopeLabel !== expectedScopeLabel) {
    addError(
      block.headingLineIdx,
      `heading scopeLabel "${scopeLabel}" does not match path scope "${scope}" (expected "${expectedScopeLabel}")`,
    );
    ok = false;
  }

  // check 4: forbidden body bullets
  for (let i = 0; i < block.bodyLines.length; i++) {
    const l = block.bodyLines[i];
    if (/^-\s+\*\*Severity:\*\*/.test(l) || /^-\s+\*\*Status:\*\*/.test(l)) {
      addError(
        block.bodyStartIdx + i,
        `forbidden body bullet (severity/status belong in the heading only): ${l.trim()}`,
      );
      ok = false;
    }
  }

  const bodyAbsoluteStart = block.bodyStartIdx;
  const blockEndIdx = bodyAbsoluteStart + block.bodyLines.length;

  // check 2: exactly one of each required label, in order
  let prevIdx = -1;
  let labelsOk = true;
  const labelIdx = {};
  for (const label of REQUIRED_LABELS) {
    const positions = labelPositions(lines, bodyAbsoluteStart, blockEndIdx, label);
    if (positions.length !== 1) {
      // Report at the actual duplicate occurrence when there is one (accurate line number for
      // e.g. a required label repeated after Last-checked); fall back to the heading when the
      // label is missing entirely (positions.length === 0, nothing else to point at).
      const errLine = positions.length > 1 ? positions[1] : block.headingLineIdx;
      addError(
        errLine,
        `label "${label}" appears ${positions.length} time(s) in ${block.heading.trim()} (want exactly 1)`,
      );
      labelsOk = false;
      ok = false;
      continue;
    }
    const idx = positions[0];
    labelIdx[label] = idx;
    if (idx < prevIdx) {
      addError(idx, `label "${label}" is out of order (expected after the previous required label)`);
      labelsOk = false;
      ok = false;
    }
    prevIdx = idx;
  }
  if (!labelsOk) return null;

  // Fingerprint grammar
  const fpLineIdx = labelIdx["**Fingerprint:**"];
  const fpLine = lines[fpLineIdx];
  const fpMatch = fpLine.match(FP_RE);
  if (!fpMatch) {
    addError(fpLineIdx, `Fingerprint line does not match grammar: ${fpLine.trim()}`);
    ok = false;
  } else {
    const [, fpScope, fpDomain] = fpMatch.map((s) => (typeof s === "string" ? s.trim() : s));
    if (fpScope !== scope) {
      addError(fpLineIdx, `Fingerprint scope="${fpScope}" does not match path scope="${scope}"`);
      ok = false;
    }
    if (fpDomain !== domain) {
      addError(fpLineIdx, `Fingerprint domain="${fpDomain}" does not match path domain="${domain}"`);
      ok = false;
    }
  }

  // Last-checked grammar
  const lcLineIdx = labelIdx["**Last-checked:**"];
  const lcLine = lines[lcLineIdx];
  const lcValue = lcLine.replace("**Last-checked:**", "").trim();
  if (!LAST_CHECKED_RE.test(lcValue)) {
    addError(lcLineIdx, `Last-checked value does not match grammar: ${lcValue}`);
    ok = false;
  }

  // Optional trailing labels: after `**Last-checked:**`, the ONLY labels permitted in the block
  // are `**Confidence:**` (at most one) and `**Fix-attempt:**` (zero or more, repeatable), and
  // every Confidence must precede every Fix-attempt. Any other label line appearing after
  // Last-checked is an error. Multi-line values are fine — only lines that are themselves label
  // lines (start with a `**...:**` token) are considered here; continuation prose is skipped.
  let confidenceIdx;
  let deploymentStateIdx;
  let sawFixAttempt = false;
  for (let i = lcLineIdx + 1; i < blockEndIdx; i++) {
    if (!isLabelLine(lines[i])) continue;
    const line = lines[i];

    if (lineStartsWithLabel(line, CONFIDENCE_LABEL)) {
      if (confidenceIdx !== undefined) {
        addError(i, `label "${CONFIDENCE_LABEL}" appears more than once (want at most 1)`);
        ok = false;
        continue;
      }
      if (deploymentStateIdx !== undefined || sawFixAttempt) {
        addError(
          i,
          `"${CONFIDENCE_LABEL}" must appear before "${DEPLOYMENT_STATE_LABEL}" and any "${FIX_ATTEMPT_LABEL}" line`,
        );
        ok = false;
        continue;
      }
      confidenceIdx = i;
      const confValue = line.replace(/^\s+/, "").replace(CONFIDENCE_LABEL, "").trim();
      if (!CONFIDENCE_VALUES.has(confValue)) {
        addError(
          i,
          `"${CONFIDENCE_LABEL}" value "${confValue}" is not one of: ${[...CONFIDENCE_VALUES].join(", ")}`,
        );
        ok = false;
      }
    } else if (lineStartsWithLabel(line, DEPLOYMENT_STATE_LABEL)) {
      if (deploymentStateIdx !== undefined) {
        addError(i, `label "${DEPLOYMENT_STATE_LABEL}" appears more than once (want at most 1)`);
        ok = false;
        continue;
      }
      if (sawFixAttempt) {
        addError(i, `"${DEPLOYMENT_STATE_LABEL}" must appear before any "${FIX_ATTEMPT_LABEL}" line`);
        ok = false;
        continue;
      }
      deploymentStateIdx = i;
      const value = line.replace(/^\s+/, "").replace(DEPLOYMENT_STATE_LABEL, "").trim();
      if (!DEPLOYMENT_STATE_RE.test(value)) {
        addError(i, `"${DEPLOYMENT_STATE_LABEL}" must be active, not-applicable, unverified-from-repo, or pending (reason)`);
        ok = false;
      }
    } else if (lineStartsWithLabel(line, FIX_ATTEMPT_LABEL)) {
      sawFixAttempt = true;
    } else {
      addError(
        i,
        `unexpected label after "**Last-checked:**": only "${CONFIDENCE_LABEL}" and "${DEPLOYMENT_STATE_LABEL}" ` +
          `(at most one each) then "${FIX_ATTEMPT_LABEL}" (repeatable) are permitted — found: ${line.trim()}`,
      );
      ok = false;
    }
  }

  if (!ok) return null;
  return { severity, status };
}

function validateFindingsFile(filePath, scope, domain, workspaceDir) {
  const rel = relative(workspaceDir, filePath);
  const errors = [];
  const addError = (lineIdx, message) => {
    // lineIdx is a 0-based index into `lines`; report 1-based line numbers.
    errors.push({ line: lineIdx + 1, message });
  };

  let content;
  try {
    content = readFileSync(filePath, "utf8");
  } catch (err) {
    return { rel, errors: [{ line: 1, message: `could not read file: ${err.message}` }], counts: null };
  }

  if (!(domain in DOMAIN_CODES)) {
    return {
      rel,
      errors: [{ line: 1, message: `unknown domain "${domain}" (not in the domain-code table)` }],
      counts: null,
    };
  }

  const lines = content.split("\n");

  // check 3: malformed finding-shaped headings anywhere in the file
  for (const m of scanMalformedHeadings(lines)) {
    addError(m.lineIdx, `malformed finding heading (must be canonical column-0 "## " grammar): ${m.text}`);
  }

  const blocks = splitFindingBlocks(lines);

  // check 5: empty findings file must have the header stamp
  if (blocks.length === 0) {
    if (!HEADER_STAMP_RE.test(content)) {
      addError(1, `empty findings file is missing the file header stamp ("> Generated: ... scope: ...")`);
    }
    return { rel, errors, counts: { total: 0, bySeverity: {}, byStatus: {} } };
  }

  const bySeverity = { "🔴": 0, "🟡": 0, "🟢": 0 };
  const byStatus = {};
  let total = 0;

  for (const block of blocks) {
    const result = validateBlock(block, content, lines, scope, domain, errors, addError);
    if (result) {
      total++;
      bySeverity[result.severity] = (bySeverity[result.severity] || 0) + 1;
      // Normalize "fixed (merged into X)" into "fixed (merged)" bucket for reporting brevity.
      const statusKey = result.status.startsWith("fixed (merged into")
        ? "fixed (merged)"
        : result.status.startsWith("wontfix")
          ? "wontfix"
          : result.status;
      byStatus[statusKey] = (byStatus[statusKey] || 0) + 1;
    }
  }

  return { rel, errors, counts: { total, bySeverity, byStatus } };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const argPath = process.argv[2];
if (!argPath) {
  usageError("usage: node validate-findings.mjs <path-to-.craftsman-workspace-or-project-root>");
}

const workspaceDir = resolveWorkspaceDir(argPath);
let files;
try {
  files = findFindingsFiles(workspaceDir);
} catch (err) {
  usageError(err.message);
}

if (files.length === 0) {
  usageError(`no audits/<scope>/<domain>/findings.md files found under ${workspaceDir}`);
}

let totalErrors = 0;
let filesPassed = 0;
let totalFindings = 0;

for (const { path: filePath, scope, domain } of files) {
  const { rel, errors, counts } = validateFindingsFile(filePath, scope, domain, workspaceDir);

  if (errors.length > 0) {
    for (const e of errors) {
      console.error(`${rel}:${e.line}: ${e.message}`);
    }
    totalErrors += errors.length;
    continue;
  }

  filesPassed++;
  totalFindings += counts.total;

  const sevParts = SEVERITY_ORDER.map((s) => `${s} ${counts.bySeverity[s] || 0}`).join(" / ");
  const statusParts =
    Object.keys(counts.byStatus).length > 0
      ? Object.entries(counts.byStatus)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([status, n]) => `${status}=${n}`)
          .join(", ")
      : "none";
  console.log(
    `OK: ${rel} — ${counts.total} finding(s) — severity: ${sevParts} — status: ${statusParts}`,
  );
}

console.log("");
console.log(
  `${filesPassed}/${files.length} findings.md file(s) passed, ${totalFindings} finding(s) validated, errors=${totalErrors}.`,
);

if (totalErrors > 0) {
  console.log(`FAIL: ${totalErrors} error(s) across ${files.length - filesPassed} file(s).`);
  process.exit(1);
}

console.log(`OK: all ${files.length} findings.md file(s) passed mechanical validation.`);
process.exit(0);
