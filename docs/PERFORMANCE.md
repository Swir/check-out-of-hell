# Performance Hardening

CHECKOUT OF HELL keeps its performance work deliberately conservative: reduce unnecessary script/thinker overhead without changing the authored combat rhythm, Overtime thresholds, boss-wave order, objective rules or visual readability.

## Current pass

The current hardening pass targets event/watch actors that previously evaluated their objective state every game tic even though their trigger conditions change only occasionally.

- `CheckoutOvertimeSpawner` now samples its inventory/stage gate every **7 tics** instead of every tic, while preserving the existing `55 / 38 / 25` second reinforcement cadence.
- `CheckoutManagerSpawner`, `CheckoutStaffShutter`, `CheckoutFullPowerCacheSpawner` and `CheckoutRegionalManagerSpawner` sample their objective gates every **7 tics**. At 35 tics per second, worst-case trigger latency stays below **0.2 seconds**.
- `CheckoutBossWaveSpawner` samples every **4 tics** because it owns the authored `15 / 34 / 54 / 76` second response sequence. The sequence and ordering are unchanged.
- One-shot watcher actors destroy themselves after their job is complete instead of remaining as idle thinkers for the rest of the department.
- Overtime and boss-wave reinforcement watchers also destroy themselves once supervisor clearance proves that fresh pressure must stop.
- The environmental Overtime hazard anchor is now clearance-aware ZScript rather than an uninterruptible DECORATE state loop. It keeps the same authored `90 / 135 / 180 / 212 / 244 / 270` second opening schedule and 20-second Hell Rush cadence, samples supervisor clearance sparsely, and retires after the Night Manager is down instead of continuing to create fresh traps during the clock-out leg.
- The post-boss clock-out guide watcher samples every **7 tics** and destroys itself immediately after spawning its one non-blocking guide.

This reduces repeated inventory/stage polling substantially per watcher while keeping the player-facing timing deterministic and readable.

## What this does not claim

This pass does **not** claim a specific FPS uplift, minimum hardware target or final Windows performance certification. Hosted CI hardware and software rendering are not representative enough for a truthful frame-rate promise.

The repository instead verifies the optimization structurally and continues to parse/run the package with the pinned GZDoom runtime. Final public-demo sign-off still requires an interactive target-Windows playtest that includes a performance sanity check during Overtime/Hell Rush, alongside controller, save/load and level-polish confirmation.

## Regression policy

`tools/test_performance_contract.py` protects the main performance-sensitive watcher behavior, while `tools/test_overtime_hazard_contract.py` and `tools/test_post_boss_clockout_polish_contract.py` protect the clearance-aware hazard/guide lifecycle. Together they check source and packaged PK3 content for:

- sparse watcher polling,
- self-destruction of completed one-shot watchers,
- supervisor-clear cleanup,
- unchanged Overtime reinforcement and environmental-hazard cadence,
- unchanged Night Manager wave thresholds,
- CI wiring for the relevant contracts.

The contracts intentionally avoid a noisy CI FPS threshold. If a future deterministic runtime benchmark becomes reliable across runners, it can supplement this gate rather than replacing target-machine playtesting.
