# CHECKOUT OF HELL

[![Build prototype](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml/badge.svg)](https://github.com/Swir/check-out-of-hell/actions/workflows/build.yml)

A fast, funny retro-FPS set during the worst night shift imaginable.

> **Status:** Prototype 0.2-dev — two-map combat foundation  
> **Project progress:** `██░░░░░░░░ 20%`

## Premise

The store is closed. The lights are flickering. Self-checkouts are angry.
Shopping carts are hunting staff. The night manager has definitely had enough.

CHECKOUT OF HELL is an original comedy-horror FPS inspired by the speed and
readability of classic shooters while building its own setting, characters,
weapons, jokes, levels and final art.

## What already works

- buildable `.pk3` prototype,
- generated UDMF `MAP01 — Closing Time`,
- generated UDMF `MAP02 — Warehouse 13.5`,
- **Emergency Mop**,
- **Receipt Ripper**,
- **Price-Gun SMG**,
- **Turbo Can Launcher** with explosive can projectile,
- **Angry Self-Checkout**,
- **Cart of Doom**,
- **Night Manager**,
- **Security Price Scanner** turret,
- **Possessed Pallet Jack**,
- **The Regional Manager** prototype boss,
- Windows development launchers,
- automated build + smoke tests,
- verified GitHub Actions artifact build,
- original project icon concept,
- documented asset policy, weapon plan and level direction.

The prototype deliberately does **not** redistribute Doom game data.

## Development runtime

Target:
- GZDoom 4.14.2+ as the initial stable target,
- future compatibility testing with the UZDoom line.

For a legally redistributable development IWAD, use **Freedoom Phase 2**.
Put these files in `external/`:

```text
external/
  gzdoom.exe
  freedoom2.wad
```

Then run:

```text
build-and-run.bat
```

or:

```powershell
python tools/build.py
python tools/smoke_test.py
external\gzdoom.exe -iwad external\freedoom2.wad -file dist\checkout-of-hell-prototype.pk3 +map MAP01
```

## Prototype weapons

- Slot 1: Emergency Mop
- Shotgun pickup: Receipt Ripper
- Chaingun pickup: Price-Gun SMG
- Rocket Launcher pickup: Turbo Can Launcher

See [`docs/WEAPONS.md`](docs/WEAPONS.md).

## Maps

- `MAP01` — **Closing Time**
- `MAP02` — **Warehouse 13.5**

See [`docs/LEVEL_DESIGN.md`](docs/LEVEL_DESIGN.md).

## Asset policy

No proprietary Doom, Star Wars or other commercial game assets belong in this
repository. Prototype visuals may temporarily reference sprite names supplied
by a compatible IWAD at runtime; those assets are not distributed here.
Final art, audio, UI, characters and map decoration are planned to be original.

See [`docs/ASSET_POLICY.md`](docs/ASSET_POLICY.md).

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

## Author

**by Swir**  
GitHub: https://github.com/Swir
