# Windows Packaging

CHECKOUT OF HELL follows one rule for player-facing builds: **the player must not have to hunt for runtime files manually**.

## Development portable artifact

Run:

```powershell
python tools/package_portable.py
python tools/test_portable_package.py
```

The builder creates:

```text
dist/CHECKOUT-OF-HELL-Windows-Portable-dev.zip
dist/CHECKOUT-OF-HELL-Windows-Portable-dev.zip.sha256
```

The ZIP contains the prebuilt game PK3 and only the files required for first-run runtime bootstrap and attribution:

- `PLAY.bat` — player launcher with no Python/build dependency,
- `dist/checkout-of-hell-prototype.pk3` — prebuilt game package,
- `runtime-lock.json` — pinned upstream runtime versions,
- `tools/bootstrap_runtime.ps1` — official-source runtime downloader,
- `docs/THIRD_PARTY.md` — third-party runtime/license notes,
- `branding/icon.svg` — project branding source,
- `LICENSE`,
- `README-FIRST.txt`.

The development artifact intentionally does **not** contain GZDoom executables or Freedoom WAD data. On first launch, `PLAY.bat` invokes the same pinned official-source bootstrap used by the source checkout. This keeps the development ZIP small while preserving the one-click player experience.

## Windows portable release-candidate artifact

Run:

```powershell
python tools/package_release_candidate.py
python tools/test_release_candidate_package.py
python tools/test_legal_content_package_contract.py
```

The release-candidate builder creates:

```text
dist/CHECKOUT-OF-HELL-Windows-Portable-rc.zip
dist/CHECKOUT-OF-HELL-Windows-Portable-rc.zip.sha256
```

This artifact is the verified packaging path intended to become the public Windows portable demo package after the remaining manual demo gates pass. It is still **not a public demo release** and is only published as a CI artifact.

Compared with the development ZIP, the release candidate uses a stable player-facing payload layout, a local integrity gate and a bundled legal base-content layer:

- `PLAY.bat` — dedicated one-click release-candidate launcher,
- `game/CHECKOUT-OF-HELL.pk3` — prebuilt player-facing game payload,
- `external/freedoom2.wad` — pinned Freedoom base content obtained from the official upstream release during packaging,
- `licenses/FREEDOOM-COPYING.adoc` — exact BSD 3-Clause notice copied from that upstream release,
- `third_party/FREEDOOM-PROVENANCE.json` — official release/checksum URLs plus archive/WAD/license SHA-256 provenance,
- `package-manifest.json` — deterministic SHA-256 + byte-count manifest for every bundled project/content file,
- `tools/verify_player_package.ps1` — local integrity and bundled-license/provenance verifier run before any engine download,
- `runtime-lock.json` — the authoritative pinned upstream runtime/content versions,
- `tools/bootstrap_runtime.ps1` — official-source GZDoom resolver plus recovery path for missing/corrupt Freedoom content,
- `docs/THIRD_PARTY.md`, project `LICENSE` and branding,
- `README-FIRST.txt` with the player path and non-public-release warning.

### Freedoom packaging gate

The RC builder does not copy an arbitrary local WAD. It resolves the exact pinned `freedoom/freedoom` release from the official GitHub API, downloads the matching official release ZIP and `freedoom-*-CHECKSUM` asset, parses the archive SHA-256 and refuses to package the WAD unless the downloaded archive matches it.

The builder then extracts `freedoom2.wad` and the upstream `COPYING.adoc`, records their SHA-256 values in deterministic provenance metadata, and includes both in the package-wide manifest. The Windows verifier independently re-hashes the WAD and notice and checks that the provenance tag/path/license information matches the package runtime pin.

This closes the standalone **legal base-content** packaging gate without pretending the engine is bundled: GZDoom remains on the official-source bootstrap path in the current RC.

### First launch and later launches

`PLAY.bat` verifies the extracted package first. Because verified Freedoom content is already bundled, the normal RC path only needs to prepare GZDoom. On the first launch without a verified engine cache, `tools/bootstrap_runtime.ps1` downloads the exact pinned GZDoom release from official upstream and installs it locally. Later launches verify and reuse the cached engine, so the package can start without another API/download round-trip once the runtime cache is valid.

If bundled Freedoom is missing or fails provenance/hash validation, the bootstrap does not silently trust it: it falls back to the pinned official upstream Freedoom release and requires the official SHA-256 checksum before extracting a replacement.

A damaged or incomplete package stops before launch with an actionable message instead of silently substituting files from unofficial mirrors.

## Player contract

A normal Windows player should only need to:

1. extract the ZIP,
2. double-click `PLAY.bat`.

For the release-candidate path the launcher first checks bundled-file SHA-256 values from `package-manifest.json`, verifies the bundled Freedoom notice/provenance, prepares only missing pinned runtime components from official upstream, caches verified runtime files locally, and starts the prebuilt PK3. The player does not need Python and does not need to locate a WAD or engine manually.

## CI contract

GitHub Actions builds and validates the PK3, the development portable ZIP and the release-candidate ZIP.

`tools/test_portable_package.py` verifies the development artifact. `tools/test_release_candidate_package.py` additionally verifies that:

- all required release-candidate entries exist,
- no GZDoom executable or unexpected WAD/source tree is silently bundled,
- the player launcher verifies package integrity before runtime bootstrap and launch,
- no Python/source toolchain is needed by the player,
- every `package-manifest.json` SHA-256 and byte count matches the ZIP contents,
- runtime/content pins and delivery modes match `runtime-lock.json`,
- bundled Freedoom is plausibly sized and accompanied by the exact BSD notice/provenance paths,
- provenance WAD/license hashes match the packaged bytes and official URLs point to the pinned upstream release,
- the artifact is explicitly marked as non-public-release metadata,
- the generated outer SHA-256 sidecar matches the ZIP.

`tools/test_legal_content_package_contract.py` protects the official-source/checksum/notice/provenance design at source level. The Windows CI job additionally extracts the candidate and executes `tools/verify_player_package.ps1` with Windows PowerShell, while the existing runtime job separately resolves the pinned official engine and asks GZDoom to parse the current PK3.

## Public demo gate

The verified portable release-candidate artifact does **not** authorize a public demo release by itself. Standalone legal base-content packaging is now implemented/testable, but a public demo still requires the interactive target-Windows Closing Time playtest, manual save/load confirmation, real-controller confirmation, final balance/polish sign-off, real-hardware performance sanity, release notes and an explicit GitHub Release decision.

No GitHub Release should be created until those gates are genuinely complete.

**by Swir** — https://github.com/Swir
