# Third-party runtime components

CHECKOUT OF HELL is developed so players do not have to hunt for dependencies manually. The source checkout uses pinned official-source bootstrap logic, while the Windows release-candidate package now redistributes the compatible Freedoom base-content WAD with its upstream license notice and deterministic provenance record.

## GZDoom

- Upstream: `ZDoom/gzdoom`
- Pinned runtime tag: `g4.14.2`
- Source code license: GNU GPL v3
- Delivery in the Windows release candidate: **not redistributed**; obtained automatically from the official GitHub Release API/release asset on first launch when a verified cached copy is not already present

GZDoom is not authored by the CHECKOUT OF HELL project. Its upstream copyright and license terms remain in force. The current player package deliberately keeps the engine on the official-source bootstrap path instead of copying a GZDoom binary into the ZIP.

## Freedoom

- Upstream: `freedoom/freedoom`
- Pinned runtime tag: `v0.13.0`
- Content license: BSD 3-Clause
- Official release asset: selected from the pinned upstream GitHub Release using `runtime-lock.json`
- Integrity source: the matching official `freedoom-*-CHECKSUM` release asset

### Windows release-candidate redistribution path

`tools/package_release_candidate.py` resolves the exact pinned Freedoom release from the official GitHub API, downloads the official release ZIP and checksum asset, requires a parsable SHA-256 entry for that archive, and refuses to continue if the downloaded archive does not match.

After that verification the builder extracts `freedoom2.wad` from the checksum-verified release ZIP. The Freedoom `v0.13.0` binary release ZIP does not contain `COPYING.adoc`, so the builder obtains the exact notice separately from the **same pinned upstream repository tag** (`freedoom/freedoom` at `v0.13.0`) and writes it to `licenses/FREEDOOM-COPYING.adoc`. This keeps both the content and its legal notice tied to immutable official upstream sources without weakening the archive checksum gate.

The generated package also contains `third_party/FREEDOOM-PROVENANCE.json` with the pinned repo/tag, official archive/checksum URLs, pinned-tag license URL, archive SHA-256, WAD SHA-256, license SHA-256 and package paths. `package-manifest.json` independently covers those bundled files with the package-wide integrity manifest.

The BSD 3-Clause license permits redistribution in binary form when its copyright notice, conditions and disclaimer are reproduced in the documentation and/or other materials provided with the distribution. The release-candidate package therefore carries the exact upstream `COPYING.adoc` alongside the redistributed WAD. The package does not use the Freedoom project or contributor names as an endorsement.

For a source checkout or recovery case where the bundled WAD is absent, corrupt or does not match its verified provenance, `tools/bootstrap_runtime.ps1` can still obtain the pinned Freedoom archive from the official upstream release and requires the official checksum to verify it before extraction.

## Portable Python build runtime

A source checkout may need Python to build the prototype PK3. If no system Python is available, the source launcher downloads the pinned Windows embeddable package directly from `python.org`.

- Pinned version: Python 3.12.10
- Upstream: Python Software Foundation
- Purpose: local source-build tooling only

The packaged player release candidate contains the already-built game PK3 and does not require Python during normal play.

## Project policy

- No unofficial mirrors are used by the automatic bootstrap or release-candidate content builder.
- No proprietary Doom IWAD or commercial game assets are downloaded or bundled.
- Runtime/content versions are pinned in `runtime-lock.json` for reproducibility.
- Freedoom redistribution includes its exact upstream BSD notice and a machine-verifiable provenance record.
- GZDoom remains an automatic official-source first-run dependency in the current release-candidate package.
- Runtime pins should only be changed after compatibility validation.

This document describes the project distribution design and bundled notices; it is not a substitute for upstream license texts. The exact Freedoom license text carried by a generated player package is `licenses/FREEDOOM-COPYING.adoc`.
