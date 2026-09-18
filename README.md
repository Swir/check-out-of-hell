<!-- SWIR-README-STANDARD:v2 -->

<div align="center">

<img width="100%" src="assets/readme/hero.svg" alt="CHECKOUT OF HELL — comedy-horror retro FPS set in a haunted supermarket night shift" />

<br>

[![Build prototype](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml/badge.svg)](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml)
![Prototype](https://img.shields.io/badge/STATUS-PROTOTYPE-02050A?style=for-the-badge&labelColor=02050A&color=02050A)
![GZDoom](https://img.shields.io/badge/GZDoom-g4.14.2-02050A?style=for-the-badge&logoColor=62E5FF)
![License](https://img.shields.io/badge/LICENSE-MIT-02050A?style=for-the-badge&logoColor=62E5FF)

**A fast, readable comedy-horror retro FPS about surviving the worst supermarket night shift imaginable.**

[**Highlights**](#-highlights) · [**Quick Start**](#-quick-start--windows) · [**Roadmap**](#-roadmap--releases) · [**Releases**](https://github.com/Swir/check-out-of-hell/releases)

</div>

## 📌 Project status

| Item | Status |
| --- | --- |
| Current stage | Prototype / vertical-slice development |
| Version | `0.28-dev` |
| Implemented/testable progress | **82.8%** |
| Playable departments | `MAP01 — Closing Time`, `MAP02 — Warehouse 13.5` |
| Public demo | **Not published yet** |
| Player packaging focus | One-click Windows bootstrap + CI portable development artifact |
| Pinned runtime | GZDoom `g4.14.2` + Freedoom `v0.13.0` |

<img width="100%" src="assets/readme/progress-card.svg" alt="CHECKOUT OF HELL project progress — 82.8% implemented/testable; demo release readiness tracked separately" />

**Progress fallback:** **82.8%** implemented/testable project progress across **5 weighted roadmap phases**. **Demo Release readiness: 50.0%**, tracked separately.

Progress is based only on implemented and testable work. See [`ROADMAP.md`](ROADMAP.md) for the authoritative weighted milestone breakdown and separate release-readiness gate.

## ⚡ Overview

The store is closed. The lights are flickering. Self-checkouts are angry. Shopping carts are hunting staff. Management has decided this is somehow still your responsibility.

**CHECKOUT OF HELL** is an original comedy-horror retro FPS built around fast readable combat, a creepy empty-store atmosphere played mostly straight, absurd workplace weapons, hostile retail equipment, real department objectives and an escalating **Overtime** system. The objective is not merely to clear rooms: restore the store, survive management and clock out alive at `06:00`.

The project creates its own setting, characters, weapons, jokes, levels, art, sound and music. **No proprietary Doom, Star Wars or other ripped commercial assets belong in this repository.**

## ✨ Highlights

| Feature | What it adds |
| --- | --- |
| ⚡ Fast readable combat | Clear attacks, uncluttered lanes and classic-FPS movement pressure. |
| 🛠️ Real shift objectives | Breakers, powered routes, shutters, supervisor gates and a physical clock-out finish. |
| ⏱️ Overtime | Deterministic escalation adds alarms, enemy pressure and telegraphed electrical hazards, then retires fresh pressure after supervisor clearance for a readable escape leg. |
| 🧰 Retail arsenal | Emergency Mop, Receipt Ripper, Price-Gun SMG and Turbo Can Launcher use original presentation and audio. |
| 👹 Store hazards | Angry Self-Checkout, Cart of Doom, Security Price Scanner and Possessed Pallet Jack fill distinct combat roles. |
| 👔 Corporate bosses | Night Manager and the two-phase Regional Manager turn management into literal boss fights. |
| 🔎 Optional discoveries | Staff Only rewards, Corporate Compliance Memos and useful workplace-comedy resource stashes reward exploration. |
| ☠️ Authored difficulty | Closing Crew, Graveyard Shift and Corporate Hell tune resources and damage without hiding faster scripted hazards. |
| ♿ Readability options | Optional focus HUD and large textual warnings reinforce objectives, pressure and critical-health states without changing combat rules. |
| 🎮 Controller setup | A dedicated menu exposes core remaps, engine device/stick setup and restrained signature-weapon haptics without overwriting player bindings. |
| ⚙️ Performance hardening | Sparse objective/wave polling and self-retiring one-shot watchers reduce script overhead without retiming authored encounters. |
| 🔊 Original presentation | Project-owned generated art, combat audio and department music; no ripped commercial game assets. |
| 📦 One-click runtime setup | Missing redistributable runtime files are resolved from official upstream sources instead of making players hunt for them. |

## 🎮 Core shift loop

Every department is designed around a useful workplace task rather than pure arena shooting:

1. enter the department,
2. restore, repair or activate something useful,
3. survive hostile store equipment and possessed retail hazards,
4. exploit optional powered routes, secrets and joke interactions,
5. defeat the department supervisor while Overtime escalates,
6. finish the exit task and keep moving toward clocking out alive at `06:00`.

`MAP01 — Closing Time` currently implements the most complete version of this loop. Three Breaker Fuses pull the player through left, right and rear routes. At `2/3` power, a Staff Only side room opens. At `3/3`, a Full-Power Emergency Cache becomes available and the Night Manager enters the floor. Two management-response anchors then feed a readable Angry Self-Checkout → Cart of Doom → Security Price Scanner → Possessed Pallet Jack sequence at `15 / 34 / 54 / 76` seconds after full power. Once the supervisor is dead, fresh reinforcements and newly spawned Overtime floor hazards stop, an original `CLOCK OUT` guide appears near the front lanes, and the player must physically return to the existing checkout trigger to finish the shift.

`MAP02 — Warehouse 13.5` requires all three breakers before The Regional Manager arrives. Breaker and supervisor-clearance tokens are department-local: a normal map transition clears them before the next department objective begins, while loading a save preserves serialized shift state.

## ⏱️ Overtime

Overtime is deterministic enough to learn while still raising pressure:

| Time | State | Pressure |
| --- | --- | --- |
| `0:00–1:29` | SHIFT ACTIVE | Base encounter |
| `1:30–2:59` | STORE UNSTABLE | Warning layer + Angry Self-Checkout reinforcement pressure |
| `3:00–4:29` | OVERTIME | Cart of Doom pressure + active electrical floor hazards |
| `4:30+` | HELL RUSH | Possessed Pallet Jack pressure + faster hazard cadence |

Closing Time uses authored reinforcement and hazard anchors instead of random spawning on top of the player. Electrical hazards telegraph before dealing damage, and the front clock-out lane is protected from trap anchors. The authored warning/arc schedule remains unchanged, but the hazard anchors now retire when supervisor clearance is earned so no fresh electrical trap appears during the deliberate return-to-checkout leg; enemies already alive remain part of the escape pressure.

## ☠️ Difficulty modes

| Mode | Role | Tuning |
| --- | --- | --- |
| **Closing Crew** | Forgiving first run | +25% ammo, -25% incoming damage, +20% healing, enemies at 90% health |
| **Graveyard Shift** | Intended default | Baseline ammo, damage, healing and enemy health |
| **Corporate Hell** | High-pressure replay | -15% ammo, +25% incoming damage, -15% healing, enemies at 115% health |

Breaker gates, Night Manager wave timing and Overtime timing remain identical across all three modes. `Corporate Hell` requires explicit confirmation before clocking in.

## 🧰 Signature arsenal & threats

**Weapons:** Emergency Mop · Receipt Ripper · Price-Gun SMG · Turbo Can Launcher  
**Store hazards:** Angry Self-Checkout · Cart of Doom · Security Price Scanner · Possessed Pallet Jack  
**Corporate bosses:** Night Manager · The Regional Manager

All current signature weapons, enemies and bosses use project-owned visible combat presentation and project-owned combat-audio families. High-repeat sounds use deterministic generated variation families so combat stays recognizable without repeating one identical sample every time.

See [`docs/WEAPONS.md`](docs/WEAPONS.md).

## 🛒 Current playable content

### MAP01 — Closing Time

The current vertical-slice level includes original supermarket surfaces and signage, Customer Service / Frozen Foods / Electronics identity, safe retail clutter, failing fluorescent fixtures, optional Emergency Break Snacks, three Corporate Compliance Memos, three off-route resource stashes with workplace-comedy pickup interactions, a final-layout night-shift HUD, a full-power recovery cache, staged Overtime floor hazards, a tuned Night Manager response and a physical return-to-checkout finish. The post-boss leg now suppresses fresh reinforcements and electrical hazards and exposes a project-owned `CLOCK OUT` guide at the front approach without changing the completion zone itself.

The secret pass keeps progression readable: the Unclaimed Receipt Roll, Damaged-Goods Label Crate and Unauthorized Employee Relief Kit sit in dead-end retail corners away from the central combat/clock-out lane. They reward exploration with receipts, labels or health but never gate a breaker, boss or exit objective.

### MAP02 — Warehouse 13.5

The warehouse slice uses project-owned retail surfaces and an original soundtrack. Restoring all three breakers is required before the two-phase Regional Manager can enter the fight.

Planned departments — **Frozen Foods**, **Electronics**, **Customer Service** and **Management Floor** — remain intentionally unexpanded until they have real playable content.

See [`docs/LEVEL_DESIGN.md`](docs/LEVEL_DESIGN.md) and [`docs/GAMEPLAY_LOOP.md`](docs/GAMEPLAY_LOOP.md).

## 🔊 Original soundtrack

Every currently playable department uses project-owned music instead of inherited base-game tracks:

- **Closing Time — Empty Aisles** — slow drones, sparse vibraphone phrases and checkout-like chimes that leave room for combat and Overtime telegraphs.
- **Warehouse 13.5 — Forklift Graveyard** — colder low-register drones, restrained machinery-like percussion and a darker warehouse motif.

The tracks are deterministic Standard MIDI files produced by `tools/generate_music_assets.py` using only Python's standard library, regenerated during builds and protected by a dedicated regression contract. See [`docs/MUSIC.md`](docs/MUSIC.md).

## 💾 Save/load safety

The shift director distinguishes a fresh department from a savegame restore using GZDoom's `WorldEvent.IsSaveGame` state. Fresh departments clear only department-local Breaker Fuse and supervisor-clearance tokens; save restores keep serialized shift state intact.

The repository now runs a real **save → process exit → load** regression against the exact pinned GZDoom `g4.14.2`: CI boots the official Linux package under Xvfb/Mesa software rendering, authors unmistakable `CheckoutFuse 2/3` plus `CorporateMemo 2/3` state in live MAP01, writes a real `.zds`, starts a second engine process, reloads that save and verifies both objective counters survived. The same runtime lock and official Freedoom release are used, with the Freedoom archive SHA-256 verified against its official checksum file.

A hardened Windows desktop helper is retained for target-machine confirmation. GitHub's hosted Windows runner remains parser/startup validation only because it does not expose a suitable live GZDoom graphics context; final demo sign-off still requires an interactive Windows playtest including a save/load confirmation.

## 🚀 Quick Start — Windows

**Players should never need to hunt for required runtime files manually.** From a source checkout, double-click:

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

## 📦 Portable Windows development artifact

CI builds and verifies `CHECKOUT-OF-HELL-Windows-Portable-dev.zip` plus a SHA-256 sidecar. It contains the prebuilt PK3, dedicated `PLAY.bat`, runtime lock, official-source bootstrap and license notices. No Python or source build toolchain is required on the player's PC; first launch obtains only missing pinned redistributable runtime dependencies from official upstream sources.

This is intentionally a **development artifact, not a public demo release**.

## 🖥️ Requirements & compatibility

| Component | Pinned target |
| --- | --- |
| GZDoom | `g4.14.2` |
| Freedoom | `v0.13.0` |
| Build/bootstrap Python | `3.12.10` portable fallback |
| Player packaging focus | Windows portable/source bootstrap |

Runtime pins live in `runtime-lock.json` and change only after compatibility validation. The repository does **not** claim a public demo, installer or polished final-game support yet.

## ♿ Accessibility & sensory readability

Open **Options → CHECKOUT OF HELL Accessibility** to enable player-local comfort/readability aids:

- **Focus HUD** adds a compact high-contrast text block with the current objective, breaker/memo counts and Overtime pressure.
- **Large warnings** adds larger textual warnings for critical health, Overtime and Hell Rush states.

Both options are disabled by default and do not alter combat timing, difficulty or objective logic. Overtime remains communicated through words/patterns as well as color, while failing fluorescent props now use a slower light-change cadence instead of rapid two-tic flash cuts. See [`docs/ACCESSIBILITY.md`](docs/ACCESSIBILITY.md).

## 🎮 Controller support

Open **Options → CHECKOUT OF HELL Controller** for the project-level controller setup. It exposes primary/alternate fire, use, jump, crouch, run, weapon cycling and automap as normal GZDoom actions, plus direct links to the engine's device/stick setup and complete control-binding menu. The project does **not** overwrite an existing user's bindings.

On a fresh compatible GZDoom setup, the engine baseline uses left stick for movement, right stick for looking, right trigger/R2 for primary fire, left trigger/L2 for alternate fire, A/Cross for use, Y/Triangle for jump, shoulder buttons for weapon cycling and L3 for crouch toggle. Exact button labels depend on the connected device/SDL mapping and user configuration.

Emergency Mop, Receipt Ripper, Price-Gun SMG and Turbo Can Launcher firing cues use restrained built-in GZDoom rumble profiles. Enemy attacks, alarms and ambient Overtime cues deliberately do not rumble, avoiding constant vibration during long fights. This support pass is engine/parser/contract validated; a real-controller target-Windows playtest is still required before public-demo sign-off. See [`docs/CONTROLLER.md`](docs/CONTROLLER.md).

## ⚙️ Performance hardening

Objective and encounter watcher actors now avoid unnecessary 35-Hz inventory/stage polling. Most slow-changing gates sample every **7 tics** (worst-case response below 0.2 seconds), while the authored Night Manager response sequence samples every **4 tics**. One-shot manager/cache/shutter/clock-out-guide watchers remove themselves after completing their job, reinforcement watchers retire after supervisor clearance, and Overtime hazard anchors now use sparse clearance checks while preserving their authored schedule.

The `55 / 38 / 25` second Overtime reinforcement cadence, `15 / 34 / 54 / 76` second Night Manager wave thresholds and `90 / 135 / 180 / 212 / 244 / 270` second initial environmental-hazard events are unchanged. CI protects these invariants and the pinned-engine parser still validates the resulting ZScript. This is script-overhead and lifecycle hardening, **not** a fabricated FPS claim; real-hardware Windows performance sanity remains part of final demo sign-off. See [`docs/PERFORMANCE.md`](docs/PERFORMANCE.md).

## 🧪 Development & validation

The project combines static contracts with real engine validation. CI builds the PK3, checks gameplay/objective contracts, accessibility, controller and performance hardening, generated art/audio/music, the Closing Time secret pass and post-boss clock-out polish, portable packaging and bootstrap behavior, asks pinned GZDoom on Windows to parse the current package, and performs a true two-process save/load round-trip with the same pinned engine version under Xvfb/Mesa on Linux. Save/load runtime logs and official-source runtime manifests are retained as CI artifacts for diagnosis.

Useful developer commands:

```powershell
python tools/build.py
python tools/smoke_test.py
python tools/test_gameplay_contract.py
python tools/test_save_load_state_contract.py
python tools/test_gzdoom_save_load_smoke_contract.py
python tools/test_readme_standard_contract.py
python tools/generate_progress_svgs.py --check
python tools/test_closing_time_pacing_contract.py
python tools/test_closing_time_secrets_contract.py
python tools/test_post_boss_clockout_polish_contract.py
python tools/test_hud_contract.py
python tools/test_accessibility_contract.py
python tools/test_controller_support_contract.py
python tools/test_performance_contract.py
python tools/test_overtime_hazard_contract.py
python tools/test_original_assets.py
python tools/test_combat_audio_polish.py
python tools/test_music_contract.py
python tools/test_bootstrap_contract.py
python tools/package_portable.py
python tools/test_portable_package.py
.\tools\gzdoom_runtime_smoke.ps1
.\tools\gzdoom_save_load_smoke.ps1
```

The automated headless round-trip additionally uses `tools/bootstrap_linux_runtime.py` and `tools/gzdoom_save_load_smoke_linux.py` inside the Linux CI job.

## 🧱 Technology & architecture

| Layer | Role |
| --- | --- |
| **GZDoom / ZScript** | Gameplay, HUD, bosses, objective state and encounter direction |
| **UDMF** | Department geometry and gameplay layers |
| **PK3** | Game package format |
| **Python 3** | Deterministic original asset/music generation, builds and regression contracts |
| **PowerShell / Batch** | Windows bootstrap, pinned runtime validation and one-click launch flow |
| **GitHub Actions** | Build/package contracts plus pinned-engine parser and two-process save/load validation |

## ⚖️ Asset & distribution policy

No proprietary Doom, Star Wars or other commercial game assets are committed. Current runtime art, audio and MIDI music are generated from original repository source. Compatible legal engine/base-game data is obtained from official upstream sources at setup time rather than copied into the project.

For a public demo, the preferred package is fully self-contained where licenses permit redistribution. Otherwise first run must automatically obtain every missing redistributable dependency from official upstream sources so a normal Windows player never has to search for files manually.

See [`docs/ASSET_POLICY.md`](docs/ASSET_POLICY.md) and [`docs/THIRD_PARTY.md`](docs/THIRD_PARTY.md).

## 🧭 Roadmap & releases

- Authoritative roadmap: [`ROADMAP.md`](ROADMAP.md)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)
- GitHub Releases: [releases](https://github.com/Swir/check-out-of-hell/releases)

**Public demo rule:** no demo release until the project is genuinely presentable, fun enough to represent the final direction and one-click for a normal Windows player. Current portable packages are development artifacts only.

## ⚠️ Current limitations

- `Closing Time` has its authored post-boss clock-out polish and a complete first secrets/joke-interaction pass, but is not yet signed off as the first fully polished level.
- `Warehouse 13.5` is playable but not yet fully polished.
- The cross-process save/load serialization gate is green on the exact pinned engine, but a final target-Windows interactive save/load confirmation is still required before demo sign-off.
- Controller setup/haptics and the script-overhead performance pass are implemented and contract-tested, but physical controller and real-hardware performance confirmation remain part of the target-Windows demo sign-off.
- Later departments remain planned until they have real playable content.

## 🔎 Search Keywords

`retro FPS` • `comedy horror FPS` • `supermarket horror game` • `workplace horror game` • `retail horror game` • `boomer shooter` • `GZDoom game` • `GZDoom ZScript` • `UDMF FPS` • `PK3 game` • `Windows retro shooter` • `controller retro FPS` • `Overtime mechanic` • `original GZDoom project` • `one-click Windows game bootstrap` • `Freedoom runtime` • `night shift horror`

<div align="center">

### `SCAN • STOCK • SURVIVE • CLOCK OUT`

**CHECKOUT OF HELL — by Swir**

⭐ **If this project looks interesting, consider leaving a star.**

[**← SWIR profile**](https://github.com/Swir) · [**All projects →**](https://github.com/Swir?tab=repositories)

</div>