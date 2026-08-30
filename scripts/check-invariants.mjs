#!/usr/bin/env node
// Invariant checks for the craftsman-marketplace repo. No dependencies — plain Node.
//
// Checks:
//   (a) all 3 plugin/marketplace JSON files parse
//   (b) every plugins/craftsman/skills/*/references/*.md file is mentioned in its skill's SKILL.md,
//       and every reference mentioned in a SKILL.md reference-index section exists on disk
//   (c) every SKILL.md contains the exact heading "## Audit checklist (for craft-audit)"
//   (d) every SKILL.md frontmatter description is <=1200 chars
//   (e) no tracked .md file contains the literal string "/Volumes/"
//   (f) findings emission contract:
//       (f1) every plugins/craftsman/examples/**/findings.md matches the canonical heading/body grammar
//       (f2) every domain skill restates "Canonical findings.md emission format" + its DOMAINCODE
//       (f3) soft: craft-audit/SKILL.md contains path-binding language ("Path binding")
//   (g) vendored third-party content stays inert data:
//       (g1) web-interface-guidelines.md keeps its provenance rows (pinned commit + source hash)
//       (g2) its rule list carries no URL, prompt-template marker, or code fence, and no
//            soft-flagged tool/network verb
//       (g3) review-protocol.md still carries the do-not-fetch-at-review-time prohibition
//   (h) every `references/x.md` pointer resolves in its own skill, or in the
//       block-scoped skill that qualifies it
//   (i) taxcraft parity: manifests parse and agree on version, every marketplace source
//       path exists, the tax description fits, and every concrete router-table path exists
//
// Run: node scripts/check-invariants.mjs

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, dirname, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

let failures = 0;
let warnings = 0;

function fail(msg) {
  console.error(`FAIL: ${msg}`);
  failures++;
}

function warn(msg) {
  console.warn(`WARN: ${msg}`);
  warnings++;
}

function ok(msg) {
  console.log(`OK: ${msg}`);
}

// ---------------------------------------------------------------------------
// (a) JSON manifests parse
// ---------------------------------------------------------------------------
function checkJsonManifests() {
  const manifests = [
    ".claude-plugin/marketplace.json",
    "plugins/craftsman/.claude-plugin/plugin.json",
    "plugins/craftsman/.codex-plugin/plugin.json",
  ];
  const parsed = new Map();
  for (const rel of manifests) {
    const path = join(ROOT, rel);
    try {
      const raw = readFileSync(path, "utf8");
      parsed.set(rel, JSON.parse(raw));
      ok(`${rel} parses as valid JSON`);
    } catch (err) {
      fail(`${rel} failed to parse: ${err.message}`);
    }
  }

  const versions = [
    parsed.get(".claude-plugin/marketplace.json")?.plugins?.find((plugin) => plugin.name === "craftsman")?.version,
    parsed.get("plugins/craftsman/.claude-plugin/plugin.json")?.version,
    parsed.get("plugins/craftsman/.codex-plugin/plugin.json")?.version,
  ];
  if (versions.every(Boolean) && new Set(versions).size === 1) {
    ok(`all plugin manifests declare version ${versions[0]}`);
  } else {
    fail(`plugin manifest versions disagree: ${versions.map((version) => version || "missing").join(", ")}`);
  }

  const codexInterface = parsed.get("plugins/craftsman/.codex-plugin/plugin.json")?.interface;
  for (const key of ["composerIcon", "logo"]) {
    const asset = codexInterface?.[key];
    if (typeof asset !== "string" || !asset.startsWith("./")) {
      fail(`plugins/craftsman/.codex-plugin/plugin.json: interface.${key} must be a relative asset path`);
      continue;
    }
    const assetPath = join(ROOT, "plugins", "craftsman", asset.slice(2));
    if (!existsSync(assetPath)) {
      fail(`plugins/craftsman/.codex-plugin/plugin.json: interface.${key} points to missing asset ${asset}`);
    } else {
      ok(`plugins/craftsman/.codex-plugin/plugin.json: interface.${key} asset exists`);
    }
  }
}

// ---------------------------------------------------------------------------
// Helpers for skill discovery
// ---------------------------------------------------------------------------
function getSkillDirs() {
  const skillsRoot = join(ROOT, "plugins", "craftsman", "skills");
  return readdirSync(skillsRoot)
    .filter((name) => statSync(join(skillsRoot, name)).isDirectory())
    .map((name) => join(skillsRoot, name));
}

// Folders under references/ that hold non-prose fixture/example assets rather than reference docs
// proper (e.g. craft-ux's scanner-fixtures/*.tsx + its own README). Not part of the reference index.
const FIXTURE_DIR_NAMES = new Set(["scanner-fixtures"]);

function listReferenceMdFiles(skillDir) {
  const refsDir = join(skillDir, "references");
  const results = [];
  try {
    const walk = (dir) => {
      for (const entry of readdirSync(dir)) {
        const full = join(dir, entry);
        if (statSync(full).isDirectory()) {
          if (FIXTURE_DIR_NAMES.has(entry)) continue;
          walk(full);
        } else if (entry.endsWith(".md")) {
          results.push(relative(refsDir, full).replace(/\\/g, "/"));
        }
      }
    };
    walk(refsDir);
  } catch {
    // no references/ dir — fine for a skill with none, though all current skills have one
  }
  return results;
}

// ---------------------------------------------------------------------------
// (b) reference cross-linking
// ---------------------------------------------------------------------------

// Extracts the text of the "## Reference index" section: from that heading line
// (inclusive) to the next line starting with "## " (exclusive), or end of file.
function extractReferenceIndexSection(skillMd, skillName) {
  const lines = skillMd.split("\n");
  const startIdx = lines.findIndex((l) => l.trim() === "## Reference index");
  if (startIdx === -1) {
    fail(`${skillName}: missing "## Reference index" heading in SKILL.md`);
    return null;
  }
  let endIdx = lines.length;
  for (let i = startIdx + 1; i < lines.length; i++) {
    if (lines[i].startsWith("## ")) {
      endIdx = i;
      break;
    }
  }
  return lines.slice(startIdx, endIdx).join("\n");
}

function checkReferenceCrossLinking() {
  for (const skillDir of getSkillDirs()) {
    const skillName = relative(join(ROOT, "plugins", "craftsman", "skills"), skillDir);
    const skillMdPath = join(skillDir, "SKILL.md");
    let skillMd;
    try {
      skillMd = readFileSync(skillMdPath, "utf8");
    } catch {
      fail(`${skillName}: missing SKILL.md`);
      continue;
    }

    const onDisk = new Set(listReferenceMdFiles(skillDir));

    const indexSection = extractReferenceIndexSection(skillMd, skillName);
    if (indexSection == null) continue;

    // Every reference path mentioned in the "## Reference index" section as `references/...md`,
    // excluding cross-references to another skill's own references (e.g.
    // "craft-security references/authz.md" or "craft-security → `references/authz.md`") — those
    // point at a different skill's files, not this skill's own reference index, so they're
    // intentionally not required to exist here.
    const CROSS_SKILL_PREFIX = /`?(?:craft-[a-z0-9-]*)`?\s*(?:→|->)?\s*`?$/i;
    const mentioned = new Set();
    for (const m of indexSection.matchAll(/references\/([A-Za-z0-9_\-./]+\.md)/g)) {
      const before = indexSection.slice(Math.max(0, m.index - 40), m.index);
      if (CROSS_SKILL_PREFIX.test(before)) continue;
      mentioned.add(m[1]);
    }

    // (b1) every file on disk is mentioned in the Reference index section
    for (const file of onDisk) {
      if (!mentioned.has(file)) {
        fail(`${skillName}: references/${file} exists on disk but is not mentioned in SKILL.md's "## Reference index" section`);
      }
    }

    // (b2) every reference mentioned in the Reference index section exists on disk
    for (const file of mentioned) {
      if (!onDisk.has(file)) {
        fail(`${skillName}: SKILL.md's "## Reference index" section mentions references/${file} but it does not exist on disk`);
      }
    }

    if ([...onDisk].every((f) => mentioned.has(f)) && [...mentioned].every((f) => onDisk.has(f))) {
      ok(`${skillName}: reference index matches references/ on disk (${onDisk.size} files)`);
    }
  }
}

// ---------------------------------------------------------------------------
// (b2) cross-skill pointer validation
// ---------------------------------------------------------------------------

// Generic recursive .md finder, rooted at plugins/craftsman/skills — covers SKILL.md and
// every references/*.md (including nested dirs, e.g. craft-ux's motion/ subfolder).
function findAllSkillMdFiles() {
  const skillsRoot = join(ROOT, "plugins", "craftsman", "skills");
  const results = [];
  const walk = (dir) => {
    for (const entry of readdirSync(dir)) {
      const full = join(dir, entry);
      if (statSync(full).isDirectory()) {
        walk(full);
      } else if (entry.endsWith(".md")) {
        results.push(full);
      }
    }
  };
  walk(skillsRoot);
  return results;
}

// Cross-skill pointer patterns. Each matches `<skill>-craft ... <file>.md` in one of the
// prose shapes actually used across these docs (backtick-wrapped skill name + arrow +
// backtick-wrapped file, plain "references/" mentions, or a direct path). The gap between
// skill token and filename is bounded and excludes newlines so we don't span paragraphs.
const CROSS_SKILL_PATTERNS = [
  // "craft-security ... references/authz.md" (literal "references/" substring)
  /(craft-[a-z0-9-]*)[^\n]{0,80}?references\/([a-z0-9-]+\.md)/g,
  // "`craft-security` → `authz.md`" / "craft-security's `authz.md`" (backtick-only form)
  /(craft-[a-z0-9-]*)[`*'"\s]{0,10}(?:→|->|'s)[^\n]{0,60}?`([a-z0-9-]+\.md)`/g,
  // direct path form: "craft-security/references/authz.md"
  /(craft-[a-z0-9-]*)\/references\/([a-z0-9-]+\.md)/g,
];

function checkCrossSkillPointers() {
  const skillsRoot = join(ROOT, "plugins", "craftsman", "skills");
  for (const file of findAllSkillMdFiles()) {
    const relPath = relative(ROOT, file);
    // The skill this file itself belongs to, e.g. "plugins/craftsman/skills/craft-backend/..." -> "craft-backend"
    const ownSkill = relative(skillsRoot, file).split("/")[0];
    const text = readFileSync(file, "utf8");

    const seen = new Set(); // dedupe identical (skill, file) pairs per source file
    for (const pattern of CROSS_SKILL_PATTERNS) {
      for (const m of text.matchAll(pattern)) {
        const skillTok = m[1];
        const fileTok = m[m.length - 1];
        if (skillTok === ownSkill) continue; // self-reference — covered by (b)
        const key = `${skillTok}/${fileTok}`;
        if (seen.has(key)) continue;
        seen.add(key);

        // If the file actually lives under the CURRENT file's own skill's references/,
        // this is a self-reference misattributed to a nearby-but-unrelated skill token
        // (e.g. an aside like "...serverless pooling constraints → craft-infra) →
        // `references/connection-pooling.md`" where connection-pooling.md is this skill's
        // own file, not craft-infra's). Skip it — already covered by (b).
        if (existsSync(join(skillsRoot, ownSkill, "references", fileTok))) continue;

        const target = join(skillsRoot, skillTok, "references", fileTok);
        if (!existsSync(target)) {
          fail(
            `${relPath}: cross-skill pointer "${skillTok}...${fileTok}" but plugins/craftsman/skills/${skillTok}/references/${fileTok} does not exist`
          );
        }
      }
    }
  }
  ok("cross-skill pointers all resolve to files that exist");
}

// ---------------------------------------------------------------------------
// (c) exact audit-checklist heading present
// ---------------------------------------------------------------------------
function checkAuditChecklistHeading() {
  const HEADING = "## Audit checklist (for craft-audit)";
  // craft-fix is an action skill, not an audit domain — it fixes findings that
  // craft-audit produces, so it has no domain checklist for the orchestrator to source.
  const EXEMPT_SKILLS = new Set(["craft-fix"]);
  for (const skillDir of getSkillDirs()) {
    const skillName = relative(join(ROOT, "plugins", "craftsman", "skills"), skillDir);
    if (EXEMPT_SKILLS.has(skillName)) {
      ok(`${skillName}: exempt from "${HEADING}" heading requirement (action skill, not an audit domain)`);
      continue;
    }
    const skillMdPath = join(skillDir, "SKILL.md");
    let skillMd;
    try {
      skillMd = readFileSync(skillMdPath, "utf8");
    } catch {
      continue; // already reported in (b)
    }
    if (skillMd.includes(HEADING)) {
      ok(`${skillName}: has exact "${HEADING}" heading`);
    } else {
      fail(`${skillName}: missing exact heading "${HEADING}"`);
    }
  }
}

// ---------------------------------------------------------------------------
// (d) frontmatter description length
// ---------------------------------------------------------------------------
function checkDescriptionLength() {
  const MAX = 1200;
  for (const skillDir of getSkillDirs()) {
    const skillName = relative(join(ROOT, "plugins", "craftsman", "skills"), skillDir);
    const skillMdPath = join(skillDir, "SKILL.md");
    let skillMd;
    try {
      skillMd = readFileSync(skillMdPath, "utf8");
    } catch {
      continue;
    }

    const frontmatterMatch = skillMd.match(/^---\n([\s\S]*?)\n---/);
    if (!frontmatterMatch) {
      fail(`${skillName}: SKILL.md has no frontmatter block`);
      continue;
    }
    const frontmatter = frontmatterMatch[1];

    // description: >-  (folded block scalar) followed by indented lines, until a line at column 0
    const descMatch = frontmatter.match(/description:\s*>-\n((?:[ \t]+.*\n?)+)/);
    let description;
    if (descMatch) {
      description = descMatch[1]
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean)
        .join(" ");
    } else {
      // fall back to a plain single-line description: "..."
      const plainMatch = frontmatter.match(/description:\s*(.+)/);
      description = plainMatch ? plainMatch[1].trim().replace(/^["']|["']$/g, "") : null;
    }

    if (description == null) {
      fail(`${skillName}: could not find a description: field in frontmatter`);
      continue;
    }

    if (description.length <= MAX) {
      ok(`${skillName}: description is ${description.length} chars (<= ${MAX})`);
    } else {
      fail(`${skillName}: description is ${description.length} chars, exceeds ${MAX}`);
    }
  }
}

// ---------------------------------------------------------------------------
// (e) no /Volumes/ literal in any tracked .md file
// ---------------------------------------------------------------------------
function listTrackedMdFiles() {
  // Uses `git ls-files` since this repo is a git repo in every environment this runs (local + CI).
  // execFileSync (argument array, no shell) avoids any command-injection risk from the pattern arg.
  const out = execFileSync("git", ["ls-files", "*.md"], { cwd: ROOT, encoding: "utf8" });
  return out.split("\n").filter(Boolean);
}

function checkNoAbsoluteVolumesPaths() {
  let files;
  try {
    files = listTrackedMdFiles();
  } catch (err) {
    warn(`could not list tracked .md files via git (${err.message}); skipping check (e)`);
    return;
  }

  for (const rel of files) {
    let content;
    try {
      content = readFileSync(join(ROOT, rel), "utf8");
    } catch {
      continue; // tracked but not present locally (shouldn't happen) — skip rather than crash
    }
    if (content.includes("/Volumes/")) {
      fail(`${rel}: contains a literal "/Volumes/" absolute path`);
    }
  }
  ok(`no tracked .md file contains a literal "/Volumes/" path`);
}

// ---------------------------------------------------------------------------
// (f) findings emission contract
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

const HEADING_RE =
  /^## ([A-Za-z0-9][A-Za-z0-9-]*)-(UX|FE|BE|DB|SEC|INFRA|OBS|TEST|LINT|AI)-(\d{3}) · severity ([🔴🟡🟢]) · status (open|fixed|regressed|wontfix \(.+\)|fixed \(merged into .+\))$/u;
const LAST_CHECKED_RE = /^\d{4}-\d{2}-\d{2} · ([0-9a-f]{4,40}|none \(no git\))$/;
const FP_RE = /`scope=([^`]+) · domain=([^`]+) · class=([^`]+) · resource=([^`]+)`/;
// Fix-attempt: YYYY-MM-DD · <identity> · <text>
// identity = literal "working-tree" OR short/full git sha (7–40 hex). Optional " · did not hold (...)" suffix.
const FIX_ATTEMPT_LINE_RE =
  /^\*\*Fix-attempt:\*\* (\d{4}-\d{2}-\d{2}) · (working-tree|[0-9a-f]{7,40}) · .+/;
const FIX_ATTEMPT_LABEL = "**Fix-attempt:**";
const CONFIDENCE_LABEL = "**Confidence:**";
const CONFIDENCE_VALUES = new Set(["verified", "inferred", "unverified-from-repo"]);
const DEPLOYMENT_STATE_LABEL = "**Deployment-state:**";
const DEPLOYMENT_STATE_RE = /^(active|not-applicable|unverified-from-repo|pending \(.+\))$/;

const REQUIRED_LABELS = [
  "**What breaks (plain language):**",
  "**Technical:**",
  "**Fix:**",
  "**Fingerprint:**",
  "**Last-checked:**",
];

function findExampleFindingsFiles() {
  const examplesRoot = join(ROOT, "plugins", "craftsman", "examples");
  const results = [];
  if (!existsSync(examplesRoot)) return results;
  const walk = (dir) => {
    for (const entry of readdirSync(dir)) {
      const full = join(dir, entry);
      if (statSync(full).isDirectory()) {
        walk(full);
      } else if (entry === "findings.md") {
        results.push(full);
      }
    }
  };
  walk(examplesRoot);
  return results;
}

function parseFindingsPath(filePath) {
  // Expect: .../.craftsman/audits/<scope...>/<domain>/findings.md
  // scope may be multi-segment (apps/web); domain is the last directory before findings.md.
  const parts = filePath.split(/[/\\]/);
  const auditsIdx = parts.lastIndexOf("audits");
  if (auditsIdx === -1) return null;
  const after = parts.slice(auditsIdx + 1); // [scope..., domain, findings.md]
  if (after.length < 3 || after[after.length - 1] !== "findings.md") return null;
  const domain = after[after.length - 2];
  const scopeParts = after.slice(0, -2);
  if (scopeParts.length === 0) return null;
  return { scope: scopeParts.join("/"), domain };
}

function splitFindingBlocks(content) {
  // Only column-0 `## ` starts a finding block — that is the canonical form.
  // Non-canonical finding-shaped headings are rejected separately by scanFindingShapedHeadings.
  const lines = content.split("\n");
  const blocks = [];
  let current = null;
  for (const line of lines) {
    if (line.startsWith("## ")) {
      if (current) blocks.push(current);
      current = { heading: line, body: [] };
    } else if (current) {
      current.body.push(line);
    }
  }
  if (current) blocks.push(current);
  return blocks;
}

// Finding-shaped heading detector — used to reject non-canonical finding headings
// (incl. empty-file bypass via #/###, indent, Setext, blockquote, list containers).
const FINDING_SHAPED_HEADING =
  /severity\s*[🔴🟡🟢]|status\s+(open|fixed|regressed|wontfix)|[🔴🟡🟢]\s*·\s*(open|fixed)|·\s*severity\s*[🔴🟡🟢]|-(UX|FE|BE|DB|SEC|INFRA|OBS|TEST|LINT|AI)-\d{3}\b/iu;

/**
 * Strip whitespace + Markdown container prefixes (blockquotes, list markers)
 * repeatedly so nested forms like `> 1. ## …` or list-continuation-indented
 * `    ## …` still surface the inner heading text. Any amount of leading
 * whitespace is removed — canonical findings are only column-0 `##` lines.
 */
function unwrapMarkdownContainers(line) {
  let s = line;
  for (let guard = 0; guard < 12; guard++) {
    let next = s.replace(/^\s+/, ""); // all leading whitespace (spaces/tabs)
    next = next.replace(/^(?:> ?)+/, ""); // one or more blockquote markers
    next = next.replace(/^(?:[-*+]|\d+\.)\s+/, ""); // list marker
    if (next === s) break;
    s = next;
  }
  return s;
}

/**
 * Collect every finding-shaped heading candidate. Canonical form is only a
 * column-0 `## …` line matching HEADING_RE. Everything else finding-shaped is
 * malformed — including Setext, indented ATX, blockquoted/list-nested headings,
 * and nested-list continuation indents (4+ spaces).
 * Returns { text, kind } where kind is "canonical-h2" | "malformed".
 */
function scanFindingShapedHeadings(content) {
  const lines = content.split("\n");
  const out = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Canonical short-circuit: exact column-0 grammar is fine.
    if (HEADING_RE.test(line)) {
      out.push({ text: line, kind: "canonical-h2" });
      continue;
    }

    const unwrapped = unwrapMarkdownContainers(line);
    if (!unwrapped) continue;

    // ATX after unwrap (any level) — finding-shaped => malformed (not column-0 canonical)
    const atx = unwrapped.match(/^(#{1,6})\s+(\S.*)$/);
    if (atx) {
      const rest = atx[2];
      if (FINDING_SHAPED_HEADING.test(rest)) {
        out.push({ text: line.trimEnd() || unwrapped, kind: "malformed" });
      }
      continue;
    }

    // Setext underline under a finding-shaped title
    if (i + 1 < lines.length) {
      const under = unwrapMarkdownContainers(lines[i + 1]);
      if (
        /^(=+|-+)\s*$/.test(under) &&
        FINDING_SHAPED_HEADING.test(unwrapped) &&
        unwrapped.trim() !== ""
      ) {
        out.push({ text: `${unwrapped.trim()} / ${under.trim()}`, kind: "malformed" });
      }
    }
  }
  return out;
}

function labelOccurrences(blockText, label) {
  let count = 0;
  let idx = 0;
  while (true) {
    const found = blockText.indexOf(label, idx);
    if (found === -1) break;
    count++;
    idx = found + label.length;
  }
  return count;
}

function firstLabelIndex(blockText, label) {
  return blockText.indexOf(label);
}
/**
 * Validate findings.md content for a known (scope, domain) path.
 * Returns { validated, errors: string[] } without touching the global fail/ok counters
 * so regression fixtures can assert fail-closed behavior.
 */
function validateFindingsContent(rel, content, scope, domain) {
  const errors = [];
  if (!(domain in DOMAIN_CODES)) {
    return { validated: 0, errors: [`unknown domain "${domain}"`] };
  }
  const expectedCode = DOMAIN_CODES[domain];
  const expectedScopeLabel = scope.replaceAll("/", "-");

  // Reject every finding-shaped non-canonical heading BEFORE the empty-file success path.
  for (const h of scanFindingShapedHeadings(content)) {
    if (h.kind === "malformed") {
      errors.push(`malformed finding heading (must be canonical ## grammar): ${h.text}`);
    }
  }

  const blocks = splitFindingBlocks(content);
  if (blocks.length === 0) {
    return { validated: 0, errors };
  }

  let validated = 0;
  for (const block of blocks) {
    const hm = block.heading.match(HEADING_RE);
    if (!hm) {
      errors.push(`heading does not match canonical grammar: ${block.heading}`);
      continue;
    }
    const [, scopeLabel, domainCode] = hm;
    if (domainCode !== expectedCode) {
      errors.push(
        `heading DOMAINCODE ${domainCode} does not match path domain ${domain} (expected ${expectedCode}): ${block.heading}`
      );
      continue;
    }
    if (scopeLabel !== expectedScopeLabel) {
      errors.push(
        `heading scopeLabel "${scopeLabel}" does not match path scope "${scope}" (expected "${expectedScopeLabel}"): ${block.heading}`
      );
      continue;
    }

    const bodyText = block.body.join("\n");
    const fullBlock = block.heading + "\n" + bodyText;

    if (/^-\s+\*\*Severity:\*\*/m.test(bodyText) || /^-\s+\*\*Status:\*\*/m.test(bodyText)) {
      errors.push(`finding body has forbidden Severity/Status bullets under ${block.heading}`);
      continue;
    }

    let labelOrderOk = true;
    let prevIdx = -1;
    for (const label of REQUIRED_LABELS) {
      const count = labelOccurrences(fullBlock, label);
      if (count !== 1) {
        errors.push(`label "${label}" appears ${count} time(s) (want exactly 1) in ${block.heading}`);
        labelOrderOk = false;
        break;
      }
      const idx = firstLabelIndex(fullBlock, label);
      if (idx < prevIdx) {
        errors.push(`label "${label}" out of order in ${block.heading}`);
        labelOrderOk = false;
        break;
      }
      prevIdx = idx;
    }
    if (!labelOrderOk) continue;

    const fpLine = block.body.find((l) => l.includes("**Fingerprint:**"));
    if (!fpLine) {
      errors.push(`missing Fingerprint line in ${block.heading}`);
      continue;
    }
    const fpMatch = fpLine.match(FP_RE);
    if (!fpMatch) {
      errors.push(`Fingerprint line does not match grammar in ${block.heading}: ${fpLine.trim()}`);
      continue;
    }
    const [, fpScope, fpDomain] = fpMatch;
    if (fpScope !== scope) {
      errors.push(`Fingerprint scope="${fpScope}" does not match path scope="${scope}" in ${block.heading}`);
      continue;
    }
    if (fpDomain !== domain) {
      errors.push(`Fingerprint domain="${fpDomain}" does not match path domain="${domain}" in ${block.heading}`);
      continue;
    }

    const lcLine = block.body.find((l) => l.includes("**Last-checked:**"));
    if (!lcLine) {
      errors.push(`missing Last-checked line in ${block.heading}`);
      continue;
    }
    const lcValue = lcLine.replace("**Last-checked:**", "").trim();
    if (!LAST_CHECKED_RE.test(lcValue)) {
      errors.push(`Last-checked value does not match grammar in ${block.heading}: ${lcValue}`);
      continue;
    }

    // Optional trailing labels follow the canonical order: Confidence, Deployment-state, Fix-attempt.
    const lcIdx = firstLabelIndex(fullBlock, "**Last-checked:**");
    const confidenceLines = block.body.filter((l) => l.includes(CONFIDENCE_LABEL));
    if (confidenceLines.length > 1) {
      errors.push(`Confidence appears ${confidenceLines.length} times (want at most 1) in ${block.heading}`);
      continue;
    }
    if (confidenceLines.length === 1) {
      const confidenceIdx = firstLabelIndex(fullBlock, CONFIDENCE_LABEL);
      const confidenceValue = confidenceLines[0].trim().replace(CONFIDENCE_LABEL, "").trim();
      if (confidenceIdx < lcIdx || !CONFIDENCE_VALUES.has(confidenceValue)) {
        errors.push(`Confidence must follow Last-checked and be verified, inferred, or unverified-from-repo in ${block.heading}`);
        continue;
      }
    }
    const deploymentStateLines = block.body.filter((l) => l.includes(DEPLOYMENT_STATE_LABEL));
    if (deploymentStateLines.length > 1) {
      errors.push(`Deployment-state appears ${deploymentStateLines.length} times (want at most 1) in ${block.heading}`);
      continue;
    }
    if (deploymentStateLines.length === 1) {
      const dsIdx = firstLabelIndex(fullBlock, DEPLOYMENT_STATE_LABEL);
      const dsValue = deploymentStateLines[0].trim().replace(DEPLOYMENT_STATE_LABEL, "").trim();
      const confidenceIdx = confidenceLines.length === 1 ? firstLabelIndex(fullBlock, CONFIDENCE_LABEL) : -1;
      if (dsIdx < lcIdx || (confidenceIdx !== -1 && dsIdx < confidenceIdx) || !DEPLOYMENT_STATE_RE.test(dsValue)) {
        errors.push(`Deployment-state must follow Confidence (when present) and be active, not-applicable, unverified-from-repo, or pending (reason) in ${block.heading}`);
        continue;
      }
    }
    const fixAttemptIdxs = [];
    {
      let searchFrom = 0;
      while (true) {
        const found = fullBlock.indexOf(FIX_ATTEMPT_LABEL, searchFrom);
        if (found === -1) break;
        fixAttemptIdxs.push(found);
        searchFrom = found + FIX_ATTEMPT_LABEL.length;
      }
    }
    let fixAttemptOk = true;
    for (const faIdx of fixAttemptIdxs) {
      if (faIdx < lcIdx) {
        errors.push(
          `Fix-attempt must appear after Last-checked in ${block.heading}`
        );
        fixAttemptOk = false;
        break;
      }
    }
    if (deploymentStateLines.length === 1 && fixAttemptIdxs.some((faIdx) => faIdx < firstLabelIndex(fullBlock, DEPLOYMENT_STATE_LABEL))) {
      errors.push(`Deployment-state must appear before Fix-attempt in ${block.heading}`);
      continue;
    }
    if (!fixAttemptOk) continue;

    const faLines = block.body.filter((l) => l.includes(FIX_ATTEMPT_LABEL));
    for (const faLine of faLines) {
      const trimmed = faLine.trim();
      // Allow optional " · did not hold (<date>)" (or similar) suffix after the one-line text.
      // Core grammar: **Fix-attempt:** YYYY-MM-DD · <identity> · <text>
      if (!FIX_ATTEMPT_LINE_RE.test(trimmed)) {
        // Detect clearly wrong identity shapes when the rest of the structure is close.
        const loose = trimmed.match(
          /^\*\*Fix-attempt:\*\* (\d{4}-\d{2}-\d{2}) · ([^·]+) · (.+)$/
        );
        if (loose) {
          const identity = loose[2].trim();
          if (identity !== "working-tree" && !/^[0-9a-f]{7,40}$/.test(identity)) {
            errors.push(
              `Fix-attempt identity must be "working-tree" or a git sha (7+ hex), got "${identity}" in ${block.heading}`
            );
            fixAttemptOk = false;
            continue;
          }
        }
        errors.push(
          `Fix-attempt line does not match grammar in ${block.heading}: ${trimmed}`
        );
        fixAttemptOk = false;
      }
    }
    if (!fixAttemptOk) continue;

    validated++;
  }
  return { validated, errors };
}

function validateFindingsFile(filePath) {
  const rel = relative(ROOT, filePath);
  const parsed = parseFindingsPath(filePath);
  if (!parsed) {
    fail(`${rel}: path does not match .../audits/<scope...>/<domain>/findings.md`);
    return 0;
  }
  const { scope, domain } = parsed;
  if (!(domain in DOMAIN_CODES)) {
    fail(`${rel}: unknown domain "${domain}" (expected one of ${Object.keys(DOMAIN_CODES).join(", ")})`);
    return 0;
  }

  let content;
  try {
    content = readFileSync(filePath, "utf8");
  } catch (err) {
    fail(`${rel}: could not read: ${err.message}`);
    return 0;
  }

  const { validated, errors } = validateFindingsContent(rel, content, scope, domain);
  for (const e of errors) fail(`${rel}: ${e}`);
  if (validated === 0 && errors.length === 0) {
    ok(`${rel}: empty findings file (header only) — 0 findings`);
  }
  return validated;
}

/** In-memory regression fixtures for the empty-file / non-## heading bypass. */
function checkFindingsGrammarRegressions() {
  const body = [
    "**What breaks (plain language):** x",
    "**Technical:** y",
    "**Fix:** z",
    "**Fingerprint:** `scope=root · domain=backend · class=c · resource=r`",
    "**Last-checked:** 2026-06-22 · a1bec8f",
  ].join("\n");

  const cases = [
    {
      name: "h1 finding-shaped heading must fail",
      content: `# Backend Findings — root\n\n# root-BE-001 · severity 🔴 · status open\n${body}\n`,
      mustFail: true,
    },
    {
      name: "h3 finding-shaped heading must fail",
      content: `# Backend Findings — root\n\n### root-BE-001 · severity 🔴 · status open\n${body}\n`,
      mustFail: true,
    },
    {
      name: "h4 finding-shaped heading must fail",
      content: `# Backend Findings — root\n\n#### root-BE-001 · 🔴 · open\n${body}\n`,
      mustFail: true,
    },
    {
      name: "indented h3 finding-shaped heading must fail",
      content: `# Backend Findings — root\n\n   ### root-BE-001 · severity 🔴 · status open\n${body}\n`,
      mustFail: true,
    },
    {
      name: "indented ## finding-shaped heading must fail (canonical is column-0 only)",
      content: `# Backend Findings — root\n\n  ## root-BE-001 · severity 🔴 · status open\n${body}\n`,
      mustFail: true,
    },
    {
      name: "setext finding-shaped heading must fail",
      content: `# Backend Findings — root\n\nroot-BE-001 · severity 🔴 · status open\n===\n${body}\n`,
      mustFail: true,
    },
    {
      name: "blockquote ## finding-shaped heading must fail",
      content: `# Backend Findings — root\n\n> ## root-BE-001 · severity 🔴 · status open\n${body}\n`,
      mustFail: true,
    },
    {
      name: "list-nested ## finding-shaped heading must fail",
      content: `# Backend Findings — root\n\n- ## root-BE-001 · severity 🔴 · status open\n${body}\n`,
      mustFail: true,
    },
    {
      name: "nested-list continuation (4-space indent) ## must fail",
      content: `# Backend Findings — root\n\n- note:\n    ## root-BE-001 · severity 🔴 · status open\n${body}\n`,
      mustFail: true,
    },
    {
      name: "header-only empty file is valid",
      content: `# Backend Findings — root\n\n> Generated: 2026-06-22 · commit a1bec8f · driven by craft-backend · scope: root\n`,
      mustFail: false,
      expectValidated: 0,
    },
    {
      name: "canonical ## finding is valid",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n${body}\n`,
      mustFail: false,
      expectValidated: 1,
    },
    {
      name: "Fix-attempt with short-sha after Last-checked is valid",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n${body}\n**Fix-attempt:** 2026-06-25 · b2c9d1e · scoped the query to orgId\n`,
      mustFail: false,
      expectValidated: 1,
    },
    {
      name: "Fix-attempt with working-tree after Last-checked is valid",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n${body}\n**Fix-attempt:** 2026-06-25 · working-tree · scoped the query to orgId\n`,
      mustFail: false,
      expectValidated: 1,
    },
    {
      name: "ordinary prose beginning with a finding ID is valid",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n${body}\nroot-INFRA-002, this is ordinary prose in the finding body.\n`,
      mustFail: false,
      expectValidated: 1,
    },
    {
      name: "pending deployment state after Last-checked is valid",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n${body}\n**Deployment-state:** pending (migration not applied)\n**Fix-attempt:** 2026-06-25 · b2c9d1e · added migration\n`,
      mustFail: false,
      expectValidated: 1,
    },
    {
      name: "Confidence before deployment state is valid",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n${body}\n**Confidence:** inferred\n**Deployment-state:** unverified-from-repo\n`,
      mustFail: false,
      expectValidated: 1,
    },
    {
      name: "Confidence after deployment state must fail",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n${body}\n**Deployment-state:** pending (migration not applied)\n**Confidence:** inferred\n`,
      mustFail: true,
    },
    {
      name: "invalid Confidence value must fail",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n${body}\n**Confidence:** maybe\n`,
      mustFail: true,
    },
    {
      name: "Fix-attempt before Last-checked must fail",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n**What breaks (plain language):** x\n**Technical:** y\n**Fix:** z\n**Fingerprint:** \`scope=root · domain=backend · class=c · resource=r\`\n**Fix-attempt:** 2026-06-25 · working-tree · too early\n**Last-checked:** 2026-06-22 · a1bec8f\n`,
      mustFail: true,
    },
    {
      name: "Fix-attempt with nonsense identity must fail",
      content: `# Backend Findings — root\n\n## root-BE-001 · severity 🔴 · status open\n${body}\n**Fix-attempt:** 2026-06-25 · pre-change-HEAD · not a valid identity\n`,
      mustFail: true,
    },
  ];

  let regFails = 0;
  for (const c of cases) {
    const { validated, errors } = validateFindingsContent(
      `regression:${c.name}`,
      c.content,
      "root",
      "backend"
    );
    const failed = errors.length > 0;
    if (c.mustFail && !failed) {
      fail(`findings grammar regression: expected fail — ${c.name}`);
      regFails++;
    } else if (!c.mustFail && failed) {
      fail(`findings grammar regression: unexpected fail — ${c.name}: ${errors[0]}`);
      regFails++;
    } else if (!c.mustFail && c.expectValidated != null && validated !== c.expectValidated) {
      fail(
        `findings grammar regression: ${c.name} validated=${validated}, want ${c.expectValidated}`
      );
      regFails++;
    }
  }
  if (regFails === 0) {
    ok(`findings grammar regressions: ${cases.length} fixture(s) passed`);
  }
}

function checkFindingsGrammar() {
  // (f0) Regression fixtures (empty-file bypass, non-## finding headings)
  checkFindingsGrammarRegressions();

  // (f1) Worked-example findings.md grammar
  const files = findExampleFindingsFiles();
  if (files.length === 0) {
    fail("no plugins/craftsman/examples/**/findings.md files found to validate");
  } else {
    const failuresBefore = failures;
    let total = 0;
    for (const file of files) {
      total += validateFindingsFile(file);
    }
    if (failures === failuresBefore) {
      ok(
        `findings grammar: validated ${total} finding(s) across ${files.length} examples/**/findings.md file(s)`
      );
    }
  }

  // (f2) Domain skills restate canonical emission
  const SKILL_DOMAIN_CODES = {
    "craft-ux": "UX",
    "craft-frontend": "FE",
    "craft-backend": "BE",
    "craft-db": "DB",
    "craft-security": "SEC",
    "craft-infra": "INFRA",
    "craft-observability": "OBS",
    "craft-testing": "TEST",
    "craft-lint": "LINT",
    "craft-ai": "AI",
  };
  const EXEMPT = new Set(["craft-audit", "craft-fix"]);
  for (const skillDir of getSkillDirs()) {
    const skillName = relative(join(ROOT, "plugins", "craftsman", "skills"), skillDir);
    if (EXEMPT.has(skillName)) continue;
    const code = SKILL_DOMAIN_CODES[skillName];
    if (!code) {
      fail(`${skillName}: domain skill missing DOMAIN_CODES mapping in check (f2)`);
      continue;
    }
    const skillMdPath = join(skillDir, "SKILL.md");
    let skillMd;
    try {
      skillMd = readFileSync(skillMdPath, "utf8");
    } catch {
      fail(`${skillName}: missing SKILL.md for findings-emission check`);
      continue;
    }
    // Collapse whitespace so a mid-phrase line wrap still counts as containing the string.
    const collapsed = skillMd.replace(/\s+/g, " ");
    if (!collapsed.includes("Canonical findings.md emission format")) {
      fail(`${skillName}: SKILL.md must restate "Canonical findings.md emission format"`);
    } else if (
      !(
        skillMd.includes(`-${code}-`) ||
        skillMd.includes(`${code}-<NNN>`) ||
        skillMd.includes(`${code}-NNN`)
      )
    ) {
      fail(
        `${skillName}: SKILL.md must include its DOMAINCODE (${code}) in a heading grammar example (e.g. -${code}- or ${code}-<NNN>)`
      );
    } else {
      ok(`${skillName}: restates canonical findings emission format with DOMAINCODE ${code}`);
    }
  }

  // (f3) Optional soft check — craft-audit path binding language
  const auditSkill = join(ROOT, "plugins", "craftsman", "skills", "craft-audit", "SKILL.md");
  try {
    const text = readFileSync(auditSkill, "utf8");
    if (text.includes("Path binding")) {
      ok('craft-audit/SKILL.md contains path binding language ("Path binding")');
    } else {
      warn('craft-audit/SKILL.md missing soft path-binding language ("Path binding")');
    }
  } catch {
    warn("could not read craft-audit/SKILL.md for soft path-binding check");
  }
}

// ---------------------------------------------------------------------------
// (g) vendored third-party content stays inert data
// ---------------------------------------------------------------------------
//
// craft-ux vendors Vercel's Web Interface Guidelines rather than fetching them at review time,
// because upstream is a slash-command prompt on a mutable branch: fetching it would make a
// third-party repo an instruction channel into every craftsman user's codebase. That decision is
// only as durable as the checks around it, so the guarantees are asserted here rather than left
// to prose in the refresh script and the vendored file's own header.

const VENDORED_GUIDELINES = join(
  ROOT,
  "plugins/craftsman/skills/craft-ux/references/web-interface-guidelines.md",
);
const REVIEW_PROTOCOL = join(
  ROOT,
  "plugins/craftsman/skills/craft-ux/references/review-protocol.md",
);
const RULES_HEADING = "## Rules";
const NO_FETCH_CANARY = "Do not fetch the rules over the network at review time.";

// Rows that must survive every refresh: without them the payload is no longer pinned or
// attributable, and a reviewer cannot tell which upstream commit produced it.
const PROVENANCE_ROWS = [
  { label: "Upstream", re: /^\|\s*Upstream\s*\|\s*`https:\/\/github\.com\/\S+`\s*\|$/m },
  { label: "Commit", re: /^\|\s*Commit\s*\|\s*`[0-9a-f]{40}`\s*\|$/m },
  { label: "License", re: /^\|\s*License\s*\|\s*\S[^|]*\|$/m },
  {
    label: "SHA-256 of fetched source",
    re: /^\|\s*SHA-256 of fetched source\s*\|\s*`[0-9a-f]{64}`\s*\|$/m,
  },
];

// Structural signals: none of these can occur in a legitimate rule list, so their presence means
// the vendored payload has stopped being inert data. Hard failures.
const INSTRUCTION_SIGNALS = [
  { name: "URL", re: /https?:\/\//i },
  { name: "prompt-template marker", re: /\$ARGUMENTS|\{\{/ },
  { name: "fenced code block", re: /^\s*```/ },
];

// Softer signal: a rule could legitimately use one of these words, but a refresh that introduces
// one deserves a human read of the diff before it ships.
const TOOL_VERB_RE = /\b(fetch|curl|wget|WebFetch|npm install|pip install|download|execute)\b/i;

function checkVendoredGuidelines() {
  let text;
  try {
    text = readFileSync(VENDORED_GUIDELINES, "utf8");
  } catch {
    fail(
      "craft-ux/references/web-interface-guidelines.md: vendored rule list missing — " +
        "craft-ux must never fall back to fetching upstream at review time",
    );
    return;
  }

  const rulesIdx = text.indexOf(`\n${RULES_HEADING}`);
  if (rulesIdx === -1) {
    fail(
      `web-interface-guidelines.md: no "${RULES_HEADING}" heading — cannot separate the ` +
        "provenance header from the vendored rules",
    );
    return;
  }

  // rulesIdx points at the newline *before* the heading, so slicing past it puts "## Rules" on
  // line 0 of `rules`, and the line count of everything before it is that heading's 1-based
  // file line number.
  const provenance = text.slice(0, rulesIdx + 1);
  const rules = text.slice(rulesIdx + 1);
  const rulesLineOffset = provenance.split("\n").length;

  // (g1) provenance intact
  for (const row of PROVENANCE_ROWS) {
    if (row.re.test(provenance)) {
      ok(`web-interface-guidelines.md: provenance row "${row.label}" present and well-formed`);
    } else {
      fail(
        `web-interface-guidelines.md: provenance row "${row.label}" missing or malformed — ` +
          "vendored content must stay pinned to an upstream commit and attributed",
      );
    }
  }

  // (g2) the rules themselves stayed inert
  const lines = rules.split("\n");
  let structural = 0;
  let verbs = 0;
  for (let i = 0; i < lines.length; i++) {
    const lineNo = rulesLineOffset + i;
    for (const sig of INSTRUCTION_SIGNALS) {
      if (sig.re.test(lines[i])) {
        structural++;
        fail(
          `web-interface-guidelines.md:${lineNo}: ${sig.name} in the vendored rule list — ` +
            "the rules are data, not instructions; strip it or reject the refresh",
        );
      }
    }
    if (TOOL_VERB_RE.test(lines[i])) {
      verbs++;
      warn(
        `web-interface-guidelines.md:${lineNo}: tool/network verb in the vendored rule list — ` +
          "read this refresh diff before shipping it",
      );
    }
  }
  if (structural === 0) {
    ok("web-interface-guidelines.md: rule list carries no URL, template marker, or code fence");
  }
  if (verbs === 0) {
    ok("web-interface-guidelines.md: rule list carries no tool/network verbs");
  }

  // (g3) the prohibition that keeps review time offline
  try {
    const protocol = readFileSync(REVIEW_PROTOCOL, "utf8");
    if (protocol.includes(NO_FETCH_CANARY)) {
      ok("review-protocol.md: retains the do-not-fetch-at-review-time prohibition");
    } else {
      fail(
        `review-protocol.md: missing the prohibition "${NO_FETCH_CANARY}" — without it a ` +
          "review pass may fetch upstream rules over the network",
      );
    }
  } catch {
    fail("review-protocol.md: unreadable, cannot verify the do-not-fetch prohibition");
  }
}

// ---------------------------------------------------------------------------
// (h) every `references/x.md` pointer resolves — in its own skill, or in the skill
// that qualifies it.
//
// checkCrossSkillPointers only sees pointers whose qualifying skill token sits on the
// same line, and these docs wrap at ~100 cols. A bare `references/x.md` that resolves
// nowhere is the dangerous form: a reader follows it into their own skill's references/
// dir, finds nothing, and either guesses or drops the guidance.
//
// Scoping is by Markdown block, not by a character window. A skill named in the
// *previous* list item does not qualify a pointer in this one — that was the exact
// ambiguity being caught — and a skill named in the previous *paragraph* does not
// either, which a raw character lookback would have silently exempted.
// ---------------------------------------------------------------------------

// A block ends at a blank line, a heading, a list item, or a table row. Indented
// continuation lines stay with the item that opened the block. A leading "> " is
// stripped first, so a blockquote scopes by the same rules as the prose it quotes —
// its wrapped lines stay together, its bullets still split. Fenced code is dropped:
// an example path inside a fence is illustration, not navigation.
function splitIntoBlocks(text) {
  const blocks = [];
  let current = [];
  let inFence = false;
  const flush = () => {
    if (current.length) blocks.push(current.join(" "));
    current = [];
  };
  for (let line of text.split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence;
      flush();
      continue;
    }
    if (inFence) continue;
    line = line.replace(/^(\s*)>\s?/, "$1");
    const opensBlock =
      line.trim() === "" ||
      /^#{1,6}\s/.test(line) ||
      /^\s*([-*+]|\d+\.)\s/.test(line) ||
      /^\s*\|/.test(line);
    if (opensBlock) flush();
    if (line.trim() !== "") current.push(line);
  }
  flush();
  return blocks;
}

// A skill token only owns a pointer when it is syntactically attached to it: nothing
// between them but decoration, whitespace (these docs wrap mid-pointer), and a connector
// (`→`, `->`, `'s`, `:`, `/`, an opening paren). Merely being the nearest earlier token is
// not enough — "route to craft-infra (pipeline mechanism) → `references/strategy.md`"
// points at the *current* skill's file, and reading the aside as the qualifier would send
// the check hunting for it in craft-infra. Any word or other punctuation between the two
// breaks the attachment, which is the same judgment a reader makes.
const ATTACHED_QUALIFIER = /^[\s`*'"]*(?:(?:→|->|'s|:|\/|\()[\s`*'"]*){0,3}$/;

function checkReferencePointersResolve() {
  const skillsRoot = join(ROOT, "plugins", "craftsman", "skills");
  let dangling = 0;
  let checked = 0;
  for (const file of findAllSkillMdFiles()) {
    const relPath = relative(ROOT, file);
    const ownSkill = relative(skillsRoot, file).split("/")[0];

    for (const block of splitIntoBlocks(readFileSync(file, "utf8"))) {
      for (const m of block.matchAll(/references\/([a-z0-9-]+\.md)/g)) {
        const fileTok = m[1];
        checked++;

        const before = block.slice(0, m.index);
        const tokens = [...before.matchAll(/craft-[a-z0-9-]+/g)];
        const last = tokens.length ? tokens[tokens.length - 1] : null;
        const attached =
          last && ATTACHED_QUALIFIER.test(before.slice(last.index + last[0].length));
        const qualifier = attached && last[0] !== ownSkill ? last[0] : null;

        // No attached qualifier (or it names this skill): the file must be this skill's own.
        if (!qualifier) {
          if (existsSync(join(skillsRoot, ownSkill, "references", fileTok))) continue;
          fail(
            `${relPath}: pointer "references/${fileTok}" does not exist in ${ownSkill}'s own ` +
              'references/ — name the owning skill ("`craft-x` → `references/…`") or fix the path',
          );
          dangling++;
          continue;
        }

        // Attached to another skill: it must exist there. No own-skill fallback — the
        // pointer said whose file it is, so that is the claim being checked.
        if (existsSync(join(skillsRoot, qualifier, "references", fileTok))) continue;
        fail(
          `${relPath}: pointer "${qualifier} → references/${fileTok}" does not exist in ` +
            `${qualifier}/references/`,
        );
        dangling++;
      }
    }
  }
  if (dangling === 0) {
    ok(`all ${checked} references/ pointers resolve in their own or their qualifying skill`);
  }
}

// ---------------------------------------------------------------------------
// (i) taxcraft parity: the tax plugin ships alongside craftsman and gets the same
// manifest, description, and router-integrity guarantees. Its SKILL.md is a router
// whose sub-skill table is the load-bearing index — a row naming a file that does
// not exist sends the model looking for guidance that was never shipped.
// ---------------------------------------------------------------------------
function checkTaxcraft() {
  const manifests = [
    ".claude-plugin/marketplace.json",
    "plugins/taxcraft/.claude-plugin/plugin.json",
    "plugins/taxcraft/.codex-plugin/plugin.json",
  ];
  const parsed = new Map();
  for (const rel of manifests) {
    try {
      parsed.set(rel, JSON.parse(readFileSync(join(ROOT, rel), "utf8")));
      if (rel.startsWith("plugins/")) ok(`${rel} parses as valid JSON`);
    } catch (err) {
      fail(`${rel} failed to parse: ${err.message}`);
    }
  }

  const versions = [
    parsed.get(".claude-plugin/marketplace.json")?.plugins?.find((p) => p.name === "taxcraft")?.version,
    parsed.get("plugins/taxcraft/.claude-plugin/plugin.json")?.version,
    parsed.get("plugins/taxcraft/.codex-plugin/plugin.json")?.version,
  ];
  if (versions.every(Boolean) && new Set(versions).size === 1) {
    ok(`all taxcraft manifests declare version ${versions[0]}`);
  } else {
    fail(`taxcraft manifest versions disagree: ${versions.map((v) => v || "missing").join(", ")}`);
  }

  // every marketplace entry's source directory exists
  for (const plugin of parsed.get(".claude-plugin/marketplace.json")?.plugins ?? []) {
    const src = join(ROOT, plugin.source.replace(/^\.\//, ""));
    if (existsSync(src)) {
      ok(`marketplace entry "${plugin.name}" source ${plugin.source} exists`);
    } else {
      fail(`marketplace entry "${plugin.name}" source ${plugin.source} does not exist`);
    }
  }

  const skillPath = join(ROOT, "plugins/taxcraft/skills/tax/SKILL.md");
  const text = readFileSync(skillPath, "utf8");

  const desc = /^description:\s*(.*)$/m.exec(text)?.[1] ?? "";
  if (desc.length > 0 && desc.length <= 1200) {
    ok(`tax: description is ${desc.length} chars (<= 1200)`);
  } else {
    fail(`tax: description is ${desc.length} chars (must be 1-1200)`);
  }

  // Sub-skill table rows: first cell is a backticked path. Rows using a
  // `<placeholder>` glob (e.g. `individual/<domain>.md`) name a family, not a file.
  const taxRoot = join(ROOT, "plugins/taxcraft/skills/tax");
  const table = /^## Sub-skill files \(loaded on demand\)\n([\s\S]*?)(?=\n## )/m.exec(text)?.[1];
  if (!table) {
    fail("tax/SKILL.md: missing the \"## Sub-skill files (loaded on demand)\" router table");
    return;
  }
  let bad = 0;
  let checked = 0;
  for (const row of table.matchAll(/^\|([^|\n]+)\|/gm)) {
    // A first cell can name more than one path, e.g. "`rules/manifest.json` +
    // `rules/schema-v{1,2}.json`". Check every backticked token in it, not just the
    // first — a row-shape assumption is how an unchecked path hides behind a green line.
    for (const tok of row[1].matchAll(/`([^`]+)`/g)) {
      const target = tok[1];
      if (!/\.[a-z0-9]+$/i.test(target) && !target.endsWith("/")) continue; // not a path
      if (/[<>*]/.test(target)) continue; // family placeholder, not a file
      // Brace alternation names a set: `schema-v{1,2}.json` -> schema-v1.json, schema-v2.json
      const expanded = /\{([^}]+)\}/.test(target)
        ? target.match(/\{([^}]+)\}/)[1].split(",").map((alt) => target.replace(/\{[^}]+\}/, alt.trim()))
        : [target];
      for (const path of expanded) {
        checked++;
        if (!existsSync(join(taxRoot, path))) {
          fail(`tax/SKILL.md: router table names \`${path}\`, which does not exist`);
          bad++;
        }
      }
    }
  }
  if (checked === 0) {
    fail("tax/SKILL.md: router table parsed but yielded no checkable paths");
    return;
  }
  if (bad === 0) ok(`tax/SKILL.md: all ${checked} concrete router-table paths exist`);
}

// ---------------------------------------------------------------------------
// Run all checks
// ---------------------------------------------------------------------------
checkJsonManifests();
checkReferenceCrossLinking();
checkCrossSkillPointers();
checkAuditChecklistHeading();
checkDescriptionLength();
checkNoAbsoluteVolumesPaths();
checkFindingsGrammar();
checkVendoredGuidelines();
checkReferencePointersResolve();
checkTaxcraft();

console.log("");
console.log(`${failures} failure(s), ${warnings} warning(s).`);
if (failures > 0) {
  process.exit(1);
}
