# Changelog

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
