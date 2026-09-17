# Changelog

## 0.19.0-dev — 2026-09-17

### Added
- Three authored MAPINFO difficulty modes: forgiving `Closing Crew`, default `Graveyard Shift`, and confirmation-gated `Corporate Hell`.
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
