# TrueFastball

[English](README.md) | [Русский](README_RU.md)

TrueFastball is a Borderlands 2-style Fastball overhaul for Borderlands 3: it increases Fastball damage and makes the throw feel more responsive while deliberately keeping Borderlands 3's native Fastball projectile speed and trajectory.

The mod multiplies the already-computed runtime `GrenadeDamage`, preserving the game's native level and Mayhem scaling, and temporarily accelerates the tested grenade throw animation only during a Fastball throw.

## Features

- The damage multiplier applies only to Fastball grenades.
- Default **Fastball Damage Multiplier:** `2.56`.
- Multiplies runtime `GrenadeDamage` instead of writing an absolute damage value.
- Preserves native level and Mayhem scaling.
- Updates the Fastball Damage value shown on the item card to reflect the active multiplier.
- Default **Throw Animation RateScale:** `2.0`.
- Restores temporary throw-animation changes when the owning grenade action ends.
- Does not modify Fastball projectile speed, gravity, upward velocity or trajectory.
- Exposes both release settings through the in-game Mod Menu.
- Validates manually edited or otherwise invalid saved settings before use.
- Normal gameplay logging is limited to errors.

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
