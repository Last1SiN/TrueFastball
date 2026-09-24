# TrueFastball

[English](README.md) | [Русский](README_RU.md)

TrueFastball makes the Fastball feel like the heavy hitter it used to be.

It boosts Fastball damage and speeds up the throw, but leaves Borderlands 3's projectile speed and arc alone. The result is a harder-hitting, snappier Fastball without turning it into a different grenade.

Both damage and throw speed can be adjusted from the Mod Menu.

## Features

- More Fastball damage; default multiplier is **2.56x**.
- Faster throw animation; default speed is **2.0x**.
- Keeps Borderlands 3's normal Fastball projectile speed and trajectory.
- Damage still scales normally with level and Mayhem.
- The item card reflects the active damage multiplier.
- Both settings are available in the Mod Menu.
- Temporary animation changes are restored when the throw ends.

## Configuration

Default values:

- **Fastball Damage Multiplier:** `2.56`
- **Throw Animation RateScale:** `2.0`

Allowed ranges:

- **Fastball Damage Multiplier:** `1.00-4.00`, step `0.01`
- **Throw Animation RateScale:** `1.0-5.0`, step `0.1`

Available through **MODS -> TrueFastball -> Options**.

The current throw-animation acceleration targets the tested **FL4K / Beastmaster** grenade animation assets. The damage modification itself is not tied to those animation assets.

## Requirements

- Borderlands 3
- [BL3 PythonSDK / Oak Mod Manager](https://github.com/bl-sdk/oak-mod-manager/releases/latest)

Use the [official BL3 SDK / Oak installation guide](https://bl-sdk.github.io/oak-mod-db/) for SDK installation and updates.

## Installing the mod

1. Install or update BL3 PythonSDK / Oak using the official guide above.
2. Download `TrueFastball.sdkmod` from [GitHub Releases](https://github.com/Last1SiN/TrueFastball/releases/latest).
3. With Borderlands 3 closed, copy the `.sdkmod` file intact to `Borderlands 3\sdk_mods\`. Do not extract the `.sdkmod` itself.
4. Remove old Fastball test/probe builds so only one Fastball runtime mod can load.
5. Start the game, open **MODS -> TrueFastball**, enable the mod and configure the two values under **Options** if desired.

To update TrueFastball, replace the existing `.sdkmod` with the newer file and restart the game.

## Compatibility and license

- The damage multiplier applies only to Fastball grenades.
- Borderlands 3 Fastball projectile speed, gravity and trajectory are intentionally unchanged.
- Co-op support: **Unknown** — behavior with the mod installed only on a client while the host does not have it has not yet been validated.
- License: **GNU GPLv3 with [Section 7 additional provenance terms](ADDITIONAL_TERMS.md)**

## Credits

**Development:** Sol / GPT-5.6 Sol  
**Design, testing & QA:** Last1SiN

**BL3 PythonSDK / Oak Mod Manager:** created by [apple1417](https://github.com/apple1417), with contributions from the [BL-SDK](https://github.com/bl-sdk) project and contributors.
