# Changelog

## 0.25.0-dev — 2026-09-17

### Added
- Dedicated `Options → CHECKOUT OF HELL Accessibility` menu exposing engine-native UI scale, notification scale, crosshair scale, centered notifications, reduced notification pulsing, intermission subtitles and direct display/input/audio shortcuts.
- `docs/ACCESSIBILITY.md` documenting the first accessibility pass, reduced-flash Overtime presentation and remaining scope honestly.
- `tools/test_accessibility_contract.py`, validating accessibility menu wiring, packaged `MENUDEF`, unchanged Overtime gameplay timing and the reduced-flash presentation contract.
- GitHub Actions execution of the accessibility contract.

### Changed
- Overtime warning and electrical-arc actors now use one short three-tic Bright pulse followed by normal-lit telegraph frames instead of remaining Bright through most of their visible lifetime; sound, damage, thresholds and hazard cadence are unchanged.
- Build packaging now includes the project `MENUDEF` lump.
- README/ROADMAP progress raised to **77%** and Demo Release progress to **30%** for the implemented/testable accessibility milestone; target-Windows playtesting, controller validation and performance work remain open before demo sign-off.

## 0.24.0-dev — 2026-09-17

### Added
- Real two-process pinned-GZDoom save → process exit → load validation in CI under Xvfb/Mesa software rendering.
- Official-source Linux runtime resolver for the exact locked GZDoom release plus official Freedoom release, including Freedoom SHA-256 verification against the upstream checksum asset.
- `tools/gzdoom_save_load_smoke_linux.py`, which authors `CheckoutFuse 2/3` and `CorporateMemo 2/3` in live MAP01, writes a real `.zds`, launches a second GZDoom process and verifies both counters survive restore.
- `tools/test_gzdoom_save_load_smoke_contract.py`, protecting runtime-lock use, process-boundary behavior, save-file sanity checks and CI wiring.

### Fixed
- Generated embedded UDMF WADs now include canonical `MAPxx -> TEXTMAP -> ENDMAP` markers so GZDoom registers MAP01/MAP02 as real maps at runtime.
- Runtime-only ZScript issues exposed by the live pinned-engine pass: UI-scope helper declarations, `Level.ExitLevel`, `String.Length()` and terminated state-frame statements.
- HUD runtime scope no longer calls play-scoped overtime helpers from `RenderOverlay`.

### Changed
- The Windows save/load helper now has bounded polling, explicit engine logs, hard process cleanup and stronger serialized-state checks for normal target-machine validation.
- CI retains pinned Windows parser/startup validation and adds the real same-version two-process runtime round-trip on Linux because the hosted Windows runner does not expose a suitable interactive GZDoom graphics context.
- README/ROADMAP progress raised to **76%** and Vertical Slice progress to **94%** for the now-green end-to-end runtime serialization milestone. A final interactive target-Windows playtest/save-load confirmation remains required before demo sign-off.

## 0.23.0-dev — 2026-09-17

### Added
- Three optional Closing Time side-route resource stashes: Unclaimed Receipt Roll, Damaged-Goods Label Crate and Unauthorized Employee Relief Kit.
- Workplace-comedy pickup interactions for the new secrets while keeping every reward useful and fully optional.
- `tools/test_closing_time_secrets_contract.py`, validating authored placements, project-owned visible sprites, the existing three-memo scavenger route, packaged DECORATE and built MAP01 contents.
- GitHub Actions execution of the Closing Time secrets/joke-interactions contract.

### Changed
- Closing Time now has a complete first secrets/joke-interaction pass across the existing Corporate Compliance Memos, Staff Only reward route, Emergency Break Snacks and three new dead-end resource stashes.
- New resource stashes stay outside the central combat/clock-out lane and do not gate breakers, bosses or exit progression.
- README/ROADMAP progress raised to **74%** and Vertical Slice progress to **91%** for the implemented/testable exploration milestone; the level is still not marked fully polished before end-to-end Windows playtesting.

## 0.22.0-dev — 2026-09-17

### Added
- Project-specific dark/electric-cyan `assets/readme/hero.svg` with CHECKOUT OF HELL branding, haunted-cart motif and `06:00` clock-out target.
- `tools/test_readme_standard_contract.py`, enforcing the canonical SWIR README PRO v2 marker, required project sections, 8–20 accurate search phrases, truthful README/ROADMAP progress synchronization and hero identity.
- GitHub Actions execution of the SWIR README PRO v2 documentation contract.

### Changed
- README was rebuilt around the current `Swir/Swir/SWIR-README-STANDARD.md` v2 family: centered hero, truthful prototype badges/status, highlights, one-click setup, requirements, architecture, legal/distribution clarity, limitations, roadmap/release links and restrained by Swir footer.
- Save/load documentation now explicitly distinguishes the existing static/package regression coverage and pinned Windows parser validation from the still-open real save → process exit → load runtime gate.
- Project progress remains **72%** and Vertical Slice remains **88%**; documentation/branding improvements do not inflate gameplay completion.

### Validation
- A Linux/Xvfb process-level save/load experiment was rejected rather than merged after repeated headless GZDoom timeouts. The demo-readiness runtime gate remains open for a target-Windows implementation.

## 0.21.0-dev — 2026-09-17

### Added
- Deterministic standard-library MIDI soundtrack generator with original themes for `Closing Time` and `Warehouse 13.5`.
- `docs/MUSIC.md`, documenting soundtrack intent, legal/original-content policy and build validation.
- `tools/test_music_contract.py`, validating deterministic regeneration, Standard MIDI structure, MAPINFO wiring and packaged PK3 contents.
- GitHub Actions execution of the original soundtrack contract.

### Changed
- MAP01 and MAP02 now use project-owned `D_COH01` / `D_COH02` music instead of inherited compatible-IWAD music lumps.
- The build pipeline now generates and packages the `music/` namespace alongside visual and sound assets.
- README/ROADMAP progress raised to 72% and Vertical Slice progress to 88% for the implemented/testable soundtrack milestone.

## 0.20.0-dev — 2026-09-17

### Added
- `tools/test_save_load_state_contract.py`, covering savegame guarding, packaged ZScript wiring, immediate supervisor-clear persistence and fresh-department objective reset behavior.
- GitHub Actions execution of the save/load state contract.

### Fixed
- `CheckoutShiftDirector.WorldLoaded` no longer resets serialized shift state when GZDoom is restoring a savegame.
- Breaker Fuses and `SupervisorClearanceToken` are now cleared only on genuinely fresh department loads, preventing MAP01 completion state from making the MAP02 Regional Manager objective auto-complete or spawn early.
- Supervisor clearance is written to player inventory on the same tic as a Night Manager/Regional Manager death and can be used to recover cleared state from older development saves.

### Changed
- README/ROADMAP progress raised to 70% and Vertical Slice progress to 85% for the implemented/testable save-state hardening milestone. Full interactive Windows save → quit → load validation remains intentionally open before demo readiness.

## 0.19.0-dev — 2026-09-17

### Added
- Three authored MAPINFO difficulties: forgiving `Closing Crew`, default `Graveyard Shift`, and confirmation-gated `Corporate Hell`.
- `tools/test_difficulty_modes_contract.py`, validating skill ordering, exact combat/resource multipliers, readability safeguards and packaged PK3 wiring.
- GitHub Actions execution of the difficulty-mode contract.

### Changed
- Difficulty now tunes ammo economy, incoming damage, healing and enemy health while leaving breaker gates, Night Manager waves and scripted Overtime/hazard timing deterministic across all modes.
- `docs/GAMEPLAY_LOOP.md` was refreshed to match the current three-breaker gates, `15 / 34 / 54 / 76` second management response, post-supervisor reinforcement cutoff, final HUD and difficulty behavior.
- README/ROADMAP progress raised to 68% and Vertical Slice progress to 82% for the implemented/testable difficulty milestone; end-to-end Windows playtesting and save/load validation remain primary vertical-slice blockers.

## 0.18.0-dev — 2026-09-17

### Added
- Guaranteed `CheckoutPowerCache` at full power before the Night Manager encounter.
- `CheckoutFullPowerCacheSpawner` / DoomEdNum `17128` and invisible `SupervisorClearanceToken` shift-state marker.
- Dedicated Closing Time pacing regression contract.

### Changed
- Night Manager reinforcements widened to `15 / 34 / 54 / 76` seconds for clearer combat spacing.
- Ambient Overtime and unfinished supervisor waves stop creating new threats after the supervisor dies; enemies already alive remain active.
- Project progress reached 66%, Vertical Slice 78%.

## 0.17.0-dev — 2026-09-17

### Added
- Deterministic standard-library combat-audio polish generator for all signature weapons, core enemies and bosses.
- Runtime variation families for 31 logical combat cues.
- PCM, duration, audible-level, peak-headroom, random-family and PK3 regression coverage.

### Changed
- Existing actor sound names and gameplay timing remain stable while SNDINFO selects generated variations at runtime.
- Project progress reached 64%.

## 0.16.0-dev — 2026-09-17

### Added
- Project-owned Customer Service, Frozen Foods, Electronics/Returns and Lane 06 signage.
- Safe wet-floor cone/restock-box clutter, six failing fluorescent fixtures and two Emergency Break Snacks.
- Separate environment DECORATE/UDMF layer, deterministic environment generator and dedicated CI contract.

### Changed
- Closing Time gained stronger retail identity without compromising movement or the front clock-out lane.
- Project progress reached 61%.

## 0.15.0-dev — 2026-09-17

### Added
- Final-layout objective-first night-shift HUD.
- Explicit `06:00` target, next-escalation countdown, health and signature-ammo reserve readouts.
- Text/pattern state cues in addition to color and a dedicated HUD regression contract.

### Changed
- Replaced the tall prototype status stack with a compact layout that keeps the playfield center clear.
- Project progress reached 58%.

## 0.14.0-dev — 2026-09-17

### Added
- Four authored Overtime environmental hazard anchors in Closing Time.
- Warning alarms from 90 seconds, telegraphed electrical arcs from 180 seconds and faster Hell Rush cadence from 270 seconds.
- Project-owned hazard sprites/audio, generator and dedicated CI contract.

### Changed
- Overtime now changes the physical store as well as enemy pressure while preserving readable telegraphs.
- Project progress reached 55%.

## 0.13.0-dev — 2026-09-17

### Added
- Three optional Corporate Compliance Memos across normal, combat and Staff Only routes.
- Staged workplace-comedy messages, HUD memo tracking, project-owned memo sprite/cue and presentation contract.

### Changed
- Closing Time gained a lightweight optional exploration/comedy route without making collectibles mandatory.
- Project progress reached 53%.

## 0.12.0-dev — 2026-09-17

### Added
- Original fifteen-frame Regional Manager boss presentation.
- Corporate Red Tape and Executive Stamp projectiles, dedicated boss cues and health-gated second phase.
- Power-gated Regional Manager spawner plus dedicated asset/gameplay contract.

### Changed
- Warehouse 13.5 now uses project-owned retail surfaces and keeps the boss off the floor until all three breakers are restored.
- Project progress reached 51%.

## 0.11.0-dev — 2026-09-17

### Added
- Original eleven-frame Cart of Doom and Possessed Pallet Jack animation sets.
- Dedicated charge/fork-lunge tells, combat cues and vehicle-enemy asset contract.

### Changed
- Both vehicle threats stopped relying on compatible-IWAD visible combat sprites.
- Project progress reached 48%.

## 0.10.0-dev — 2026-09-17

### Added
- Original Price-Gun SMG pickup/view animation and barcode-label impact feedback.
- Original Turbo Can Launcher pickup/view, can projectile/explosion and sound cues.
- Original Security Price Scanner animation, scan-beam projectile and combat cues.

### Changed
- Mid/heavy signature combat presentation moved away from visible compatible-IWAD placeholders.
- Project progress reached 45%.

## 0.9.0-dev — 2026-09-17

### Added
- Original Receipt Ripper pickup/view animation and fire/cycle cues.
- Original Angry Self-Checkout animation, hostile receipt projectile and combat cues.
- Expanded deterministic combat asset generator and asset regression coverage.

### Changed
- Receipt Ripper and Angry Self-Checkout visible combat presentation became project-owned.
- Project progress reached 42%.

## 0.8.0-dev — 2026-09-16

### Added
- Four original Emergency Mop first-person frames and swing cue.
- Original Night Manager animation set, Manager Memo projectile and combat cues.
- ZDoom-compatible `grAb` offsets from the asset generator.

### Changed
- Emergency Mop and Night Manager stopped relying on visible compatible-IWAD combat placeholders.
- Project progress reached 40%.

## 0.7.0-dev — 2026-09-16

### Added
- First original Closing Time supermarket material pack.
- Original Breaker Fuse, Staff Only shutter and Employee of the Month Stash sprites.
- Original breaker/shutter/Overtime/boss/clock-out cues, deterministic asset generator and asset CI contract.

### Changed
- MAP01 moved from placeholder surfaces to project-owned retail presentation.
- Project progress reached 38%.

## 0.6.0-dev — 2026-09-16

### Added
- `CheckoutBossWaveSpawner` and two rear management-response anchors.
- Initial deterministic supervisor reinforcement sequence and physical return-to-checkout objective.
- `TIMECARD ACCEPTED` completion beat and boss/escape regression contract.

### Changed
- Killing the supervisor no longer auto-completes the map from anywhere.
- Project progress reached 35%.

## 0.5.0-dev — 2026-09-16

### Added
- First optional power-gated Staff Only side route and Employee of the Month Stash.
- Staff security unlock at `2/3` breakers and per-breaker restoration feedback.
- Dedicated Staff Only route regression contract.

### Changed
- Mandatory progression was kept outside the optional room.
- Project progress reached 32%.

## 0.4.0-dev — 2026-09-16

### Added
- First structured Closing Time supermarket-floor pass with separated breaker routes.
- Power-gated Night Manager arrival and contextual objective HUD.
- Third Overtime anchor, layout contract, reproducible portable Windows artifact builder and checksum test.

### Changed
- MAP01 moved from a flat arena toward authored restoration → management response → escape progression.
- Project progress reached 30%.

## 0.3.0-dev — 2026-09-16

### Added
- First real three-breaker + supervisor shift objective.
- `CheckoutShiftDirector`, four-stage Overtime director and map-placed reinforcement spawners.
- Prototype HUD, gameplay contract and pinned-GZDoom `-norun` parser validation on Windows CI.

### Changed
- MAP01/MAP02 became completable objective maps rather than endless combat sandboxes.
- Project progress reached 25%.

## 0.2.0-dev — 2026-09-16

### Added
- Warehouse 13.5 prototype arena.
- Receipt Ripper, Price-Gun SMG, Security Price Scanner, Possessed Pallet Jack and Regional Manager prototype.
- GitHub Actions build/artifact workflow and expanded smoke tests.
- One-click Windows launcher, official GZDoom/Freedoom bootstrap, checksum validation and official portable-Python fallback.
- Pinned `runtime-lock.json`, runtime manifest and third-party/license documentation.

### Changed
- MAP01 now progresses to MAP02 and Windows users no longer need to manually hunt for GZDoom/Freedoom.

## 0.1.0-dev — 2026-09-16

### Added
- Initial CHECKOUT OF HELL project structure and buildable PK3 prototype.
- MAP01 combat sandbox.
- Emergency Mop, Turbo Can Launcher, Angry Self-Checkout, Cart of Doom and Night Manager prototype content.
- Smoke-test tooling, Windows development launch scripts, README, roadmap and asset policy.