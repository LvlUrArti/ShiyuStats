"""Config file for enkanetwork.py."""

# pyright: reportMissingTypeStubs=false

from __future__ import annotations

import csv
import os.path
import sys
from pathlib import Path

sys.path.append("../scripts/")
from comp_rates_config import BASE_RESULT_PATH, RECENT_PHASE
from enka.zzz import AgentStatType, SkillType, StatType

skip_self = False
skip_random = False
print_chart = False

# stat.py
run_all_chars = True
run_chars_name = ["Miyabi"]


if os.path.exists(f"../{BASE_RESULT_PATH}/uids.csv"):
    with open(f"../{BASE_RESULT_PATH}/uids.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        uids = list(reader)
        uids = [int(uid[0]) for uid in uids]
        uids = list(dict.fromkeys(uids))
else:
    uids = [1301113181]

make_path = "results_real/" + RECENT_PHASE
if not os.path.exists(make_path):
    os.makedirs(make_path)

filename = "../data/raw_csvs_real/" + RECENT_PHASE + "_build"
char_filename = filename + "_char.csv"
filename = filename + ".csv"


def get_start_index(id_list: list[int]) -> int:
    """Determine the index in `id_list` from which to start collecting new data."""
    # If CSV doesn't exist, start from the beginning
    if not Path(filename).exists():
        return 0

    # Read the last row of the CSV
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Get the last row by iterating to the end
        last_row = None
        for row in reader:
            last_row = row
        if last_row is None:  # only header or empty
            return 0

    # Find the index of the last ID in the original list
    try:
        idx = id_list.index(int(last_row["uid"]))
    except ValueError:
        # ID is not in the list
        return 0

    # Resume from the next ID
    return idx + 1


start_index = get_start_index(uids)


def to_snake_case(key: str) -> str:
    """Convert strings to snake_case (handles spaces, camelCase, etc.)."""
    return key.replace(" ", "_").lower()


dmg_bonus_dict: dict[AgentStatType, str] = {
    AgentStatType.ICE_DMG_BONUS: "DMG Bonus",
    AgentStatType.FIRE_DMG_BONUS: "DMG Bonus",
    AgentStatType.ETHER_DMG_BONUS: "DMG Bonus",
    AgentStatType.ELECTRIC_DMG_BONUS: "DMG Bonus",
    AgentStatType.PHYSICAL_DMG_BONUS: "DMG Bonus",
    AgentStatType.WIND_DMG_BONUS: "DMG Bonus",
}


desired_stats_dict: dict[AgentStatType, str] = {
    AgentStatType.MAX_HP: "Base HP",
    AgentStatType.ATK: "Base ATK",
    AgentStatType.DEF: "Base DEF",
    AgentStatType.IMPACT: "Base Impact",
    AgentStatType.CRIT_RATE: "CRIT Rate",
    AgentStatType.CRIT_DMG: "CRIT DMG",
    AgentStatType.ANOMALY_MASTERY: "Anomaly Mastery",
    AgentStatType.ANOMALY_PROFICIENCY: "Anomaly Proficiency",
    AgentStatType.PEN_RATIO: "PEN Ratio",
    AgentStatType.PEN: "PEN",
    AgentStatType.ENERGY_REGEN: "Base Energy Regen",
    AgentStatType.SHEER_FORCE: "Sheer Force",
    **dmg_bonus_dict,
}

desired_stats_keys: list[str] = list(dict.fromkeys(desired_stats_dict.values()))

substat_dict = {
    StatType.HP_PERCENT: "Percent HP",
    StatType.ATK_PERCENT: "Percent ATK",
    StatType.DEF_PERCENT: "Percent DEF",
    StatType.CRIT_RATE_FLAT: "CRIT Rate",
    StatType.CRIT_DMG_FLAT: "CRIT DMG",
    StatType.PEN_RATIO_FLAT: "PEN",
    StatType.ANOMALY_PRO_FLAT: "Anomaly Proficiency",
}

skill_dict = {
    SkillType.BASIC_ATK: "BASIC_ATK",
    SkillType.SPECIAL_ATK: "SPECIAL_ATK",
    SkillType.DASH: "DASH",
    SkillType.ULTIMATE: "ULTIMATE",
    SkillType.CORE_SKILL: "CORE_SKILL",
    SkillType.ASSIST: "ASSIST",
}

output_keys = [
    "uid",
    "player_level",
    "character",
    "char_level",
    "element",
    "w_engine",
    "w_engine_level",
    *[to_snake_case(key) for key in skill_dict.values()],
    *[to_snake_case(key) for key in desired_stats_keys],
    *[f"{to_snake_case(key)}_sub" for key in substat_dict.values()],
    "drive_slot_4",
    "drive_slot_5",
    "drive_slot_6",
    "drive_sets",
]
