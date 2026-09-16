# Third-party runtime components

CHECKOUT OF HELL is developed so that players do not have to hunt for dependencies manually.
The one-click launcher downloads required redistributable runtime components directly from their official upstream sources.

## GZDoom

- Upstream: `ZDoom/gzdoom`
- Pinned runtime tag: `g4.14.2`
- Source code license: GNU GPL v3
- Download source used by the bootstrap: the official GitHub Release API and its official release asset URL

GZDoom is not authored by the CHECKOUT OF HELL project. Its upstream copyright and license terms remain in force.

## Freedoom

- Upstream: `freedoom/freedoom`
- Pinned runtime tag: `v0.13.0`
- Content license: BSD 3-Clause
- Download source used by the bootstrap: the official GitHub Release API and its official release asset URL

The bootstrap downloads the official checksum file when available and verifies the selected Freedoom archive SHA-256 when the checksum entry can be parsed.

## Portable Python build runtime

A source checkout may need Python to build the prototype PK3. If no system Python is available, the launcher downloads the pinned Windows embeddable package directly from `python.org`.

- Pinned version: Python 3.12.10
- Upstream: Python Software Foundation
- Purpose: local source-build tooling only

A packaged player release is expected to contain the already-built game PK3 and therefore should not require Python during normal play.

## Project policy

- No unofficial mirrors are used by the automatic bootstrap.
- No proprietary Doom IWAD or commercial game assets are downloaded or bundled.
- Runtime versions are pinned in `runtime-lock.json` for reproducibility.
- Runtime pins should only be changed after compatibility validation.
