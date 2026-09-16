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

The artifact intentionally does **not** contain GZDoom executables or Freedoom WAD data. On first launch, `PLAY.bat` invokes the same pinned official-source bootstrap used by the source checkout. This keeps the package small and makes runtime provenance explicit while still preserving the one-click player experience.

## Player contract

A normal Windows player should only need to:

1. extract the ZIP,
2. double-click `PLAY.bat`.

The launcher resolves the pinned official GZDoom/Freedoom releases, downloads them, verifies Freedoom against the official checksum when parsable, caches the runtime locally, and starts the prebuilt PK3. The player does not need Python and does not need to locate a WAD or engine manually.

## CI contract

GitHub Actions must build and validate both the PK3 and the portable ZIP. `tools/test_portable_package.py` verifies that:

- all required portable entries exist,
- the package contains the prebuilt PK3,
- the portable launcher has no Python/build dependency,
- runtime EXE/WAD files are not silently bundled,
- the player-facing no-manual-search rule is documented,
- the generated SHA-256 sidecar matches the ZIP.

The existing Windows runtime job separately resolves the pinned official runtime and asks GZDoom to parse the current PK3.

## Public demo gate

The portable development artifact is **not** a public demo release by itself. A public demo still requires presentable original visual/audio content, a real gameplay playtest, controller/accessibility/performance passes, stable packaging and release notes. When those gates are met, this portable builder can become the basis for the downloadable demo package.

**by Swir** — https://github.com/Swir
