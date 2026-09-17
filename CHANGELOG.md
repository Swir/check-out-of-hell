# Changelog

## 0.15.0-dev — 2026-09-17

### Added
- Final-layout night-shift HUD helpers for objective hierarchy, route guidance and four-stage Overtime pressure presentation.
- Explicit `06:00` clock-out target, next-escalation countdown, worker-health readout and reserve counters for Price-Gun labels, Receipt Ripper receipts and Turbo Can ammo.
- Text and patterned pressure cues alongside color so Overtime state and critical-health warnings are not color-only.
- `tools/test_hud_contract.py`, validating objective states, Overtime labels/pressure meter, critical-health feedback, signature-ammo readouts and packaged ZScript markers.
- GitHub Actions execution of the final HUD regression contract.

### Changed
- The old tall prototype status stack is replaced by a compact objective-first layout that keeps the center of the playfield clear.
- Staff Only guidance now appears as a contextual route hint at partial power instead of a detached bonus line.
- README/ROADMAP progress raised to 58% for the implemented/testable final HUD milestone; full combat-audio polish and the first fully decorated Closing Time pass remain open.

## 0.14.0-dev — 2026-09-17

### Added
- Four dedicated Overtime environmental hazard anchors in `MAP01 — Closing Time`, positioned away from the player start and clock-out lane.
- Stage-matched hazard behavior: warning-alarm flashes beginning at 90 seconds, telegraphed electrical floor arcs beginning at 180 seconds, and a 20-second Hell Rush trap cadence beginning at 270 seconds.
- Project-owned warning and electrical-arc sprite set plus dedicated alarm/electrical cues generated deterministically with Python's standard library.
- `game/DECORATE_OVERTIME` and `game/MAP01_OVERTIME.udmf` subsystem fragments, composed into the final PK3/map by the build without duplicating core source actors or geometry.
- `tools/generate_overtime_assets.py` for deterministic Overtime presentation assets.
- `tools/test_overtime_hazard_contract.py`, validating PNG offsets, WAV format, stage timing, damage telegraph, map placement, PK3 composition and sound/build wiring.
- GitHub Actions execution of the Overtime environmental hazard contract.

### Changed
- Overtime now changes the physical store floor as well as reinforcement pressure, making prolonged shifts progressively more hazardous while keeping traps readable and avoidable.
- The build now composes optional DECORATE and UDMF subsystem fragments into the packaged game, keeping core source files readable as prototype systems grow.
- README/ROADMAP progress raised to 55% for the implemented/testable Overtime environmental-pressure milestone; final HUD, full sound polish and a fully decorated Closing Time still remain open.

## 0.13.0-dev — 2026-09-17

### Added
- Three optional `CorporateMemo` pickups in `MAP01 — Closing Time`, distributed across a front detour, east-side combat detour and the powered Staff Only room.
- Staged workplace-comedy policy messages for collecting memo 1/3, 2/3 and 3/3 without making the scavenger route mandatory for progression.
- Project-owned Corporate Compliance Memo pickup sprite and cue generated deterministically with Python's standard library.
- HUD next-Overtime countdown, three-cell power display, optional memo counter and partial-power Staff Only route hint.
- `tools/generate_presentation_assets.py` for deterministic presentation-side assets.
- `tools/test_closing_time_presentation_contract.py`, validating memo PNG offsets, audio, PK3 packaging, map placement, HUD markers, Overtime deadlines, build wiring and SNDINFO registration.
- GitHub Actions execution of the Closing Time presentation contract.

### Changed
- Closing Time now rewards exploration with an optional joke collectible route that crosses normal traversal, enemy pressure and the powered side room.
- The prototype HUD exposes when the next Overtime stage will trigger instead of only showing the current state after escalation happens.
- README/ROADMAP progress raised to 53% for the implemented and testable presentation/readability slice; the final custom HUD and fully polished level remain intentionally incomplete.

## 0.12.0-dev — 2026-09-17

### Added
- Project-owned fifteen-frame Regional Manager animation covering pursuit, ranged tells, pain, collapse and raise presentation.
- Original `CorporateRedTapeProjectile` and `ExecutiveStampProjectile` boss attacks with generated projectile/impact frames.
- Dedicated Regional Manager idle, attack, phase-change, stamp, hit and defeat cues.
- Health-gated second Regional Manager attack phase below 50% health with a wider red-tape barrage and heavy executive-stamp finisher.
- `CheckoutRegionalManagerSpawner` and DoomEdNum `17104`, allowing Warehouse 13.5 to keep the boss off the floor until all three breakers are restored.
- `tools/generate_regional_manager_assets.py`, a deterministic standard-library-only boss asset generator.
- `tools/test_regional_manager_contract.py`, validating PNG offsets, WAVs, PK3 packaging, actor wiring, two-phase behavior, MAP02 power gating and project-owned retail surfaces.
- GitHub Actions execution of the Regional Manager boss contract.

### Changed
- `MAP02 — Warehouse 13.5` now uses the project-owned retail floor, ceiling and wall materials instead of compatible-IWAD placeholder surfaces.
- Warehouse 13.5 no longer pre-places the Regional Manager; restoring all three breakers now triggers the boss arrival.
- Regional Manager visible combat states no longer rely on compatible-IWAD Cyberdemon sprites or its stock primary attack presentation.
- Build tooling now generates the Regional Manager presentation before PK3 packaging.
- README/ROADMAP progress raised to 51% for the boss-identity and Warehouse objective-gate milestone.

## 0.11.0-dev — 2026-09-17

### Added
- Project-owned eleven-frame Cart of Doom animation covering pursuit, charge tell, pain, collapse and raise presentation.
- Dedicated Cart of Doom idle, charge, hit and defeat cues.
- Project-owned eleven-frame Possessed Pallet Jack animation covering pursuit, fork-lunge melee tell, pain, collapse and raise presentation.
- Dedicated Possessed Pallet Jack idle, attack, hit and defeat cues.
- `tools/generate_vehicle_enemy_assets.py`, a deterministic standard-library-only generator for the two vehicle-style enemies.
- `tools/test_vehicle_enemy_assets.py`, a dedicated regression contract covering PNG validity, ZDoom `grAb` offsets, WAV format/duration, PK3 packaging, sound mappings, actor-state wiring and removal of compatible-IWAD visible sprite references.
- GitHub Actions execution of the vehicle-enemy asset contract.

### Changed
- Cart of Doom active visible states no longer rely on compatible-IWAD Lost Soul sprites and now telegraph its rush with project-owned art/audio.
- Possessed Pallet Jack active visible states no longer rely on compatible-IWAD Demon sprites and now telegraph its fork-lunge melee attack with project-owned art/audio.
- Build tooling now generates the vehicle-enemy presentation before PK3 packaging.
- The remaining high-visibility combat-art placeholder is the Regional Manager prototype boss.
- README/ROADMAP progress raised to 48% for the verified vehicle-enemy combat slice.

## 0.10.0-dev — 2026-09-17

### Added
- Project-owned Price-Gun SMG world pickup plus five-frame first-person automatic firing animation.
- Barcode-label impact puff presentation and dedicated Price-Gun trigger/label-feed cues.
- Project-owned Turbo Can Launcher world pickup plus five-frame first-person firing animation.
- Original Turbo Can projectile/impact animation and dedicated launch/explosion cues.
- Original Security Price Scanner turret animation set, custom scanning beam projectile and idle/attack/pain/down cues.
- Expanded deterministic combat asset generation for the new weapon and turret presentation.
- Expanded original-asset regression contract covering the new PNG offsets, WAVs, PK3 packaging, sound mappings, actor-state wiring and removal of compatible-IWAD weapon/turret sprite references.

### Changed
- Price-Gun SMG active pickup/view states no longer use compatible-IWAD chaingun sprites.
- Turbo Can Launcher and Turbo Can projectile no longer use compatible-IWAD rocket-launcher/rocket visuals.
- Security Price Scanner now uses project-owned visible states and a custom scan-beam attack instead of compatible-IWAD chaingun-guy presentation.
- README/ROADMAP progress raised to 45% for the expanded original retail combat slice.

## 0.9.0-dev — 2026-09-17

### Added
- Project-owned Receipt Ripper world pickup plus five-frame first-person animation set.
- Dedicated original Receipt Ripper fire and paper-cycle cues.
- Ten-frame original Angry Self-Checkout animation set covering idle/chase/attack/pain/death/raise presentation.
- Original `CheckoutReceiptProjectile` with generated receipt-flight/impact animation.
- Original Angry Self-Checkout idle, attack, pain and defeat cues.
- `tools/generate_combat_assets.py`, a deterministic standard-library-only extension for signature combat assets.
- Expanded original-asset regression contract covering Receipt Ripper and Angry Self-Checkout PNG offsets, PK3 packaging, sound mappings and actor-state wiring.

### Changed
- Receipt Ripper active view/pickup states no longer use compatible-IWAD shotgun sprites.
- Angry Self-Checkout visible actor states and primary ranged attack no longer use compatible-IWAD shotgun-guy sprites/attack presentation.
- Build tooling now generates the atmosphere asset pack and signature combat extension before PK3 packaging.
- README/ROADMAP progress raised to 42% for the second verified signature combat-art slice.

## 0.8.0-dev — 2026-09-16

### Added
- Four project-owned first-person sprite frames for the Emergency Mop, generated deterministically during the build.
- Original Emergency Mop swing cue wired directly into the melee attack state.
- Eleven-frame original Night Manager prototype sprite sequence covering idle/chase/attack/pain/death/raise states.
- Original `ManagerMemoProjectile` with a generated glowing paperwork projectile/explosion animation.
- Dedicated original Night Manager attack and defeat cues.
- ZDoom-compatible `grAb` sprite offsets emitted directly by the stdlib-only PNG generator.
- Extended original-asset contract covering the new combat sprites, PNG offsets, audio mappings, PK3 contents and actor-state wiring.

### Changed
- Emergency Mop no longer uses the compatible-IWAD fist view sprites.
- Night Manager no longer uses the compatible-IWAD Baron actor sprites or projectile visual for its primary attack presentation.
- Asset policy now distinguishes the first fully project-owned signature combat presentation from the remaining placeholder weapons/enemies.
- README/ROADMAP progress raised to 40% after the signature combat-art milestone was implemented and prepared for full CI/runtime validation.

## 0.7.0-dev — 2026-09-16

### Added
- First original Closing Time retail atmosphere pack: supermarket wall, shelf, Staff Only, floor and ceiling materials.
- Original prototype sprites for Breaker Fuse, Staff Only shutter and Employee of the Month Stash.
- Original synthesized interaction cues for breaker restoration, shutter opening, Overtime escalation, Night Manager arrival and clock-out.
- `tools/generate_assets.py`, a deterministic Python-standard-library-only generator for the original prototype art/audio pack.
- `game/SNDINFO` registry for project-owned interaction cues.
- `tools/test_original_assets.py` validating generated PNG/WAV integrity, PK3 packaging, map usage, sprite states and gameplay sound wiring.
- GitHub Actions execution of the original visual/audio asset contract.

### Changed
- `MAP01 — Closing Time` now uses project-owned supermarket surfaces instead of Doom placeholder floor/wall materials.
- Breaker, Staff Only barrier and staff-room reward visuals now use project-owned generated sprites.
- Overtime stage changes now fire PA-style audio cues; full-power boss arrival and physical clock-out have their own sound feedback.
- PK3 build now generates and packages original textures, flats, sprites and sounds before map packaging.
- Generated runtime assets are ignored in source control because their canonical source is the deterministic generator.
- README/ROADMAP progress raised to 38% after the first original visual/audio atmosphere pass and dedicated regression contract were implemented.

## 0.6.0-dev — 2026-09-16

### Added
- `CheckoutBossWaveSpawner` ZScript actor and DoomEdNum `17103`.
- Two dedicated rear supervisor-response anchors in `MAP01 — Closing Time`.
- Deterministic full-power boss-response sequence: Angry Self-Checkout at 12s, Cart of Doom at 26s, Security Price Scanner at 42s and Possessed Pallet Jack at 58s.
- Teleport-fog arrival cues for the Night Manager and each staged reinforcement wave.
- Physical return-to-front-checkout clock-out objective after supervisor clearance.
- Explicit `TIMECARD ACCEPTED` completion feedback and one-second clock-out beat before level transition.
- `tools/test_boss_escape_contract.py` covering boss-wave anchors, wave order/timing and front-checkout completion geometry.
- CI execution of the boss + escape contract.

### Changed
- Killing the supervisor no longer auto-completes the level from anywhere on the map.
- HUD progression now ends with `RETURN TO FRONT CHECKOUT`, then `TIMECARD ACCEPTED` when the player reaches the front timecard zone.
- Closing Time now behaves as restoration → supervisor response → escape/clock-out instead of restoration → boss → automatic exit.
- README/ROADMAP progress raised to 35% to reflect the implemented and contract-tested supervisor encounter/clock-out milestone.

## 0.5.0-dev — 2026-09-16

### Added
- First optional power-gated side route in `MAP01 — Closing Time`.
- Rear-left Staff Only room with a physical three-blocker security barrier.
- `CheckoutStaffShutter` ZScript actor and DoomEdNum `17102`.
- Staff Only access unlocking after `2/3` breakers so partial power has a useful gameplay consequence.
- `Employee of the Month Stash` optional reward with workplace-comedy pickup text.
- Visible breaker-restoration feedback banners for `1/3`, `2/3` and `3/3` power states.
- Short teleport-fog power pulse when a breaker is restored.
- `tools/test_staff_room_contract.py` protecting the optional-room geometry, unlock threshold, reward and non-mandatory progression contract.
- CI execution of the Staff Only route contract.

### Changed
- The left-side mandatory breaker and Overtime anchor were moved outside the Staff Only room so the side route cannot become a hidden required path.
- MAP01 rear-left geometry now creates an actual employee-room pocket instead of another open arena corner.
- Gameplay and level-design documentation now define optional powered side routes as part of the department loop.
- README/ROADMAP project progress raised to 32% after the Staff Only route, breaker feedback, dedicated contract test, portable artifact build and post-merge pinned-GZDoom validation all passed on `main`.

## 0.4.0-dev — 2026-09-16

### Added
- First structured `MAP01 — Closing Time` supermarket-floor pass with internal aisle/counter barriers and a larger traversal footprint.
- Breaker route separation across left, right and rear store zones.
- `CheckoutManagerSpawner` ZScript actor and DoomEdNum `17101`.
- Power-gated Night Manager arrival after the player restores all three breakers.
- Contextual HUD task line that changes from power restoration to supervisor clearance and clock-out.
- Third Overtime reinforcement anchor in MAP01 to distribute escalation across the expanded floor.
- `tools/test_closing_time_layout.py` contract test covering floor scale, route separation, supervisor staging and Overtime coverage.
- CI execution of the Closing Time layout contract.
- Reproducible `tools/package_portable.py` Windows development artifact builder.
- Dedicated player-facing portable `PLAY.bat` that launches a prebuilt PK3 and requires no Python/build toolchain.
- Portable ZIP SHA-256 sidecar generation.
- `tools/test_portable_package.py` contract test for artifact contents, no-manual-dependency-search behavior and checksum integrity.
- CI upload of the portable Windows development ZIP and checksum.
- Windows packaging documentation.
- Verified main-branch GitHub Actions artifact `checkout-of-hell-windows-portable-dev` from the merged packaging commit.

### Changed
- MAP01 no longer pre-places Night Manager before the power objective is complete.
- MAP01 enemy positions now support left/right/rear traversal instead of a single flat arena engagement.
- Gameplay and level-design documentation now describe the staged Closing Time progression contract.
- Portable artifacts intentionally omit runtime EXE/WAD payloads and rely on the pinned official-source bootstrap on first launch.
- README/ROADMAP project progress raised to 30% after the portable artifact builder, checksum contract, artifact upload and post-merge pinned-GZDoom validation all passed on `main`.

## 0.3.0-dev — 2026-09-16

### Added
- First real shift objective loop: collect three Breaker Fuses and defeat the department supervisor.
- Automatic level exit two seconds after both objective conditions are satisfied.
- ZScript `CheckoutShiftDirector` event handler.
- Four-stage Overtime pressure system: Shift Active, Store Unstable, Overtime and Hell Rush.
- Map-placed Overtime reinforcement spawners that escalate from Angry Self-Checkout to Cart of Doom and Possessed Pallet Jack.
- HUD overlay showing shift timer, Overtime state, breaker progress and supervisor state.
- Breaker Fuse pickup actor placed three times in each prototype map.
- Gameplay contract test covering Overtime thresholds, objective requirements and prototype map progression.
- Smoke-test coverage for ZScript packaging, objective pickups and Overtime spawners.
- Gameplay loop documentation.
- Windows CI runtime smoke test that downloads the pinned official GZDoom/Freedoom runtime and asks GZDoom to parse the built PK3 through `-norun`.
- Archived GZDoom runtime smoke log for CI diagnosis.

### Changed
- MAP01 and MAP02 now contain actual completion objectives instead of functioning only as endless combat sandboxes.
- PK3 build now packages the `ZSCRIPT` lump.
- GitHub Actions now runs the gameplay contract test before producing the artifact.
- Runtime CI now validates the prototype with the actual pinned GZDoom executable instead of only resolving download metadata.
- README/ROADMAP progress raised to 25% after the objective/Overtime systems and pinned-engine parser validation were verified.

## 0.2.0-dev — 2026-09-16

### Added
- MAP02: Warehouse 13.5 prototype arena.
- Receipt Ripper weapon.
- Price-Gun SMG weapon.
- Security Price Scanner enemy.
- Possessed Pallet Jack enemy.
- Regional Manager prototype boss.
- GitHub Actions build and artifact workflow.
- Weapon design documentation.
- Level design documentation.
- Expanded smoke tests covering both generated maps and actor registry.
- `PLAY.bat` one-click Windows launcher.
- Automatic pinned GZDoom and Freedoom bootstrap from official GitHub Releases.
- Official Freedoom checksum verification when a parsable SHA-256 entry is available.
- Portable Python fallback downloaded from `python.org` when a source build requires Python.
- `runtime-lock.json` for reproducible runtime versions and download selection.
- Runtime manifest with local SHA-256 hashes.
- Bootstrap contract test and Windows CI dry-run for official release resolution.
- Third-party runtime/license documentation.

### Changed
- MAP01 now progresses to MAP02.
- Build tooling now packages multiple maps.
- Windows launchers no longer require users to manually locate GZDoom or Freedoom.
- README and roadmap now reflect the automatic dependency policy.

## 0.1.0-dev — 2026-09-16

### Added
- Initial CHECKOUT OF HELL project structure.
- Buildable PK3 prototype.
- Generated MAP01 combat sandbox.
- Emergency Mop prototype weapon.
- Turbo Can Launcher prototype weapon.
- Angry Self-Checkout placeholder enemy.
- Cart of Doom placeholder enemy.
- Night Manager placeholder mini-boss.
- Smoke-test tooling.
- Windows development launch scripts.
- Initial README, roadmap and asset policy.