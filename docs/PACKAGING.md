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

The development artifact intentionally does **not** contain GZDoom executables or Freedoom WAD data. On first launch, `PLAY.bat` invokes the same pinned official-source bootstrap used by the source checkout. This keeps the package small and makes runtime provenance explicit while still preserving the one-click player experience.

## Windows portable release-candidate artifact

Run:

```powershell
python tools/package_release_candidate.py
python tools/test_release_candidate_package.py
```

The release-candidate builder creates:

```text
dist/CHECKOUT-OF-HELL-Windows-Portable-rc.zip
dist/CHECKOUT-OF-HELL-Windows-Portable-rc.zip.sha256
```

This artifact is the verified packaging path intended to become the public Windows portable demo package after the remaining manual demo gates pass. It is still **not a public demo release** and is only published as a CI artifact.

Compared with the development ZIP, the release candidate adds a stable player-facing payload layout and a local integrity gate:

- `PLAY.bat` — dedicated one-click release-candidate launcher,
- `game/CHECKOUT-OF-HELL.pk3` — prebuilt player-facing game payload,
- `package-manifest.json` — deterministic SHA-256 + byte-count manifest for every bundled project file,
- `tools/verify_player_package.ps1` — local integrity verifier run before any runtime download,
- `runtime-lock.json` — the authoritative pinned upstream runtime versions,
- `tools/bootstrap_runtime.ps1` — official-source GZDoom/Freedoom resolver,
- `docs/THIRD_PARTY.md`, `LICENSE` and project branding,
- `README-FIRST.txt` with the player path and non-public-release warning.

`PLAY.bat` verifies the extracted package first, then prepares the runtime, then starts MAP01. A damaged or incomplete package stops before launch with an actionable message instead of silently substituting files.

### Why the current release candidate still downloads the runtime

The project deliberately does not redistribute GZDoom executables or Freedoom WAD data inside the current CHECKOUT OF HELL ZIP. The package instead resolves the exact pinned upstream releases automatically on first launch. This keeps third-party provenance and license boundaries explicit while still satisfying the player rule: **extract once, double-click once, never hunt for dependencies manually**.

A future truly self-contained legal package remains a separate roadmap item. It will only be marked complete if every redistributed third-party component and corresponding notice/source obligation is handled correctly.

## Player contract

A normal Windows player should only need to:

1. extract the ZIP,
2. double-click `PLAY.bat`.

For the release-candidate path the launcher first checks bundled-file SHA-256 values from `package-manifest.json`, then resolves the pinned official GZDoom/Freedoom releases, downloads them, verifies Freedoom against the official checksum when parsable, caches the runtime locally, and starts the prebuilt PK3. The player does not need Python and does not need to locate a WAD or engine manually.

## CI contract

GitHub Actions builds and validates the PK3, the development portable ZIP and the release-candidate ZIP.

`tools/test_portable_package.py` verifies the development artifact. `tools/test_release_candidate_package.py` additionally verifies that:

- all required release-candidate entries exist,
- no source tree or third-party runtime EXE/WAD is silently bundled,
- the player launcher verifies package integrity before runtime bootstrap and launch,
- no Python/source toolchain is needed by the player,
- every `package-manifest.json` SHA-256 and byte count matches the ZIP contents,
- runtime pins in the package manifest match `runtime-lock.json`,
- the artifact is explicitly marked as non-public-release metadata,
- the generated outer SHA-256 sidecar matches the ZIP.

The Windows CI job also extracts the candidate and executes `tools/verify_player_package.ps1` with Windows PowerShell, while the existing runtime job separately resolves the pinned official runtime and asks GZDoom to parse the current PK3.

## Public demo gate

The verified portable release-candidate artifact does **not** authorize a public demo release by itself. A public demo still requires the interactive target-Windows Closing Time playtest, save/load confirmation, real-controller confirmation, final balance/polish sign-off, real-hardware performance sanity, release notes and the remaining legal packaging decision.

No GitHub Release should be created until those gates are genuinely complete.

**by Swir** — https://github.com/Swir
