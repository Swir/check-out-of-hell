# CHECKOUT OF HELL

[![Build prototype](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml/badge.svg)](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml)

A fast, funny retro-FPS set during the worst night shift imaginable.

> **Status:** Prototype 0.14-dev — Overtime environmental hazard pass  
> **Project progress:** `██████░░░░ 55%`

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

Prototype `0.13-dev` added a lightweight exploration/comedy layer to that route. Closing Time
hides **three optional Corporate Compliance Memos** across a front detour, an east-side
combat detour and the powered Staff Only room. Each pickup advances a different absurd policy
message, while the HUD tracks `OPTIONAL MEMOS 0/3` without making the collectibles mandatory.
The memo sprite and pickup cue are project-owned and generated deterministically during builds.

Prototype `0.14-dev` makes **Overtime change the floor itself**, not just enemy pressure.
Four dedicated hazard anchors are positioned away from the spawn/clock-out lane. At `90s`,
they begin readable warning-alarm flashes; at `180s`, those locations start discharging
telegraphed electrical floor arcs; at `270s / HELL RUSH`, the trap cadence accelerates to one
pulse every 20 seconds per anchor. The arcs have a visible warning phase before dealing a small
area burst, so Overtime is dangerous without becoming random or unreadable. The warning and arc
sprites/audio are entirely project-owned and generated deterministically from repository code.

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

Prototype `0.10-dev` expanded that owned presentation across the mid/heavy combat loop:

- **Price-Gun SMG** — original world pickup and five-frame automatic weapon view,
  barcode-label impact puffs and dedicated trigger/label-feed cues.
- **Turbo Can Launcher** — original world pickup, five-frame launcher view, original
  soda-can projectile/explosion frames and dedicated launch/explosion cues.
- **Security Price Scanner** — original stationary turret animation, original scanning
  beam projectile and dedicated idle/attack/pain/down cues.

Prototype `0.11-dev` replaced two more high-visibility enemy placeholders:

- **Cart of Doom** — project-owned eleven-frame shopping-cart animation covering pursuit,
  a readable charge tell, pain, collapse and raise states, plus dedicated idle/charge/hit/down cues.
- **Possessed Pallet Jack** — project-owned eleven-frame industrial pallet-jack animation
  covering pursuit, fork-lunge melee tells, pain, collapse and raise states, plus dedicated
  idle/attack/hit/down cues.

Prototype `0.12-dev` gives the campaign boss its own identity:

- **The Regional Manager** — project-owned fifteen-frame executive-horror animation set,
  custom **Corporate Red Tape** and **Executive Stamp** projectiles, dedicated boss cues,
  and a health-gated second attack phase below 50% health.
- `MAP02 — Warehouse 13.5` now uses project-owned retail surfaces and does not pre-place
  the Regional Manager. Restoring all three breakers powers the boss in through a dedicated
  spawner, so the arena follows the same restore-power-before-management rule as Closing Time.

All current project-owned prototype combat art/audio is generated deterministically from
repository code using Python's standard library. Sprite PNGs carry ZDoom `grAb` offsets,
and CI verifies generated files, PK3 packaging, sound mappings and actor wiring.

Waiting around is increasingly dangerous. The **Overtime** director escalates through
`SHIFT ACTIVE` → `STORE UNSTABLE` → `OVERTIME` → `HELL RUSH`. Dedicated map
spawners add increasingly aggressive reinforcements as the shift drags on. Closing Time now
also layers synchronized workplace alarms and electrical floor hazards on top of the enemy
pressure, while preserving clear telegraphs and keeping the clock-out lane free of trap anchors.
The HUD shows an explicit countdown to the next escalation, a three-cell power display,
optional memo progress, supervisor state, current objective and a Staff Only route cue once
partial power unlocks it.

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
- generated UDMF `MAP02 — Warehouse 13.5` power-gated boss arena prototype,
- **Emergency Mop**, **Receipt Ripper**, **Price-Gun SMG**, **Turbo Can Launcher**,
- **Angry Self-Checkout**, **Cart of Doom**, **Night Manager**, **Security Price Scanner**, **Possessed Pallet Jack** and **The Regional Manager**,
- three-breaker + supervisor-clear objective loop,
- staged Night Manager reinforcement waves and physical return-to-checkout objective,
- power-gated Regional Manager arrival in MAP02 after three restored breakers,
- optional Staff Only side room and Employee of the Month reward stash,
- three optional Corporate Compliance Memo pickups with staged workplace-comedy messages,
- Overtime escalation director with timed reinforcement spawners,
- Closing Time Overtime warning alarms plus telegraphed electrical floor hazards that accelerate during Hell Rush,
- shift/objective/Overtime HUD overlay with next-escalation countdown, power cells and optional-collectible tracking,
- first original supermarket wall/shelf/staff/floor/ceiling material pack,
- original breaker, shutter, stash and Corporate Memo prototype sprites,
- original Overtime warning/floor-arc sprite set with dedicated alarm/electrical cues,
- original **Emergency Mop** first-person sprite/animation set with combat swing cue,
- original **Receipt Ripper** pickup/view sprite set with fire/cycle cues,
- original **Price-Gun SMG** pickup/view sprite set with barcode-label impact feedback and weapon cues,
- original **Turbo Can Launcher** pickup/view sprite set plus original can projectile/explosion and weapon cues,
- original **Angry Self-Checkout** animation set, receipt projectile and combat cues,
- original **Security Price Scanner** animation set, scanning projectile and combat cues,
- original **Cart of Doom** charge/pain/death animation set and combat cues,
- original **Possessed Pallet Jack** fork-lunge/pain/death animation set and combat cues,
- original **Night Manager** animation set, Manager Memo projectile and boss combat cues,
- original **Regional Manager** animation set, two custom projectile families and two-phase attack behavior,
- deterministic stdlib-only asset generation with ZDoom sprite offsets and dedicated CI asset contracts,
- one-click Windows dependency bootstrap and pinned reproducible runtime lock,
- verified portable Windows artifact builder with SHA-256 sidecar,
- automated build + gameplay + layout + Staff Only + Closing Time presentation + Overtime hazard + boss/escape + original-asset + vehicle-enemy + Regional Manager + packaging contract tests,
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
python tools/test_closing_time_presentation_contract.py
python tools/test_overtime_hazard_contract.py
python tools/test_boss_escape_contract.py
python tools/test_original_assets.py
python tools/test_vehicle_enemy_assets.py
python tools/test_regional_manager_contract.py
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

- `MAP01` — **Closing Time** — structured objective prototype with original retail surfaces, powered side route, optional memo scavenger route, staged Overtime floor hazards, supervisor fight and checkout escape
- `MAP02` — **Warehouse 13.5** — power-restoration arena with original retail surfaces and a gated two-phase Regional Manager boss

See [`docs/LEVEL_DESIGN.md`](docs/LEVEL_DESIGN.md).

## Asset policy

No proprietary Doom, Star Wars or other commercial game assets belong in this repository.
The current runtime art/audio pack is generated from our own source code during the build.
All current core weapons and signature enemies/bosses now have project-owned visible combat
presentation; compatible runtime data is still used as the legal engine/base-game layer only,
not copied into this repository or release package.

See [`docs/ASSET_POLICY.md`](docs/ASSET_POLICY.md).

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

## Author

**by Swir**  
GitHub: https://github.com/Swir