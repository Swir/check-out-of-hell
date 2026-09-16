# Prototype Weapons

## Emergency Mop
Melee panic tool. Fast enough to stay useful when ammunition is low.

The current 0.8-dev prototype uses a project-owned four-frame first-person mop animation
and an original synthesized swing cue. The sprite PNGs are generated deterministically by
`tools/generate_assets.py` and contain explicit ZDoom `grAb` offsets. This means the first
weapon the player sees no longer depends on the compatible IWAD fist view sprites.

## Receipt Ripper
A close-range spread weapon themed as an industrial receipt mechanism.
Its final art should look unmistakably retail-built rather than like a normal shotgun.
Original view sprites and combat audio are still pending.

## Price-Gun SMG
Fast automatic weapon. Final projectiles and impacts should use price labels,
barcode sparks and checkout-style feedback. Original view sprites/audio remain pending.

## Turbo Can Launcher
Explosive soda-can launcher. The can projectile is already implemented;
original sprite/audio work is still pending.

## Planned
- Fire-Exit Extinguisher
- Industrial Stapler
- Pallet-Jack Ram
- Barcode Beam
- Refund Denied superweapon
