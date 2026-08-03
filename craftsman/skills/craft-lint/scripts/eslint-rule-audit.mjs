#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

// NOTE: This script assumes it is run against the REPOSITORY ROOT (where the git root /
// top-level node_modules lives), not an individual workspace package. findUpPackageVersion()
// and the eslint-entry resolver walk upward from each package dir but stop at targetRoot —
// if you point this script at a single workspace package in a monorepo with hoisted
// dependencies at the true repo root (a parent of targetRoot), eslint/typescript-eslint
// resolution will incorrectly report "no-eslint-bin" / missing versions. Always invoke this
// script with the repo root as argv[2] (or omit argv[2] to use the current working directory,
// provided you cd to the repo root first).

const targetRoot = path.resolve(process.argv[2] || process.cwd());
const outDir = path.join(targetRoot, ".craftsman", "lint-audit");
fs.mkdirSync(outDir, { recursive: true });

const skip = new Set([
  "node_modules",
  ".git",
  ".next",
  ".claude",
  "venv",
  "dist",
  "build",
  "coverage",
  ".turbo",
  ".vercel",
  ".output",
  ".svelte-kit",
  ".nuxt",
  "out",
  "vendor",
]);

const configNames = new Set([
  "eslint.config.js",
  "eslint.config.mjs",
  "eslint.config.cjs",
  "eslint.config.ts",
  "eslint.config.mts",
  "eslint.config.cts",
  ".eslintrc",
  ".eslintrc.js",
  ".eslintrc.cjs",
  ".eslintrc.json",
  ".eslintrc.yml",
  ".eslintrc.yaml",
]);

const standardRules = [
  "@typescript-eslint/no-explicit-any",
  "@typescript-eslint/no-floating-promises",
  "@typescript-eslint/no-misused-promises",
  "@typescript-eslint/await-thenable",
  "@typescript-eslint/no-unsafe-assignment",
  "@typescript-eslint/no-unsafe-call",
  "@typescript-eslint/no-unsafe-member-access",
  "@typescript-eslint/no-unsafe-return",
  "@typescript-eslint/no-unsafe-argument",
  "@typescript-eslint/strict-boolean-expressions",
  "@typescript-eslint/no-unnecessary-condition",
  "@typescript-eslint/switch-exhaustiveness-check",
  "@typescript-eslint/no-non-null-assertion",
  "@typescript-eslint/consistent-type-imports",
  "@typescript-eslint/no-import-type-side-effects",
  "react-hooks/rules-of-hooks",
  "react-hooks/exhaustive-deps",
  "react/jsx-no-leaked-render",
  "jsx-a11y/alt-text",
  "jsx-a11y/anchor-is-valid",
  "eqeqeq",
  "curly",
  "no-debugger",
  "no-console",
  "no-restricted-properties",
  "no-restricted-imports",
  "no-restricted-syntax",
  "sonarjs/cognitive-complexity",
  "security/detect-eval-with-expression",
  "security/detect-object-injection",
];

function excluded(filePath) {
  return filePath.split(path.sep).some((segment) => skip.has(segment));
}

function walk(dir, predicate, out = []) {
  let entries = [];
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (excluded(fullPath)) continue;
    if (entry.isDirectory()) walk(fullPath, predicate, out);
    else if (predicate(fullPath, entry.name)) out.push(fullPath);
  }
  return out;
}

function readPackage(dir) {
  try {
    return JSON.parse(fs.readFileSync(path.join(dir, "package.json"), "utf8"));
  } catch {
    return {};
  }
}

function findPackageDirs() {
  return walk(targetRoot, (_filePath, name) => name === "package.json").map((filePath) =>
    path.dirname(filePath),
  );
}

function findUpPackageVersion(start, packageName) {
  let current = start;
  while (current.startsWith(targetRoot)) {
    const packageFile = path.join(current, "node_modules", packageName, "package.json");
    if (fs.existsSync(packageFile)) {
      try {
        return JSON.parse(fs.readFileSync(packageFile, "utf8")).version;
      } catch {
        return null;
      }
    }
    const next = path.dirname(current);
    if (next === current) break;
    current = next;
  }
  return null;
}

function findEslintEntry(start) {
  let current = start;
  while (current.startsWith(targetRoot)) {
    const eslintDir = path.join(current, "node_modules", "eslint");
    const pkgFile = path.join(eslintDir, "package.json");
    if (fs.existsSync(pkgFile)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(pkgFile, "utf8"));
        const bin = typeof pkg.bin === "string" ? pkg.bin : pkg.bin?.eslint;
        if (bin) return path.join(eslintDir, bin);
      } catch {
        return null;
      }
    }
    const next = path.dirname(current);
    if (next === current) break;
    current = next;
  }
  return null;
}

function hasLocalConfig(dir) {
  try {
    return fs.readdirSync(dir).some((name) => configNames.has(name));
  } catch {
    return false;
  }
}

function hasLintScript(dir) {
  const pkg = readPackage(dir);
  return Object.entries(pkg.scripts || {}).some(([name, value]) =>
    /lint|eslint/i.test(`${name} ${value}`),
  );
}

function findRepresentativeFile(dir) {
  const files = walk(
    dir,
    (filePath, name) =>
      /\.(tsx|ts|jsx|js|mjs|cjs)$/.test(name) &&
      !/\.d\.ts$/.test(name) &&
      !/eslint|prettier|postcss|tailwind|next\.config|vite\.config/i.test(filePath),
  );
  const sourceDirs = new Set(["src", "app", "apps", "packages", "lib", "server", "worker"]);
  const sourceLike = files.filter((filePath) =>
    filePath.split(path.sep).some((segment) => sourceDirs.has(segment)),
  );
  return sourceLike[0] || files[0] || null;
}

function severity(value) {
  if (value == null) return "missing";
  const raw = Array.isArray(value) ? value[0] : value;
  if (raw === 2 || raw === "error") return "error";
  if (raw === 1 || raw === "warn") return "warn";
  if (raw === 0 || raw === "off") return "off";
  return String(raw);
}

const packageDirs = findPackageDirs();
const targets = packageDirs.filter(
  (dir) => hasLocalConfig(dir) || hasLintScript(dir) || findUpPackageVersion(dir, "eslint"),
);

const results = [];
for (const dir of targets) {
  const pkg = readPackage(dir);
  const representative = findRepresentativeFile(dir);
  const eslintEntry = findEslintEntry(dir);
  const result = {
    dir,
    rel: path.relative(targetRoot, dir) || ".",
    name: pkg.name || path.basename(dir),
    eslintVersion: findUpPackageVersion(dir, "eslint"),
    tseslintVersion:
      findUpPackageVersion(dir, "typescript-eslint") ||
      findUpPackageVersion(dir, "@typescript-eslint/eslint-plugin"),
    representative: representative ? path.relative(dir, representative) : null,
    status: "not-run",
    ruleCount: null,
    rules: {},
    error: null,
  };

  if (!eslintEntry || !representative) {
    result.status = !eslintEntry ? "no-eslint-bin" : "no-representative-file";
    results.push(result);
    continue;
  }

  const printed = spawnSync(process.execPath, [eslintEntry, "--print-config", representative], {
    cwd: dir,
    encoding: "utf8",
    timeout: 30000,
    maxBuffer: 20 * 1024 * 1024,
  });

  if (printed.status !== 0 || printed.error) {
    result.status = "print-config-failed";
    result.error = printed.error
      ? String(printed.error)
      : (printed.stderr || printed.stdout || "").slice(0, 4000);
    if (printed.signal) {
      result.error = `${result.error} (terminated by signal: ${printed.signal})`;
    }
    result.error = result.error.slice(0, 4000);
    results.push(result);
    continue;
  }

  try {
    const config = JSON.parse(printed.stdout);
    result.status = "ok";
    result.rules = config.rules || {};
    result.ruleCount = Object.keys(result.rules).length;
    result.plugins = config.plugins || [];
  } catch (error) {
    result.status = "json-parse-failed";
    result.error = String(error).slice(0, 1000);
  }
  results.push(result);
}

const rows = results.map((result) => {
  if (result.status !== "ok") {
    return {
      project: result.rel,
      name: result.name,
      status: result.status,
      eslintVersion: result.eslintVersion,
      tseslintVersion: result.tseslintVersion,
      representative: result.representative,
      ruleCount: result.ruleCount,
      errorRules: null,
      warn: null,
      off: null,
      missing: null,
      missingRules: [],
      warningRules: [],
      offRules: [],
      error: result.error,
    };
  }
  const ruleStatuses = Object.fromEntries(
    standardRules.map((rule) => [rule, severity(result.rules?.[rule])]),
  );
  const missingRules = standardRules.filter((rule) => ruleStatuses[rule] === "missing");
  const warningRules = standardRules.filter((rule) => ruleStatuses[rule] === "warn");
  const offRules = standardRules.filter((rule) => ruleStatuses[rule] === "off");
  const errorRules = standardRules.filter((rule) => ruleStatuses[rule] === "error");
  return {
    project: result.rel,
    name: result.name,
    status: result.status,
    eslintVersion: result.eslintVersion,
    tseslintVersion: result.tseslintVersion,
    representative: result.representative,
    ruleCount: result.ruleCount,
    errorRules: errorRules.length,
    warn: warningRules.length,
    off: offRules.length,
    missing: missingRules.length,
    missingRules,
    warningRules,
    offRules,
    error: result.error,
  };
});

const topProjectSummaries = [];
const byTop = new Map();
for (const row of rows) {
  const top = row.project.split(path.sep)[0] || ".";
  if (!byTop.has(top)) byTop.set(top, []);
  byTop.get(top).push(row);
}
for (const [project, projectRows] of byTop) {
  const resolved = projectRows.filter((row) => row.status === "ok");
  const best = resolved
    .slice()
    .sort((a, b) => b.errorRules - a.errorRules || a.missing - b.missing)[0];
  topProjectSummaries.push({
    project,
    packages: projectRows.length,
    resolved: resolved.length,
    failed: projectRows.length - resolved.length,
    bestErrorRules: best?.errorRules || 0,
    bestRuleCount: best?.ruleCount || null,
    bestPackage: best?.project || null,
    commonGaps: best
      ? [
          ...best.missingRules.slice(0, 8),
          ...best.warningRules.slice(0, 4).map((rule) => `${rule} (warn)`),
          ...best.offRules.slice(0, 4).map((rule) => `${rule} (off)`),
        ].slice(0, 12)
      : ["no resolved config"],
  });
}

topProjectSummaries.sort(
  (a, b) => b.bestErrorRules - a.bestErrorRules || a.project.localeCompare(b.project),
);

fs.writeFileSync(
  path.join(outDir, "resolved-print-config-results.json"),
  JSON.stringify(results, null, 2),
);
fs.writeFileSync(
  path.join(outDir, "resolved-print-config-summary.json"),
  JSON.stringify(
    results.map((result) => ({
      project: result.rel,
      name: result.name,
      status: result.status,
      eslintVersion: result.eslintVersion,
      tseslintVersion: result.tseslintVersion,
      representative: result.representative,
      ruleCount: result.ruleCount,
      error: result.error?.split("\n").slice(0, 3).join(" "),
    })),
    null,
    2,
  ),
);
fs.writeFileSync(
  path.join(outDir, "standard-rule-gap-matrix.json"),
  JSON.stringify({ standardRules, rows }, null, 2),
);
fs.writeFileSync(
  path.join(outDir, "top-project-gap-summary.json"),
  JSON.stringify(topProjectSummaries, null, 2),
);

const markdown = [];
markdown.push("# ESLint Standard Rule Gap Matrix", "");
markdown.push(
  "Generated from `eslint --print-config` where possible. Failed/no-install projects require fallback config-file inspection.",
  "",
);
markdown.push("| Project/package | ESLint | Status | Resolved rules | Standard errors | Warn | Off | Missing | Biggest gaps |");
markdown.push("| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |");
for (const row of rows.sort((a, b) => a.project.localeCompare(b.project))) {
  const gaps =
    [
      ...row.missingRules.slice(0, 6),
      ...row.warningRules.slice(0, 3).map((rule) => `${rule} (warn)`),
      ...row.offRules.slice(0, 3).map((rule) => `${rule} (off)`),
    ]
      .slice(0, 8)
      .map((rule) => `\`${rule}\``)
      .join("<br>") || "none";
  markdown.push(
    `| \`${row.project}\` | ${row.eslintVersion || "none"} | ${row.status} | ${row.ruleCount ?? ""} | ${row.errorRules ?? "—"} / ${standardRules.length} | ${row.warn ?? "—"} | ${row.off ?? "—"} | ${row.missing ?? "—"} | ${gaps} |`,
  );
}
fs.writeFileSync(path.join(outDir, "standard-rule-gap-matrix.md"), markdown.join("\n"));

console.log(`Wrote lint audit to ${outDir}`);
console.log(`Resolved ${rows.filter((row) => row.status === "ok").length}/${rows.length} targets.`);
