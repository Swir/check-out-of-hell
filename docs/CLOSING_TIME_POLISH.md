# Closing Time polish sign-off candidate

**Status: SIGN-OFF CANDIDATE** — automated prerequisites are being hardened, but the canonical `First fully decorated/polished level` and `Level 01: Closing Time — polished` roadmap items remain open until real target-Windows human evidence passes for the exact candidate commit.

This document is the acceptance bridge between the existing automated Closing Time contracts and the manual demo-quality judgment. It does not change project progress, authorize a release or replace `docs/WINDOWS_PLAYTEST.md`.

## Acceptance matrix

| Area | Automated candidate evidence | Manual evidence required before roadmap closure |
| --- | --- | --- |
| Environment / art consistency | Project-owned supermarket surfaces, props and deterministic route-sign assets; built PK3 parity is checked. | Confirm the level reads as one coherent supermarket night shift rather than disconnected prototype pieces. |
| Combat readability | Initial threats stay off the strongest front-to-rear navigation strip; management-response pressure flanks the rear approach. | Confirm enemies, warnings and firefights remain readable on Closing Crew, Graveyard Shift and Corporate Hell. |
| Objective / route readability | Three breaker routes now receive explicit non-blocking `FUSE LEFT`, `FUSE RIGHT` and `FUSE STAFF` visual hierarchy; Lane 06 and post-boss CLOCK OUT guidance remain protected. | Complete breaker -> Night Manager -> physical clock-out on all three authored difficulties without route confusion or progression blockers. |
| Lighting / atmosphere | Six ceiling-mounted fixtures use three deterministic staggered fluorescent phases with the same slow reduced-flash cycle; the contract proves there is no all-fixture dark interval and route signs remain text-readable without relying on color alone. | Confirm the creepy empty-store atmosphere is strong without warning/hazard information disappearing into darkness or flicker. |
| Clutter / visual hierarchy | Existing low-profile cone/box clutter budget stays fixed; new signs are `+NOBLOCKMAP` and remain outside the permanent center corridor. | Confirm the floor looks dressed but not visually noisy and that movement/combat lanes remain clean. |
| Gameplay pacing / balance | Full-power recovery cache, spaced Night Manager response cadence, post-clear pressure cutoff and warned side-lane Overtime lock remain contract-tested. | Confirm each difficulty fulfils its intended role and Overtime/Night Manager pressure feels fair enough for a public demo. |
| Target-Windows human evidence | The existing sign-off harness records per-difficulty completion/readability/balance, manual save/quit/load, controller/haptics, real-hardware performance and `final_polish_signoff`; the independent verifier binds PASS evidence to the exact commit. | A real Windows run must produce `PASS`, then `tools/verify_windows_signoff_evidence.py <evidence-dir> --expected-commit <candidate-sha>` must also pass. |

## Candidate route-sign package

The final-polish candidate adds four deterministic project-owned signs in `game/MAP01_POLISH.udmf`:

- `FUSE LEFT` and `FUSE RIGHT` frame the two side-department routes from the front half of the store;
- `FUSE STAFF` identifies the rear staff-zone breaker detour without occupying the center corridor;
- `OVERTIME LANE` makes the authored deep-Overtime side-lane pressure legible before the five-second shutter event can occur.

All four signs are non-blocking, non-gravity visual actors. They do not grant inventory, move objectives, alter enemy counts, change hazard timers or modify the physical clock-out trigger.

## Staggered fluorescent phases

The six project-owned failing fluorescent fixtures are now split evenly across three deterministic timing phases. Every phase keeps the same slow `70 / 12 / 18 / 12` visible/dim cadence; phase B and phase C spend an additional visible `24` and `48` tics before entering that cycle. This keeps the unstable night-shift ceiling mood while preventing the entire sales floor from entering a dim frame at once.

`tools/test_closing_time_polish_gate.py` protects the exact `2 / 2 / 2` fixture distribution, non-blocking actors, slow-state timings, unique editor numbers, built MAP01/PK3 parity and mathematically checks six full cycles for any synchronized all-fixture dark interval. The lighting pass changes presentation only: objective state, collision, combat spawns, hazard timing and the physical clock-out trigger are unchanged.

## Canonical closure rule

Do **not** check either Closing Time polish roadmap item merely because CI is green. Both may be closed only when:

1. the exact candidate commit passes the automated build/contracts and package parity checks;
2. `WINDOWS-DEMO-SIGNOFF.bat` produces real target-Windows `PASS` evidence on a clean checkout of that same commit;
3. the evidence includes successful runs on all three difficulties, readability/balance confirmations, physical-controller/haptics confirmation, real-hardware Overtime/Night Manager performance sanity and `final_polish_signoff = true`;
4. `verify_windows_signoff_evidence.py` accepts that evidence with `--expected-commit` bound to the candidate SHA.

Until then, project progress remains **86.8%** (exact weighted **86.75%**) and Demo Release readiness remains **70.0%**. No public demo or GitHub Release is authorized by this candidate package.
