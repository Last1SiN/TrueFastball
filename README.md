# TrueFastball

TrueFastball is a Borderlands 2-style Fastball overhaul for Borderlands 3: it makes the grenade hit harder and makes the throw feel more responsive while deliberately keeping Borderlands 3's native Fastball projectile speed and trajectory.

The mod applies only to the Fastball. It multiplies the already-computed runtime `GrenadeDamage`, so the game's native level and Mayhem scaling remain intact, and temporarily accelerates the tested grenade throw animation only for a Fastball throw.

## Features

- Applies damage changes only to the actual Fastball delivery.
- Default **Fastball Damage Multiplier:** `2.56`.
- Multiplies runtime `GrenadeDamage` instead of writing an absolute damage value.
- Preserves native level and Mayhem scaling.
- Default **Throw Animation RateScale:** `2.0`.
- Restores the temporary throw-animation RateScale when the owning grenade action ends.
- Does not modify Fastball projectile speed.
- Does not modify projectile gravity, upward velocity, or trajectory.
- Exposes both release settings through the in-game Mod Menu.
- Validates manually edited or otherwise invalid saved settings before use.
- Normal successful use does not add gameplay log spam; the mod writes only errors.

## Configuration

Default values are the tested release settings:

- **Fastball Damage Multiplier:** `2.56`
- **Throw Animation RateScale:** `2.0`

Allowed ranges:

- **Fastball Damage Multiplier:** `1.00-4.00`, step `0.01`
- **Throw Animation RateScale:** `1.0-5.0`, step `0.1`

Available through **MODS -> TrueFastball -> Options**.

The current throw-animation RateScale implementation targets the tested **FL4K / Beastmaster** grenade animation assets. The Fastball damage change itself is not tied to those animation assets.

TrueFastball intentionally leaves Borderlands 3's Fastball projectile speed and trajectory untouched.

## Requirements

- Borderlands 3.
- [BL3 PythonSDK / Oak Mod Manager v1.11+ — latest stable release](https://github.com/bl-sdk/oak-mod-manager/releases/latest).
- [Official BL3 SDK installation guide](https://bl-sdk.github.io/oak-mod-db/).

Oak Mod Manager v1.11 includes Mods Base 1.12, BL3 Mod Menu 1.8, Console Mod Menu 1.6, Keybinds 2.6, pyunrealsdk 1.10.0, UI Utils 1.4, and unrealsdk 3.2.0. These components normally do not need to be downloaded separately when using that release or a newer compatible Oak release.

## Installation

1. **Fully close Borderlands 3.**
2. If BL3 PythonSDK / Oak is not installed or needs updating, open the [latest stable Oak Mod Manager release](https://github.com/bl-sdk/oak-mod-manager/releases/latest).
3. Under **Assets**, download **`bl3-sdk.zip`** — not either `Source code` archive.
4. Locate the Borderlands 3 game folder. In Steam: **Library -> right-click Borderlands 3 -> Manage -> Browse local files**.
5. Extract the contents of `bl3-sdk.zip` directly into the Borderlands 3 game folder, allowing folders/files to merge and accepting overwrite prompts. See the [official BL3 SDK installation guide](https://bl-sdk.github.io/oak-mod-db/) for the complete procedure and Proton/Linux notes.
6. Start Borderlands 3 once and verify that the **MODS** entry appears on the main menu.
7. Download the latest TrueFastball release.
8. Fully close the game and copy `TrueFastball.sdkmod` **without extracting it** to:

   `Borderlands 3\sdk_mods\`

9. Remove older Fastball probe/test builds so that only one Fastball runtime mod can load.
10. Start/restart Borderlands 3, open **MODS -> TrueFastball**, enable the mod, and open **Options** to adjust the two values if desired.

To update TrueFastball, replace the existing `TrueFastball.sdkmod` with the newer file and restart the game.

## Compatibility and license

- Fastball scope: damage modification is gated to the actual Fastball projectile delivery.
- Projectile behavior: BL3 Fastball speed, gravity and trajectory are intentionally unchanged.
- License: **GPL-3.0**

## Credits

- **Development:** Sol / GPT-5.6 Sol
- **Design, testing & QA:** Last1SiN
- **BL3 PythonSDK / Oak Mod Manager:** created by [apple1417](https://github.com/apple1417), with contributions from the [BL-SDK](https://github.com/bl-sdk) project and contributors.
