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
| Version | `0.21-dev` |
| Implemented/testable progress | **72%** |
| Playable departments | `MAP01 — Closing Time`, `MAP02 — Warehouse 13.5` |
| Public demo | **Not published yet** |
| Player packaging focus | One-click Windows bootstrap + CI portable development artifact |
| Pinned runtime | GZDoom `g4.14.2` + Freedoom `v0.13.0` |

Progress is based only on implemented and testable work. See [`ROADMAP.md`](ROADMAP.md) for the authoritative milestone breakdown.

## ⚡ Overview

The store is closed. The lights are flickering. Self-checkouts are angry. Shopping carts are hunting staff. Management has decided this is somehow still your responsibility.

**CHECKOUT OF HELL** is an original comedy-horror retro FPS built around fast readable combat, a creepy empty-store atmosphere played mostly straight, absurd workplace weapons, hostile retail equipment, real department objectives and an escalating **Overtime** system. The objective is not merely to clear rooms: restore the store, survive management and clock out alive at `06:00`.

The project creates its own setting, characters, weapons, jokes, levels, art, sound and music. **No proprietary Doom, Star Wars or other ripped commercial assets belong in this repository.**

## ✨ Highlights

| Feature | What it adds |
| --- | --- |
| ⚡ Fast readable combat | Clear attacks, uncluttered lanes and classic-FPS movement pressure. |
| 🛠️ Real shift objectives | Breakers, powered routes, shutters, supervisor gates and a physical clock-out finish. |
| ⏱️ Overtime | Deterministic escalation adds alarms, enemy pressure and telegraphed electrical hazards as the shift drags on. |
| 🧰 Retail arsenal | Emergency Mop, Receipt Ripper, Price-Gun SMG and Turbo Can Launcher use original presentation and audio. |
| 👹 Store hazards | Angry Self-Checkout, Cart of Doom, Security Price Scanner and Possessed Pallet Jack fill distinct combat roles. |
| 👔 Corporate bosses | Night Manager and the two-phase Regional Manager turn management into literal boss fights. |
| 🔎 Optional discoveries | Staff Only rewards, Corporate Compliance Memos, secrets and workplace-comedy interactions reward exploration. |
| ☠️ Authored difficulty | Closing Crew, Graveyard Shift and Corporate Hell tune resources and damage without hiding faster scripted hazards. |
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

`MAP01 — Closing Time` currently implements the most complete version of this loop. Three Breaker Fuses pull the player through left, right and rear routes. At `2/3` power, a Staff Only side room opens. At `3/3`, a Full-Power Emergency Cache becomes available and the Night Manager enters the floor. Two management-response anchors then feed a readable Angry Self-Checkout → Cart of Doom → Security Price Scanner → Possessed Pallet Jack sequence at `15 / 34 / 54 / 76` seconds after full power. Once the supervisor is dead, fresh reinforcements stop and the player must physically return to the front checkout to clock out.

`MAP02 — Warehouse 13.5` requires all three breakers before The Regional Manager arrives. Breaker and supervisor-clearance tokens are department-local: a normal map transition clears them before the next department objective begins, while loading a save preserves serialized shift state.

## ⏱️ Overtime

Overtime is deterministic enough to learn while still raising pressure:

| Time | State | Pressure |
| --- | --- | --- |
| `0:00–1:29` | SHIFT ACTIVE | Base encounter |
| `1:30–2:59` | STORE UNSTABLE | Warning layer + Angry Self-Checkout reinforcement pressure |
| `3:00–4:29` | OVERTIME | Cart of Doom pressure + active electrical floor hazards |
| `4:30+` | HELL RUSH | Possessed Pallet Jack pressure + faster hazard cadence |

Closing Time uses authored reinforcement and hazard anchors instead of random spawning on top of the player. Electrical hazards telegraph before dealing damage, and the front clock-out lane is protected from trap anchors.

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

The current vertical-slice level includes original supermarket surfaces and signage, Customer Service / Frozen Foods / Electronics identity, safe retail clutter, failing fluorescent fixtures, optional Emergency Break Snacks, three Corporate Compliance Memos, a final-layout night-shift HUD, a full-power recovery cache, staged Overtime floor hazards, a tuned Night Manager response and a physical return-to-checkout finish.

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

Static/package regression coverage is already active. A real pinned-GZDoom **save → process exit → load** round-trip is being validated in CI before this milestone is considered demo-ready. The roadmap item remains open until the runtime gate is green.

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

## 🧪 Development & validation

The project combines static contracts with real engine validation. CI builds the PK3, checks gameplay/objective contracts, generated art/audio/music, portable packaging and bootstrap behavior, then asks pinned GZDoom to parse the package. The in-progress save/load gate additionally launches the real pinned engine twice under an isolated CI runtime to prove objective state survives process exit and restore.

Useful developer commands:

```powershell
python tools/build.py
python tools/smoke_test.py
python tools/test_gameplay_contract.py
python tools/test_save_load_state_contract.py
python tools/test_runtime_save_load_smoke_contract.py
python tools/test_closing_time_pacing_contract.py
python tools/test_hud_contract.py
python tools/test_overtime_hazard_contract.py
python tools/test_original_assets.py
python tools/test_combat_audio_polish.py
python tools/test_music_contract.py
python tools/test_bootstrap_contract.py
python tools/package_portable.py
python tools/test_portable_package.py
.\tools\gzdoom_runtime_smoke.ps1
```

## 🧱 Technology & architecture

| Layer | Role |
| --- | --- |
| **GZDoom / ZScript** | Gameplay, HUD, bosses, objective state and encounter direction |
| **UDMF** | Department geometry and gameplay layers |
| **PK3** | Game package format |
| **Python 3** | Deterministic original asset/music generation, builds and regression contracts |
| **PowerShell / Batch** | Windows bootstrap, pinned runtime validation and one-click launch flow |
| **GitHub Actions** | Build/package contracts plus pinned-engine runtime gates |

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

- `Closing Time` is not yet signed off as the first fully polished level.
- `Warehouse 13.5` is playable but not yet fully polished.
- The real pinned-engine save/load round-trip remains a demo-readiness gate until CI proves it green.
- Controller, accessibility-option and performance passes for the public demo are not complete.
- Later departments remain planned until they have real playable content.

## 🔎 Search Keywords

`retro FPS` • `comedy horror FPS` • `supermarket horror game` • `workplace horror game` • `retail horror game` • `boomer shooter` • `GZDoom game` • `GZDoom ZScript` • `UDMF FPS` • `PK3 game` • `Windows retro shooter` • `Overtime mechanic` • `original GZDoom project` • `one-click Windows game bootstrap` • `Freedoom runtime` • `night shift horror`

<div align="center">

### `SCAN • STOCK • SURVIVE • CLOCK OUT`

**CHECKOUT OF HELL — by Swir**

⭐ **If this project looks interesting, consider leaving a star.**

[**← SWIR profile**](https://github.com/Swir) · [**All projects →**](https://github.com/Swir?tab=repositories)

</div>
