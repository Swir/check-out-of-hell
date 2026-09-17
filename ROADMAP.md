# ROADMAP — CHECKOUT OF HELL

**Overall progress:** `████████░░ 76%`

The percentage reflects implemented/testable milestones, not ideas.

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
- [x] MAP02 combat sandbox
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

## Phase 2 — Vertical Slice — 94%
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
- [x] Warehouse 13.5 uses project-owned retail surfaces and power-gates Regional Manager behind all three breakers
- [x] Closing Time HUD readability + optional Corporate Memo joke route implemented with a dedicated CI contract
- [x] Closing Time Overtime escalation now adds readable warning alarms and timed electrical floor hazards with a dedicated CI contract
- [x] Final-layout night-shift HUD presents objective/route hierarchy, 06:00 target, Overtime pressure, health and weapon reserves without color-only state cues
- [x] Closing Time environment dressing adds readable department identity, off-route clutter, ceiling flicker and two optional useful joke rewards without blocking combat lanes
- [x] Signature combat audio uses project-owned randomized cue families with deterministic generation, PCM/headroom checks and runtime parser coverage
- [x] Closing Time full-power pre-boss recovery and post-supervisor reinforcement cutoff implemented with dedicated CI coverage
- [x] Save-state hardening preserves serialized shift-director state and resets department-local objective tokens only on fresh map loads
- [ ] Level 01: Closing Time — polished
- [ ] Level 02: Warehouse 13.5 — polished
- [ ] Level 03: Frozen Foods
- [x] Boss: The Regional Manager — original behavior/art
- [x] Secrets and joke interactions — full Closing Time level pass
- [x] Difficulty modes
- [x] Original soundtrack for every currently playable department, generated deterministically and regression-tested
- [x] End-to-end runtime save/load validation with a real two-process pinned-GZDoom round-trip; target-Windows interactive confirmation remains a demo sign-off task

## Phase 3 — Demo Release — 20%
- [x] Automatic first-run dependency bootstrap design implemented
- [x] Portable Windows development artifact builder verified in CI
- [ ] Installer/portable Windows release package
- [ ] Standalone legal content package
- [ ] Controller support pass
- [ ] Accessibility options
- [ ] Performance pass
- [ ] Release notes
- [ ] GitHub Release

**Release rule:** a normal Windows player must not need to search for dependencies manually. A demo release must either contain every legally redistributable required runtime file or automatically obtain missing redistributable dependencies from official upstream sources on first run.

**Current demo-readiness gate:** finish an interactive target-Windows playtest of Closing Time, including save/load confirmation, balance/polish sign-off, and the remaining controller/accessibility/performance passes before any public demo is published.

## Phase 4 — Full Game — 0%
- [ ] Full campaign
- [ ] More departments / biomes
- [ ] More bosses
- [ ] Achievements
- [ ] Co-op investigation
- [ ] Localization
