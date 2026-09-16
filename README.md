# CHECKOUT OF HELL

[![Build prototype](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml/badge.svg)](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml)

A fast, funny retro-FPS set during the worst night shift imaginable.

> **Status:** Prototype 0.2-dev — two-map combat foundation + Overtime pressure  
> **Project progress:** `██░░░░░░░░ 22%`

## Premise

The store is closed. The lights are flickering. Self-checkouts are angry.
Shopping carts are hunting staff. The night manager has definitely had enough.

CHECKOUT OF HELL is an original comedy-horror FPS inspired by the speed and
readability of classic shooters while building its own setting, characters,
weapons, jokes, levels and final art.

## One-click Windows start

**Players should not have to search the internet for game dependencies.**

From a source checkout, double-click:

```text
PLAY.bat
```

The launcher automatically:

1. resolves the runtime versions pinned in `runtime-lock.json`,
2. downloads GZDoom from the official `ZDoom/gzdoom` GitHub Release,
3. downloads Freedoom from the official `freedoom/freedoom` GitHub Release,
4. verifies the Freedoom SHA-256 against its official checksum when available,
5. downloads an official portable Python build from `python.org` only when a source build needs Python and none is installed,
6. builds and smoke-tests the PK3 when necessary,
7. starts the game.

Downloaded runtime files are cached locally, so later starts normally do not need to download them again. Network failures stop with a clear error instead of redirecting the user to unofficial mirrors.

See [`docs/THIRD_PARTY.md`](docs/THIRD_PARTY.md) for runtime sources and license notes.

## What already works

- buildable `.pk3` prototype,
- generated UDMF `MAP01 — Closing Time`,
- generated UDMF `MAP02 — Warehouse 13.5`,
- **Emergency Mop**,
- **Receipt Ripper**,
- **Price-Gun SMG**,
- **Turbo Can Launcher** with explosive can projectile,
- **Angry Self-Checkout**,
- **Cart of Doom**,
- **Night Manager**,
- **Security Price Scanner** turret,
- **Possessed Pallet Jack**,
- **The Regional Manager** prototype boss,
- map-specific **Overtime** escalation that adds pressure when the player stays too long,
- one-click Windows dependency bootstrap,
- pinned reproducible runtime lock,
- Windows development launchers,
- automated structural build/smoke tests,
- verified Windows download/bootstrap resolution with the real pinned runtime,
- real GZDoom `g4.14.2` startup/parser validation in headless Linux CI using Mesa software rendering,
- verified GitHub Actions prototype artifact build,
- original project icon concept,
- documented asset policy, weapon plan, level direction and Overtime rules.

The prototype deliberately does **not** redistribute proprietary Doom game data.

## Overtime

Overtime is the first signature gameplay system rather than a cosmetic feature. Each prototype department owns its own escalation timing:

- `MAP01 — Closing Time`: pressure begins after 30 seconds and escalates through carts, a scanner/pallet-jack wave and the Night Manager before recurring pressure waves.
- `MAP02 — Warehouse 13.5`: machinery pressure begins after 20 seconds and escalates faster, with carts, pallet jacks and scanner turrets before recurring waves.

The purpose is to make objectives feel urgent without using invisible damage or simply inflating enemy health. Future passes will add alarm/lighting/HUD feedback and connect the pressure system to real shift objectives.

See [`docs/OVERTIME.md`](docs/OVERTIME.md).

## Development runtime

The current pinned runtime is GZDoom `g4.14.2` plus Freedoom `v0.13.0`. Contributors do not need to download these manually; `PLAY.bat` handles them. Runtime pins live in `runtime-lock.json` and should only change after compatibility validation.

Manual developer commands remain available:

```powershell
python tools/build.py
python tools/smoke_test.py
```

CI now separates concerns deliberately:

- Ubuntu structural tests build and inspect the PK3/maps/actor contracts.
- Windows CI resolves, downloads and verifies the same official runtime payload used by `PLAY.bat`.
- Headless Ubuntu CI installs the pinned official GZDoom build and runs the PK3 through the real engine parser/startup path under Xvfb + Mesa software rendering.

GitHub's hosted Windows runner does not expose a usable OpenGL/Vulkan graphics device for GZDoom, so **interactive Windows rendering is not claimed as CI-verified**. A real Windows playtest remains a separate release gate.

## Prototype weapons

- Slot 1: Emergency Mop
- Shotgun pickup: Receipt Ripper
- Chaingun pickup: Price-Gun SMG
- Rocket Launcher pickup: Turbo Can Launcher

See [`docs/WEAPONS.md`](docs/WEAPONS.md).

## Maps

- `MAP01` — **Closing Time**
- `MAP02` — **Warehouse 13.5**

See [`docs/LEVEL_DESIGN.md`](docs/LEVEL_DESIGN.md).

## Asset policy

No proprietary Doom, Star Wars or other commercial game assets belong in this repository. Prototype visuals may temporarily reference sprite names supplied by a compatible IWAD at runtime; those assets are not distributed here. Final art, audio, UI, characters and map decoration are planned to be original.

See [`docs/ASSET_POLICY.md`](docs/ASSET_POLICY.md).

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

## Author

**by Swir**  
GitHub: https://github.com/Swir
