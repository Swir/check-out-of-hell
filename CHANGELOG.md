# Changelog

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
- Bootstrap contract test and Windows CI verification of official release resolution/downloads.
- Third-party runtime/license documentation.
- Map-specific staged **Overtime** pressure directors for Closing Time and Warehouse 13.5.
- Overtime contract tests that guard map placement, timing stages and recurring pressure spawns.
- Headless real-engine validation with the pinned official GZDoom `g4.14.2` Linux build under Xvfb/Mesa.
- Archived GZDoom startup/parser log artifact for CI diagnostics.
- Overtime gameplay design documentation.

### Changed
- MAP01 now progresses to MAP02.
- Build tooling now packages multiple maps.
- Windows launchers no longer require users to manually locate GZDoom or Freedoom.
- README and roadmap now reflect the automatic dependency policy.
- CI separates structural tests, Windows runtime download/bootstrap verification and real GZDoom parser/startup validation.

### Validation notes
- Hosted Windows runners successfully resolve/download the pinned Windows runtime and verify Freedoom's official SHA-256, but they do not provide the OpenGL/Vulkan graphics support required for an interactive GZDoom render session.
- Real GZDoom parser/startup validation therefore runs headlessly on Linux with Mesa software rendering; an interactive physical/desktop Windows playtest remains a release gate.

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
