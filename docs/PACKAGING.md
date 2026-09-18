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
python tools/test_legal_content_bundle.py
python tools/test_legal_content_package_contract.py
python tools/test_windows_offline_runtime_cache_contract.py
```

The release-candidate builder creates:

```text
dist/CHECKOUT-OF-HELL-Windows-Portable-rc.zip
dist/CHECKOUT-OF-HELL-Windows-Portable-rc.zip.sha256
dist/CHECKOUT-OF-HELL-Legal-Content-rc.zip
dist/CHECKOUT-OF-HELL-Legal-Content-rc.zip.sha256
```

The Windows portable artifact is the verified packaging path intended to become the public Windows portable demo package after the remaining manual demo gates pass. It is still **not a public demo release** and is only published as a CI artifact.

Compared with the development ZIP, the release candidate uses a stable player-facing payload layout, a local integrity gate and a bundled legal base-content layer:

- `PLAY.bat` — dedicated one-click release-candidate launcher,
- `game/CHECKOUT-OF-HELL.pk3` — prebuilt player-facing game payload,
- `external/freedoom2.wad` — pinned Freedoom base content obtained from the official upstream release during packaging,
- `licenses/FREEDOOM-COPYING.adoc` — exact BSD 3-Clause notice obtained from the same pinned upstream repository tag,
- `third_party/FREEDOOM-PROVENANCE.json` — official release/checksum URLs, pinned-tag license URL and archive/WAD/license SHA-256 provenance,
- `package-manifest.json` — deterministic SHA-256 + byte-count manifest for every bundled project/content file,
- `tools/verify_player_package.ps1` — local integrity and bundled-license/provenance verifier run before any engine download,
- `runtime-lock.json` — the authoritative pinned upstream runtime/content versions,
- `tools/bootstrap_runtime.ps1` — official-source GZDoom resolver plus recovery path for missing/corrupt Freedoom content,
- `docs/THIRD_PARTY.md`, project `LICENSE` and branding,
- `README-FIRST.txt` with the player path and non-public-release warning.

### Freedoom packaging gate

The RC builder does not copy an arbitrary local WAD. It resolves the exact pinned `freedoom/freedoom` release from the official GitHub API, downloads the matching official release ZIP and `freedoom-*-CHECKSUM` asset, parses the archive SHA-256 and refuses to package the WAD unless the downloaded archive matches it.

The builder then extracts `freedoom2.wad` from that checksum-verified release ZIP. The `v0.13.0` binary release ZIP does not contain `COPYING.adoc`, so the exact BSD notice is fetched from the same immutable `freedoom/freedoom` tag instead. Both official source URLs and the archive/WAD/license hashes are recorded in deterministic provenance metadata and covered again by the package-wide manifest.

This closes the verified Freedoom **legal base-content** bundling step without pretending the engine is bundled: GZDoom remains on the official-source bootstrap path in the current RC.

### Standalone legal-content release candidate

The same packaging run now emits `CHECKOUT-OF-HELL-Legal-Content-rc.zip` as a deterministic content-only artifact. It is not assembled from a second download path: it is built from the exact already-verified bytes used by the Windows player RC. The bundle contains only:

- `game/CHECKOUT-OF-HELL.pk3`,
- `external/freedoom2.wad`,
- `licenses/FREEDOOM-COPYING.adoc`,
- `third_party/FREEDOOM-PROVENANCE.json`,
- project `LICENSE`,
- `docs/THIRD_PARTY.md`,
- `runtime-lock.json`,
- `README-CONTENT.txt`,
- `content-manifest.json`.

`content-manifest.json` binds the bundle to the exact source commit/ref, records MIT + BSD-3-Clause license identities, names the pinned GZDoom tag without claiming the engine is included, and covers every payload entry with SHA-256 plus byte count. The outer ZIP also receives its own `.sha256` sidecar.

The content bundle intentionally contains **no executable, DLL, batch file, PowerShell bootstrap or GZDoom binary**. It is a reusable legal-content layer for packaging/testing, not a player-facing shortcut that would force users to find an engine manually. Normal Windows players still use the portable package and `PLAY.bat`, which obtains a missing pinned GZDoom runtime automatically from official upstream.

`tools/test_legal_content_bundle.py` proves that the bundle contains exactly the audited content set, that its manifest/source provenance/hashes are valid, that Freedoom notice/provenance matches the pinned official release, and that every shared payload byte is identical to the corresponding file in the Windows RC. CI runs this contract on Ubuntu and again after packaging on Windows.

### First launch and later launches

`PLAY.bat` verifies the extracted package first. Because verified Freedoom content is already bundled, the normal RC path only needs to prepare GZDoom. On the first launch without a verified engine cache, `tools/bootstrap_runtime.ps1` downloads the exact pinned GZDoom release from official upstream and installs it locally. Later launches verify and reuse the cached engine, so the package can start without another API/download round-trip once the runtime cache is valid.

If bundled Freedoom is missing or fails provenance/hash validation, the bootstrap does not silently trust it: it falls back to the pinned official upstream Freedoom release and requires the official SHA-256 checksum before extracting a replacement.

A damaged or incomplete package stops before launch with an actionable message instead of silently substituting files from unofficial mirrors.

### Offline reuse gate

Windows CI now proves the later-launch path instead of treating it as documentation only. `tools/test_windows_offline_runtime_cache.ps1` works against the **extracted release-candidate package**: it first runs the package verifier, primes the pinned runtime once from official upstream, records the installed GZDoom/Freedoom SHA-256 values and validates the runtime manifest against `runtime-lock.json`.

The test then removes the downloaded archive cache, blocks outbound networking in the PowerShell process using both the .NET default proxy and `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY`, clears the GitHub token, and executes the packaged bootstrap a second time. The second pass must succeed without creating any archive-cache files. GZDoom and Freedoom must retain unchanged hashes, and the rewritten runtime manifest must retain the exact pinned GZDoom asset name/ID/byte count plus the bundled-verified Freedoom delivery marker.

This verifies a useful failure-resistant property: after one successful preparation, a valid extracted RC can reuse its verified installed runtime without another network round-trip. It does **not** turn the current package into a fully self-contained engine redistribution and does not complete the human demo sign-off.

## Player contract

A normal Windows player should only need to:

1. extract the ZIP,
2. double-click `PLAY.bat`.

For the release-candidate path the launcher first checks bundled-file SHA-256 values from `package-manifest.json`, verifies the bundled Freedoom notice/provenance, prepares only missing pinned runtime components from official upstream, caches verified runtime files locally, and starts the prebuilt PK3. The player does not need Python and does not need to locate a WAD or engine manually.

## CI contract

GitHub Actions builds and validates the PK3, the development portable ZIP, the standalone legal-content RC and the Windows release-candidate ZIP.

`tools/test_portable_package.py` verifies the development artifact. `tools/test_release_candidate_package.py` additionally verifies that:

- all required release-candidate entries exist,
- no GZDoom executable or unexpected WAD/source tree is silently bundled,
- the player launcher verifies package integrity before runtime bootstrap and launch,
- no Python/source toolchain is needed by the player,
- every `package-manifest.json` SHA-256 and byte count matches the ZIP contents,
- runtime/content pins and delivery modes match `runtime-lock.json`,
- bundled Freedoom is plausibly sized and accompanied by the exact BSD notice/provenance paths,
- provenance WAD/license hashes match the packaged bytes and official URLs point to the pinned upstream release/tag sources,
- the artifact is explicitly marked as non-public-release metadata,
- the generated outer SHA-256 sidecar matches the ZIP.

`tools/test_legal_content_bundle.py` independently verifies the content-only artifact, its exact source binding and entry hashes, absence of executable/bootstrap files, license/provenance completeness and byte-for-byte equality with the same content in the Windows RC.

`tools/test_legal_content_package_contract.py` protects the official-source/checksum/notice/provenance design at source level. `tools/test_windows_offline_runtime_cache_contract.py` protects the extracted-RC offline reuse harness and CI wiring. The Windows CI job additionally rebuilds/verifies the standalone legal-content artifact, extracts the candidate, executes `tools/verify_player_package.ps1`, primes the pinned runtime once and then proves verified runtime reuse after archive-cache removal with outbound networking blocked. The existing runtime job separately resolves the pinned official engine and asks GZDoom to parse the current PK3.

## Public demo gate

The verified portable release-candidate artifact and standalone legal-content artifact do **not** authorize a public demo release by themselves. The standalone legal-content packaging milestone is now implemented/testable, while the player package intentionally keeps GZDoom on the pinned official-source first-run bootstrap because no engine redistribution claim is being made.

A public demo still requires the interactive target-Windows Closing Time playtest, manual save/load confirmation, real-controller confirmation, final balance/polish sign-off, real-hardware performance sanity, release notes and an explicit GitHub Release decision.

No GitHub Release should be created until those gates are genuinely complete.

**by Swir** — https://github.com/Swir