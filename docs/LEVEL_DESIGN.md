# Level Design Direction

## MAP01 — Closing Time
Purpose: first structured department flow, weapon onboarding and readable objective staging.

Current prototype includes:
- a larger supermarket floor than the original arena,
- front entrance spawn zone,
- internal aisle dividers and checkout-counter barriers,
- left, right and rear breaker routes,
- three Overtime reinforcement anchors spread across the floor,
- Security Price Scanner crossfire near the rear route,
- Night Manager spawned only after all three breakers are restored,
- two dedicated rear supervisor-response anchors that escalate through Self-Checkout, Cart, Scanner and Pallet Jack waves,
- contextual HUD task text that moves from power restoration to supervisor clearance and then a return to front checkout,
- a physical front checkout/timecard completion zone instead of automatic post-boss exit,
- short visible feedback after each breaker is restored,
- an optional rear-left Staff Only room with a physical security barrier,
- Staff Only access unlocking at `2/3` breakers instead of waiting for full power,
- an `Employee of the Month Stash` reward inside the optional room,
- no mandatory breaker inside the optional room, preserving route clarity,
- clearance-aware Overtime hazard anchors that stop creating fresh electrical hazards once the Night Manager is down,
- an original `CLOCK OUT` guide that appears near the front lanes only after supervisor clearance, pointing back toward the existing physical completion zone without changing the trigger,
- a conservative combat-readability pass that clears the front-to-rear center strip of initial hostile/reinforcement anchors, moves management-response spawns to the rear flanks and mirrors non-blocking Lane 06 wayfinding at the front approach.

The Staff Only room is deliberately a reward loop rather than a key hunt. Partial power gives the
player a useful side benefit before the main objective is complete, teaching that restoring store
systems can change the environment without making every side route mandatory.

The supervisor encounter is now a pressure sequence rather than one isolated monster spawn. Full
power activates two management-response anchors on opposite rear flanks. Their authored timing is
unchanged, but the spatial pass avoids spawning that sequence on the central supervisor sightline.
Once the Night Manager is defeated, surviving threats still matter on the run back to the registers,
but new management reinforcements and fresh Overtime floor hazards retire. The front-lane `CLOCK OUT`
guide then becomes visible, preserving tension while making the final workplace objective unambiguous.

The readability pass deliberately changes spawn placement and non-blocking wayfinding only. It does
not move solid checkout geometry, objective triggers, breaker routes or combat timing without actual
playtest evidence.

Remaining Closing Time polish:
- complete an interactive target-Windows full-level pass with manual save/load, physical-controller and real-hardware performance confirmation,
- finish balance/sign-off on all three difficulty modes using that real playtest evidence,
- change solid checkout cover or sightline geometry only where the playtest shows a readability or pacing problem,
- keep any additional lighting/geometry reactions subordinate to combat readability rather than adding decoration for its own sake.

## MAP02 — Warehouse 13.5
Purpose: heavier equipment pressure, a real loading-bay work task and the first boss-scale corporate escalation.

Current prototype includes:
- Security Price Scanners,
- Possessed Pallet Jacks,
- The Regional Manager prototype boss,
- access to Receipt Ripper, Price-Gun SMG and Turbo Can Launcher,
- three warehouse breakers that restore the loading-bay circuits,
- a project-owned `Freight Lift Override` that appears only after all three circuits are live,
- The Regional Manager held off-floor until the player deliberately engages that powered lift control,
- a deterministic four-second project-owned visual/audio Regional Manager arrival warning after the lift override before the boss enters the floor,
- warehouse-specific HUD/Focus HUD objective states for breakers, lift activation, Regional Management and the return-to-entry leg,
- project-owned freight signage, restock clutter, readable slow-failing lights and loading-bay dressing placed off the central objective/combat lane,
- an optional damaged-goods cage whose four project-owned shootable stock piles trade ammunition for a label stash and break snack without hiding mandatory progression,
- an optional full-power `Lockout/Tagout Permit` on the opposite rear side lane that isolates future Warehouse electrical floor arcs without disabling hostile Overtime reinforcements or management pressure,
- two authored deep-Overtime moving-pallet lanes on the outer warehouse routes; after at least two circuits are live and Overtime reaches stage 2, the west/east lanes arm on staggered `12 / 27` second starts, telegraph for two seconds and repeat on deterministic `30 / 22` second spacing while the central `x=-180..180` objective/clock-out corridor stays open,
- a ten-step west-wall Staff-Only Overstock Catwalk that creates an elevated optional route outside both moving-pallet lanes and the permanent central objective corridor,
- a hidden Staff Room threaded into the elevated route; its south floor entrance is sealed by one project-owned shootable stock pile, and breaking it creates a ground shortcut to optional health/label rewards without hiding any breaker, lift control, boss anchor or safety state,
- supervisor clearance retires future pallet launches, while Lockout/Tagout remains scoped to electrical floor arcs and never disables moving equipment,
- project-owned retail surfaces and an original department soundtrack.

The first Warehouse 13.5 objective sequence is now explicit: restore all three circuits, cross to the
rear loading bay, engage the freight-lift override, survive the Regional Manager response, then return
to the warehouse entry to finish the department. The lift control is separated from the boss spawn
anchor and now begins a full four-second project-owned visual/audio warning before Regional Management
materializes, so interacting with the objective cannot immediately overlap the player with the boss.
The existing rear-flank `12 / 30 / 52` second management-response cadence remains intact. Extra
loading-bay props stay non-blocking and deliberately avoid the central route so the level gains identity
without sacrificing readable combat.

A right-side damaged-goods nook adds the first breakable-stock tactical choice. Four solid, shootable
stock piles seal the opening; breaking any useful gap costs ammunition but opens access to optional
labels and health. The existing Security Price Scanner remains outside the cage approach, and no
breaker, lift control or boss anchor is inside the nook. The joke therefore changes resource routing
without becoming a key hunt or muddying the central lift/Regional Manager sightline.

The left-side Lockout/Tagout station adds a second workplace choice after full power. Taking the permit
retires only future Warehouse electrical floor arcs, representing a useful system repair rather than a
magic combat-off button. Ambient Overtime enemy reinforcements, the freight-lift objective, management
response waves, moving pallet traffic and The Regional Manager all remain active, so the player trades
a short detour for a safer floor while preserving the department's combat pressure.

Deep Overtime now adds predictable equipment movement instead of random lane punishment. Once at least
two warehouse circuits are live and Overtime reaches stage 2, the west and east outer lanes arm at
staggered `12 / 27` second offsets. Every Runaway Restock Pallet receives a full two-second warning,
then travels only along its authored Y-axis lane at `x=-300` or `x=300`. Stage 2 repeats every 30
seconds per lane and Hell Rush tightens that to 22 seconds. The permanent central `x=-180..180`
objective/clock-out corridor therefore never closes, and supervisor clearance retires an armed warning
or future launch before the return-to-entry leg.

The west-wall Overstock Catwalk turns the previously flat Warehouse into a deliberate vertical side
route without creating a second mandatory progression path. Ten authored bridge steps climb along the
wall outside both pallet lanes and the central corridor, letting the player reposition above equipment
pressure while keeping all breakers, the lift objective and Regional Management readable from the main
floor. The route uses only project-owned warehouse presentation and remains optional.

The hidden Staff Room gives that vertical route a useful workplace-comedy payoff and a two-way shortcut.
The elevated path reaches the room from above, while one familiar shootable stock pile seals its south
floor entrance. Breaking the barrier opens a ground shortcut and exposes optional health/label rewards.
No breaker, Freight Lift Override, boss anchor or Lockout/Tagout state lives inside the room, so the
secret changes routing and resource economy without becoming a key hunt or bypassing the department's
objective logic.

Remaining Warehouse 13.5 polish:
- complete an interactive target-machine balance/readability pass across all three authored difficulties, including the four-second boss handoff, pallet traffic and optional elevated/Staff Room routes,
- confirm manual save/quit/load, physical-controller behavior and real-hardware Overtime/boss performance as part of the shared target-Windows sign-off,
- change final encounter timing, cover or route geometry only where that interactive evidence identifies a real pacing/readability problem before calling the level polished.

## MAP03 — Frozen Foods
Purpose: first playable cold-storage department with readable aisle routing, refrigeration atmosphere and a breaker → compressor reset → management → clock-out loop.

Current prototype includes:
- four authored freezer-aisle blockers that create side routes while leaving a readable central service lane,
- two cold-chain breaker circuits distributed across opposite freezer routes,
- a project-owned rear `Cold-Chain Compressor Reset` that appears only after both breakers are restored and supplies the final `3/3` power step,
- a three-second telegraphed right-flank response after each breaker repair: Security Price Scanner first, then Cart of Doom, with no third instant enemy on the compressor transition,
- Angry Self-Checkout, Security Price Scanner, Cart of Doom and Possessed Pallet Jack pressure placed off the entry centerline,
- the existing power-gated Night Manager as the current department supervisor rather than inventing an unvalidated new boss,
- a deterministic management-response anchor after full power,
- a full-power recovery cache before the supervisor fight,
- four telegraphed environmental Overtime hazard anchors kept away from the entry/clock-out approach,
- one full-power compressor-surge anchor on the right service flank that activates only once Overtime is live, waits 18 seconds before its first burst, telegraphs for two seconds and repeats at deterministic `34 / 26 / 20` second spacing as pressure rises,
- one optional opposite-side `Compressor Surge Isolation` control that suppresses only future refrigeration bursts while hostile Overtime and management remain active,
- one optional rear-left **Recall Freezer** enclosed by project-owned shelf geometry and sealed by a shootable `Recall-Hold Stock Pile`; opening it yields a compliance memo, useful multi-ammo stash and contained Angry Self-Checkout without moving any breaker, compressor, management or Overtime anchor into the secret,
- paired project-owned `FROZEN FOODS` signs, generated compressor-reset/isolation/burst sprites, safe restock/cone clutter, slow-failing lights and optional Emergency Break Snacks,
- three department-local Corporate Compliance Memos as an optional exploration route,
- a map-local initializer that clears only memo progress carried from the previous department and then destroys itself so normal save/restore inside MAP03 preserves newly collected memos,
- a save-aware surge-state handler that clears isolation only on fresh transitions so a saved safety choice remains stable,
- an original deterministic department track, **Frozen Foods — Compressor Choir**,
- a post-clear `CLOCK OUT` guide and the existing physical front completion rule.

The Frozen Foods objective sequence is now deliberately more department-specific without adding a
random movement gimmick: restore the left/right cold-chain breakers, cross to the rear service position,
perform the compressor reset, use the full-power recovery option if needed, survive the Night Manager
plus authored response pressure, then return to the entry and clock out. The compressor control grants
the same authoritative final power token that hardened cache/boss/wave systems already use, so the new
work task changes route language without forking core progression state.

The first two breaker repairs trigger a readable side-lane answer only after a three-second warning.
The final compressor action deliberately does not spawn another instant side enemy; full power instead
hands pressure to the Night Manager and existing management-response sequence. If Overtime is already
active, the powered compressor can begin a separate right-flank refrigeration surge only after an
18-second grace period. Every burst uses the same visible/audio warning language for two full seconds,
and the authored spacing tightens with Overtime stage rather than randomizing the player's safe route.

The opposite-side isolation station is a deliberate optional work task rather than a combat-off switch.
Taking it retires future compressor bursts only. Ambient Overtime enemies, standard electrical hazard
anchors, management waves and the Night Manager remain active. Supervisor clearance also cancels any
armed compressor burst so the post-boss return remains readable. This creates a real workplace choice:
spend movement/time on safety or accept a predictable side-lane hazard while fighting management.

The rear-left Recall Freezer adds a second kind of optional decision without touching the cold-chain
objective. One shootable project-owned stock pile seals a 64-unit shelf doorway; spending ammunition to
open it exposes a Corporate Compliance Memo, a useful multi-ammo stash and one contained Angry
Self-Checkout. Breakers, the compressor reset, recovery/safety controls, management anchors and Overtime
hazards remain outside, so the secret increases cold-storage-specific exploration and encounter variety
without becoming a key hunt or obscuring the central service lane.

This is playable vertical-slice content, not a claim that Frozen Foods is a polished final campaign
level. Future passes should deepen encounter variety only after the current route survives real gameplay
validation; additional refrigeration gimmicks must never become random punishment or obscure the central
service lane.

Remaining Frozen Foods polish:
- target-machine balance/readability playtesting across all three difficulty modes, including surge spacing, isolation-station placement and the Recall Freezer risk/reward loop,
- additional cold-storage encounter variation only where it remains readable around the two breaker routes and compressor task,
- final lighting/geometry polish after the objective route and refrigeration pressure survive real play.

## MAP04 — Electronics
Purpose: first playable showroom department with alternating display-wall sightlines, a physical network-recovery task and readable powered-hardware hazards.

Current prototype includes:
- four alternating solid display-wall rows that break long sightlines while preserving a clean central service lane,
- two opposite-side UPS/breaker repairs,
- a project-owned rear `Store Network Reboot` that appears only after both repairs and supplies the final authoritative `3/3` power step,
- a three-second telegraphed side response after each repair: Security Price Scanner first, then Angry Self-Checkout,
- initial Scanner, Self-Checkout, Cart and Pallet Jack pressure placed off the central entry/exit lane,
- a power-gated Night Manager plus the shared deterministic management-response anchor,
- a full-power recovery cache and three optional Corporate Compliance Memos,
- three standard outer-lane Overtime electrical hazard anchors plus one department-specific right-side demo-wall surge,
- a 16-second grace period before the first display surge, two-second warning before every burst and deterministic `32 / 24 / 18` second spacing as Overtime pressure rises,
- one optional opposite-side `Demo Wall Kill Switch` that suppresses only future display surges while hostile Overtime and management remain active,
- paired project-owned Electronics signs, generated network-reboot/kill-switch/surge sprites, safe clutter, slow-failing fixtures and optional Emergency Break Snacks,
- a one-shot entry initializer that clears carried memo/kill-switch state and then destroys itself so saves made after entry preserve local progress,
- the original deterministic **Electronics — Dead Pixel Choir** soundtrack,
- the existing post-clear non-blocking `CLOCK OUT` guide and physical front completion rule.

Electronics deliberately makes the useful workplace task the last power step rather than a cosmetic prop.
The player restores two display/UPS circuits, crosses to the rear service position, physically performs the
Store Network Reboot and only then reaches full power. That pickup grants the same `CheckoutFuse` token
consumed by the hardened full-power cache, supervisor and clock-out systems, avoiding a parallel progression
ledger. The final reboot itself does not spawn a third instant side-lane enemy; management becomes the next
clear pressure beat.

Once full power overlaps Overtime, one outer demo wall can begin faulting. Every burst is announced by the
same project-owned warning language for two seconds, and the first fault cannot occur until a 16-second grace
window has passed. The optional kill switch sits on the opposite side of the floor so choosing safety costs
movement without becoming mandatory. Taking it removes only this Electronics-specific fault source; ambient
Overtime enemies, shared electrical anchors and management continue normally.

This is playable development content, not a polished final campaign level. Future work should deepen showroom
secrets and diversify hardware encounters only after real play confirms that the alternating display walls
stay readable during Overtime and the Night Manager sequence.

Remaining Electronics polish:
- target-machine balance/readability playtesting across all three difficulty modes,
- stronger showroom secrets and useful joke interactions without hiding mandatory power work,
- final lighting/geometry and encounter polish after the current route survives real play.

## MAP05 — Customer Service
Purpose: a tighter complaint-desk department built around serpentine queue sightlines, a real refund-authorization task and escalating customer-pressure jokes that remain readable combat mechanics.

Current prototype includes:
- a long serpentine queue that shapes movement without blocking the central return lane,
- two mandatory service-desk circuits on opposite queue routes,
- a physical rear `Refund Authorization Terminal` that appears after both circuits are restored,
- a save-safe twelve-second Corporate verification hold instead of an instant third power token,
- an authored outer-queue audit sequence: Angry Self-Checkout at 2 seconds, warnings at 5 and 9 seconds, Security Price Scanner at 7 seconds and the Returns Policy Enforcer at 10 seconds,
- the final authoritative `CheckoutFuse 3/3` only at 12 seconds, keeping the shared Night Manager/full-power/clock-out gates authoritative,
- the **Returns Policy Enforcer** miniboss with 220 health, project-owned Self-Checkout presentation and a readable three-way Corporate Red Tape volley,
- a complaint-queue Overtime layer that starts only after a desk circuit is live, waits 20 seconds, warns for two seconds and then calls stage-scaled extra customers at deterministic `38 / 30 / 22` second spacing,
- an eight-second complaint-queue recovery window after the refund audit so the department-specific pressure systems do not stack unfairly,
- an optional opposite-side `Take-A-Number Queue Reset` that suppresses only future complaint-queue calls while standard Overtime and management pressure remain active,
- three optional Corporate Compliance Memos, an optional stash and the existing shared recovery/clock-out systems,
- the original deterministic **Customer Service — Please Hold Forever** soundtrack.

The refund terminal turns a workplace joke into a real objective without forking progression state. The
player restores the two service circuits, crosses to the rear desk and deliberately starts the twelve-second
audit. The first two responses are familiar retail threats, but the final 10-second answer is the
Customer Service-specific Returns Policy Enforcer rather than another Cart of Doom. Its three-way red-tape
fan raises pressure while reusing only project-owned presentation; it never owns a fuse, supervisor token or
separate completion flag. Surviving until 12 seconds grants the same final `CheckoutFuse` consumed by the
shared full-power and Night Manager logic.

Customer Service's extra Overtime layer is deliberately separate from the fixed refund audit. Once a desk
circuit is live and Overtime begins, one authored outer queue lane can call an additional hostile customer
after a 20-second grace period and two-second warning. The response escalates from Angry Self-Checkout to
Security Price Scanner to Cart of Doom as Overtime deepens. While the audit is active the complaint caller
pauses, then gives the player eight seconds to recover before it can resume. Taking the optional Queue Reset
retires only this department-specific caller; it does not disable global Overtime, standard floor hazards,
management waves or the Night Manager.

This is playable development content, not a polished final campaign level. Future work should strengthen
Customer Service-specific visual dressing, secrets and encounter variety only after target-machine playtests
confirm that the queue remains readable during the refund hold, complaint calls and Night Manager pressure.

Remaining Customer Service polish:
- target-machine balance/readability playtesting across all three difficulty modes, especially the 10-second Enforcer handoff and complaint-queue spacing,
- stronger returns-counter/customer-service presentation without replacing project-owned combat assets with proprietary material,
- more useful joke interactions and secrets that do not hide the two service circuits or refund terminal,
- final lighting/geometry and encounter polish after the current route survives real play.

## MAP06 — Management Floor
Purpose: a first playable executive-floor department built around a real Corporate authorization task, readable boardroom pressure and the next boss-scale management escalation.

Current prototype includes:
- paired executive-office wings around a permanently open center corridor,
- two opposite-side **Executive Access circuits**,
- a narrow rear boardroom doorway physically closed by two powered shutters until `2/3` power,
- one project-owned **Boardroom Breaker Authorization** behind the shutters,
- a save-safe ten-second Boardroom Review instead of an instant final power token,
- a fixed outer-boardroom review sequence: Security Price Scanner at 4 seconds, second warning at 7 seconds, Angry Self-Checkout at 9 seconds and the final authoritative `CheckoutFuse 3/3` only at 10 seconds,
- a separate four-second visual/audio warning after full authorization before **The District Director** enters,
- a 1400-health first-pass District Director that reuses only project-owned Regional Manager presentation while changing durability and projectile rhythm,
- a separate death handler that grants shared supervisor clearance so the boss actor does not own progression state,
- a department-specific deep-Overtime **Executive Audit** that cannot begin until both circuits are live and Overtime reaches stage 2,
- a 16-second initial audit delay, two-second warning and deterministic `32 / 22` second recurrence, using Scanner pressure at stage 2 and Cart pressure in Hell Rush,
- Boardroom Review isolation from recurring audit pressure: starting the fixed review cancels any armed audit and leaves eight seconds of recovery afterward,
- outer-lane baseline Overtime anchors and initial threats kept away from the permanent center route,
- three optional Corporate Compliance Memos plus a useful off-route reward,
- the original deterministic **Management Floor — Synergy Funeral** soundtrack,
- the shared physical front clock-out trigger after supervisor clearance.

The core workplace task is intentionally staged. Restoring both Executive Access circuits does not finish
power immediately; it only opens the boardroom. The player must then cross into the rear room and deliberately
start the Boardroom Review. Its exact `4 / 7 / 9 / 10` second sequence creates a short hold-the-floor beat while
keeping the last `CheckoutFuse` authoritative in the same shared progression system used by earlier departments.
Full power then begins a separate four-second boss handoff, preventing the District Director from materializing
on top of the authorization interaction.

Executive Audit is the department's distinct Overtime layer rather than another random trap. Once both office
circuits are live and Overtime reaches stage 2, the outer-right response lane waits 16 seconds, warns for two
seconds and produces a Security Price Scanner; Hell Rush substitutes a Cart of Doom. Repeats stay deterministic
at 32/22 seconds. The fixed Boardroom Review owns its encounter beat, so recurring audits pause for the entire
review and leave eight seconds of recovery. The central route is never closed by this system.

The District Director is deliberately treated as a gameplay prototype, not a falsely finished final boss.
The current actor inherits project-owned Regional Manager visual/audio material, raises durability and changes
its projectile rhythm. Objective state remains outside the actor; a Management Floor death handler supplies the
existing supervisor-clearance token, preserving the hardened post-boss Overtime retirement and clock-out flow.
A later unique visual pass is desirable only after real play validates the encounter.

See [`MANAGEMENT_FLOOR.md`](MANAGEMENT_FLOOR.md) for the exact implementation/contract note.

Remaining Management Floor polish:
- add dedicated normal HUD / Focus HUD wording for Executive Access, active Boardroom Review, District Director clearance and return-to-clock-out,
- add optional executive-floor secrets/useful workplace interactions only where mandatory circuits and the boardroom route remain obvious,
- give the District Director a more distinct project-owned visual identity after its gameplay survives real playtesting,
- complete target-Windows balance/readability playtesting on all three difficulty modes, including manual save/quit/load, physical controller and real-hardware performance,
- change final cover, lighting or route geometry only from interactive evidence.

## Design rule
Every room should have at least one gameplay joke that still works as a useful combat mechanic.
Humor must not replace readability, and progression gates must be visually understandable without
forcing the player to read long instructions during combat.
