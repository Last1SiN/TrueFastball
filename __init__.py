from __future__ import annotations

import math
from typing import Any

import unrealsdk
from mods_base import Game, Mod, SliderOption, build_mod, hook
from unrealsdk import logging
from unrealsdk.hooks import Type
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

assert Game.get_current() is Game.BL3, "TrueFastball supports Borderlands 3 only"

FASTBALL_AUG = (
    "/Game/Gear/GrenadeMods/_Design/_Unique/Fastball/Parts/"
    "Part_GM_Aug_Fastball.Part_GM_Aug_Fastball"
)
FASTBALL_PART_PACKAGE = (
    "/Game/Gear/GrenadeMods/_Design/_Unique/Fastball/Parts/"
    "Part_GM_Aug_Fastball"
)
FASTBALL_DAMAGE_ATTRIBUTE = (
    "/Game/Gear/GrenadeMods/_Design/Attributes/"
    "Att_GrenadeMod_Damage.Att_GrenadeMod_Damage"
)

ACTION_BEGIN = (
    "/Game/PlayerCharacters/_Shared/_Design/GrenadeThrow/"
    "Action_GrenadeThrow_Base.Action_GrenadeThrow_Base_C:OnBegin"
)
ACTION_END = (
    "/Game/PlayerCharacters/_Shared/_Design/GrenadeThrow/"
    "Action_GrenadeThrow_Base.Action_GrenadeThrow_Base_C:OnEnd"
)

# Same tested FL4K / Beastmaster grenade-throw animation assets used by FasterLongbow.
TARGET_ASSETS = {
    "/Game/PlayerCharacters/Beastmaster/_Shared/Animation/Skills/CharacterSkills/3rd/"
    "AS_UA_Grenade.AS_UA_Grenade",
    "/Game/PlayerCharacters/Beastmaster/_Shared/Animation/Skills/CharacterSkills/3rd/"
    "AS_Grenade_Offhand.AS_Grenade_Offhand",
    "/Game/PlayerCharacters/Beastmaster/_Shared/Animation/Skills/CharacterSkills/3rd/"
    "AS_Grenade_Crouch.AS_Grenade_Crouch",
    "/Game/PlayerCharacters/Beastmaster/_Shared/Animation/Skills/CharacterSkills/3rd/"
    "AS_Grenade.AS_Grenade",
}

DAMAGE_DEFAULT = 2.56
DAMAGE_MIN = 1.00
DAMAGE_MAX = 4.00

RATE_DEFAULT = 2.0
RATE_MIN = 1.0
RATE_MAX = 5.0


def _error(message: str) -> None:
    logging.error(f"[TrueFastball] {message}")


def _path(obj: Any) -> str:
    if obj is None:
        return "<None>"
    try:
        return str(obj._path_name())
    except Exception:
        return "<unreadable-path>"


def _validated(
    raw: Any,
    default: float,
    minimum: float,
    maximum: float,
    label: str,
) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        _error(f"{label}: invalid value {raw!r}; using default {default:.3f}")
        return default

    if not math.isfinite(value):
        _error(f"{label}: non-finite value {value!r}; using default {default:.3f}")
        return default

    if value < minimum:
        _error(f"{label}: {value:.3f} below minimum; clamped to {minimum:.3f}")
        return minimum

    if value > maximum:
        _error(f"{label}: {value:.3f} above maximum; clamped to {maximum:.3f}")
        return maximum

    return value


_damage_part: UObject | None = None
_damage_effect_index: int | None = None
_damage_original_scale: float | None = None
_damage_owned_scale: float | None = None
_damage_patch_active = False


def _find_fastball_part() -> UObject | None:
    global _damage_part

    if _damage_part is not None and _path(_damage_part) == FASTBALL_AUG:
        return _damage_part

    try:
        unrealsdk.load_package(FASTBALL_PART_PACKAGE)
    except Exception as exc:
        _error(f"could not load Fastball part package: {exc}")
        return None

    try:
        part = unrealsdk.find_object("InventoryPartData", FASTBALL_AUG)
    except Exception:
        part = None

    if part is None:
        try:
            for candidate in unrealsdk.find_all("InventoryPartData", exact=False):
                if _path(candidate) == FASTBALL_AUG:
                    part = candidate
                    break
        except Exception as exc:
            _error(f"could not scan loaded inventory parts: {exc}")
            return None

    if part is None:
        _error("could not locate Part_GM_Aug_Fastball after loading its package")
        return None

    _damage_part = part
    return part


def _locate_damage_effect(part: UObject) -> tuple[int, Any] | None:
    try:
        effects = part.InventoryAttributeEffects
    except Exception as exc:
        _error(f"could not read Fastball InventoryAttributeEffects: {exc}")
        return None

    for index, effect in enumerate(effects):
        try:
            if _path(effect.AttributeToModify) == FASTBALL_DAMAGE_ATTRIBUTE:
                return index, effect
        except Exception:
            continue

    _error("Fastball damage InventoryAttributeEffect was not found")
    return None


def _write_effect_scale(part: UObject, index: int, scale: float) -> bool:
    try:
        modifier_value = part.InventoryAttributeEffects[index].ModifierValue
        modifier_value.BaseValueScale = scale
        return True
    except Exception as exc:
        _error(f"could not write Fastball damage BaseValueScale: {exc}")
        return False


def _apply_damage_multiplier(raw_multiplier: Any | None = None) -> bool:
    global _damage_effect_index
    global _damage_original_scale
    global _damage_owned_scale
    global _damage_patch_active

    multiplier = _validated(
        damage_option.value if raw_multiplier is None else raw_multiplier,
        DAMAGE_DEFAULT,
        DAMAGE_MIN,
        DAMAGE_MAX,
        "Fastball Damage Multiplier",
    )

    part = _find_fastball_part()
    if part is None:
        return False

    located = _locate_damage_effect(part)
    if located is None:
        return False

    index, effect = located

    try:
        current_scale = float(effect.ModifierValue.BaseValueScale)
    except Exception as exc:
        _error(f"could not read Fastball damage BaseValueScale: {exc}")
        return False

    if not math.isfinite(current_scale):
        _error(f"Fastball damage BaseValueScale is non-finite: {current_scale!r}")
        return False

    if not _damage_patch_active:
        _damage_effect_index = index
        _damage_original_scale = current_scale
    elif _damage_effect_index != index:
        _error("Fastball damage effect index changed while the mod was active")
        return False

    if _damage_original_scale is None:
        _error("Fastball damage original BaseValueScale is unavailable")
        return False

    target_scale = _damage_original_scale * multiplier
    if not math.isfinite(target_scale):
        _error(f"calculated Fastball damage BaseValueScale is invalid: {target_scale!r}")
        return False

    if not _write_effect_scale(part, index, target_scale):
        return False

    _damage_owned_scale = target_scale
    _damage_patch_active = True
    return True


def _restore_damage_patch() -> None:
    global _damage_effect_index
    global _damage_original_scale
    global _damage_owned_scale
    global _damage_patch_active

    if not _damage_patch_active:
        return

    part = _damage_part
    index = _damage_effect_index
    original = _damage_original_scale
    owned = _damage_owned_scale

    if part is None or index is None or original is None or owned is None:
        _damage_effect_index = None
        _damage_original_scale = None
        _damage_owned_scale = None
        _damage_patch_active = False
        return

    try:
        current = float(part.InventoryAttributeEffects[index].ModifierValue.BaseValueScale)
    except Exception:
        current = None

    # Restore only if the value is still ours. Do not overwrite another mod
    # which may have changed the same Fastball source after TrueFastball.
    if current is not None and math.isclose(current, owned, rel_tol=1e-6, abs_tol=1e-6):
        _write_effect_scale(part, index, original)

    _damage_effect_index = None
    _damage_original_scale = None
    _damage_owned_scale = None
    _damage_patch_active = False


def _on_damage_option_changed(_option: SliderOption, new_value: float) -> None:
    _apply_damage_multiplier(new_value)


damage_option = SliderOption(
    "damage_multiplier",
    DAMAGE_DEFAULT,
    DAMAGE_MIN,
    DAMAGE_MAX,
    0.01,
    is_integer=False,
    display_name="Fastball Damage Multiplier",
    description=(
        "Scales the Fastball's own damage attribute before inventory/UI stats are built, "
        "so the item card and actual grenade damage use the same value. "
        "Default: 2.56. Range: 1.00-4.00."
    ),
    on_change_while_enabled=_on_damage_option_changed,
)

throw_rate_option = SliderOption(
    "throw_rate_scale",
    RATE_DEFAULT,
    RATE_MIN,
    RATE_MAX,
    0.1,
    is_integer=False,
    display_name="Throw Animation RateScale",
    description=(
        "Speed multiplier for the Fastball grenade throw animation. "
        "Stock is 1.0. Default: 2.0. Range: 1.0-5.0."
    ),
)

OPTIONS = (
    damage_option,
    throw_rate_option,
)

_anim_assets: list[tuple[UObject, float]] = []
_anim_cache_ready = False
_throw_patch_owner: UObject | None = None
_throw_patch_active = False


def _sanitize_loaded_settings(mod: Mod) -> None:
    corrected = False

    specs = (
        (
            damage_option,
            DAMAGE_DEFAULT,
            DAMAGE_MIN,
            DAMAGE_MAX,
            "Fastball Damage Multiplier",
        ),
        (
            throw_rate_option,
            RATE_DEFAULT,
            RATE_MIN,
            RATE_MAX,
            "Throw Animation RateScale",
        ),
    )

    for option, default, minimum, maximum, label in specs:
        safe = _validated(option.value, default, minimum, maximum, label)
        try:
            current = float(option.value)
        except (TypeError, ValueError):
            current = float("nan")

        if not math.isfinite(current) or current != safe:
            option.value = safe
            corrected = True

    if corrected:
        try:
            mod.save_settings()
        except Exception as exc:
            _error(f"could not persist corrected settings: {exc}")


def _find_equipped_fastball(player: UObject) -> UObject | None:
    try:
        slots = player.EquippedInventory.InventorySlots
    except Exception:
        return None

    for slot in slots:
        try:
            item = slot.EquippedInventory
        except Exception:
            continue
        if item is None:
            continue

        try:
            state = item.BalanceStateComponent
            if state is None:
                continue
            parts = state.GetPartList()
        except Exception:
            continue

        for part in parts:
            if part is None:
                continue
            if _path(part) == FASTBALL_AUG:
                return item

    return None


def _cache_anim_assets() -> bool:
    global _anim_cache_ready, _anim_assets

    if _anim_cache_ready and _anim_assets:
        return True

    found: list[tuple[UObject, float]] = []

    try:
        loaded = list(unrealsdk.find_all("AnimSequenceBase", exact=False))
    except Exception as exc:
        _error(f"animation scan failed: {exc}")
        return False

    for asset in loaded:
        if _path(asset) not in TARGET_ASSETS:
            continue

        try:
            original = float(asset.RateScale)
        except Exception:
            continue

        found.append((asset, original))

    if not found:
        return False

    _anim_assets = found
    _anim_cache_ready = True
    return True


def _restore_throw_patch(owner: UObject | None = None) -> None:
    global _throw_patch_owner, _throw_patch_active

    if not _throw_patch_active:
        return

    if owner is not None and _throw_patch_owner is not owner:
        return

    for asset, original in _anim_assets:
        try:
            asset.RateScale = original
        except Exception:
            pass

    _throw_patch_owner = None
    _throw_patch_active = False


def _apply_throw_rate(owner: UObject) -> None:
    global _throw_patch_owner, _throw_patch_active

    _restore_throw_patch()

    rate = _validated(
        throw_rate_option.value,
        RATE_DEFAULT,
        RATE_MIN,
        RATE_MAX,
        "Throw Animation RateScale",
    )

    if not _cache_anim_assets():
        _error("grenade animation assets were not available at OnBegin")
        return

    changed = False
    for asset, _original in _anim_assets:
        try:
            asset.RateScale = rate
            changed = True
        except Exception:
            pass

    if changed:
        _throw_patch_owner = owner
        _throw_patch_active = True


def _on_enable() -> None:
    _apply_damage_multiplier()


def _on_disable() -> None:
    _restore_damage_patch()
    _restore_throw_patch()


@hook(ACTION_BEGIN, Type.PRE)
def _grenade_throw_begin(
    obj: UObject,
    args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    _restore_throw_patch()

    try:
        player = args.Actor
    except Exception:
        return

    if _find_equipped_fastball(player) is None:
        return

    _apply_throw_rate(obj)


@hook(ACTION_END, Type.POST)
def _grenade_throw_end(
    obj: UObject,
    _args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    if _throw_patch_owner is obj:
        _restore_throw_patch(owner=obj)


# Try to cache eagerly; OnBegin retries if the character assets are not loaded yet.
_cache_anim_assets()

mod = build_mod(
    options=OPTIONS,
    on_enable=_on_enable,
    on_disable=_on_disable,
)

# build_mod() loads persisted settings before returning. Sanitize those values,
# including hand-edited JSON, before any gameplay use.
_sanitize_loaded_settings(mod)
