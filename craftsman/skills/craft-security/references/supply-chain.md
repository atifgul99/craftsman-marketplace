# Supply Chain

Every package you `import` is code that runs with your app's privileges — your secrets, your network, your users' data. The supply-chain discipline: **pin what you depend on, scan it in CI, gate merges on the severity that matters, and treat each dependency as code you own.** A transitive package three levels deep that runs a `postinstall` script is as much your attack surface as the code you wrote.

> **Scope split.** This file owns dependency *security*: pinning/lockfiles, CI vulnerability scanning, triage thresholds, provenance/integrity, and the "is this dep worth adding" call from a *risk* angle. The dependency *weight* call (bundle size, tree-shaking, what ships to the browser) belongs to **`craft-frontend`** → `performance.md`; the *discover-before-adding* / does-this-already-exist instinct belongs to **`craft-frontend`** → `architecture.md` (and the same method is in this skill's SKILL.md). Vuln-driven runtime hardening (validation, output encoding) is `input-output.md`; leaked-credential rotation is `secrets.md`.

---

## Contents

- [Pin dependencies](#pin-dependencies)
- [Scan in CI](#scan-in-ci)
- [Triage thresholds](#triage-thresholds)
- [A vuln with no fix](#a-vuln-with-no-fix)
- [Every dependency is code you own](#every-dependency-is-code-you-own)
- [License risk](#license-risk)
- [Provenance & integrity](#provenance--integrity)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Pin dependencies

- **Commit the lockfile** (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `Cargo.lock`, `poetry.lock`, `uv.lock`, `go.mod` + `go.sum` — the manifest pins versions, `go.sum` records the checksums). The lockfile pins the *entire resolved tree* — direct and transitive — to exact versions and integrity hashes. Without it committed, two installs of the same `package.json` can resolve to different code. A missing/gitignored lockfile in an app repo is a gap.
- **Install from the lockfile in CI**, not from the manifest. Use the frozen-install mode so CI fails if the lockfile is stale instead of silently re-resolving: `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable`. `npm install` mutates the lockfile and defeats the pin.
- **Floating ranges in the *manifest* are fine *because* the lockfile pins the actual install.** `^1.2.3` in `package.json` + a committed lockfile = reproducible. The danger is a floating range with *no* lockfile, or `latest`/`*`/`next` dist-tags that re-resolve every install and auto-pull unreviewed code (a known vector for compromised-package and dist-tag-hijack attacks).
- **Library packages are the exception**: a published library *should* keep a permissive range in its manifest (so consumers dedupe). A library may still commit a lockfile for its own dev/CI reproducibility, but that lockfile does *not* constrain a consumer's install — so don't treat a committed lockfile as the security control for a *published* package. The committed-lockfile-as-pin rule is for *applications / deployables*. Discover which you're in before flagging.
- **Updates are deliberate, batched, and reviewed** — via Dependabot/Renovate PRs that bump the lockfile, run the full test + scan suite, and get read like any other diff. Auto-merge only patch bumps of *trusted* deps, and only behind green CI.

---

## Scan in CI

Discover what's already wired (`grep` workflows for `audit`, `snyk`, look for `dependabot.yml`) before adding a second scanner.

- **Run a vulnerability scanner on every PR**, against the committed lockfile, as a required check. Common tooling: `npm audit` / `pnpm audit` / `yarn npm audit` (Yarn Berry; `yarn audit` on Yarn v1) (free, baseline), GitHub **Dependabot alerts** (advisory DB + auto-fix PRs), **Snyk** / **Socket** / **osv-scanner** / **Trivy** (deeper, license + behavior signals). One scanner gating merges beats three that only email.
- **The scan must be able to *fail the build*** — exit non-zero on findings at/above your threshold, not just print a report nobody reads. `npm audit --audit-level=high` exits non-zero on high+; pair with `--omit=dev` only if dev-only vulns are tracked separately, not ignored.
- **Pin the scanner's input to the lockfile**, and keep the advisory DB fresh — a scanner caching a stale DB is worse than none because it reads as green.
- **Scan the runtime surface too**, not just `node_modules`: container base images and OS packages (Trivy/Grype) ship CVEs your lockfile scanner never sees.

---

## Triage thresholds

A scanner result is a *signal*, not a verdict — CVSS severity is generic; your exploitability depends on whether the vulnerable code path is reachable. The default gate:

| Severity | CI gate | Action |
| --- | --- | --- |
| **Critical** | **Block merge** | Fix now (upgrade) or apply an explicit, reviewed override before merge |
| **High** | **Block merge** | Same; downgrade to "tracked" only with a written reachability justification |
| **Moderate** | Tracked, time-boxed | Ticket + due date; batch into the next dependency-bump PR |
| **Low** | Tracked | Cleared during routine updates; don't let them accumulate unbounded |

- **Block on critical and high; track moderate and low** — but *track* means a ticket with an owner and a date, not an ignore file that grows forever.
- **Reachability beats raw severity.** A critical in a dev-only build tool that never touches prod, or in a code path you provably don't call, can be downgraded — but write the reason next to the suppression. Conversely, a "moderate" on the request path handling untrusted input may deserve critical treatment. Don't blindly gate *or* blindly ignore.
- **Suppressions expire.** Every override/ignore entry carries a reason, an owner, and an expiry so it gets re-reviewed instead of becoming permanent.

---

## A vuln with no fix

When the scanner flags a package with no patched version available, pick one — in rough order of preference — and **leave a dated note in the suppression/override entry** either way:

1. **Override the transitive version** if a *fixed* version exists deeper in the tree but a parent pins an old one. Force-resolve it: `overrides` (npm), `resolutions` (yarn), `pnpm.overrides` (pnpm). Verify the forced version is actually compatible (run the tests) — this is the cleanest fix when it works.
2. **Pin to the last safe version** and freeze upgrades until a patch lands.
3. **Replace the dependency** with a maintained alternative (or vendor/inline a small slice you actually use). Best long-term answer for an *unmaintained* package — no-fix-available often means no-maintainer.
4. **Accept the risk — explicitly.** Only after establishing the path is unreachable or the impact is tolerable. Record severity, why it's accepted, the owner, and a re-review date in the ignore file (`.snyk`, `audit-ci` allowlist, Dependabot config). An undocumented suppression is indistinguishable from negligence at the next audit.

Never silence the scanner globally to get green. Suppress the *specific* advisory, scoped and dated.

---

## Every dependency is code you own

You're responsible for everything in your tree, including code you never read. Minimize and justify.

- **Minimize the tree.** Fewer dependencies = smaller attack surface, fewer transitive surprises, less to patch. Audit periodically (`npm ls`, `depcheck`, `knip`) and prune unused, duplicated, and one-function deps you could inline.
- **Justify every new dependency from the risk angle.** Every dep is ongoing maintenance + CVE exposure you sign up for. Is it actively maintained (recent releases, open-issue triage, more than one maintainer — single-maintainer and abandoned packages are the higher supply-chain risk)? Weigh that cost against the lines it saves; a left-pad-sized dep rarely earns its supply-chain risk. Whether the capability already exists and how to discover it first is the architecture call — `craft-frontend` → `architecture.md`.
- **Weight ties to the perf budget.** For anything that ships to the client, a dep adding more than **~20 KB gzipped** needs a deliberate justification against the frontend performance budget — see **`craft-frontend`** → `performance.md` for the bundle-weight analysis and lighter alternatives. (Server-only deps don't hit the bundle, but still carry CVE + maintenance cost.)
- **Beware typosquatting and slop-squatting.** Confirm the *exact* package name and that it's the canonical one (right repo, expected download counts, expected maintainer) before adding — a transposed character or a hallucinated name can be a malicious clone. Be especially careful with package names an AI suggested but you didn't verify exist.
- **Treat install scripts as code execution.** A `postinstall`/`preinstall` script runs arbitrary code on every dev machine and CI runner. Review them on new/updated deps; consider `--ignore-scripts` by default and allow-list the few that genuinely need a build step (pnpm's `onlyBuiltDependencies` does this). A package that suddenly *adds* an install script is a red flag.
- **Review transitive deps, not just direct ones.** Most of your tree is transitive. The lockfile diff in a bump PR is the actual change set — read it; a one-line `package.json` bump can pull in dozens of new transitive packages.

---

## License risk

A vuln scanner won't catch this one: a dependency's *license*, not its code, can be the thing that
hurts you. The two copyleft licenses that actually bite differ in *how* they trigger, and conflating
them overstates or understates the risk depending on which one you have:

- **AGPL is the one that reaches a hosted SaaS.** Its network-copyleft clause triggers on *running*
  the software as a network service — merely deploying an AGPL dependency behind your API can create
  an obligation to offer your own source, even though you never shipped a binary to anyone. Treat any
  AGPL dependency in a server-side path as a real exposure, not a theoretical one.
- **Plain GPL triggers on *distribution*, not use.** Running a GPL-licensed package server-side and
  never handing the binary to a user generally isn't "distribution," so a GPL dependency that only
  ever runs on your own servers is usually lower risk. The exception: anything you actually ship —
  a distributed client, a compiled binary, an Electron/desktop app, a mobile SDK — *does* distribute,
  and GPL obligations kick in there exactly like AGPL would.

This bites the vibe-coded MVP hardest: nobody reviews license terms when `npm install`-ing a package
that looked like it just solved a problem.

- **One-pass check.** Run `npx license-checker` (or `pnpm licenses list`) to see every license actually
  in your tree — direct and transitive. Do this before a launch or a fundraising due-diligence pass,
  not after someone asks.
- **Permissive licenses need no action.** MIT, Apache-2.0, BSD, ISC — these are fine, use freely.
- **On a copyleft hit (AGPL always; GPL when it's shipped/distributed; LGPL in some cases), do one of
  three things**: replace it with a permissively-licensed alternative, isolate it (e.g. run it as a
  separate service you don't distribute or link against, if the license permits that), or get real
  advice. **This skill does not give legal advice** — it flags the exposure and stops there; loop in
  a lawyer for anything beyond "swap the package."

---

## Provenance & integrity

Pinning a version isn't enough if the bytes behind that version can change.

- **Integrity hashes.** Modern lockfiles store a per-package integrity hash (npm/pnpm record an `integrity` SRI string, usually sha512; Cargo, Go, and Poetry use their own checksum fields). A recorded integrity hash is verified against the downloaded bytes on install whenever the lockfile is committed, so a tampered artifact fails. Frozen-install mode adds the guarantee that the lockfile is not silently re-resolved or allowed to drift — use it so the pinned, hash-verified tree is exactly what installs.
- **npm provenance.** Packages published with provenance (`npm publish --provenance` from CI) carry a signed, verifiable link back to the source commit and build. Prefer dependencies that publish it; if *you* publish packages, turn it on so your consumers can verify yours.
- **SBOM.** SBOM generation is recommended when a compliance driver exists — SOC 2, HIPAA, or
  enterprise procurement that requires a bill of materials. For internal MVPs with no compliance
  requirement, defer SBOM until it is asked for: prioritize dependency pinning and CI audit tooling
  first, which give the same "are we affected by CVE-X?" answer at lower overhead. If you do
  generate one: CycloneDX / SPDX format (e.g. via `syft` or `cdxgen`) as a CI build artifact covers
  the typical compliance expectation.
- **Lock the registry source.** Ensure installs come from the expected registry (`.npmrc` / scoped registries); a hijacked or substituted registry sidesteps every other control. Watch for dependency-confusion (an internal package name claimed publicly) — scope internal packages.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| App repo with no committed lockfile | Commit the lockfile; install with the frozen flag |
| `latest` / `*` / `next` dist-tag in a manifest | Pin a real version range; rely on the lockfile |
| CI uses `npm install` (mutates lockfile) | Use `npm ci` / `--frozen-lockfile` / `--immutable` |
| No dependency scanner gating PRs | Wire `npm audit --audit-level=high` (or Snyk/Dependabot) as a required check |
| Scanner runs but only prints (can't fail build) | Make it exit non-zero at/above threshold |
| Critical/high vuln merged with no override or note | Block, fix, or add a dated reachability-justified override |
| `.snyk` / audit ignore entry with no reason or expiry | Add owner, reason, re-review date; scope to the specific advisory |
| New client dep > ~20 KB gzipped, no justification | Justify vs perf budget or find a lighter option (`craft-frontend` → `performance.md`) |
| New dep that duplicates platform/existing capability | Use what exists (discover first; `craft-frontend` → `architecture.md`) |
| Unverified / typosquat-prone package name | Confirm canonical name, repo, maintainer, download counts |
| New/updated dep runs a `postinstall` script | Review the script; `--ignore-scripts` + allow-list trusted builds |
| Dependency bump PR merged without reading the lockfile diff | Review the transitive change set, not just `package.json` |
| AGPL dependency in a server-side path, no isolation/replacement plan | Run `license-checker`; replace, isolate, or get advice — not from this skill |
| GPL dependency that's actually shipped/distributed (client, binary, Electron), no plan | Same as above — distribution is what triggers GPL, not server-side use |
