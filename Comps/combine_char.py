"""Combine JSON results from different game modes into a unified build dataset."""

import json
from sys import path as sys_path

# TODO: histograph

sys_path.append("../")
from comp_rates_config import PAST_PHASE, RECENT_PHASE
from pydantic import BaseModel
from slugify import slugify

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
# How many top items we keep per category (w-engines, drives, relic stats)
GEAR_COUNTS = {
    "weapons": 10,
    "artifacts": 10,
    "slot_4": 3,
    "slot_5": 3,
    "slot_6": 3,
}

# List of numeric fields that need weighted averaging across game modes
NUMERIC_STATS = [
    "app_0",
    "app_1",
    "app_2",
    "app_3",
    "app_4",
    "app_5",
    "app_6",
    "cons_avg",
    "char_level",
    "w_engine_level",
    "basic_atk",
    "special_atk",
    "dash",
    "ultimate",
    "core_skill",
    "assist",
    "base_hp",
    "base_atk",
    "base_def",
    "base_impact",
    "sheer_force",
    "crit_rate",
    "crit_dmg",
    "anomaly_mastery",
    "anomaly_proficiency",
    "pen_ratio",
    "pen",
    "base_energy_regen",
    "dmg_bonus",
    "percent_hp_sub",
    "percent_atk_sub",
    "percent_def_sub",
    "crit_rate_sub",
    "crit_dmg_sub",
    "pen_sub",
    "anomaly_proficiency_sub",
]

# ----------------------------------------------------------------------
# Load slug mappings and character list
# ----------------------------------------------------------------------
with open("prydwen-slug.json") as slug_file:
    SLUG = json.load(slug_file)

with open("../data/characters.json") as char_file:
    CHARACTERS: dict[str, dict[str, str | int | None]] = json.load(char_file)


# ----------------------------------------------------------------------
# Pydantic models for raw input data
# ----------------------------------------------------------------------
class BaseCharacterStats(BaseModel):
    """Base character stats from a single game mode (SD or DA)."""

    char: str
    app_rate: float
    app_rate_m0: float
    avg_round: int
    std_dev_round: int
    q1_round: int
    role: str
    rarity: str
    diff: float
    diff_rounds: int

    # W-Engines 1-10
    weapon_1: str
    weapon_1_app: float
    weapon_1_round: int
    weapon_2: str
    weapon_2_app: float
    weapon_2_round: int
    weapon_3: str
    weapon_3_app: float
    weapon_3_round: int
    weapon_4: str
    weapon_4_app: float
    weapon_4_round: int
    weapon_5: str
    weapon_5_app: float
    weapon_5_round: int
    weapon_6: str
    weapon_6_app: float
    weapon_6_round: int
    weapon_7: str
    weapon_7_app: float
    weapon_7_round: int
    weapon_8: str
    weapon_8_app: float
    weapon_8_round: int
    weapon_9: str
    weapon_9_app: float
    weapon_9_round: int
    weapon_10: str
    weapon_10_app: float
    weapon_10_round: int

    # Drives 1-10
    artifact_1: str
    artifact_1_1: str
    artifact_1_2: str
    artifact_1_3: str
    artifact_1_app: float
    artifact_1_round: int
    artifact_2: str
    artifact_2_1: str
    artifact_2_2: str
    artifact_2_3: str
    artifact_2_app: float
    artifact_2_round: int
    artifact_3: str
    artifact_3_1: str
    artifact_3_2: str
    artifact_3_3: str
    artifact_3_app: float
    artifact_3_round: int
    artifact_4: str
    artifact_4_1: str
    artifact_4_2: str
    artifact_4_3: str
    artifact_4_app: float
    artifact_4_round: int
    artifact_5: str
    artifact_5_1: str
    artifact_5_2: str
    artifact_5_3: str
    artifact_5_app: float
    artifact_5_round: int
    artifact_6: str
    artifact_6_1: str
    artifact_6_2: str
    artifact_6_3: str
    artifact_6_app: float
    artifact_6_round: int
    artifact_7: str
    artifact_7_1: str
    artifact_7_2: str
    artifact_7_3: str
    artifact_7_app: float
    artifact_7_round: int
    artifact_8: str
    artifact_8_1: str
    artifact_8_2: str
    artifact_8_3: str
    artifact_8_app: float
    artifact_8_round: int
    artifact_9: str
    artifact_9_1: str
    artifact_9_2: str
    artifact_9_3: str
    artifact_9_app: float
    artifact_9_round: int
    artifact_10: str
    artifact_10_1: str
    artifact_10_2: str
    artifact_10_3: str
    artifact_10_app: float
    artifact_10_round: int

    # Mindscape appearance rates and score data
    app_0: float
    round_0: int
    app_1: float
    round_1: int
    app_2: float
    round_2: int
    app_3: float
    round_3: int
    app_4: float
    round_4: int
    app_5: float
    round_5: int
    app_6: float
    round_6: int
    cons_avg: float
    sample: int
    sample_app_flat: int


class FullCharacterStats(BaseCharacterStats):
    """Extended stats including character levels, w-engine levels, substats, etc."""

    player_level: float
    char_level: float
    w_engine_level: float
    basic_atk: float
    special_atk: float
    dash: float
    ultimate: float
    core_skill: float
    assist: float
    base_hp: float
    base_atk: float
    base_def: float
    base_impact: float
    sheer_force: float
    crit_rate: float
    crit_dmg: float
    anomaly_mastery: float
    anomaly_proficiency: float
    pen_ratio: float
    pen: float
    base_energy_regen: float
    dmg_bonus: float
    percent_hp_sub: float
    percent_atk_sub: float
    percent_def_sub: float
    crit_rate_sub: float
    crit_dmg_sub: float
    pen_sub: float
    anomaly_proficiency_sub: float
    sample_size_players: int

    # Main stat usage on drives (slot 4, slot 5, slot 6)
    drive_slot_4_1: str | None
    drive_slot_4_1_app: float
    drive_slot_4_2: str | None
    drive_slot_4_2_app: float
    drive_slot_4_3: str | None
    drive_slot_4_3_app: float
    drive_slot_5_1: str | None
    drive_slot_5_1_app: float
    drive_slot_5_2: str | None
    drive_slot_5_2_app: float
    drive_slot_5_3: str | None
    drive_slot_5_3_app: float
    drive_slot_6_1: str | None
    drive_slot_6_1_app: float
    drive_slot_6_2: str | None
    drive_slot_6_2_app: float
    drive_slot_6_3: str | None
    drive_slot_6_3_app: float


# ----------------------------------------------------------------------
# Helper functions to load JSON data into Pydantic models
# ----------------------------------------------------------------------
def load_base_stats(file_path: str) -> dict[str, BaseCharacterStats]:
    """Load basic stats (e0s1, e1, s0 files)."""
    with open(file_path) as file:
        data = json.load(file)
    return {item["char"]: BaseCharacterStats(**item) for item in data}


def load_full_stats(file_path: str) -> dict[str, FullCharacterStats]:
    """Load full stats (all2.json files with extended info)."""
    with open(file_path) as file:
        data = json.load(file)
    return {item["char"]: FullCharacterStats(**item) for item in data}


# ----------------------------------------------------------------------
# Load all input data for each game mode
# ----------------------------------------------------------------------
BASE_PATH = f"../char_results/{RECENT_PHASE}"
BASE_PREV_PATH = f"../char_results/{PAST_PHASE}"

raw: dict[str, dict[str, BaseCharacterStats]] = {}
raw_full: dict[str, dict[str, FullCharacterStats]] = {}

for read_path in [BASE_PATH, BASE_PREV_PATH]:
    suf = "" if read_path == BASE_PATH else "_prev"
    for mode in ["sd", "da"]:
        folder_dir = f"{read_path}_{mode}" if mode != "sd" else read_path
        raw_full[f"{mode}{suf}"] = load_full_stats(f"{folder_dir}/all2.json")
        raw[f"{mode}_e1{suf}"] = load_base_stats(f"{folder_dir}/all_C1.json")
        raw[f"{mode}_s0{suf}"] = load_base_stats(f"{folder_dir}/all_E0S0.json")

    boss_configs = [(1, "1-1"), (2, "1-2"), (3, "1-3")]
    for boss_num, boss_room in boss_configs:
        file_name = f"{read_path}_da/{boss_room}"
        raw[f"da_boss_{boss_num}{suf}"] = load_base_stats(f"{file_name}.json")
        raw[f"da_boss_{boss_num}_e1{suf}"] = load_base_stats(f"{file_name}_C1.json")
        raw[f"da_boss_{boss_num}_s0{suf}"] = load_base_stats(f"{file_name}_E0S0.json")

    boss_configs = [(1, "5-1"), (2, "5-2"), (3, "5-3")]
    for boss_num, boss_room in boss_configs:
        file_name = f"{read_path}/{boss_room}"
        raw[f"sd_boss_{boss_num}{suf}"] = load_base_stats(f"{file_name}.json")
        raw[f"sd_boss_{boss_num}_e1{suf}"] = load_base_stats(f"{file_name}_C1.json")
        raw[f"sd_boss_{boss_num}_s0{suf}"] = load_base_stats(f"{file_name}_E0S0.json")


# ----------------------------------------------------------------------
# Pydantic models for aggregated usage (w-engines, drives stats)
# ----------------------------------------------------------------------
class GearStats(BaseModel):
    """Stats for a single piece of gear (w-engine, drive)."""

    app: float  # appearance percentage
    round: int  # average score
    set1: str = ""  # first drive set (for drives only)
    set2: str = ""  # second drive set (for drives only)
    set3: str = ""  # third drive set (for drives only)


class CharacterGearUsage(BaseModel):
    """Aggregated gear and relic main stat usage for one character."""

    weapons: dict[str, GearStats]
    artifacts: dict[str, GearStats]
    drive_slot_4: dict[str, float]  # main stat name -> appearance %
    drive_slot_5: dict[str, float]
    drive_slot_6: dict[str, float]


def is_valid_name(s: str | None) -> bool:
    """Return True if string is not empty and not '-'."""
    return (bool(s) and s != "-") or s is None


def build_gear_usage(
    raw_data: dict[str, FullCharacterStats],
) -> dict[str, CharacterGearUsage]:
    """Convert raw FullCharacterStats into a CharacterGearUsage dict for each character.

    This groups w-engines, drives, and relic main stats into dictionaries.
    """
    usage_by_char: dict[str, CharacterGearUsage] = {}

    for char_name, stats in raw_data.items():
        # --- W-Engines and Drives ---
        gear_collections: dict[str, dict[str, GearStats]] = {}

        for category in ["weapon", "artifact"]:
            gear_dict: dict[str, GearStats] = {}
            count = GEAR_COUNTS[f"{category}s"]  # e.g., "weapons" -> 10
            for i in range(1, count + 1):
                name = getattr(stats, f"{category}_{i}")
                if is_valid_name(name):
                    gear_dict[name] = GearStats(
                        app=getattr(stats, f"{category}_{i}_app"),
                        round=getattr(stats, f"{category}_{i}_round"),
                        set1=getattr(stats, f"{category}_{i}_1", ""),
                        set2=getattr(stats, f"{category}_{i}_2", ""),
                        set3=getattr(stats, f"{category}_{i}_3", ""),
                    )
            gear_collections[category] = gear_dict

        # --- Drive main stats (slot 4, slot 5, slot 6) ---
        drive_stats: dict[str, dict[str, float]] = {}
        for part in ["slot_4", "slot_5", "slot_6"]:
            part_dict: dict[str, float] = {}
            count = GEAR_COUNTS[part]
            for i in range(1, count + 1):
                name = getattr(stats, f"drive_{part}_{i}")
                if is_valid_name(name):
                    # Null stat name is possible,
                    # which means no drive equipped in that slot
                    part_dict[name or ""] = getattr(stats, f"drive_{part}_{i}_app")
            drive_stats[part] = part_dict

        usage_by_char[char_name] = CharacterGearUsage(
            weapons=gear_collections["weapon"],
            artifacts=gear_collections["artifact"],
            drive_slot_4=drive_stats["slot_4"],
            drive_slot_5=drive_stats["slot_5"],
            drive_slot_6=drive_stats["slot_6"],
        )

    return usage_by_char


# Build usage structures for each mode
sd_usage: dict[str, CharacterGearUsage] = build_gear_usage(raw_full["sd"])
da_usage: dict[str, CharacterGearUsage] = build_gear_usage(raw_full["da"])

# ----------------------------------------------------------------------
# Build list of all character keys (including solo/support variants)
# ----------------------------------------------------------------------
character_keys: list[str] = []
for char_iter in CHARACTERS:
    slugged = slugify(char_iter)
    if slugged in SLUG:
        slugged = SLUG[slugged]
    character_keys.append(slugged)


def process_chars() -> None:
    """Process loop over all character keys."""

    # ----------------------------------------------------------------------
    # Pydantic model for merged gear stats (after combining modes)
    # ----------------------------------------------------------------------
    class MergedGearStats(BaseModel):
        """Gear stats after merging SD and DA data."""

        app: float
        round_sd: int
        round_da: int
        set1: str
        set2: str
        set3: str

    def merge_gear_stats(
        gears_sd: dict[str, GearStats],
        gears_da: dict[str, GearStats],
    ) -> dict[str, MergedGearStats]:
        """Combine gear stats from three modes.

        Using the already computed appearance rates
        (rate_sd, rate_da) and total rate (rate_combine).
        The rates are pulled from the outer scope.
        """
        merged: dict[str, MergedGearStats] = {}
        all_gear: dict[str, GearStats] = gears_sd | gears_da

        for name, gear_set in all_gear.items():
            gear_sd = gears_sd.get(name)
            gear_da = gears_da.get(name)

            app_sd = gear_sd.app if gear_sd else 0.0
            app_da = gear_da.app if gear_da else 0.0

            app_sd = app_sd * rate_sd / rate_combine
            app_da = app_da * rate_da / rate_combine

            merged[name] = MergedGearStats(
                app=app_sd + app_da,
                round_sd=gear_sd.round if gear_sd else 0,
                round_da=gear_da.round if gear_da else 0,
                set1=gear_set.set1,
                set2=gear_set.set2,
                set3=gear_set.set3,
            )

        return merged

    def merge_drive_stats(
        relic_sd: dict[str, float],
        relic_da: dict[str, float],
    ) -> dict[str, float]:
        """Combine relic main stat appearance rates from three modes."""
        merged: dict[str, float] = {}
        all_stats = relic_sd.keys() | relic_da.keys()

        for name in all_stats:
            app_sd = relic_sd.get(name) or 0.0
            app_da = relic_da.get(name) or 0.0

            app_sd = app_sd * rate_sd / rate_combine
            app_da = app_da * rate_da / rate_combine

            merged[name] = app_sd + app_da

        return merged

    # ----------------------------------------------------------------------
    # Helper functions to populate the output dictionary for a character
    # ----------------------------------------------------------------------
    def populate_gear_usage(
        category: str,
        merged_gear: dict[str, MergedGearStats],
        out_dict: dict[str, str | float],
    ) -> None:
        """Write the top GEAR_COUNTS[category] items into out_dict with keys.

        For example: weapons_1, weapons_1_app, weapons_1_round_sd, etc.
        """
        sorted_items = sorted(
            merged_gear.items(),
            key=lambda x: x[1].app,
            reverse=True,
        )
        for i in range(GEAR_COUNTS[category]):
            if i < len(sorted_items):
                name, stats = sorted_items[i]
                out_dict[f"{category}_{i + 1}"] = name
                if category == "artifacts":
                    out_dict[f"{category}_{i + 1}_1"] = stats.set1
                    out_dict[f"{category}_{i + 1}_2"] = stats.set2
                    out_dict[f"{category}_{i + 1}_3"] = stats.set3
                out_dict[f"{category}_{i + 1}_app"] = round(stats.app, 2)
                out_dict[f"{category}_{i + 1}_round_sd"] = stats.round_sd
                out_dict[f"{category}_{i + 1}_round_da"] = stats.round_da
            else:
                out_dict[f"{category}_{i + 1}"] = ""
                if category == "artifacts":
                    out_dict[f"{category}_{i + 1}_1"] = ""
                    out_dict[f"{category}_{i + 1}_2"] = ""
                    out_dict[f"{category}_{i + 1}_3"] = ""
                out_dict[f"{category}_{i + 1}_app"] = 0.0
                out_dict[f"{category}_{i + 1}_round_sd"] = 0
                out_dict[f"{category}_{i + 1}_round_da"] = 0

    def populate_drive_stat_usage(
        part: str,
        merged_stats: dict[str, float],
        out_dict: dict[str, str | float],
    ) -> None:
        """Write top GEAR_COUNTS[part] main stats into out_dict.

        Write with keys like drive_slot_4_1, drive_slot_4_1_app, etc.
        """
        sorted_items = sorted(merged_stats.items(), key=lambda x: x[1], reverse=True)
        for i in range(GEAR_COUNTS[part]):
            if i < len(sorted_items):
                name, app = sorted_items[i]
                out_dict[f"drive_{part}_{i + 1}"] = name
                out_dict[f"drive_{part}_{i + 1}_app"] = round(app, 2)
            else:
                out_dict[f"drive_{part}_{i + 1}"] = ""
                out_dict[f"drive_{part}_{i + 1}_app"] = 0.0

    # Helper to fetch an attribute with a default value
    def get_val(
        dict_obj: dict[str, FullCharacterStats] | dict[str, BaseCharacterStats],
        attr: str,
        char: str,
    ) -> float | int:
        if char in dict_obj:
            return getattr(dict_obj[char], attr)
        return 0.0 if "app_rate" in attr else 0

    boss_suffixes = ["", "_boss_1", "_boss_2", "_boss_3"]
    variants = ["", "_e1", "_s0"]
    fields = ["app_rate", "avg_round"]

    output_data: list[dict[str, float | str]] = []

    for char in character_keys:
        # Base dictionary for this character (output format)
        out: dict[str, float | str] = {"char": char}

        # ----- 1. Simple fields (appearance rates, average score, samples) -----
        for is_prev_mode in (False, True):
            suf = "_prev" if is_prev_mode else ""

            # Mode tuples: (name, base, e1, s0, boss1_base, boss1_e1, boss1_s0, ...)
            base_modes = [
                ("sd", raw_full[f"sd{suf}"]),
                ("da", raw_full[f"da{suf}"]),
            ]

            for mode, base in base_modes:
                for boss_idx, boss_suf in enumerate(boss_suffixes):
                    for var_off, var_suf in enumerate(variants):
                        is_base = boss_idx + var_off == 0
                        data_dict = (
                            base if is_base else raw[f"{mode}{boss_suf}{var_suf}{suf}"]
                        )

                        # Additional e0s1 field for base variant only
                        if var_off == 0:
                            e0s1_key = f"app_rate_{mode}{boss_suf}_e0s1{suf}"
                            out[e0s1_key] = get_val(data_dict, "app_rate_m0", char)
                        for field in fields:
                            key = f"{field}_{mode}{boss_suf}{var_suf}{suf}"
                            out[key] = get_val(data_dict, field, char)

                # Overall sample info (from base_data, no boss suffix)
                out[f"sample_{mode}{suf}"] = get_val(base, "sample", char)
                out[f"sample_size_players_{mode}{suf}"] = get_val(
                    base,
                    "sample_size_players",
                    char,
                )

        # ----- 3. Mindscape round data (0..6) for base modes -----
        round_modes = [
            ("sd", raw_full["sd"]),
            ("da", raw_full["da"]),
        ]
        for e in range(7):
            out[f"app_{e}"] = 0
            for mode, base in round_modes:
                out[f"round_{e}_{mode}"] = getattr(base[char], f"round_{e}")

        # Set cons_avg to 0, will be used later
        out["cons_avg"] = 0.0

        # ----- 4. Compute mode appearance rates for weighting -----
        # These are used later to weight gear and numeric stats.
        rate_sd = (
            raw_full["sd"][char].app_rate
            if raw_full["sd"][char].app_rate != 0
            and raw_full["sd"][char].weapon_1_app != 0
            else 0
        )
        rate_da = (
            raw_full["da"][char].app_rate
            if raw_full["da"][char].app_rate != 0
            and raw_full["da"][char].weapon_1_app != 0
            else 0
        )
        rate_combine = rate_sd + rate_da or 1  # avoid division by zero

        # ----- 5. Merge gear stats from SD and DA -----
        merged_weapons: dict[str, MergedGearStats] = merge_gear_stats(
            sd_usage[char].weapons,
            da_usage[char].weapons,
        )
        merged_artifacts: dict[str, MergedGearStats] = merge_gear_stats(
            sd_usage[char].artifacts,
            da_usage[char].artifacts,
        )

        merged_slot_4: dict[str, float] = merge_drive_stats(
            sd_usage[char].drive_slot_4,
            da_usage[char].drive_slot_4,
        )
        merged_slot_5: dict[str, float] = merge_drive_stats(
            sd_usage[char].drive_slot_5,
            da_usage[char].drive_slot_5,
        )
        merged_slot_6: dict[str, float] = merge_drive_stats(
            sd_usage[char].drive_slot_6,
            da_usage[char].drive_slot_6,
        )

        # ----- 6. Populate output with top gear and drive stats -----
        populate_gear_usage("weapons", merged_weapons, out)
        populate_gear_usage("artifacts", merged_artifacts, out)

        populate_drive_stat_usage("slot_4", merged_slot_4, out)
        populate_drive_stat_usage("slot_5", merged_slot_5, out)
        populate_drive_stat_usage("slot_6", merged_slot_6, out)

        # ----- 7. Weighted average of numeric stats -----
        for stat in NUMERIC_STATS:
            val_sd: float = getattr(raw_full["sd"][char], stat)
            val_da: float = getattr(raw_full["da"][char], stat)

            dividend = val_sd * rate_sd + val_da * rate_da

            # Only modes where the stat is non-zero contribute to the denominator
            divisor = (
                (rate_sd if val_sd != 0 else 0) + (rate_da if val_da != 0 else 0)
            ) or 1

            out[stat] = round(
                # Mindscape data should still be divided with rate_combine
                dividend / (rate_combine if "app_" in stat else divisor),
                2,
            )

        output_data.append(out)

    # ----------------------------------------------------------------------
    # Write final JSON
    # ----------------------------------------------------------------------
    output_path = f"../char_results/{RECENT_PHASE}/builds.json"
    with open(output_path, "w") as out_file:
        json.dump(output_data, out_file, indent=2)


process_chars()
