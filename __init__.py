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
FASTBALL_DELIVERY_TOKEN = "BP_GM_Delivery_Fastball"

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

damage_option = SliderOption(
    "damage_multiplier",
    DAMAGE_DEFAULT,
    DAMAGE_MIN,
    DAMAGE_MAX,
    0.01,
    is_integer=False,
    display_name="Fastball Damage Multiplier",
    description=(
        "Multiplies the Fastball's already level/Mayhem-scaled runtime damage. "
        "Default: 2.56. Range: 1.00-4.00."
    ),
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

_pending_throw_owner: UObject | None = None

_anim_assets: list[tuple[UObject, float]] = []
_anim_cache_ready = False
_throw_patch_owner: UObject | None = None
_throw_patch_active = False


def _error(message: str) -> None:
    logging.error(f"[TrueFastball] {message}")


def _path(obj: Any) -> str:
    if obj is None:
        return "<None>"
    try:
        return str(obj._path_name())
    except Exception:
        return "<unreadable-path>"


def _class_name(obj: Any) -> str:
    if obj is None:
        return "<None>"
    try:
        return str(obj.Class.Name)
    except Exception:
        return type(obj).__name__


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
            try:
                if str(part._path_name()) == FASTBALL_AUG:
                    return item
            except Exception:
                continue

    return None


def _get_fastball_delivery(projectile: UObject) -> UObject | None:
    try:
        delivery = projectile.DeliveryMethod
    except Exception:
        return None

    if delivery is None:
        return None

    probe = f"{_class_name(delivery)} {_path(delivery)}".lower()
    if FASTBALL_DELIVERY_TOKEN.lower() not in probe:
        return None

    return delivery


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
        _error(
            "grenade animation assets were not available at OnBegin; "
            "damage patching can still proceed"
        )
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


def _patch_damage(projectile: UObject) -> None:
    multiplier = _validated(
        damage_option.value,
        DAMAGE_DEFAULT,
        DAMAGE_MIN,
        DAMAGE_MAX,
        "Fastball Damage Multiplier",
    )

    try:
        current_damage = float(projectile.GrenadeDamage)
    except Exception as exc:
        _error(f"could not read GrenadeDamage from {_path(projectile)}: {exc}")
        return

    if not math.isfinite(current_damage) or current_damage <= 0.0:
        _error(
            f"invalid GrenadeDamage {current_damage!r} on {_path(projectile)}"
        )
        return

    # Multiply the already-computed runtime value rather than writing an
    # absolute number so native level/Mayhem scaling remains intact.
    try:
        projectile.GrenadeDamage = current_damage * multiplier
    except Exception as exc:
        _error(f"could not patch Fastball damage on {_path(projectile)}: {exc}")


def _on_disable() -> None:
    global _pending_throw_owner

    _pending_throw_owner = None
    _restore_throw_patch()


@hook(ACTION_BEGIN, Type.PRE)
def _grenade_throw_begin(
    obj: UObject,
    args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    global _pending_throw_owner

    # Safety cleanup in case a previous grenade action ended abnormally.
    _pending_throw_owner = None
    _restore_throw_patch()

    try:
        player = args.Actor
    except Exception:
        return

    if _find_equipped_fastball(player) is None:
        return

    _pending_throw_owner = obj
    _apply_throw_rate(obj)


@hook(ACTION_END, Type.POST)
def _grenade_throw_end(
    obj: UObject,
    _args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    global _pending_throw_owner

    if _throw_patch_owner is obj:
        _restore_throw_patch(owner=obj)

    if _pending_throw_owner is obj:
        _pending_throw_owner = None


@hook("/Script/Engine.Actor:ReceiveBeginPlay", Type.POST)
def _actor_begin_play(
    obj: UObject,
    _args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    global _pending_throw_owner

    if _pending_throw_owner is None:
        return

    class_name = _class_name(obj).lower()
    if "grenade" not in class_name and "proj_" not in class_name:
        return

    if _get_fastball_delivery(obj) is None:
        return

    # Consume the pending throw only after positively identifying the
    # Fastball delivery object.
    _pending_throw_owner = None
    _patch_damage(obj)


# Try to cache eagerly; OnBegin retries if the character assets are not loaded yet.
_cache_anim_assets()

mod = build_mod(
    options=OPTIONS,
    on_disable=_on_disable,
)

# build_mod() loads persisted settings before returning. Sanitize those values,
# including hand-edited JSON, before any gameplay use.
_sanitize_loaded_settings(mod)
