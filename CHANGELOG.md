# Changelog

## 0.33.1-dev — 2026-09-18

### Added
- Frozen Foods now links the first two cold-chain repairs to a dedicated right-flank response: each newly restored breaker telegraphs the aisle for three seconds, then answers with a Security Price Scanner after breaker one and a Cart of Doom after breaker two.
- `FrozenBreakerResponseSpawner` uses sparse seven-tic polling, preserves pending/observed response state across normal save restores, retires on supervisor clearance, and never places a third immediate enemy at full power.

### Changed
- The third breaker deliberately hands pressure to the existing full-power Night Manager and deterministic management-response systems instead of stacking another instant spawn on top of the boss transition, keeping the repair → combat escalation readable.
- `tools/test_frozen_foods_contract.py` now protects DoomEdNum registration, exactly one side-lane response anchor, the three-second warning, first/second-breaker enemy sequence, clearance cleanup, full-power handoff and packaged MAP03/ZScript payload.
- Project progress remains **86.8%** and Demo Release readiness remains **70.0%**. This is playable Frozen Foods encounter polish; it does not complete a weighted phase, the target-Windows human sign-off, release notes or a public release.

### Validation
- The full repository CI remains the merge gate, including the expanded Frozen Foods contract, existing gameplay/performance/save-load checks, Windows RC/legal-content packaging, SWIR README PRO v2 and Progress SVG PRO.
- No proprietary Doom, Star Wars or other ripped commercial assets were added. No public demo or GitHub Release was created.

## 0.33.0-dev — 2026-09-18

### Added
- `MAP03 — Frozen Foods` as a real playable third department with four authored freezer-aisle barriers, three cold-chain breaker routes, a power-gated Night Manager encounter, a deterministic management-response anchor, full-power recovery, four telegraphed Overtime hazard anchors, three optional Corporate Compliance Memos and a post-clear return guide.
- Project-owned Frozen Foods presentation using the existing generated `FROZEN FOODS` signs, safe restock/cone clutter, slow-failing lights and optional Emergency Break Snacks, plus the new deterministic original `D_COH03.mid` theme **Frozen Foods — Compressor Choir**.
- `FrozenDepartmentInitSpawner`, a map-local one-shot initializer that clears optional memo progress carried into a fresh MAP03 and then destroys itself so ordinary save/restore inside the department preserves newly collected memos.
- `tools/test_frozen_foods_contract.py`, covering source layout, objective counts, entry/rear placement, generated presentation, MAPINFO/build wiring, packaged MAP03 WAD structure, composed ZScript and the new music payload.

### Changed
- The playable department chain is now `Closing Time -> Warehouse 13.5 -> Frozen Foods -> Closing Time`; the build, smoke test, soundtrack contract, CI workflow, README, roadmap and design/gameplay/music documentation all recognize the third playable department.
- Frozen Foods deliberately reuses hardened breaker, Overtime, Night Manager response and physical clock-out systems instead of claiming an unvalidated new boss or random slippery-floor gimmick. Its department identity comes from route geometry, cold-storage dressing, optional exploration and original music while preserving fast readable combat.
- Project progress remains **86.8%** and Demo Release readiness remains **70.0%**. Completing the first playable MAP03 implementation checks the existing Frozen Foods roadmap milestone but does not retroactively invent a new phase percentage, mark any level polished, complete the target-Windows human sign-off, write release notes or create a public release.

### Validation
- The full repository CI is the merge gate, including the new Frozen Foods contract, expanded smoke/music checks, SWIR README PRO v2 and Progress SVG PRO, pinned-GZDoom parser/runtime validation, real two-process save/load, Windows RC packaging and legal-content checks.
- No proprietary Doom, Star Wars or other ripped commercial assets were added. No public demo or GitHub Release was created.

## 0.32.8-dev — 2026-09-18

### Added
- Warehouse 13.5 now exposes one optional full-power `Lockout/Tagout Permit` on the rear-left side lane, opposite the existing recovery cache. The permit reuses the project-owned freight-control presentation and is never required for progression.
- `WarehouseSafetyStateHandler` keeps the permit department-local on fresh map transitions while preserving the token across savegame restores.

### Changed
- Taking the permit retires future Warehouse electrical Overtime floor arcs only; ambient Overtime enemy reinforcements, freight-lift progression, the `12 / 30 / 52` management-response waves and The Regional Manager remain active.
- The shared Overtime hazard anchor delays its first inventory poll by seven tics so fresh-map department-token cleanup happens before a carried Warehouse permit can affect another department.
- `tools/test_warehouse_lift_objective_contract.py` now protects the safety-station registration, full-power/department gates, fresh-map/save behavior, side-lane placement, packaged PK3/MAP02 payload and the rule that the permit cannot disable hostile Overtime or management. Project progress remains **86.8%** and Demo Release readiness remains **70.0%** because this playable polish does not complete a weighted phase or the target-Windows human sign-off.

### Validation
- The full repository CI remains the merge gate, including the expanded Warehouse contract, Overtime contract, pinned-GZDoom parser/runtime checks, real two-process save/load, RC packaging, README PRO v2 and Progress SVG PRO.
- No proprietary Doom, Star Wars or other ripped commercial assets were added. No public demo or GitHub Release was created.

## 0.32.7-dev — 2026-09-18

### Added
- Warehouse 13.5 now has a dedicated `MAP02_OVERTIME.udmf` layer with two authored side-lane Overtime hazard anchors. They reuse the project-owned warning/arc presentation and the existing deterministic `90 / 135 / 180 / 212 / 244 / 270` second schedule.

### Changed
- The new warehouse hazard anchors stay at the outer side lanes, away from the freight-lift/clock-out centerline and outside the optional Damaged Goods cage, so prolonged shifts gain physical pressure without obscuring mandatory progression.
- The shared clearance-aware hazard spawner retires both Warehouse anchors when Regional Management is cleared, preserving the readable return-to-entry leg.
- `tools/test_overtime_hazard_contract.py` now verifies both MAP01 and MAP02 source layers plus packaged WAD payloads and protects the warehouse side-lane placement. Project progress remains **86.8%** and Demo Release readiness remains **70.0%** because this gameplay polish does not complete a weighted phase or the target-Windows human sign-off.

### Validation
- The full repository CI remains the merge gate, including the expanded Overtime contract, Warehouse objective contract, pinned-GZDoom parser/runtime checks, real two-process save/load, RC packaging, README PRO v2 and Progress SVG PRO.
- No proprietary Doom, Star Wars or other ripped commercial assets were added. No public demo or GitHub Release was created.

## 0.32.6-dev — 2026-09-18

### Added
- Warehouse 13.5 now includes an optional right-side Damaged Goods cage sealed by four project-owned, shootable stock piles. Breaking a useful gap spends ammunition to reach a Damaged-Goods Label Crate and Emergency Break Snack while all mandatory objectives remain outside the nook.
- `WarehouseStockPile` (`17136`) reuses the project-owned generated `BOXE` presentation, has explicit solid/shootable collision, and clears its blocking state on destruction with an existing project-owned warehouse impact cue.

### Changed
- `tools/test_warehouse_lift_objective_contract.py` now protects the four-pile barrier, stock-pile damage/death behavior, optional side-cage geometry, reward placement, mandatory-objective exclusion and packaged PK3/MAP02 payload in addition to the existing lift, management-response, recovery-cache and return-guide gates.
- Warehouse design/gameplay documentation now records the ammo-for-supplies route and removes breakable stock piles from the remaining-polish list. Project progress remains **86.8%** and Demo Release readiness remains **70.0%** because this playable side-route improvement does not complete a weighted phase, target-Windows sign-off, release notes or a public release.

### Validation
- The full repository CI remains the merge gate, including the expanded Warehouse contract, pinned-GZDoom parser/runtime checks, real two-process save/load, RC packaging, README PRO v2 and Progress SVG PRO.
- No proprietary Doom, Star Wars or other ripped commercial assets were added. No public demo or GitHub Release was created.

## 0.32.5-dev — 2026-09-18

### Added
- Warehouse 13.5 now reveals one project-owned full-power recovery cache on a rear side lane after all three breakers are restored, before the player commits to the Freight Lift Override and Regional Management encounter.
- Supervisor clearance now reveals one existing project-owned non-blocking `CLOCK OUT` guide near the warehouse entry, making the final return-to-clock-out leg immediately readable without moving or weakening the physical exit trigger.

### Changed
- `tools/test_warehouse_lift_objective_contract.py` now protects the recovery-cache and return-guide DoomEdNums, one-shot watcher lifecycles, authored side/front placement, packaged ZScript/DECORATE actors and built MAP02 markers in addition to the existing lift gate and `12 / 30 / 52` management response.
- Project progress remains **86.8%** and Demo Release readiness remains **70.0%**. This is Warehouse encounter/return readability polish; it does not mark Warehouse 13.5 polished, complete the target-Windows Closing Time sign-off, write release notes or create a public release.

### Validation
- The full repository CI remains the merge gate, including the Warehouse objective contract, README PRO v2, Progress SVG PRO, RC packaging, pinned runtime checks and real two-process save/load validation.
- No proprietary Doom, Star Wars or other ripped commercial assets were added. No public demo or GitHub Release was created.

## 0.32.4-dev — 2026-09-18

### Added
- `CHECKOUT-OF-HELL-Legal-Content-rc.zip`, a deterministic content-only release-candidate artifact built from the exact verified bytes used by the Windows player RC: project PK3, pinned Freedoom WAD, project/Freedoom notices, provenance, third-party notes and runtime lock.
- `content-manifest.json`, binding the standalone content bundle to the exact Git source snapshot and covering every payload file with SHA-256 plus byte count while explicitly recording that GZDoom is not redistributed.
- `tools/test_legal_content_bundle.py`, which rejects executable/bootstrap leakage, verifies source/license/runtime/provenance metadata, checks the outer SHA-256 sidecar and requires byte-for-byte equality with the corresponding Windows RC content.
- A Warehouse 13.5-only management-response spawner that starts only after the player engages the Freight Lift Override, then feeds a readable rear-flank Security Price Scanner → Possessed Pallet Jack → Cart of Doom sequence at `12 / 30 / 52` seconds.

### Changed
- GitHub Actions now verifies the standalone legal-content RC on both Ubuntu and Windows and uploads it as a dedicated non-public CI artifact alongside the existing Windows player RC.
- `docs/PACKAGING.md` now documents the reusable legal-content layer separately from the player package. Normal Windows players still use `PLAY.bat`; missing pinned GZDoom files are obtained automatically from official upstream, so this content-only artifact never creates a manual engine-hunting requirement.
- The implemented/testable standalone legal-content milestone raises Demo Release readiness from **60.0%** to **70.0%**. With the documented phase weights, project progress moves from exact **84.75%** to **86.75%**, displayed as **86.8%**. The milestone does not replace the interactive target-Windows sign-off, release notes or GitHub Release gate.
- Warehouse 13.5 now gets a deterministic department-specific combat response after lift activation instead of relying only on the Regional Manager plus ambient Overtime. The response uses one off-center authored anchor, sparse seven-tic polling and retires immediately on supervisor clearance or after its final wave so the return-to-entry leg remains readable.
- The existing Warehouse freight-lift contract now verifies the new DoomEdNum registration, lift/department/clearance gates, exact response timings, flank placement and packaged MAP02/ZScript content.

### Validation
- The full repository CI remains the merge gate. It must build both RC artifacts, verify their manifest/provenance relationship, keep README PRO v2 and Progress SVG PRO checks green, and preserve the existing pinned-GZDoom parser, offline-runtime reuse and real two-process save/load gates.
- The Warehouse 13.5 objective contract now also protects the `12 / 30 / 52` second management-response cadence and requires the spawner to retire after supervisor clearance or its final wave.
- Project progress remains **86.8%** and Demo Release readiness remains **70.0%** for this encounter-polish pass; it does not mark Warehouse 13.5 polished or complete the target-Windows human sign-off.
- No proprietary Doom, Star Wars or other ripped commercial assets were added. No public demo or GitHub Release was created.

## 0.32.3-dev — 2026-09-18

### Added
- `tools/verify_windows_signoff_evidence.py`, a stdlib-only independent verifier for completed target-Windows sign-off evidence. It binds a `PASS` directory to the exact candidate commit and re-validates required human/automated gates, extracted RC manifest entries, pinned runtime identity/hashes, Freedoom provenance, the manual save and the two-process save/load completion markers.
- `tools/test_windows_signoff_evidence_verifier.py`, a synthetic evidence contract that accepts a consistent fixture and deliberately rejects a tampered game PK3, a failed physical-controller haptics gate and a mismatched expected commit.

### Changed
- `docs/WINDOWS_PLAYTEST.md` and the active ROADMAP demo gate now require completed `PASS` evidence to survive independent consistency verification against the exact candidate commit before it is accepted as release-gate evidence.
- GitHub Actions runs the verifier contract alongside the existing Windows sign-off contract. Hosted CI still never performs or claims the human gameplay/controller/performance sign-off.
- Project progress remains **84.8%** and Demo Release readiness remains **60.0%**. Evidence hardening does not mark Closing Time polished, complete the real target-Windows playtest, finish the standalone legal-content decision, write release notes or create a GitHub Release.

### Validation
- The independent verifier and synthetic tamper contract pass locally; the full repository CI remains the merge gate for this change.
- Existing README PRO v2, Progress SVG PRO, package integrity, official-source runtime, offline-reuse, pinned-GZDoom parser and real two-process save/load gates remain in force. No public demo or GitHub Release was created.

## 0.32.2-dev — 2026-09-18

### Added
- `tools/test_windows_offline_runtime_cache.ps1`, a Windows release-candidate gate that verifies the extracted package, primes the pinned runtime once from official upstream, removes downloaded archive/cache material, blocks outbound HTTP(S), reruns the packaged bootstrap and requires unchanged GZDoom/Freedoom hashes.
- `tools/test_windows_offline_runtime_cache_contract.py`, protecting the cache-removal, blocked-network, hash/identity and GitHub Actions wiring without replacing the real target-Windows gameplay sign-off.

### Changed
- Windows CI now proves the documented later-launch behavior against the exact extracted RC: after the first verified runtime preparation, the second bootstrap must succeed with outbound networking blocked and without repopulating the runtime archive cache.
- The offline reuse pass requires the rewritten runtime manifest to keep the exact pinned GZDoom tag/asset name/asset ID/archive byte count and `bundled-verified-content` Freedoom delivery, with installed runtime hashes unchanged.
- Project progress remains **84.8%** and Demo Release readiness remains **60.0%**. This packaging resilience evidence does not mark Closing Time polished, complete the interactive target-Windows controller/balance/performance sign-off, finish the standalone legal-content decision, write release notes or create a GitHub Release.

### Validation
- The Ubuntu build job statically protects the offline-runtime harness and documentation, while the Windows runtime-resolution job syntax-parses the PowerShell harness and executes the real extracted-RC online-prime → archive-cache removal → blocked-network reuse sequence.
- Existing package integrity, official-source runtime resolution, pinned-GZDoom parser, real two-process save/load, README PRO v2 and Progress SVG PRO gates remain in force; no public demo or GitHub Release was created.

## 0.32.1-dev — 2026-09-18

### Added
- Build-source provenance in every non-public Windows release-candidate `package-manifest.json`: the exact Git commit, active branch/ref and tracked-source clean state are captured before build outputs are generated.
- `docs/RC_SOURCE_PROVENANCE.md`, documenting how RC source identity is recorded, verified and kept separate from public-release authorization.

### Changed
- `tools/test_release_candidate_package.py` now rejects CI candidates without a full commit SHA, a usable branch/ref, a clean tracked source snapshot or an embedded commit that differs from the checkout validating it.
- Source archives without `.git` metadata remain buildable for development but record provenance as unavailable rather than fabricating a commit identity; such packages cannot pass the CI RC provenance contract.
- GZDoom remains a pinned official-source first-run bootstrap and verified Freedoom bundling is unchanged. Project progress remains **84.8%** and Demo Release readiness remains **60.0%**; provenance hardening does not complete the interactive Windows sign-off, standalone legal-content gate, release notes or GitHub Release.

### Validation
- The existing release-candidate package contract rebuilds the candidate and verifies the embedded source commit against `git rev-parse HEAD` in CI while retaining all package SHA-256, Freedoom license/provenance, Windows extraction, pinned-GZDoom parser and real two-process save/load gates.
- No public demo or GitHub Release was created.

## 0.32.0-dev — 2026-09-18

### Added
- A deliberate Warehouse 13.5 freight-lift objective after the existing three-breaker restoration: full power now reveals a project-owned `Freight Lift Override`, and The Regional Manager cannot enter until the player physically engages it.
- Warehouse-specific HUD and opt-in Focus HUD states for breaker restoration, lift activation, Regional Management pressure and the return-to-entry escape leg.
- Deterministic project-owned Warehouse 13.5 lift/freight signage, plus a non-blocking loading-bay environment layer kept off the central objective/combat lane.
- `tools/test_warehouse_lift_objective_contract.py`, covering source gating, generated PNG/grAb assets, map anchor spacing, accessibility synchronization and the built MAP02/PK3 payload.

### Changed
- Warehouse 13.5 is no longer only a three-breaker → automatic boss gate: the useful workplace task is now restore circuits → activate the freight lift → survive Regional Management → return to the warehouse entry.
- Department-local warehouse/lift inventory state is cleared only on genuinely fresh map loads; savegame restores preserve them alongside the existing serialized shift state.
- Project progress remains **84.8%** and Demo Release readiness remains **60.0%**. This is real playable MAP02 work, but it does not mark Warehouse 13.5 polished, complete the target-Windows Closing Time sign-off, finish legal packaging/release notes or create a release.

### Validation
- CI builds the generated warehouse assets and MAP02 layer, runs the dedicated freight-lift objective contract, then keeps the existing pinned-GZDoom parser/runtime, two-process save/load, packaging, README PRO v2 and Progress SVG PRO gates in force.
- No proprietary Doom, Star Wars or other ripped commercial assets were added, and no public demo or GitHub Release was created.

## 0.31.0-dev — 2026-09-18

### Added
- `WINDOWS-DEMO-SIGNOFF.bat` and `tools/windows_demo_signoff.ps1`, a target-Windows evidence harness that builds the exact non-public RC ZIP, verifies its manifest, prepares the pinned official runtime and runs the real two-process save/load check against the extracted player payload before any manual judgment begins.
- Guided Closing Time sign-off for Closing Crew, Graveyard Shift and Corporate Hell, including an explicit manual Graveyard save → full process exit → load confirmation, physical-controller/core-action and haptics checks, real-hardware Overtime/boss performance sanity and final balance/presentation judgment.
- Privacy-limited JSON/Markdown evidence containing source commit/branch/cleanliness, RC SHA-256, pinned runtime identity, OS/CPU/GPU/RAM and controller friendly names only; no account names, machine names, serial numbers or stable hardware/device IDs are collected or uploaded automatically.
- `docs/WINDOWS_PLAYTEST.md` plus `tools/test_windows_demo_signoff_contract.py`, documenting and protecting the exact RC → runtime → automated save/load → human sign-off chain.

### Changed
- `tools/gzdoom_save_load_smoke.ps1` can now validate caller-supplied GZDoom/Freedoom/PK3 paths and evidence locations with `-PreparedRuntime`, while preserving its original standalone build/bootstrap behavior. This lets the Windows sign-off exercise the already verified RC payload instead of silently rebuilding or swapping it.
- Windows CI now syntax-parses the interactive sign-off and save/load PowerShell scripts but deliberately does not execute or claim the human playtest. The Ubuntu contract verifies required gates, privacy limits, roadmap honesty and SVG-only progress presentation.
- `ROADMAP.md` now links the reproducible target-Windows sign-off procedure and keeps the human play/controller/balance/performance gate explicit.
- Project progress remains **84.8%** and Demo Release readiness remains **60.0%**. Evidence tooling reduces ambiguity in the remaining gate but does not complete it, mark Closing Time polished, finish legal packaging/release notes or create a release.

### Validation
- The new contract requires exact RC integrity verification before runtime bootstrap and the prepared runtime before the exact-RC save/load pass; final `PASS` requires every automated result, every manual result and a clean commit-addressable source snapshot.
- Hosted CI is restricted to static contract checks and PowerShell syntax parsing for the interactive harness; no hosted runner is allowed to masquerade as the target-Windows human sign-off.
- No public demo or GitHub Release was created.

## 0.30.0-dev — 2026-09-18

### Added
- Windows release-candidate bundling for pinned Freedoom `v0.13.0` base content: `external/freedoom2.wad`, the exact upstream BSD 3-Clause `COPYING.adoc` from the same immutable tag, and deterministic `FREEDOOM-PROVENANCE.json` metadata.
- `tools/test_legal_content_package_contract.py`, protecting the official-source release/checksum path, bundled-license/provenance policy, verified runtime cache reuse and Windows-package verifier wiring.
- Package-manifest and PowerShell verification of the bundled Freedoom WAD/license hashes and provenance before GZDoom is prepared.
- Exact official GZDoom `g4.14.2` Windows release-asset identity in `runtime-lock.json`: asset name, GitHub asset ID and byte size, so the bootstrap can reject silent replacement/re-upload drift even though that upstream release does not publish an asset digest.
- README PRO regression coverage that rejects retired block/shade and bracket-style character progress meters from active README/ROADMAP dashboards.

### Changed
- `tools/package_release_candidate.py` now resolves the pinned official Freedoom release, requires the matching official SHA-256 checksum, verifies the archive before extracting `freedoom2.wad`, and records the exact upstream license notice from the same pinned upstream tag.
- The release-candidate bootstrap accepts bundled Freedoom only when its provenance SHA-256 matches, otherwise falls back to the pinned official upstream recovery path. Verified cached GZDoom is also hash-checked and reused on later launches.
- GZDoom intentionally remains an automatic official-source first-run dependency rather than being copied into the candidate package; no proprietary Doom IWAD or unofficial mirror is introduced.
- Windows GZDoom bootstrap now verifies the official release metadata against the locked asset name/ID/byte count before download, validates the archive byte count before extraction, records that identity in the runtime manifest and requires it for cached-runtime reuse. This strengthens provenance without claiming an upstream SHA-256 that GZDoom `g4.14.2` does not provide.
- `ROADMAP.md` retired the duplicated legacy character progress meter while preserving the verified **84.8%** numeric fallback, SVG mini card, weighted calculation, milestone checklist and separate **60.0%** Demo Release readiness gate.
- Packaging and third-party documentation now describe the bundled legal base-content layer separately from the still-unbundled GZDoom engine.
- README/ROADMAP/project progress remain **84.8%** and Demo Release readiness remains **60.0%** in this iteration: this hardening/presentation pass is testable, but it does not complete a new gameplay or release-readiness milestone.

### Validation
- The first CI attempt correctly rejected an assumption that the Freedoom binary release ZIP contained `COPYING.adoc`; the implementation was corrected to obtain the exact notice from the same pinned upstream tag instead of weakening the gate.
- Bootstrap contract coverage now locks the official GZDoom Windows asset identity and Windows `-DryRun` must resolve that exact upstream asset before the runtime/package jobs proceed.
- SWIR README PRO v2 coverage now fails if an active README/ROADMAP reintroduces the retired character progress meter while preserving SVG + numeric fallback checks.
- Final CI validates the release-candidate build/package contract, bundled WAD/license/provenance on Windows, the pinned GZDoom parser, and the real two-process pinned-GZDoom save → exit → load runtime test.
- No public demo or GitHub Release was created.

## 0.29.0-dev — 2026-09-18

### Added
- `tools/test_closing_time_combat_readability_contract.py`, protecting the authored center navigation strip, flanked Night Manager response anchors, off-center Overtime reinforcement anchors, mirrored non-blocking Lane 06 wayfinding, the existing physical clock-out trigger and the built MAP01/PK3 output.
- GitHub Actions execution of the Closing Time combat-readability contract.
- `tools/package_release_candidate.py` and dedicated `packaging/PLAY-RC.bat` for a prebuilt, Python-free Windows portable release-candidate ZIP with a stable `game/CHECKOUT-OF-HELL.pk3` player payload.
- Deterministic `package-manifest.json` generation with SHA-256 and byte counts for every bundled project file, plus `tools/verify_player_package.ps1` for local integrity verification before any runtime download.
- `tools/test_release_candidate_package.py`, CI upload of the release-candidate ZIP/checksum pair and a Windows job that extracts the candidate and executes its PowerShell integrity verifier.

### Changed
- Closing Time's two inner Angry Self-Checkouts moved from the center strip to mirrored side positions, keeping initial pressure while preserving a cleaner front-to-rear navigation/sightline axis.
- The front sales-floor Overtime reinforcement anchor moved out of the physical center/clock-out approach; all three ambient reinforcement anchors now remain off that axis while preserving the existing Overtime cadence.
- Night Manager response anchors moved to the rear flanks so the authored `15 / 34 / 54 / 76` second reinforcement sequence no longer materializes on the central supervisor approach.
- Front Lane 06 wayfinding is now mirrored with a second project-owned non-blocking sign. No solid geometry, breaker route, objective trigger, Overtime timing or boss-wave timing changed.
- The new Windows candidate verifies its bundled game/project files first, then obtains pinned GZDoom/Freedoom runtime files only from official upstream releases; it does not silently bundle runtime EXE/WAD files or require Python on the player's PC.
- `docs/PACKAGING.md` and README now distinguish the development ZIP, the verified non-public release candidate and the still-open truly self-contained legal-content package gate.
- Demo Release readiness raised from **50.0%** to **60.0%** only for the implemented/testable portable Windows release-package milestone. Weighted project progress is now **84.75%**, displayed as **84.8%**; no public demo or GitHub Release was created.

### Validation
- The combat-readability contract validates source placement, packaged actor behavior and generated MAP01 `TEXTMAP` while preserving existing layout/pacing/Overtime gates.
- The release-candidate package contract recomputes its internal manifest hashes/sizes and outer ZIP SHA-256, rejects source/runtime leakage, checks one-click launch ordering and verifies runtime pins against `runtime-lock.json`.
- Windows CI additionally extracts the candidate and runs `tools/verify_player_package.ps1`; existing pinned-GZDoom parser/runtime and two-process save/load gates remain in force.

## 0.28.0-dev — 2026-09-18

### Added
- Clearance-aware `game/ZSCRIPT_CLOCKOUT` layer for the Closing Time post-boss escape, including the Overtime hazard lifecycle and one-shot front-lane clock-out guide spawner.
- Deterministic `tools/generate_clockout_assets.py` generator for the project-owned `CLOCK OUT` guide sprite.
- `tools/test_post_boss_clockout_polish_contract.py` with source, generated-asset, map and packaged-PK3 coverage, wired into GitHub Actions.

### Changed
- Closing Time Overtime environmental hazard anchors moved from an uninterruptible DECORATE state sequence to ZScript while preserving the exact authored `90 / 135 / 180 / 212 / 244 / 270` second opening schedule and 20-second Hell Rush cadence.
- Earning supervisor clearance now retires all remaining Overtime hazard anchors, matching the existing post-boss reinforcement cutoff so no fresh electrical trap appears during the deliberate return-to-checkout leg.
- Supervisor clearance now reveals one original non-blocking `CLOCK OUT` guide at the front-lane approach; the existing physical checkout completion trigger and exit logic are unchanged.
- Vertical Slice progress raised from **94%** to **95%** for this implemented/testable escape-readability milestone. Demo Release readiness remains **50.0%** because target-Windows interactive sign-off is still open. Weighted project progress is now **82.75%**, displayed as **82.8%**.

### Validation
- The Overtime contract now verifies the migrated schedule and clearance retirement behavior, while the dedicated post-boss contract verifies generated art, actor registration, single authored placement and packaged PK3/MAP01 contents. Pinned-GZDoom parser/runtime jobs remain the engine-level gate.

## 0.27.0-dev — 2026-09-18

### Added
- `docs/PERFORMANCE.md` documenting the conservative script-overhead hardening pass, preserved gameplay timing and the remaining target-Windows real-hardware sign-off.
- `tools/test_performance_contract.py` with source and packaged-PK3 coverage for sparse watcher polling, watcher retirement, unchanged authored encounter cadence and CI wiring.

### Changed
- Slow-changing objective/reinforcement watcher actors now sample their gates every 7 tics instead of every tic; the Night Manager response watcher samples every 4 tics to keep its authored `15 / 34 / 54 / 76` second sequence tight.
- One-shot manager/cache/shutter watchers destroy themselves after completing their job, while Overtime/boss-wave watchers retire after supervisor clearance instead of remaining idle thinkers.
- The existing Overtime reinforcement cadence remains `55 / 38 / 25` seconds by stage; the pass reduces repeated script polling without inventing an FPS uplift or changing combat rules.
- Demo Release readiness raised from **40.0%** to **50.0%** only after the implemented/testable performance pass; weighted project progress is now **82.35%**, displayed as **82.4%**. Interactive target-Windows save/load, physical-controller, balance/polish and real-hardware performance sanity remain release sign-off gates.

### Validation
- The performance contract models one instance of each hardened watcher and requires at least an 80% reduction in gate-check frequency versus per-tic polling, while pinned-GZDoom parser/runtime jobs remain the engine-level safety net. No CI FPS target is claimed.

## 0.26.0-dev — 2026-09-18

### Added
- Dedicated **CHECKOUT OF HELL Controller** menu in both full and simple GZDoom options, exposing remappable core gameplay actions plus direct links to engine device/stick and full-binding screens.
- Restrained GZDoom haptic mappings for the Emergency Mop, Receipt Ripper, Price-Gun SMG and Turbo Can Launcher using built-in rumble profiles only on player weapon cues.
- `docs/CONTROLLER.md` with the engine-default gamepad baseline, setup path, haptic policy and explicit target-Windows hardware sign-off requirement.
- `tools/test_controller_support_contract.py` with source and packaged-PK3 coverage, wired into GitHub Actions.

### Changed
- Controller support relies on standard GZDoom actions and never overwrites existing player bindings or hard-codes a private physical-button layout.
- Enemy, ambient, alarm and Overtime sounds remain unmapped to rumble to avoid continuous vibration during pressure-heavy encounters.
- Demo Release readiness raised from **30.0%** to **40.0%** only after the implemented/testable controller pass; weighted project progress is now **80.35%**, displayed as **80.4%**. A real-controller target-Windows playtest, Closing Time polish/sign-off and the performance pass remain open before any public demo.

## 0.25.0-dev — 2026-09-17

### Added
- Player-local `Focus HUD` accessibility option with redundant text for objective, breaker/memo progress and Overtime pressure.
- Player-local `Large warnings` accessibility option for critical health, Overtime and Hell Rush states.
- Dedicated **CHECKOUT OF HELL Accessibility** entries in both full and simple GZDoom options menus.
- `docs/ACCESSIBILITY.md` and `tools/test_accessibility_contract.py`, including packaged-PK3 regression coverage and CI execution.

### Changed
- Failing fluorescent props keep the haunted-store effect but use a slower 70/12/18/12 tic cycle instead of rapid two-tic flash cuts.
- Accessibility rendering lives in a separate event handler so the serialized `CheckoutShiftDirector` save/load state remains untouched.
- Build packaging now includes `CVARINFO`, `MENUDEF` and the accessibility ZScript layer in the generated PK3.
- Demo Release readiness raised from **20.0%** to **30.0%** only after the implemented/testable accessibility pass; weighted project progress is now **78.35%**, displayed as **78.4%**. Controller, performance and target-Windows interactive sign-off remain open.

## 0.24.0-dev — 2026-09-17

### Added
- Real two-process pinned-GZDoom save → process exit → load validation in CI under Xvfb/Mesa software rendering.
- Official-source Linux runtime resolver for the exact locked GZDoom release plus official Freedoom release, including Freedoom SHA-256 verification against the upstream checksum asset.
- `tools/gzdoom_save_load_smoke_linux.py`, which authors `CheckoutFuse 2/3` and `CorporateMemo 2/3` state in live MAP01, writes a real `.zds`, starts a second engine process and verifies both counters survive restore.
- `tools/test_gzdoom_save_load_smoke_contract.py`, protecting runtime-lock use, process-boundary behavior, save-file sanity checks and CI wiring.
- SWIR Progress SVG PRO assets: `assets/readme/progress-card.svg`, `assets/readme/progress-mini.svg` and reusable `assets/readme/progress-template.svg`.
- `tools/generate_progress_svgs.py`, a deterministic generator/check that reads the authoritative ROADMAP phase progress and weights, verifies README/ROADMAP agreement, validates bounded SVG geometry/XML and self-tests zero/partial/complete/N/A cases.
- GitHub Actions freshness enforcement for the generated progress assets.

### Fixed
- Generated embedded UDMF WADs now include canonical `MAPxx -> TEXTMAP -> ENDMAP` markers so GZDoom registers MAP01/MAP02 as real maps at runtime.
- Runtime-only ZScript issues exposed by the live pinned-engine pass: UI-scope helper declarations, `Level.ExitLevel`, `String.Length()` and terminated state-frame statements.
- HUD runtime scope no longer calls play-scoped overtime helpers from `RenderOverlay`.

### Changed
- The Windows save/load helper now has bounded polling, explicit engine logs, hard process cleanup and stronger serialized-state checks for normal target-machine validation.
- CI retains pinned Windows parser/startup validation and adds the real same-version two-process runtime round-trip on Linux because the hosted Windows runner does not expose a suitable interactive GZDoom graphics context.
- README/ROADMAP progress raised to **76%** and Vertical Slice progress to **94%** for the now-green end-to-end runtime serialization milestone. A final interactive target-Windows playtest/save-load confirmation remains required before demo sign-off.
- ROADMAP now documents the project-level weighted roll-up explicitly: Foundation 10%, Playable Prototype 25%, Vertical Slice 40%, Demo Release 20% and Full Game 5%. The unchanged milestone state computes to **76.35%**, displayed as **76.4%**; Demo Release readiness remains a separate **20.0%** gate.
- README now embeds the generated SWIR progress card near project status while ROADMAP embeds the compact companion. This documentation rollout does not increase gameplay completion and does not create a release/version bump.

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
- Supervisor clearance is written to player inventory on the same tic as a Night Manager/RegionalManager death and can be used to recover cleared state from older development saves.

### Changed
- README/ROADMAP progress raised to 70% and Vertical Slice progress to 85% for the implemented/testable save-state hardening milestone. Full interactive Windows save → quit → load validation remains intentionally open before demo readiness.

## 0.19.0-dev — 2026-09-17

### Added
- Three authored MAPINFO difficulties: forgiving `Closing Crew`, default `Graveyard Shift`, and confirmation-gated `Corporate Hell`.
- `tools/test_difficulty_modes_contract.py`, validating skill ordering, exact combat/resource multipliers, readability safeguards and packaged PK3 wiring.

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
- Project progress reached 66%.

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
