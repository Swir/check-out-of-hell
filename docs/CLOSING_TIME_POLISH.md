# Closing Time polish sign-off candidate

**Status: SIGN-OFF CANDIDATE** — automated prerequisites are being hardened, but the canonical `First fully decorated/polished level` and `Level 01: Closing Time — polished` roadmap items remain open until real target-Windows human evidence passes for the exact candidate commit.

This document is the acceptance bridge between the existing automated Closing Time contracts and the manual demo-quality judgment. It does not change project progress, authorize a release or replace `docs/WINDOWS_PLAYTEST.md`.

## Acceptance matrix

| Area | Automated candidate evidence | Manual evidence required before roadmap closure |
| --- | --- | --- |
| Environment / art consistency | Project-owned supermarket surfaces, props and deterministic route-sign assets; built PK3 parity is checked. | Confirm the level reads as one coherent supermarket night shift rather than disconnected prototype pieces. |
| Combat readability | The full authored `x=-300..300` front-to-rear corridor is protected from initial hostiles; Closing Crew uses five initial threats while Normal/Hard retain eight with the three extra actors staged behind east-side shelf geometry and sight-gated with the UDMF ambush flag so opening gunfire cannot wake them through shelf occlusion. Timed Overtime floor arcs keep their full 72-unit damage radius outside that corridor and now expose at least one full second of local visual/audio telegraph before damage. | Confirm enemies, warnings, floor hazards and firefights remain readable on Closing Crew, Graveyard Shift and Corporate Hell. |
| Objective / route readability | Each breaker route now has a two-stage visual chain: front-half orientation plus a destination confirmation sign near the actual repair point; Lane 06 and post-boss CLOCK OUT guidance remain protected. | Complete breaker -> Night Manager -> physical clock-out on all three authored difficulties without route confusion or progression blockers. |
| Lighting / atmosphere | Six ceiling-mounted fixtures use three deterministic staggered fluorescent phases with the same slow reduced-flash cycle; the contract proves there is no all-fixture dark interval and route signs remain text-readable without relying on color alone. | Confirm the creepy empty-store atmosphere is strong without warning/hazard information disappearing into darkness or flicker. |
| Clutter / visual hierarchy | Existing low-profile cone/box clutter budget stays fixed; route signs are `+NOBLOCKMAP`, reuse the established supermarket visual family, remain outside the permanent center corridor and now mirror Overtime lane warnings on both outer sides. | Confirm the floor looks dressed but not visually noisy and that movement/combat lanes remain clean. |
| Gameplay pacing / balance | Full-power recovery cache, spaced Night Manager response cadence, post-clear pressure cutoff, warned side-lane Overtime lock, staged Normal/Hard second-ring threats and side-lane floor-arc placement remain contract-tested without changing the authored hazard schedule. | Confirm each difficulty fulfils its intended role and Overtime/Night Manager pressure feels fair enough for a public demo. |
| Target-Windows human evidence | The sign-off flows record per-difficulty completion/readability/balance, manual save/quit/load, controller/haptics, real-hardware performance and `final_polish_signoff`; the independent verifier binds PASS evidence to the exact commit. | A real Windows run must produce `PASS`, then the evidence must independently verify against the exact candidate SHA. |

## Candidate route-sign package

The final-polish candidate uses **eight non-blocking sign instances from four deterministic project-owned designs** in `game/MAP01_POLISH.udmf`:

- `FUSE LEFT` appears once on the front-half approach and once beside the left breaker as destination confirmation;
- `FUSE RIGHT` appears once on the front-half approach and once beside the right breaker as destination confirmation;
- `FUSE STAFF` appears once on the rear-route approach and once at the left edge of the rear breaker lane as destination confirmation;
- `OVERTIME LANE` appears once on each outer side lane so the hazard role is readable before the five-second left-lane shutter event or the later side-lane floor arcs peak.

The duplicate breaker signs deliberately reuse the same generated art instead of adding a second signage style. The mirrored Overtime signs reuse the same project-owned warning design so both outer lanes read as intentional pressure space without adding a new visual language. All eight instances are non-blocking, non-gravity visual actors and remain outside the permanent center corridor. They do not grant inventory, move objectives, alter enemy counts, change hazard timers or modify the physical clock-out trigger.

## Staggered fluorescent phases

The six project-owned failing fluorescent fixtures are now split evenly across three deterministic timing phases. Every phase keeps the same slow `70 / 12 / 18 / 12` visible/dim cadence; phase B and phase C spend an additional visible `24` and `48` tics before entering that cycle. This keeps the unstable night-shift ceiling mood while preventing the entire sales floor from entering a dim frame at once.

`tools/test_closing_time_polish_gate.py` protects the exact route-sign instance positions/counts, the `2 / 2 / 2` fixture distribution, non-blocking actors, slow-state timings, unique editor numbers, built MAP01/PK3 parity and mathematically checks six full cycles for any synchronized all-fixture dark interval. The lighting pass changes presentation only: objective state, collision, combat spawns, hazard timing and the physical clock-out trigger are unchanged.

## Difficulty staging polish

Closing Crew keeps five initial signature threats so its first-room pressure is meaningfully lighter instead of relying only on global damage/resource multipliers. Its inner Self-Checkout flank now sits at `x=-360`, west of the authored shelf line and outside the full `x=-300..300` permanent combat/clock-out corridor, instead of occupying that corridor at `x=-220`. Graveyard Shift and Corporate Hell still use the full eight-threat footprint, but the three additional actors remain in a second east-side ring behind the authored shelf lines. Those three hard-mode additions also use the UDMF `ambush` flag, so front-lane weapon noise cannot wake them through the occluding shelves before visual contact; they reveal as player movement exposes the second ring. This preserves the harder-mode population while turning immediate spawn-side crossfire into a movement-driven escalation.

`tools/test_closing_time_combat_readability_contract.py` protects the `5 / 5 / 8 / 8 / 8` per-skill population, the full `x=-300..300` initial-hostile exclusion zone, exact easy/hard flank positions, required hard-only `ambush = true` sight-gating and built MAP01 parity. `tools/test_closing_time_polish_gate.py` independently enforces the same full-width hostile exclusion so route-sign and combat-readability definitions cannot drift apart again.

## Overtime corridor polish

Closing Time still uses exactly four authored timed Overtime floor-arc anchors and the existing `90 / 135 / 180 / 212 / 244 / 270` escalation timing remains unchanged. The rear pair sits at `x=-390` and `x=390`, so each arc's full **72-unit** damage radius stops outside the permanent `x=-300..300` navigation/combat/clock-out corridor. The front pair remains at `x=-510` and `x=510`; all four continue to retire after supervisor clearance.

Each damaging `OvertimeFloorArc` now spends **36 tics** (about **1.03 seconds**) in bright project-owned `OARC A/B` warning frames, with the Overtime alarm starting immediately, before the existing arc cue and `10` damage / `72` radius explosion. This is a local telegraph/readability change only: it does not change the spawner's authored world-time schedule, anchor count/positions, damage, radius, objective state or supervisor-clearance retirement.

The final-polish layer mirrors `OVERTIME LANE` warning signs at `x=-650` and `x=650`, both outside the permanent corridor. They are static non-blocking visual warnings only: the existing left-lane shutter remains the only authored lockdown, while the signs establish both outer lanes as escalation space before floor arcs appear.

`tools/test_overtime_hazard_contract.py` verifies the exact source positions, radius-to-corridor separation, at least **35 tics** of pre-damage floor-arc telegraph in both source and packaged DECORATE, and packaged MAP01 parity while preserving the authored hazard schedule. `tools/test_closing_time_polish_gate.py` separately locks the mirrored warning-sign count/positions and packaged MAP01 parity. This is a readability/fairness polish change only: it does not change the number of hazards, their world-time cadence, damage behavior, objective state, breaker routing, boss gates or the physical clock-out trigger.

## One-click exact-candidate evidence kit

CI builds `checkout-of-hell-closing-time-windows-signoff-kit` from the exact PR commit. Its embedded `CHECKOUT-OF-HELL-Windows-Portable-rc.zip` is SHA-256-bound to `SIGNOFF-CANDIDATE.json`, and the kit refuses to start human evidence if the RC package manifest does not identify the same clean source commit/branch.

A tester can extract the kit, connect the physical controller and double-click `RUN-SIGNOFF.bat`; no Git clone, local build, Python installation, runtime search or WAD hunt is required. After the three gameplay passes and explicit Closing Time polish review, the same flow runs independent evidence verification against that exact candidate. `VERIFY-EVIDENCE.bat` remains available for a later re-check. The kit never publishes a release. See `docs/WINDOWS_SIGNOFF_KIT.md`.

## Canonical closure rule

Do **not** check either Closing Time polish roadmap item merely because CI is green. Both may be closed only when:

1. the exact candidate commit passes the automated build/contracts and package parity checks;
2. either the exact-commit CI sign-off kit (`RUN-SIGNOFF.bat`) or the clean-checkout developer harness (`WINDOWS-DEMO-SIGNOFF.bat`) produces real target-Windows `PASS` evidence for that same commit;
3. the evidence includes successful runs on all three difficulties, readability/balance confirmations, physical-controller/haptics confirmation, real-hardware Overtime/Night Manager performance sanity and `final_polish_signoff = true`;
4. `verify_windows_signoff_evidence.py` (directly or through the kit's verification stage) accepts that evidence with the expected commit bound to the candidate SHA.

Until then, project progress remains **86.8%** (exact weighted **86.75%**) and Demo Release readiness remains **70.0%**. No public demo or GitHub Release is authorized by this candidate package.
