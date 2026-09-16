# Changelog

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
