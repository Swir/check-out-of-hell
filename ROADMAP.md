# ROADMAP — CHECKOUT OF HELL
<!-- SWIR-PROGRESS-SVG-PRO:v1 -->

**Overall progress:** ` 86.8%`

**Measured scope:** Implemented/testable project milestones  
**Progress status:** HARDENING

<img width="100%" src="assets/readme/progress-mini.svg" alt="CHECKOUT OF HELL project progress — 86.8% implemented/testable; demo release readiness tracked separately" />

**Progress fallback:** **86.8%** implemented/testable project progress across **5 weighted roadmap phases**. **Demo Release readiness: 70.0%**, tracked separately.

The percentage reflects implemented/testable milestones, not ideas.

### Progress model

Project completion is a weighted roll-up of the verified phase percentages in the phase headings below. The generator reads those headings and these phase weights directly from this file; there is no second progress ledger. Demo Release readiness stays a separate phase/gate and is never substituted for overall project completion.

<!-- SWIR-PROGRESS-WEIGHTS:BEGIN -->
| Phase | Project weight |
| --- | ---: |
| Foundation | 10% |
| Playable Prototype | 25% |
| Vertical Slice | 40% |
| Demo Release | 20% |
| Full Game | 5% |
<!-- SWIR-PROGRESS-WEIGHTS:END -->

Current weighted calculation: `(100 × 10%) + (99 × 25%) + (95 × 40%) + (70 × 20%) + (0 × 5%) = 86.75%`, displayed as **86.8%**. Geometry uses the unrounded `86.75%` fraction.

## Phase 0 — Foundation — 100%
- [x] Project identity and concept
- [x] Legal/open development asset policy
- [x] Build system for PK3
- [x] Generated UDMF maps
- [x] Windows development launcher
- [x] Smoke-test script
- [x] GitHub repository created
- [x] GitHub Actions build workflow
- [x] First successful CI artifact verified
- [x] Pinned runtime lock file
- [x] One-click automatic GZDoom/Freedoom bootstrap from official sources
- [x] Automatic portable Python fallback for source builds
- [x] Third-party runtime/license documentation

## Phase 1 — Playable Prototype — 99%
- [x] Emergency Mop
- [x] Receipt Ripper
- [x] Price-Gun SMG
- [x] Turbo Can Launcher
- [x] Angry Self-Checkout
- [x] Cart of Doom
- [x] Night Manager mini-boss
- [x] Security Price Scanner
- [x] Possessed Pallet Jack
- [x] Regional Manager prototype boss
- [x] MAP01 structured objective prototype with separated breaker routes and a power-gated supervisor
- [x] MAP02 Warehouse 13.5 objective/combat sandbox
- [x] Three-breaker + supervisor-clear objective loop
- [x] Overtime escalation prototype with timed reinforcements
- [x] Prototype shift/objective HUD
- [x] Runtime parser/startup test on Windows with current pinned GZDoom
- [x] Power-gated optional Staff Only side route and reward
- [x] Per-breaker power restoration feedback
- [x] Staged Night Manager arena reinforcement sequence
- [x] Physical return-to-checkout clock-out objective after supervisor clearance
- [x] First original supermarket surface pack for Closing Time
- [x] Original objective pickup + Staff Only shutter sprites
- [x] Original shift interaction/PA sound cues wired into gameplay
- [x] Deterministic stdlib-only original asset generator + CI contract
- [x] Emergency Mop original first-person sprite set + swing cue
- [x] Night Manager original sprite set + original memo projectile + combat cues
- [x] Receipt Ripper original pickup/view sprite set + fire/cycle cues
- [x] Angry Self-Checkout original sprite set + hostile receipt projectile + combat cues
- [x] Price-Gun SMG + Turbo Can Launcher original sprite/audio pass
- [x] Security Price Scanner original sprite/projectile/audio pass
- [x] Cart of Doom original charge/pain/death sprite + audio pass
- [x] Possessed Pallet Jack original fork-lunge/pain/death sprite + audio pass
- [x] Regional Manager original boss sprite/behavior/audio pass
- [x] HUD readability pass with Overtime countdown, power cells and optional-route cue
- [x] Three-memo optional Corporate Compliance scavenger route in Closing Time
- [x] Overtime environmental warning/trap layer with stage-matched escalation
- [x] Proper final custom HUD with objective hierarchy, Overtime pressure, worker condition and signature-ammo reserves
- [x] Closing Time department signage, safe retail clutter, flickering ceiling fixtures and optional Emergency Break Snack rewards
- [x] Full original combat/weapon sound set polish with deterministic runtime cue variation
- [x] Closing Time supervisor pacing pass with a full-power recovery cache, widened reinforcement cadence and post-clear reinforcement cutoff
- [x] Three authored difficulty modes with regression coverage and pinned-engine parser validation
- [x] Department-local breaker/supervisor objective reset without clobbering save-restored shift state
- [x] Closing Time side-route secret pass with three useful workplace-comedy resource stashes and dedicated regression coverage
- [ ] First fully decorated/polished level

## Phase 2 — Vertical Slice — 95%
- [x] Level concepts documented
- [x] Core shift objective loop implemented
- [x] Overtime pressure system implemented
- [x] First optional powered secret/reward route implemented and regression-tested
- [x] Closing Time boss encounter pacing + post-boss escape/clock-out route implemented
- [x] Closing Time first original visual/audio atmosphere pass implemented and contract-tested
- [x] Signature Emergency Mop + Night Manager combat presentation implemented and engine-validated
- [x] Receipt Ripper + Angry Self-Checkout signature combat presentation implemented and contract-tested
- [x] Price-Gun SMG + Turbo Can Launcher weapon presentation and Security Price Scanner combat presentation implemented and contract-tested
- [x] Cart of Doom + Possessed Pallet Jack original combat presentation implemented with dedicated CI contract
- [x] Regional Manager original two-phase behavior/art/audio implemented with dedicated CI contract
- [x] Warehouse 13.5 uses project-owned retail/loading-bay presentation and a contract-tested breakers → freight-lift override → Regional Manager objective gate
- [x] Warehouse 13.5 optional damaged-goods cage uses breakable project-owned stock piles to trade ammunition for useful supplies without hiding mandatory progression
- [x] Closing Time HUD readability + optional Corporate Memo joke route implemented with a dedicated CI contract
- [x] Closing Time Overtime escalation now adds readable warning alarms and timed electrical floor hazards with a dedicated CI contract
- [x] Final-layout night-shift HUD presents objective/route hierarchy, 06:00 target, Overtime pressure, health and weapon reserves without color-only state cues
- [x] Closing Time environment dressing adds readable department identity, off-route clutter, ceiling flicker and two optional useful joke rewards without blocking combat lanes
- [x] Signature combat audio uses project-owned randomized cue families with deterministic generation, PCM/headroom checks and runtime parser coverage
- [x] Closing Time full-power pre-boss recovery and post-supervisor reinforcement cutoff implemented with dedicated CI coverage
- [x] Save-state hardening preserves serialized shift-director state and resets department-local objective tokens only on fresh map loads
- [x] Closing Time post-supervisor escape polish retires fresh Overtime floor hazards and reveals an original front-lane CLOCK OUT guide without moving the physical completion trigger
- [ ] Level 01: Closing Time — polished
- [ ] Level 02: Warehouse 13.5 — polished
- [x] Level 03: Frozen Foods
- [x] Boss: The Regional Manager — original behavior/art
- [x] Secrets and joke interactions — full Closing Time level pass
- [x] Difficulty modes
- [x] Original soundtrack for every currently playable department, generated deterministically and regression-tested
- [x] End-to-end runtime save/load validation with a real two-process pinned-GZDoom round-trip; target-Windows interactive confirmation remains a demo sign-off task

## Phase 3 — Demo Release — 70%
- [x] Automatic first-run dependency bootstrap design implemented
- [x] Portable Windows development artifact builder verified in CI
- [x] Installer/portable Windows release package — verified non-public release-candidate ZIP with local SHA-256 manifest and Windows integrity check
- [x] Standalone legal content package — content-only RC with exact source binding, SHA-256 manifest, MIT/BSD notices and verified byte identity with the Windows RC payload
- [x] Controller support pass
- [x] Accessibility options
- [x] Performance pass
- [ ] Release notes
- [ ] GitHub Release

**Release rule:** a normal Windows player must not need to search for dependencies manually. A demo release must either contain every legally redistributable required runtime file or automatically obtain missing redistributable dependencies from official upstream sources on first run.

**Current demo-readiness gate:** complete the interactive target-Windows sign-off documented in [`docs/WINDOWS_PLAYTEST.md`](docs/WINDOWS_PLAYTEST.md): full Closing Time runs on all three authored difficulties, manual save/quit/load confirmation, physical-controller confirmation, final balance/polish judgment and a real-hardware Overtime/boss performance sanity check before any public demo is published. The harness first validates the exact extracted RC package/runtime/save-load chain and records evidence, but it cannot replace the human gameplay confirmations. A completed `PASS` evidence directory must also pass the independent `tools/verify_windows_signoff_evidence.py` consistency verifier against the exact candidate commit before it is accepted as release-gate evidence. The verified Windows RC and standalone legal-content RC do not replace the required human sign-off or release notes; GZDoom remains the pinned official-source first-run bootstrap so players never have to hunt for it manually.

## Phase 4 — Full Game — 0%
- [ ] Full campaign
- [ ] More departments / biomes
- [ ] More bosses
- [ ] Achievements
- [ ] Co-op investigation
- [ ] Localization

**Implemented evidence without milestone closure:** `MAP04 — Electronics` and `MAP05 — Customer Service` now exist as playable development departments with their own objective/hazard contracts. Phase 4 intentionally remains **0%** because two first-pass departments do not complete the broader `More departments / biomes` milestone or any other Full Game checklist item.
