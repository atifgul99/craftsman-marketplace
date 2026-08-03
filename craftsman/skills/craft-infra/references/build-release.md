# Build & Release

A build that can't be reproduced is a liability, and a release process that lives in one person's
head is an outage waiting to happen. **Build once, produce an immutable artifact, promote it across
environments without rebuilding.** The failure modes this prevents: environment-specific bugs from
recompiling on deploy, version drift between what was tested and what runs in production, and
"nobody knows how to ship on a Friday" emergencies that devolve into manual production edits.

> **Scope split.** This file owns the *artifact*: how it is built reproducibly, named immutably,
> and promoted across environments — and the *release process* that wraps that promotion. The
> pipeline that runs the build steps (`ci-cd.md`) and the environment variable schema baked into
> the artifact (`config.md`) are siblings. Release tagging pairs directly with
> **`craft-observability`** → `sentry.md` (uploading sourcemaps and setting the release name so
> errors map to source). Lockfile-pinned, provenance-signed inputs to the build are the domain of
> **`craft-security`** → `supply-chain.md`.

> **See also:** `ci-cd.md` (pipeline gates, deploy automation, rollback) · `config.md`
> (env-var schema, fail-closed validation) · **`craft-observability`** → `sentry.md` (release
> tagging, sourcemap upload) · **`craft-security`** → `supply-chain.md` (lockfile pinning,
> provenance, SBOM).

---

## Contents

- [Reproducible builds](#reproducible-builds)
- [Immutable, content-addressed artifacts](#immutable-content-addressed-artifacts)
- [Build once, promote across environments](#build-once-promote-across-environments)
- [Version and release tagging](#version-and-release-tagging)
- [The release process](#the-release-process)
- [Rollback is part of the release design](#rollback-is-part-of-the-release-design)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Reproducible builds

A reproducible build produces bit-for-bit (or functionally) identical output given the same source
and the same tool versions. Without it you can't trust that what CI tested is what production runs.

- **Pin the full dependency tree via a committed lockfile** and install with the frozen flag in CI
  (`npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable` (Berry/v2+) or
  `yarn install --frozen-lockfile` (Yarn 1.x)). A build that re-resolves
  from ranges rather than the lockfile can silently pull a different transitive package on each run.
  The full lockfile story — integrity hashes, scanner pairing, provenance — is in
  **`craft-security`** → `supply-chain.md`; the obligation here is to *never bypass it during build*.
- **Pin the Node/runtime version.** Use the project's `.node-version` or `.nvmrc` and ensure CI
  installs exactly that version (e.g. via the `actions/setup-node` `node-version-file` option, or a
  matching `.tool-versions` for `asdf`/`mise`). The `engines` field in `package.json` is advisory
  only — npm prints a warning when the running Node version doesn't match but continues unless
  `engine-strict=true` is set in `.npmrc` (or `--engine-strict` is passed), and it does not install
  the correct version; treat it as documentation, not enforcement. Discover which convention is
  already in the repo before adding a new one.
- **Pin build-tool versions.** The bundler (Vite, esbuild, webpack, Turbopack, Rollup, etc.),
  compiler (tsc, swc, babel), and any CLI tools invoked during the build are dependencies — they
  should appear in `package.json` (dev deps) and resolve through the lockfile, not be installed
  globally or assumed from the runner's ambient PATH.
- **Capture the build environment.** Record the Node version, OS, and key tool versions in the build
  output or as a CI artifact. This makes post-incident "what exactly ran?" a lookup rather than a
  reconstruction.
- **`NODE_ENV=production` for production builds.** Many bundlers and frameworks gate dead-code
  elimination, minification, and dev-only code paths on this variable. Note that `vite build` and
  `next build` set it automatically — the risk is tools invoked outside those entry points (custom
  scripts, programmatic API usage, or less-common bundlers) that do not. A production artifact built
  without it is larger and may expose debug internals.

---

## Immutable, content-addressed artifacts

An artifact is immutable when, once created and named, its bytes never change. Content-addressing
ties the name to a cryptographic digest of the content so any tampering is detectable.

- **Tag container images with the full commit SHA**, not just a mutable label like `latest` or
  `main`. `sha-${GIT_SHA}` will never be *reused* for different code (each commit produces a unique
  SHA), whereas `latest` is actively repointed. For true byte-level immutability — preventing any
  push from overwriting the tag — configure tag protection in the registry (e.g. ECR
  `imageTagMutability: IMMUTABLE`) or reference deployments by digest (see below). Mutable tags break
  the "what ran in production?" audit trail and cause rollbacks to re-pull an unknown version.

  Use the **full commit SHA** for immutable image tags — short SHAs are a convenience label only and
  are not collision-proof at scale. For digest-based enforcement (the strongest guarantee), reference
  deployments by `image@sha256:…` regardless of tag.

  ```sh
  # Use the full CI SHA for the immutable tag — short SHAs are not collision-proof long-term.
  # GitHub Actions: GIT_SHA="${GITHUB_SHA}"          (full 40-char SHA)
  # GitLab CI:      GIT_SHA="${CI_COMMIT_SHA}"
  # CircleCI:       GIT_SHA="${CIRCLE_SHA1}"
  # Generic:        GIT_SHA="$(git rev-parse HEAD)"
  # Short SHA (7-char) may be used as a human-readable convenience label alongside the full tag,
  # but must not be the sole immutable handle — enforce immutability via registry tag protection
  # or digest references instead.

  # Push both: the full-SHA tag for immutability, a human-readable tag for promotion tracking
  docker build -t registry.example.com/app:sha-${GIT_SHA} .
  docker tag registry.example.com/app:sha-${GIT_SHA} registry.example.com/app:main
  docker push registry.example.com/app:sha-${GIT_SHA}
  docker push registry.example.com/app:main
  ```

- **For serverless/static deployments** (Vercel, Netlify, Cloudflare Pages, etc.) the platform
  typically assigns its own immutable deployment ID — capture it and tie it to the git SHA in CI
  output (and to the release tag; see below). Discover the platform's deployment ID convention
  rather than assuming one. **Fly.io** is containerized, not serverless: the immutable handle is the
  image digest or SHA-tagged image plus Fly release/version metadata (`fly releases list`); treat
  Fly deploys with the container image guidance above, not the serverless/static path.
- **Store build artifacts in a content-addressed registry.** Container registries (ECR, GCR, GHCR,
  Docker Hub) store images by digest in addition to tags. Reference images by digest
  (`image@sha256:…`) in deployment manifests (Kubernetes, Fly.io, etc.) so a tag update can never
  silently change what's running.
- **Version static asset bundles** with a content hash in the filename
  (e.g. `main.4f3c9a.js`). Most bundlers do this by default. It enables aggressive long-lived CDN
  caching: the filename changes when the content does, so stale-cache bugs become impossible for
  assets served under a permanent cache policy.
- **Never mutate a released artifact.** If a bug is found after release, build a new artifact from
  the fixed source and release that. Patching bytes in place defeats every integrity guarantee.

---

## Build once, promote across environments

Building separately for staging and production is the most common source of "it worked in staging"
bugs. The compiled output can differ even when the source is identical: subtle differences in ambient
runner state (OS patch level, cached artifacts, build-tool versions preinstalled on the runner but
not resolved through the lockfile), or `NODE_ENV` flags applied inconsistently.

- **Build exactly once in CI**, on merge to the release branch (or on tag, depending on the
  branching strategy). The artifact from that single build is the one that goes to staging, then
  production. Environment-specific concerns are injected at *runtime* via environment variables —
  never baked into a separate build.

  **Caveat for browser/static apps:** Frameworks that inline env vars at bundle time
  (`NEXT_PUBLIC_*`, Vite's `import.meta.env.VITE_*`, CRA's `REACT_APP_*`, etc.) cannot inject those
  values at runtime — they are substituted during the build itself. For these apps,
  build-once/promote is only achievable if the platform supports runtime config injection for static
  bundles (e.g. edge config, a server-side bootstrap script, or a runtime-generated config endpoint).
  If the platform does not support this, each environment requires a **distinct, separately built and
  tested immutable artifact** — and that per-env artifact must itself be promoted through the gate
  sequence (staging build tested → production deploy) rather than substituted on the fly. See
  `config.md` for the client vs server boundary details.

- **All environment differences belong in config, not in the artifact.** Database URLs, API keys,
  feature flags, third-party endpoints — these differ across environments and must be provided at
  startup via validated env vars (see `config.md`). An artifact with staging URLs compiled in is not
  promotable to production; it's a liability. For build-time-inlined browser vars, follow the
  per-env artifact path described above.
- **The promotion path is: build → staging deploy → (smoke test / approval gate) → production
  deploy.** The same artifact SHA or deployment ID advances through that path. CI and the deployment
  platform enforce the gates; the artifact itself is passive.
- **Staging must be production-equivalent.** Same Docker image or platform runtime, same config
  schema, same migrations applied. A staging environment on a different Node version or missing a
  required env var is a test theatre, not a gate.

---

## Version and release tagging

A release without a version tag is invisible in production incidents. "Which version is running?"
should be answerable in under 30 seconds from the dashboard.

- **Tag releases in git.** Use semantic versioning (`v1.4.2`) or a date-based scheme (`2026.06.19`)
  — pick the one that fits the project's release cadence and apply it consistently. A git tag is the
  human-readable anchor for "what shipped"; the commit SHA is the machine-verifiable one. Discover
  whether the repo already uses a tagging convention (`git tag -l`) before introducing a new scheme.
- **Record the version in the running process.** Expose it via the health endpoint, a build-time
  constant, or an environment variable set by CI at build time (e.g.
  `NEXT_PUBLIC_APP_VERSION=v1.4.2`). The pattern depends on the framework — discover it. The
  requirement is that an observability query can filter by release version at any time.
- **Pass the release identifier to the error tracker and APM.** Sentry, Datadog, New Relic, and most
  APM tools accept a `release` string. Wire the git SHA (or version tag) as that string so errors
  automatically group by release and regressions become immediately visible. The sourcemap upload
  that pairs with this is in **`craft-observability`** → `sentry.md`.
- **Set the version at build time in CI**, not by developers manually. A CI step that runs
  `git describe --tags --always` or reads the `GITHUB_SHA` / `GITHUB_REF_NAME` produces a
  consistent, automated value. Manual version bumps that require a human to remember a step are
  release process debt.

---

## The release process

A release process that lives in tribal knowledge is a bus-factor risk and an incident multiplier.
Every team member should be able to trigger a release correctly at 11 PM without calling the person
who "knows how it works."

- **Document the release process in the repo** — a `RELEASING.md` or a section in the project's
  `README`. At minimum: how to create a release tag, what CI automation that triggers, how to monitor
  the deploy, and what "done" looks like (health check URL, expected log line, platform dashboard URL).
  Keep it short enough to read in two minutes.
- **Automate the happy path.** For most projects this means: push a git tag → CI builds the artifact,
  runs the full gate suite (lint, types, tests, build), tags the Docker image or platform deploy,
  promotes to staging, waits for a smoke-test gate, then promotes to production. The goal is that a
  release requires a `git tag` and a `git push`, not a 20-step wiki page. Discover what CI system is
  in use (`ci-cd.md`) and wire the automation there.
- **Approval gates for production** should be explicit and auditable: a manual GitHub Actions
  environment approval, a deploy lock, or a required Slack/PR comment. The gate should be in CI
  config, not a verbal agreement. Keep the gate light enough that it's used rather than bypassed.
- **Separate "release" from "deploy."** A release is cutting an immutable artifact and tagging it; a
  deploy is activating it for traffic. This separation allows feature flags, blue/green, and canary
  deployments — all of which change *which* release is serving traffic without creating a new artifact.
  Canary and blue/green mechanics live in `ci-cd.md`; the point here is that the release process
  should not conflate artifact creation with traffic promotion.

---

## Rollback is part of the release design

A release without a tested rollback path is incomplete. The question to answer before shipping:
"if this release causes an incident 10 minutes after promotion, how do we get back in under 5 minutes?"

- **Know the rollback mechanism before you need it.** The mechanism is platform-specific — discover
  it from the IaC and platform config in the repo (`fly.toml`, `vercel.json`, k8s manifests,
  Terraform outputs) and document it in the release runbook. Full per-platform rollback commands are
  in `ci-cd.md` section *Rollback: one step per deploy path*.
- **The previous artifact must still be available.** Don't prune old images from the registry
  aggressively — retain at least the last N production-deployed artifacts (N ≥ 3 is a reasonable
  floor). A rollback that requires rebuilding defeats the immutable-artifact guarantee and adds
  10–20 minutes to the incident timeline.
- **Database migrations must be backward-compatible with the previous artifact** if rollback is to
  work without data restoration. A migration that drops a column the previous version still reads
  from makes rollback a data-loss event. Expand-contract patterns (add the new column, migrate data,
  delete the old column across two separate releases) keep the rollback path clean. Schema migration
  strategy is covered in **`craft-db`** → `migrations.md`; the obligation here is that the release
  process does not close the rollback window by shipping a breaking migration alongside the code
  change that removes the dependency on it.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| CI installs with `npm install` / `yarn install` (mutates lockfile) | Use `npm ci` / `--frozen-lockfile` / `--immutable`; install from the committed lockfile |
| Node/runtime version not pinned (no `.nvmrc`, `.node-version`, or `engines`) | Add a version pin file; configure CI to install that exact version |
| Build tools installed from ambient CI PATH, not from `package.json` dev deps | Add bundler/compiler versions as dev deps so they resolve through the lockfile |
| Container image tagged only as `latest` or a mutable branch name | Also push `sha-${GIT_SHA}` tag; reference deployments by SHA or digest |
| Separate build runs for staging and production | Build once on merge/tag; promote the same artifact; inject env vars at runtime |
| Environment-specific values (URLs, keys, flags) compiled into the artifact | Move all env differences to runtime config validated by the env schema (`config.md`) |
| No git tag convention; releases identified only by branch or "last deploy" | Adopt a consistent tag scheme (`vX.Y.Z` or date-based); automate tagging in CI |
| Release version not exposed in the running process or error tracker | Set `release`/`version` in Sentry/APM config and health endpoint from the git SHA |
| Release process documented only in someone's head or a chat thread | Write a `RELEASING.md` or README section; keep it under 2 minutes to read |
| Production promotion is manual, untracked, or requires SSH access | Automate in CI with an explicit approval gate; no manual `kubectl apply` or `rsync` |
| Old production images pruned aggressively (no rollback artifact available) | Retain at least the last 3 production-deployed artifacts in the registry |
| Breaking migration shipped in the same release as the code that removes its dependency | Use expand-contract: decouple the migration from the code change across two releases |
