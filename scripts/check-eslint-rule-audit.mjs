#!/usr/bin/env node
// Regression checks for craft-lint's user-facing helper. No dependencies.

import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const helper = join(ROOT, "craftsman", "skills", "craft-lint", "scripts", "eslint-rule-audit.mjs");
const testRoot = mkdtempSync(join(tmpdir(), "craftsman-lint-audit-"));
let failures = 0;

function check(condition, message) {
  if (condition) console.log(`OK: ${message}`);
  else {
    console.error(`FAIL: ${message}`);
    failures++;
  }
}

try {
  const help = spawnSync(process.execPath, [helper, "--help"], { encoding: "utf8" });
  check(help.status === 0, "--help exits successfully");
  check(help.stdout.includes("Usage: node eslint-rule-audit.mjs"), "--help prints usage");
  check(!existsSync(join(ROOT, "--help")), "--help does not create a workspace in the current directory");

  const missingRoot = join(testRoot, "does-not-exist");
  const invalid = spawnSync(process.execPath, [helper, missingRoot], { encoding: "utf8" });
  check(invalid.status === 2, "a missing root exits with a usage error");
  check(invalid.stderr.includes("repository root does not exist"), "a missing root explains the failure");
  check(!existsSync(missingRoot), "a missing root is never created");
} finally {
  rmSync(testRoot, { recursive: true, force: true });
}

if (failures > 0) process.exit(1);
