# CHECKOUT OF HELL

[![Build prototype](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml/badge.svg)](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml)

A fast, funny retro-FPS set during the worst night shift imaginable.

> **Status:** Prototype 0.3-dev — first objective loop + Overtime director  
> **Project progress:** `██░░░░░░░░ 25%`

## Premise

The store is closed. The lights are flickering. Self-checkouts are angry.
Shopping carts are hunting staff. The night manager has definitely had enough.

CHECKOUT OF HELL is an original comedy-horror FPS inspired by the speed and
readability of classic shooters while building its own setting, characters,
weapons, jokes, levels and final art.

## Current playable loop

The prototype now has its first real shift objective instead of pure arena combat:

1. enter the department,
2. find and collect **three Breaker Fuses**,
3. survive the supervisor and hostile store equipment,
4. defeat the department supervisor,
5. clock out automatically when both conditions are complete.

Waiting around is increasingly dangerous. The **Overtime** director escalates through
`SHIFT ACTIVE` → `STORE UNSTABLE` → `OVERTIME` → `HELL RUSH`. Dedicated map
spawners add increasingly aggressive reinforcements as the shift drags on, while the
HUD shows the shift timer, current Overtime state, breaker progress and supervisor state.

The two current prototype maps use the same loop with different enemy sets. The final
campaign will replace these simple arenas with fully structured supermarket departments,
objectives, secrets and environmental interactions.

See [`docs/GAMEPLAY_LOOP.md`](docs/GAMEPLAY_LOOP.md).

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
- three-breaker + supervisor-clear objective loop,
- Overtime escalation director with timed reinforcement spawners,
- shift/objective/Overtime HUD overlay,
- automatic map completion once the shift objective is satisfied,
- one-click Windows dependency bootstrap,
- pinned reproducible runtime lock,
- Windows development launchers,
- automated build + smoke + gameplay contract tests,
- pinned GZDoom `-norun` startup/parser validation on Windows CI,
- verified GitHub Actions artifact build,
- original project icon concept,
- documented asset policy, weapon plan and level direction.

The prototype deliberately does **not** redistribute proprietary Doom game data.

## Development runtime

The current pinned runtime is GZDoom `g4.14.2` plus Freedoom `v0.13.0`. Contributors do not need to download these manually; `PLAY.bat` handles them. Runtime pins live in `runtime-lock.json` and should only change after compatibility validation.

CI also downloads the pinned official runtime and asks GZDoom itself to load and parse the current PK3 through its non-interactive `-norun` startup path. This catches engine-level script or package errors that static Python contract tests cannot detect.

Manual developer commands remain available:

```powershell
python tools/build.py
python tools/smoke_test.py
python tools/test_gameplay_contract.py
.\tools\gzdoom_runtime_smoke.ps1
```

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
