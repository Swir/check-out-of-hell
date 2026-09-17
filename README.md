# CHECKOUT OF HELL

[![Build prototype](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml/badge.svg)](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml)

A fast, readable comedy-horror retro FPS about surviving the worst supermarket night shift imaginable.

> **Status:** Prototype 0.19-dev — authored night-shift difficulty modes  
> **Project progress:** `███████░░░ 68%`

## Premise

The store is closed. The lights are flickering. Self-checkouts are angry. Shopping carts are hunting staff. Management has decided this is somehow still your responsibility.

CHECKOUT OF HELL is an original project inspired by the speed and readability of classic shooters while building its own setting, characters, weapons, jokes, levels, art and sound. No proprietary Doom, Star Wars or other ripped commercial assets belong in this repository.

## Core shift loop

Every department is built around a real workplace objective rather than pure arena shooting:

1. enter the department,
2. restore, repair or activate something useful,
3. survive hostile store equipment and possessed retail hazards,
4. exploit optional powered routes, secrets and joke interactions,
5. defeat the department supervisor while Overtime escalates,
6. reach the required exit task and keep moving toward clocking out alive at `06:00`.

`MAP01 — Closing Time` currently implements the most complete version of that loop. Three Breaker Fuses pull the player through left, right and rear routes. At `2/3` power, a Staff Only side room opens. At `3/3`, a Full-Power Emergency Cache becomes available and the Night Manager enters the floor. Two management-response anchors then feed a readable sequence of Angry Self-Checkout → Cart of Doom → Security Price Scanner → Possessed Pallet Jack at `15 / 34 / 54 / 76` seconds after full power. Once the supervisor is dead, fresh reinforcements stop and the player must physically return to the front checkout to clock out.

`MAP02 — Warehouse 13.5` also requires all three breakers before The Regional Manager arrives, preserving the same restore-power-before-management rule.

## Overtime

Waiting is dangerous. Overtime escalates deterministically so the player can learn it:

| Time | State | Pressure |
| --- | --- | --- |
| `0:00–1:29` | SHIFT ACTIVE | base encounter |
| `1:30–2:59` | STORE UNSTABLE | warning layer + Angry Self-Checkout reinforcement pressure |
| `3:00–4:29` | OVERTIME | Cart of Doom pressure + active electrical floor hazards |
| `4:30+` | HELL RUSH | Possessed Pallet Jack pressure + faster hazard cadence |

Closing Time uses authored reinforcement and hazard anchors instead of random spawning on top of the player. Electrical hazards telegraph before they deal damage, and the front clock-out lane is protected from trap anchors.

## Difficulty modes

Prototype `0.19-dev` adds three authored shift difficulties while keeping breaker gates, boss-wave timing and Overtime timing identical across all modes:

| Mode | Role | Tuning |
| --- | --- | --- |
| **Closing Crew** | forgiving first run | +25% ammo, -25% incoming damage, +20% healing, enemies at 90% health |
| **Graveyard Shift** | intended default | baseline ammo, damage, healing and enemy health |
| **Corporate Hell** | high-pressure replay | -15% ammo, +25% incoming damage, -15% healing, enemies at 115% health |

`Graveyard Shift` is the default. `Corporate Hell` requires an explicit confirmation before clocking in. Difficulty deliberately changes combat forgiveness and resource pressure instead of hiding faster scripted traps or opaque respawn rules behind the selection.

## Signature arsenal

- **Emergency Mop** — melee opener with original first-person animation and swing cue family.
- **Receipt Ripper** — paper-shredding shotgun analogue with original pickup/view animation and fire/cycle cues.
- **Price-Gun SMG** — automatic label weapon with barcode-label impact feedback.
- **Turbo Can Launcher** — heavy soda-can launcher with an original projectile and explosion presentation.

See [`docs/WEAPONS.md`](docs/WEAPONS.md).

## Signature threats

- **Angry Self-Checkout**
- **Cart of Doom**
- **Security Price Scanner**
- **Possessed Pallet Jack**
- **Night Manager**
- **The Regional Manager**

All current signature weapons, enemies and bosses use project-owned visible combat presentation and project-owned combat-audio families. High-repeat sounds are selected from deterministic generated variation families so combat stays recognizable without repeating one identical sample every time.

## Closing Time presentation

The current vertical-slice work includes:

- original supermarket wall, shelf, floor, ceiling and Staff Only surfaces,
- Customer Service, Frozen Foods, Electronics/Returns and Lane 06 signage,
- low-profile retail clutter that does not block combat lanes,
- animated failing fluorescent fixtures,
- optional Emergency Break Snacks,
- three Corporate Compliance Memos with workplace-comedy messages,
- project-owned breaker, shutter, stash, memo and Overtime hazard sprites,
- a compact final-layout HUD with objective/route hierarchy, `06:00` target, Overtime pressure, worker health and signature-ammo reserves,
- text/pattern state cues in addition to color for critical HUD information,
- a guaranteed full-power recovery cache before the Night Manager encounter,
- post-supervisor cutoff for new reinforcements so the clock-out leg remains tense without becoming an endless spawn treadmill.

Project-owned runtime art/audio is generated deterministically from repository code using Python's standard library. Sprite PNGs include ZDoom `grAb` offsets and CI checks generated assets, sound mappings, actor wiring and packaged PK3 contents.

## One-click Windows start

**Players should never need to hunt for required runtime files manually.**

From a source checkout, double-click:

```text
PLAY.bat
```

The launcher automatically:

1. reads pinned versions from `runtime-lock.json`,
2. resolves GZDoom from the official `ZDoom/gzdoom` GitHub Release,
3. resolves Freedoom from the official `freedoom/freedoom` GitHub Release,
4. verifies Freedoom SHA-256 against its official checksum when available,
5. downloads an official portable Python build from `python.org` only when a source build needs Python and none is installed,
6. builds and smoke-tests the PK3 when necessary,
7. launches the game.

Downloaded runtime files are cached locally. Network or verification failures stop with clear actionable errors; the project does not silently fall back to unofficial mirrors.

See [`docs/THIRD_PARTY.md`](docs/THIRD_PARTY.md) and [`docs/PACKAGING.md`](docs/PACKAGING.md).

## Portable Windows development artifact

CI builds and verifies `CHECKOUT-OF-HELL-Windows-Portable-dev.zip`. It contains the prebuilt PK3, a dedicated `PLAY.bat`, runtime lock, official-source bootstrap and license notices. No Python or source build toolchain is required on the player's PC. First launch obtains only missing pinned redistributable runtime dependencies from official upstream sources. A SHA-256 sidecar is generated and validated in CI.

This is intentionally a **development artifact**, not a public demo release.

## What already works

- buildable PK3 prototype,
- structured `Closing Time` and power-gated `Warehouse 13.5`,
- three-breaker objective loop and physical clock-out finish,
- Overtime reinforcement director plus telegraphed environmental hazards,
- tuned Night Manager management-response sequence,
- powered Staff Only optional route and exploration rewards,
- Corporate Compliance Memo scavenger route,
- final-layout night-shift HUD,
- three authored difficulty modes — Closing Crew, default Graveyard Shift and Corporate Hell,
- original presentation for the four signature weapons and all current signature enemies/bosses,
- deterministic stdlib-only visual/audio generation,
- randomized combat-audio families with PCM/headroom regression coverage,
- one-click official-source dependency bootstrap,
- verified portable Windows artifact builder with SHA-256 sidecar,
- pinned GZDoom runtime parser/startup validation on Windows CI,
- custom CHECKOUT OF HELL branding/icon concept.

## Development runtime

The current pinned runtime is GZDoom `g4.14.2` plus Freedoom `v0.13.0`. Runtime pins live in `runtime-lock.json` and should only change after compatibility validation.

CI downloads the pinned official runtime and asks GZDoom itself to load and parse the current PK3 through its non-interactive `-norun` startup path. This catches engine-level MAPINFO/ZScript/package errors that static Python checks cannot detect.

Manual developer commands:

```powershell
python tools/build.py
python tools/smoke_test.py
python tools/test_gameplay_contract.py
python tools/test_difficulty_modes_contract.py
python tools/test_closing_time_layout.py
python tools/test_staff_room_contract.py
python tools/test_closing_time_presentation_contract.py
python tools/test_environment_polish_contract.py
python tools/test_closing_time_pacing_contract.py
python tools/test_hud_contract.py
python tools/test_overtime_hazard_contract.py
python tools/test_boss_escape_contract.py
python tools/test_original_assets.py
python tools/test_combat_audio_polish.py
python tools/test_vehicle_enemy_assets.py
python tools/test_regional_manager_contract.py
python tools/test_bootstrap_contract.py
python tools/package_portable.py
python tools/test_portable_package.py
.\tools\gzdoom_runtime_smoke.ps1
```

The automated Linux job runs all static/build/package contracts, including the dedicated difficulty-mode contract. The Windows job resolves the official pinned runtime and validates the packaged prototype with GZDoom itself.

## Maps

- `MAP01` — **Closing Time** — structured objective slice with original retail surfaces, department signage, optional powered exploration, staged Overtime floor hazards, tuned supervisor response and physical clock-out escape.
- `MAP02` — **Warehouse 13.5** — power-restoration arena with original retail surfaces and a gated two-phase Regional Manager boss.
- Planned departments include **Frozen Foods**, **Electronics**, **Customer Service** and **Management Floor**, but they will only be expanded when there is real playable content.

See [`docs/LEVEL_DESIGN.md`](docs/LEVEL_DESIGN.md) and [`docs/GAMEPLAY_LOOP.md`](docs/GAMEPLAY_LOOP.md).

## Asset and distribution policy

No proprietary Doom, Star Wars or other commercial game assets are committed. The current runtime art/audio pack is generated from original repository source. Compatible legal engine/base-game data is obtained from upstream at setup time rather than copied into the project.

For a public demo, the preferred package is fully self-contained where licenses permit redistribution. Otherwise first run must automatically obtain every missing redistributable dependency from official upstream sources so a normal Windows player never has to search for files manually.

See [`docs/ASSET_POLICY.md`](docs/ASSET_POLICY.md).

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

## Author

**by Swir**  
GitHub: https://github.com/Swir
