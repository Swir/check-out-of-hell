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