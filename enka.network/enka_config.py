"""Config file for enkanetwork.py."""

from __future__ import annotations

import csv
import json
import os.path
import sys

sys.path.append("../scripts/")
from comp_rates_config import RECENT_PHASE, da_mode
from enka.zzz import AgentStatType  # pyright: ignore[reportMissingTypeStubs]

skip_self = False
skip_random = False
print_chart = False

# stats.py
comp_stats = []
check_char = True
check_char_name = "Yanqing"
check_stats: list[str] = []

# stat.py
run_all_chars = True
run_chars_name = ["Miyabi"]


phase_num = str(RECENT_PHASE)
if da_mode:
    phase_num = phase_num + "_da"

with open("../data/drive_sets.json") as f:
    relics_data = json.load(f)

with open(".enka_py/assets/zzz/equipments.json") as f:
    drive_data = json.load(f)

with open("../data/characters.json") as f:
    characters = json.load(f)

trailblazer_ids: list[str] = []
for char in characters.values():
    if "trailblazer_ids" in char:
        trailblazer_ids.extend(
            trailblazer_id for trailblazer_id in char["trailblazer_ids"]
        )

if os.path.exists("../char_results/uids.csv"):
    with open("../char_results/uids.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        uids = list(reader)
        uids = [int(uid[0]) for uid in uids]
        uids = list(dict.fromkeys(uids))
else:
    uids = [1301113181]

for make_path in [
    "results_real/" + phase_num,
]:
    if not os.path.exists(make_path):
        os.makedirs(make_path)

filename = "../data/raw_csvs_real/" + RECENT_PHASE + "_build"
char_filename = filename + "_char.csv"
filename = filename + ".csv"


def to_snake_case(key: str) -> str:
    """Convert strings to snake_case (handles spaces, camelCase, etc.)."""
    return key.replace(" ", "_").lower()


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
    AgentStatType.ICE_DMG_BONUS: "DMG Bonus",
    AgentStatType.FIRE_DMG_BONUS: "DMG Bonus",
    AgentStatType.ETHER_DMG_BONUS: "DMG Bonus",
    AgentStatType.ELECTRIC_DMG_BONUS: "DMG Bonus",
    AgentStatType.PHYSICAL_DMG_BONUS: "DMG Bonus",
}

desired_stats_keys: list[str] = list(dict.fromkeys(desired_stats_dict.values()))

substat_keys = [
    "Percent HP",
    "Percent ATK",
    "Percent DEF",
    "CRIT Rate",
    "CRIT DMG",
    "PEN",
    "Anomaly Proficiency",
]

skill_keys = [
    "BASIC_ATK",
    "SPECIAL_ATK",
    "DASH",
    "ULTIMATE",
    "CORE_SKILL",
    "ASSIST",
]

output_keys = [
    "uid",
    "player_level",
    "character",
    "char_level",
    "element",
    "w_engine",
    "w_engine_level",
    *[to_snake_case(key) for key in skill_keys],
    *[to_snake_case(key) for key in desired_stats_keys],
    *[f"{to_snake_case(key)}_sub" for key in substat_keys],
    "drive_slot_4",
    "drive_slot_5",
    "drive_slot_6",
    "drive_sets",
]
