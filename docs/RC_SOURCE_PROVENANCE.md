# Release-candidate source provenance

CHECKOUT OF HELL release-candidate packages must be traceable to the exact repository snapshot that produced them. This is an auditability gate for non-public Windows candidates; it does not authorize a public demo or replace the target-Windows gameplay sign-off.

## Manifest record

`tools/package_release_candidate.py` captures source identity before generating build outputs and writes it into `package-manifest.json`:

- `source.commit` — the full 40-character Git commit SHA when Git metadata is available,
- `source.branch` — the active branch/ref reported by CI or Git,
- `source.clean` — whether the tracked source tree was clean before the package build started.

Untracked build/cache output is intentionally excluded from the clean-tree check so repeated package builds do not invalidate an otherwise unchanged checkout. Tracked source edits still make the snapshot dirty.

When a source archive has no `.git` metadata, the packager records source identity as unavailable rather than inventing a commit. Such a package can still be useful for local development, but it cannot pass the CI release-candidate provenance contract.

## CI gate

`tools/test_release_candidate_package.py` requires a CI candidate to contain:

1. a full commit SHA,
2. a non-empty branch/ref,
3. `source.clean: true`,
4. an embedded commit that exactly matches `git rev-parse HEAD` in the checkout validating the package.

These checks run in addition to the existing package-wide SHA-256/byte-count manifest, bundled Freedoom license/provenance verification, official-source GZDoom bootstrap policy and outer ZIP checksum.

## Relationship to Windows sign-off

`WINDOWS-DEMO-SIGNOFF.bat` already records the source branch/commit/cleanliness of the checkout used for the interactive evidence run and builds the exact RC from that checkout. The package now carries its own source snapshot as well, so the candidate artifact remains traceable after extraction or transfer.

A source-provenance PASS does **not** mean the demo is ready. The human Closing Time difficulty/controller/performance/polish evidence, remaining legal/release gates, release notes and explicit GitHub Release decision remain separate requirements in `ROADMAP.md`.

**by Swir** — https://github.com/Swir
