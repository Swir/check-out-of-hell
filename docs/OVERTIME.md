# Overtime System

Overtime is CHECKOUT OF HELL's first signature systemic mechanic. It punishes lingering without turning every encounter into an endless horde mode.

## Prototype contract

The current implementation uses invisible map-placed director actors that advance through deterministic timed stages and spawn additional hostile store equipment around a safe central director point.

### MAP01 — Closing Time

- 00:30 — two **Carts of Doom** enter the shift.
- 01:00 — one **Security Price Scanner** and one **Possessed Pallet Jack** join.
- 01:30 — the **Night Manager** is added.
- After escalation — a Cart + Pallet Jack pressure pair is added every 20 seconds.

### MAP02 — Warehouse 13.5

Warehouse pressure starts earlier and favors machinery:

- 00:20 — two Carts of Doom.
- 00:40 — two Possessed Pallet Jacks.
- 01:00 — two Security Price Scanners.
- After escalation — a Cart + Pallet Jack pressure pair is added every 15 seconds.

## Design rules

1. **Overtime must create urgency, not grind.** Objectives should let a skilled player leave before late pressure becomes overwhelming.
2. **Escalation must be readable.** Future art/audio passes should add clear alarm, lighting and HUD feedback before a new stage activates.
3. **Maps own their pacing.** Different departments may use different director variants instead of one global timer.
4. **No invisible unavoidable damage.** Overtime creates threats the player can see, dodge and kill.
5. **Performance is bounded by encounter design.** Recurring waves must be tuned together with cleanup, corpse settings and level duration before demo release.
6. **Difficulty should eventually scale timings/counts**, not simply multiply enemy health.

## Next implementation slice

Add the first real shift objective to `MAP01` (restore a breaker / obtain access / reach the checkout exit), then connect objective progress to visible Overtime feedback so the player understands both what to do and why staying too long is dangerous.
