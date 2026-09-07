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
DAMAGE_UI_STAT = "/Game/Gear/GrenadeMods/UIStats/UIStat_Grenade_Damage.UIStat_Grenade_Damage"

ACTION_BEGIN = (
    "/Game/PlayerCharacters/_Shared/_Design/GrenadeThrow/"
    "Action_GrenadeThrow_Base.Action_GrenadeThrow_Base_C:OnBegin"
)
ACTION_END = (
    "/Game/PlayerCharacters/_Shared/_Design/GrenadeThrow/"
    "Action_GrenadeThrow_Base.Action_GrenadeThrow_Base_C:OnEnd"
)

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

_pending_throw_owner: UObject | None = None
_anim_assets: list[tuple[UObject, float]] = []
_anim_cache_ready = False
_throw_patch_owner: UObject | None = None
_throw_patch_active = False

# key -> {state, baseline_text, baseline_cmp, owned_text, owned_cmp}
_ui_records: dict[str, dict[str, Any]] = {}


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


def _validated(raw: Any, default: float, minimum: float, maximum: float, label: str) -> float:
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


def _format_damage(value: float) -> str:
    # BL3's grenade Damage card uses an integer, without thousands separators.
    # Values are positive, so +0.5 provides stable nearest-integer rounding.
    return str(int(math.floor(value + 0.5)))


def _is_fastball_state(state: UObject | None) -> bool:
    if state is None:
        return False
    try:
        parts = state.GetPartList()
    except Exception:
        return False
    for part in parts:
        if part is not None and _path(part) == FASTBALL_AUG:
            return True
    return False


def _find_damage_entry(state: UObject) -> Any | None:
    try:
        sections = state.UIStats.Sections
    except Exception:
        return None
    for section in sections:
        try:
            stats = section.Stats
        except Exception:
            continue
        for entry in stats:
            try:
                stat_obj = entry.Stat
            except Exception:
                continue
            if stat_obj is not None and _path(stat_obj) == DAMAGE_UI_STAT:
                return entry
    return None


def _state_key(state: UObject) -> str:
    return _path(state)


def _write_damage_entry(state: UObject, value_text: str, comparison_value: float) -> bool:
    entry = _find_damage_entry(state)
    if entry is None:
        return False
    try:
        entry.ValueText = value_text
        entry.ComparisonValue = comparison_value
    except Exception as exc:
        _error(f"could not write cached Damage stat for {_path(state)}: {exc}")
        return False

    # Verify the underlying inline struct really changed. This catches a copy-only
    # wrapper instead of silently claiming success.
    verify = _find_damage_entry(state)
    if verify is None:
        return False
    try:
        got_text = str(verify.ValueText)
        got_cmp = float(verify.ComparisonValue)
    except Exception:
        return False
    return got_text == value_text and math.isclose(
        got_cmp, comparison_value, rel_tol=1e-6, abs_tol=0.01
    )


def _apply_ui_to_state(state: UObject, multiplier: float, *, reason: str) -> bool:
    if not _is_fastball_state(state):
        return False

    entry = _find_damage_entry(state)
    if entry is None:
        return False

    key = _state_key(state)
    record = _ui_records.get(key)

    if record is None:
        try:
            baseline_text = str(entry.ValueText)
            baseline_cmp = float(entry.ComparisonValue)
        except Exception as exc:
            _error(f"could not read cached Damage baseline for {key}: {exc}")
            return False
        if not math.isfinite(baseline_cmp) or baseline_cmp <= 0.0:
            _error(f"invalid cached Damage baseline {baseline_cmp!r} for {key}")
            return False
        record = {
            "state": state,
            "baseline_text": baseline_text,
            "baseline_cmp": baseline_cmp,
            "owned_text": None,
            "owned_cmp": None,
        }
        _ui_records[key] = record
    else:
        # Refresh the UObject reference in case Python produced a newer wrapper.
        record["state"] = state

    baseline_cmp = float(record["baseline_cmp"])
    target_cmp = baseline_cmp * multiplier
    target_text = _format_damage(target_cmp)

    if not _write_damage_entry(state, target_text, target_cmp):
        _error(f"cached Damage write did not stick for {key}")
        return False

    record["owned_text"] = target_text
    record["owned_cmp"] = target_cmp
    return True


def _scan_loaded_fastballs(multiplier: float, *, reason: str) -> tuple[int, int]:
    try:
        states = list(unrealsdk.find_all("InventoryBalanceStateComponent", exact=False))
    except Exception as exc:
        _error(f"balance-state scan failed: {exc}")
        return 0, 0

    found = 0
    patched = 0
    for state in states:
        if not _is_fastball_state(state):
            continue
        found += 1
        if _apply_ui_to_state(state, multiplier, reason=reason):
            patched += 1
    return found, patched


def _restore_all_ui() -> tuple[int, int]:
    restored = 0
    skipped = 0
    for key, record in list(_ui_records.items()):
        state = record.get("state")
        if state is None:
            skipped += 1
            continue

        entry = _find_damage_entry(state)
        if entry is None:
            skipped += 1
            continue

        # Ownership guard: restore only if the current cached value is still ours.
        # If another mod changed it afterwards, leave that value alone.
        try:
            current_text = str(entry.ValueText)
            current_cmp = float(entry.ComparisonValue)
        except Exception:
            skipped += 1
            continue

        owned_text = record.get("owned_text")
        owned_cmp = record.get("owned_cmp")
        if owned_text is None or owned_cmp is None:
            skipped += 1
            continue

        if current_text != str(owned_text) or not math.isclose(
            current_cmp, float(owned_cmp), rel_tol=1e-6, abs_tol=0.01
        ):
            skipped += 1
            continue

        if _write_damage_entry(
            state,
            str(record["baseline_text"]),
            float(record["baseline_cmp"]),
        ):
            restored += 1
        else:
            skipped += 1

    _ui_records.clear()
    return restored, skipped


def _current_damage_multiplier() -> float:
    return _validated(
        damage_option.value,
        DAMAGE_DEFAULT,
        DAMAGE_MIN,
        DAMAGE_MAX,
        "Fastball Damage Multiplier",
    )


def _on_damage_option_changed(_option: SliderOption, new_value: float) -> None:
    multiplier = _validated(
        new_value,
        DAMAGE_DEFAULT,
        DAMAGE_MIN,
        DAMAGE_MAX,
        "Fastball Damage Multiplier",
    )
    _scan_loaded_fastballs(multiplier, reason="slider")


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

OPTIONS = (damage_option, throw_rate_option)


def _sanitize_loaded_settings(mod: Mod) -> None:
    corrected = False
    specs = (
        (damage_option, DAMAGE_DEFAULT, DAMAGE_MIN, DAMAGE_MAX, "Fastball Damage Multiplier"),
        (throw_rate_option, RATE_DEFAULT, RATE_MIN, RATE_MAX, "Throw Animation RateScale"),
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
        except Exception:
            continue
        if _is_fastball_state(state):
            return item
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


def _patch_runtime_damage(projectile: UObject) -> None:
    multiplier = _current_damage_multiplier()
    try:
        current_damage = float(projectile.GrenadeDamage)
    except Exception as exc:
        _error(f"could not read GrenadeDamage from {_path(projectile)}: {exc}")
        return
    if not math.isfinite(current_damage) or current_damage <= 0.0:
        _error(f"invalid GrenadeDamage {current_damage!r} on {_path(projectile)}")
        return
    try:
        projectile.GrenadeDamage = current_damage * multiplier
    except Exception as exc:
        _error(f"could not patch Fastball runtime damage on {_path(projectile)}: {exc}")


def _on_enable() -> None:
    multiplier = _current_damage_multiplier()
    _scan_loaded_fastballs(multiplier, reason="enable")


def _on_disable() -> None:
    global _pending_throw_owner
    _pending_throw_owner = None
    _restore_throw_patch()
    _restore_all_ui()


@hook(ACTION_BEGIN, Type.PRE)
def _grenade_throw_begin(
    obj: UObject,
    args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    global _pending_throw_owner
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
    _pending_throw_owner = None
    _patch_runtime_damage(obj)


@hook("/Script/GbxInventory.InventoryBalanceStateComponent:PostBeginPlay", Type.POST)
def _inventory_state_begin_play(
    obj: UObject,
    _args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    # Covers Fastballs created/dropped after the mod was enabled. If UIStats are
    # not populated yet, OnRep_ReplicatedUIStats and card compare hooks retry.
    if _is_fastball_state(obj):
        _apply_ui_to_state(obj, _current_damage_multiplier(), reason="new-state")


@hook("/Script/GbxInventory.InventoryBalanceStateComponent:OnRep_ReplicatedUIStats", Type.POST)
def _inventory_ui_stats_replicated(
    obj: UObject,
    _args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    if _is_fastball_state(obj):
        _apply_ui_to_state(obj, _current_damage_multiplier(), reason="ui-rep")


@hook("/Script/OakGame.GFxItemCardAbbreviated:OnCompareToEquippedItem", Type.PRE)
def _item_card_compare(
    _obj: UObject,
    args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    # Opportunistic refresh immediately before an inventory comparison card is
    # populated. This also catches Fastballs which existed before a late enable.
    multiplier = _current_damage_multiplier()
    for field in ("HeldItem", "OtherItem"):
        try:
            state = getattr(args, field)
        except Exception:
            continue
        if state is not None and _is_fastball_state(state):
            _apply_ui_to_state(state, multiplier, reason="card-compare")


_cache_anim_assets()

mod = build_mod(
    options=OPTIONS,
    on_enable=_on_enable,
    on_disable=_on_disable,
)
mod.coop_support = None  # type: ignore[assignment]
_sanitize_loaded_settings(mod)
