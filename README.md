# CHECKOUT OF HELL

[![Build prototype](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml/badge.svg)](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml)

A fast, funny retro-FPS set during the worst night shift imaginable.

> **Status:** Prototype 0.10-dev — expanding original retail combat pass  
> **Project progress:** `█████░░░░░ 45%`

## Premise

The store is closed. The lights are flickering. Self-checkouts are angry.
Shopping carts are hunting staff. The night manager has definitely had enough.

CHECKOUT OF HELL is an original comedy-horror FPS inspired by the speed and
readability of classic shooters while building its own setting, characters,
weapons, jokes, levels and final art.

## Current playable loop

The prototype has a real shift objective instead of pure arena combat:

1. enter the department,
2. find and collect **three Breaker Fuses**,
3. survive hostile store equipment and escalating Overtime pressure,
4. exploit optional powered side routes when partial power comes back,
5. defeat the department supervisor while management reinforcements escalate,
6. return to the **front checkout** and physically clock out to finish the shift.

`MAP01 — Closing Time` stages that loop across a larger supermarket floor. Internal
retail barriers split traversal into lanes, the three breakers pull the player into left,
right and rear routes, and the **Night Manager does not enter the floor until all three
breakers are restored**. The HUD explicitly moves from `RESTORE ALL BREAKERS` to
`CLEAR THE SUPERVISOR`, then to `RETURN TO FRONT CHECKOUT` after the boss falls.

Full power starts a deliberate supervisor encounter instead of just spawning one boss.
Two rear-arena management-response anchors feed staged reinforcements into the fight:
**Angry Self-Checkout → Cart of Doom → Security Price Scanner → Possessed Pallet Jack**.
After the Night Manager is defeated, the player must fight back through the store to the
front checkout/timecard zone, where the shift is finally accepted and the map advances.

Partial power also changes the level. At `2/3` breakers, a rear-left **Staff Only**
security barrier powers down and opens an optional employee room with an **Employee of
the Month Stash**. No mandatory breaker is hidden in that room, so the reward is a real
side route rather than a disguised progression lock.

## Original combat presentation

The first combat encounters are progressively moving away from compatible-IWAD placeholders.
`Closing Time` already uses project-owned supermarket wall, shelf, Staff Only, floor and
ceiling surfaces plus original breaker, shutter and stash sprites.

The **Emergency Mop** uses four original first-person attack frames with its own swing cue.
The **Night Manager** uses an original animation set and the glowing **Manager Memo**
projectile with dedicated attack/down cues.

Prototype `0.9-dev` added the second complete signature slice:

- **Receipt Ripper** — original world pickup, five-frame first-person firing/cycling
  animation and dedicated fire/cycle sounds. Its view states no longer reference the
  compatible-IWAD shotgun sprite.
- **Angry Self-Checkout** — original ten-frame kiosk animation set, original hostile
  receipt projectile, original idle/attack/pain/down sounds and custom attack behavior.
  Its visible states no longer reference the compatible-IWAD shotgun-guy sprite.

Prototype `0.10-dev` expands that owned presentation across the mid/heavy combat loop:

- **Price-Gun SMG** — original world pickup and five-frame automatic weapon view,
  barcode-label impact puffs and dedicated trigger/label-feed cues.
- **Turbo Can Launcher** — original world pickup, five-frame launcher view, original
  soda-can projectile/explosion frames and dedicated launch/explosion cues.
- **Security Price Scanner** — original stationary turret animation, original scanning
  beam projectile and dedicated idle/attack/pain/down cues.

All current project-owned prototype combat art/audio is generated deterministically from
repository code using Python's standard library. Sprite PNGs carry ZDoom `grAb` offsets,
and CI verifies generated files, PK3 packaging, sound mappings and actor wiring.

`MAP02 — Warehouse 13.5` remains the heavier arena-style prototype while its dedicated
objective flow is developed.

Waiting around is increasingly dangerous. The **Overtime** director escalates through
`SHIFT ACTIVE` → `STORE UNSTABLE` → `OVERTIME` → `HELL RUSH`. Dedicated map
spawners add increasingly aggressive reinforcements as the shift drags on, while the
HUD shows the shift timer, current Overtime state, breaker progress, supervisor state
and the current task.

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

## Portable Windows development artifact

CI builds and verifies a player-facing portable ZIP that already contains the prebuilt
PK3 and therefore requires **no Python or source build toolchain on the player's PC**.
The verified artifact is named `checkout-of-hell-windows-portable-dev` in GitHub Actions.

The generated `CHECKOUT-OF-HELL-Windows-Portable-dev.zip` contains a dedicated
`PLAY.bat`, the prebuilt game package, runtime lock, official-source bootstrap and license
notices. The first launch downloads only the pinned legal runtime dependencies; the player
does not need to find an engine, WAD or Python manually. A SHA-256 sidecar is generated and
validated in CI. This remains a development artifact, not a public demo release.

See [`docs/PACKAGING.md`](docs/PACKAGING.md).

## What already works

- buildable `.pk3` prototype,
- structured UDMF `MAP01 — Closing Time` objective prototype,
- generated UDMF `MAP02 — Warehouse 13.5` arena prototype,
- **Emergency Mop**, **Receipt Ripper**, **Price-Gun SMG**, **Turbo Can Launcher**,
- **Angry Self-Checkout**, **Cart of Doom**, **Night Manager**, **Security Price Scanner**, **Possessed Pallet Jack** and **The Regional Manager** prototype,
- three-breaker + supervisor-clear objective loop,
- staged Night Manager reinforcement waves and physical return-to-checkout objective,
- optional Staff Only side room and Employee of the Month reward stash,
- Overtime escalation director with timed reinforcement spawners,
- shift/objective/Overtime HUD overlay,
- first original supermarket wall/shelf/staff/floor/ceiling material pack,
- original breaker, shutter and stash prototype sprites,
- original **Emergency Mop** first-person sprite/animation set with combat swing cue,
- original **Receipt Ripper** pickup/view sprite set with fire/cycle cues,
- original **Price-Gun SMG** pickup/view sprite set with barcode-label impact feedback and weapon cues,
- original **Turbo Can Launcher** pickup/view sprite set plus original can projectile/explosion and weapon cues,
- original **Angry Self-Checkout** animation set, receipt projectile and combat cues,
- original **Security Price Scanner** animation set, scanning projectile and combat cues,
- original **Night Manager** animation set, Manager Memo projectile and boss combat cues,
- deterministic stdlib-only asset generation with ZDoom sprite offsets and dedicated CI asset contract,
- one-click Windows dependency bootstrap and pinned reproducible runtime lock,
- verified portable Windows artifact builder with SHA-256 sidecar,
- automated build + gameplay + layout + Staff Only + boss/escape + original-asset + packaging contract tests,
- pinned GZDoom `-norun` startup/parser validation on Windows CI,
- original project icon concept and documented asset/weapon/level/packaging direction.

The prototype deliberately does **not** redistribute proprietary Doom game data.

## Development runtime

The current pinned runtime is GZDoom `g4.14.2` plus Freedoom `v0.13.0`. Contributors do not need to download these manually; `PLAY.bat` handles them. Runtime pins live in `runtime-lock.json` and should only change after compatibility validation.

CI also downloads the pinned official runtime and asks GZDoom itself to load and parse the current PK3 through its non-interactive `-norun` startup path. This catches engine-level script or package errors that static Python contract tests cannot detect.

Manual developer commands remain available:

```powershell
python tools/build.py
python tools/smoke_test.py
python tools/test_gameplay_contract.py
python tools/test_closing_time_layout.py
python tools/test_staff_room_contract.py
python tools/test_boss_escape_contract.py
python tools/test_original_assets.py
python tools/package_portable.py
python tools/test_portable_package.py
.\tools\gzdoom_runtime_smoke.ps1
```

## Prototype weapons

- Slot 1: Emergency Mop — original prototype view sprites + original swing cue
- Shotgun pickup: Receipt Ripper — original pickup/view sprites + original fire/cycle cues
- Chaingun pickup: Price-Gun SMG — original pickup/view sprites + barcode-label impact feedback
- Rocket Launcher pickup: Turbo Can Launcher — original pickup/view sprites + original soda-can projectile/explosion

See [`docs/WEAPONS.md`](docs/WEAPONS.md).

## Maps

- `MAP01` — **Closing Time** — structured objective prototype with original retail surfaces, powered side route, staged supervisor fight and checkout escape
- `MAP02` — **Warehouse 13.5** — combat/pressure prototype

See [`docs/LEVEL_DESIGN.md`](docs/LEVEL_DESIGN.md).

## Asset policy

No proprietary Doom, Star Wars or other commercial game assets belong in this repository.
The current runtime art/audio pack is generated from our own source code during the build.
Emergency Mop, Receipt Ripper, Price-Gun SMG, Turbo Can Launcher, Angry Self-Checkout,
Security Price Scanner and Night Manager now have project-owned visible combat presentation.
Cart of Doom, Possessed Pallet Jack and Regional Manager still use compatible-runtime
placeholder visuals and must be replaced before standalone release.

See [`docs/ASSET_POLICY.md`](docs/ASSET_POLICY.md).

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

## Author

**by Swir**  
GitHub: https://github.com/Swir
