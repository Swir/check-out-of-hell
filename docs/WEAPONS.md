# Prototype Weapons

## Emergency Mop
Melee panic tool. Fast enough to stay useful when ammunition is low.

The current prototype uses a project-owned four-frame first-person mop animation
and an original synthesized swing cue. The sprite PNGs are generated deterministically by
`tools/generate_assets.py` and contain explicit ZDoom `grAb` offsets. This means the first
weapon the player sees no longer depends on the compatible IWAD fist view sprites.

## Receipt Ripper
A close-range spread weapon themed as an industrial receipt mechanism.

Prototype 0.9-dev gives the weapon its own retail-built visual identity: a project-owned
world pickup, five first-person animation frames, a paper-feed/recoil firing beat and
separate original fire/cycle cues. Its active weapon states no longer reference the
compatible-IWAD shotgun sprite.

## Price-Gun SMG
Fast automatic weapon built around a handheld pricing-gun silhouette rather than a normal firearm.

Prototype 0.10-dev adds a project-owned world pickup and five-frame first-person animation.
Its hitscan shots now spawn short-lived barcode-label puffs at impact points, with original
trigger and label-feed cues. The active weapon states no longer reference the compatible-IWAD
chaingun view sprites.

## Turbo Can Launcher
Explosive soda-can launcher.

Prototype 0.10-dev gives the launcher a project-owned pickup and five-frame first-person
animation plus a fully original soda-can projectile/explosion sequence. Launch and impact
cues are generated with the same deterministic standard-library asset pipeline, so the
weapon no longer needs compatible-IWAD rocket launcher or rocket projectile visuals.

## Security Price Scanner synergy
The mid-range weapon pass also gives the hostile Security Price Scanner an original turret
animation and custom scan-beam projectile. This keeps the Price-Gun/Scanner visual language
consistent while making friend and foe silhouettes readable at a glance.

## Planned
- Fire-Exit Extinguisher
- Industrial Stapler
- Pallet-Jack Ram
- Barcode Beam
- Refund Denied superweapon
