"""Combine character data."""

# pyright: reportGeneralTypeIssues=false, reportUnknownArgumentType=false, reportOperatorIssue=false, reportIndexIssue=false, reportArgumentType=false, reportUnknownMemberType=false, reportAttributeAccessIssue=false, reportUnnecessaryComparison=false, reportUnknownVariableType=false
from __future__ import annotations

import json
import re

from comp_rates_config import RECENT_PHASE, da_mode
from slugify import slugify

with open("../Comps/prydwen-slug.json") as slug_file:
    slug = json.load(slug_file)

sd_phase = RECENT_PHASE
da_phase = RECENT_PHASE

with open("../data/characters.json") as char_file:
    CHARACTERS = json.load(char_file)
with open("../char_results/" + sd_phase + "/all2.json") as stats:
    sd_dict = json.load(stats)
with open("../char_results/" + sd_phase + "/all_C1.json") as stats:
    sd_dict_e1 = json.load(stats)
with open("../char_results/" + sd_phase + "/all_E0S0.json") as stats:
    sd_dict_s0 = json.load(stats)
with open("../char_results/" + sd_phase + "/5-1.json") as stats:
    sd_dict_boss_1 = json.load(stats)
with open("../char_results/" + sd_phase + "/5-2.json") as stats:
    sd_dict_boss_2 = json.load(stats)
with open("../char_results/" + sd_phase + "/5-3.json") as stats:
    sd_dict_boss_3 = json.load(stats)
with open("../char_results/" + da_phase + "_da/all2.json") as stats:
    da_dict = json.load(stats)
with open("../char_results/" + da_phase + "_da/all_C1.json") as stats:
    da_dict_e1 = json.load(stats)
with open("../char_results/" + da_phase + "_da/all_E0S0.json") as stats:
    da_dict_s0 = json.load(stats)
with open("../char_results/" + da_phase + "_da/1-1.json") as stats:
    da_dict_boss_1 = json.load(stats)
with open("../char_results/" + da_phase + "_da/1-2.json") as stats:
    da_dict_boss_2 = json.load(stats)
with open("../char_results/" + da_phase + "_da/1-3.json") as stats:
    da_dict_boss_3 = json.load(stats)

uses = []
uses_sd: dict[str, dict[str, dict[str, float | dict[str, str]]]] = {}
uses_da: dict[str, dict[str, dict[str, float | dict[str, str]]]] = {}
stats_len = {
    "weapons": str(10),
    "artifacts": str(10),
    "drive_slot_4": str(3),
    "drive_slot_5": str(3),
    "drive_slot_6": str(3),
}

for char in sd_dict:
    char["char"] = slugify(char["char"])
    if char["char"] in slug:
        char["char"] = slug[char["char"]]
    uses_sd[char["char"]] = char.copy()
    uses_sd[char["char"]]["weapons"] = {}
    uses_sd[char["char"]]["artifacts"] = {}
    uses_sd[char["char"]]["drive_slot_4"] = {}
    uses_sd[char["char"]]["drive_slot_5"] = {}
    uses_sd[char["char"]]["drive_slot_6"] = {}
    for stat in char:
        for stat_name in [
            "weapon",
            "artifact",
            "drive_slot_4",
            "drive_slot_5",
            "drive_slot_6",
        ]:
            if (
                re.sub(r"\d(?!.*\d)", "", stat) == stat_name + "_"
                and char[stat] != ""
                and char[stat] != "-"
            ):
                temp_dict = {}
                if stat_name == "artifact":
                    temp_dict["1"] = char[stat + "_1"]
                    temp_dict["2"] = char[stat + "_2"]
                    temp_dict["3"] = char[stat + "_3"]
                temp_dict["app"] = char[stat + "_app"]
                if stat_name in ["weapon", "artifact"]:
                    temp_dict["round_sd"] = char[stat + "_round"]
                    temp_dict["round_da"] = 0.0
                    uses_sd[char["char"]][stat_name + "s"][char[stat]] = temp_dict
                else:
                    uses_sd[char["char"]][stat_name][char[stat]] = temp_dict
for char in da_dict:
    char["char"] = slugify(char["char"])
    if char["char"] in slug:
        char["char"] = slug[char["char"]]
    uses_da[char["char"]] = char.copy()
    uses_da[char["char"]]["weapons"] = {}
    uses_da[char["char"]]["artifacts"] = {}
    uses_da[char["char"]]["drive_slot_4"] = {}
    uses_da[char["char"]]["drive_slot_5"] = {}
    uses_da[char["char"]]["drive_slot_6"] = {}
    for stat in char:
        for stat_name in [
            "weapon",
            "artifact",
            "drive_slot_4",
            "drive_slot_5",
            "drive_slot_6",
        ]:
            if (
                re.sub(r"\d(?!.*\d)", "", stat) == stat_name + "_"
                and char[stat] != ""
                and char[stat] != "-"
            ):
                temp_dict = {}
                if stat_name == "artifact":
                    temp_dict["1"] = char[stat + "_1"]
                    temp_dict["2"] = char[stat + "_2"]
                    temp_dict["3"] = char[stat + "_3"]
                temp_dict["app"] = char[stat + "_app"]
                if stat_name in ["weapon", "artifact"]:
                    temp_dict["round_sd"] = 600
                    temp_dict["round_da"] = char[stat + "_round"]
                    uses_da[char["char"]][stat_name + "s"][char[stat]] = temp_dict
                else:
                    uses_da[char["char"]][stat_name][char[stat]] = temp_dict

for char in CHARACTERS:
    char = slugify(char)
    if char in slug:
        char = slug[char]
    sd_dict_e1_char: dict[str, str] = next(
        (x for x in sd_dict_e1 if x["char"] == char),
        dict[str, str](),
    )
    sd_dict_s0_char: dict[str, str] = next(
        (x for x in sd_dict_s0 if x["char"] == char),
        dict[str, str](),
    )
    sd_dict_boss_1_char: dict[str, str] = next(
        (x for x in sd_dict_boss_1 if x["char"] == char),
        dict[str, str](),
    )
    sd_dict_boss_2_char: dict[str, str] = next(
        (x for x in sd_dict_boss_2 if x["char"] == char),
        dict[str, str](),
    )
    sd_dict_boss_3_char: dict[str, str] = next(
        (x for x in sd_dict_boss_3 if x["char"] == char),
        dict[str, str](),
    )
    da_dict_e1_char: dict[str, str] = next(
        (x for x in da_dict_e1 if x["char"] == char),
        dict[str, str](),
    )
    da_dict_s0_char: dict[str, str] = next(
        (x for x in da_dict_s0 if x["char"] == char),
        dict[str, str](),
    )
    da_dict_boss_1_char: dict[str, str] = next(
        (x for x in da_dict_boss_1 if x["char"] == char),
        dict[str, str](),
    )
    da_dict_boss_2_char: dict[str, str] = next(
        (x for x in da_dict_boss_2 if x["char"] == char),
        dict[str, str](),
    )
    da_dict_boss_3_char: dict[str, str] = next(
        (x for x in da_dict_boss_3 if x["char"] == char),
        dict[str, str](),
    )
    uses_temp = {
        "char": char,
        "app_rate_sd": uses_sd.get(char, {}).get("app_rate", 0),
        "app_rate_sd_e1": sd_dict_e1_char.get("app_rate", 0),
        "app_rate_sd_s0": sd_dict_s0_char.get("app_rate", 0),
        "avg_round_sd": uses_sd.get(char, {}).get("avg_round", 600),
        "avg_round_q1_sd": uses_sd.get(char, {}).get("q1_round", 600),
        "avg_round_sd_e1": sd_dict_e1_char.get("avg_round", 600),
        "avg_round_q1_sd_e1": sd_dict_e1_char.get("q1_round", 600),
        "avg_round_sd_s0": sd_dict_s0_char.get("avg_round", 600),
        "avg_round_q1_sd_s0": sd_dict_s0_char.get("q1_round", 600),
        "app_rate_sd_boss_1": sd_dict_boss_1_char.get("app_rate", 0),
        "avg_round_sd_boss_1": sd_dict_boss_1_char.get("avg_round", 0),
        "avg_round_q1_sd_boss_1": sd_dict_boss_1_char.get("q1_round", 0),
        "app_rate_sd_boss_2": sd_dict_boss_2_char.get("app_rate", 0),
        "avg_round_sd_boss_2": sd_dict_boss_2_char.get("avg_round", 0),
        "avg_round_q1_sd_boss_2": sd_dict_boss_2_char.get("q1_round", 0),
        "app_rate_sd_boss_3": sd_dict_boss_3_char.get("app_rate", 0),
        "avg_round_sd_boss_3": sd_dict_boss_3_char.get("avg_round", 0),
        "avg_round_q1_sd_boss_3": sd_dict_boss_3_char.get("q1_round", 0),
        "sample_sd": uses_sd.get(char, {}).get("sample", 0),
        "sample_size_players_sd": (uses_sd.get(char, {}).get("sample_size_players", 0)),
        "app_rate_da": uses_da.get(char, {}).get("app_rate", 0),
        "app_rate_da_e1": da_dict_e1_char.get("app_rate", 0),
        "app_rate_da_s0": da_dict_s0_char.get("app_rate", 0),
        "avg_round_da": uses_da.get(char, {}).get("avg_round", 0),
        "avg_round_q1_da": uses_da.get(char, {}).get("q1_round", 0),
        "avg_round_da_e1": da_dict_e1_char.get("avg_round", 0),
        "avg_round_q1_da_e1": da_dict_e1_char.get("q1_round", 0),
        "avg_round_da_s0": da_dict_s0_char.get("avg_round", 0),
        "avg_round_q1_da_s0": da_dict_s0_char.get("q1_round", 0),
        "app_rate_da_boss_1": da_dict_boss_1_char.get("app_rate", 0),
        "avg_round_da_boss_1": da_dict_boss_1_char.get("avg_round", 0),
        "avg_round_q1_da_boss_1": da_dict_boss_1_char.get("q1_round", 0),
        "app_rate_da_boss_2": da_dict_boss_2_char.get("app_rate", 0),
        "avg_round_da_boss_2": da_dict_boss_2_char.get("avg_round", 0),
        "avg_round_q1_da_boss_2": da_dict_boss_2_char.get("q1_round", 0),
        "app_rate_da_boss_3": da_dict_boss_3_char.get("app_rate", 0),
        "avg_round_da_boss_3": da_dict_boss_3_char.get("avg_round", 0),
        "avg_round_q1_da_boss_3": da_dict_boss_3_char.get("q1_round", 0),
        "sample_da": uses_da.get(char, {}).get("sample", 0),
        "sample_size_players_da": (uses_da.get(char, {}).get("sample_size_players", 0)),
        "app_0": 0,
        "round_0_sd": uses_sd.get(char, {}).get("round_0", 600),
        "round_0_da": uses_da.get(char, {}).get("round_0", 0),
        "app_1": 0,
        "round_1_sd": uses_sd.get(char, {}).get("round_1", 600),
        "round_1_da": uses_da.get(char, {}).get("round_1", 0),
        "app_2": 0,
        "round_2_sd": uses_sd.get(char, {}).get("round_2", 600),
        "round_2_da": uses_da.get(char, {}).get("round_2", 0),
        "app_3": 0,
        "round_3_sd": uses_sd.get(char, {}).get("round_3", 600),
        "round_3_da": uses_da.get(char, {}).get("round_3", 0),
        "app_4": 0,
        "round_4_sd": uses_sd.get(char, {}).get("round_4", 600),
        "round_4_da": uses_da.get(char, {}).get("round_4", 0),
        "app_5": 0,
        "round_5_sd": uses_sd.get(char, {}).get("round_5", 600),
        "round_5_da": uses_da.get(char, {}).get("round_5", 0),
        "app_6": 0,
        "round_6_sd": uses_sd.get(char, {}).get("round_6", 600),
        "round_6_da": uses_da.get(char, {}).get("round_6", 0),
        "cons_avg": 0,
        "weapons": uses_sd.get(char, {}).get("weapons", {}),
        "artifacts": uses_sd.get(char, {}).get("artifacts", {}),
        "drive_slot_4": uses_sd.get(char, {}).get("drive_slot_4", {}),
        "drive_slot_5": uses_sd.get(char, {}).get("drive_slot_5", {}),
        "drive_slot_6": uses_sd.get(char, {}).get("drive_slot_6", {}),
    }

    rate_sd = float(
        uses_temp["app_rate_sd"]
        if (uses_temp["app_rate_sd"] == 0)
        == (str(uses_sd.get(char, {}).get("weapon_1_app", {})) == 0)
        else 0
    )
    rate_da = float(
        uses_temp["app_rate_da"]
        if (uses_temp["app_rate_da"] == 0)
        == (str(uses_da.get(char, {}).get("weapon_1_app", {})) == 0)
        else 0
    )
    rate_combine = rate_sd + rate_da
    rate_combine = rate_combine if rate_combine else 1

    for stat, stat_item in stats_len.items():
        for item in uses_temp[stat]:
            uses_temp[stat][item]["app"] = round(
                uses_temp[stat][item]["app"] * rate_sd / rate_combine,
                2,
            )
        for item in uses_da.get(char, {}).get(stat, {}):
            if item != "" and item != "-":
                if item in uses_temp[stat]:
                    uses_temp[stat][item]["app"] = round(
                        uses_temp[stat][item]["app"]
                        + uses_da[char][stat][item]["app"] * rate_da / rate_combine,
                        2,
                    )
                    if stat in ["weapons", "artifacts"]:
                        uses_temp[stat][item]["round_da"] = uses_da[char][stat][item][
                            "round_da"
                        ]
                else:
                    uses_temp[stat][item] = uses_da[char][stat][item].copy()
                    uses_temp[stat][item]["app"] = round(
                        uses_temp[stat][item]["app"] * rate_da / rate_combine,
                        2,
                    )

        sorted_items = sorted(
            uses_temp[stat].items(),
            key=lambda t: t[1]["app"],
            reverse=True,
        )
        uses_temp[stat] = dict(sorted_items)

        for i in range(int(stat_item)):
            if i < len(list(uses_temp[stat])):
                uses_temp[stat + "_" + str(i + 1)] = list(uses_temp[stat])[i]
                if stat == "artifacts":
                    uses_temp[stat + "_" + str(i + 1) + "_1"] = list(
                        uses_temp[stat].values(),
                    )[i]["1"]
                    uses_temp[stat + "_" + str(i + 1) + "_2"] = list(
                        uses_temp[stat].values(),
                    )[i]["2"]
                    uses_temp[stat + "_" + str(i + 1) + "_3"] = list(
                        uses_temp[stat].values(),
                    )[i]["3"]
                uses_temp[stat + "_" + str(i + 1) + "_app"] = list(
                    uses_temp[stat].values(),
                )[i]["app"]
                if stat in ["weapons", "artifacts"]:
                    uses_temp[stat + "_" + str(i + 1) + "_round_sd"] = list(
                        uses_temp[stat].values(),
                    )[i]["round_sd"]
                    uses_temp[stat + "_" + str(i + 1) + "_round_da"] = list(
                        uses_temp[stat].values(),
                    )[i]["round_da"]
            else:
                uses_temp[stat + "_" + str(i + 1)] = ""
                if stat == "artifacts":
                    uses_temp[stat + "_" + str(i + 1) + "_1"] = ""
                    uses_temp[stat + "_" + str(i + 1) + "_2"] = ""
                    uses_temp[stat + "_" + str(i + 1) + "_3"] = ""
                uses_temp[stat + "_" + str(i + 1) + "_app"] = 0.0
                if stat in ["weapons", "artifacts"]:
                    uses_temp[stat + "_" + str(i + 1) + "_round_sd"] = 600
                    uses_temp[stat + "_" + str(i + 1) + "_round_da"] = 0.0
        del uses_temp[stat]

    stats_iter = [
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
    for stat in stats_iter:
        stat_sd = uses_sd.get(char, {}).get(stat) or 0
        stat_da = uses_da.get(char, {}).get(stat) or 0
        uses_temp[stat] = round(
            ((stat_sd * rate_sd) + (stat_da * rate_da))
            / (((rate_sd) if stat_sd != 0 else 0) + ((rate_da) if stat_da != 0 else 0))
            if (rate_sd * stat_sd + rate_da * stat_da != 0)
            else 1,
            2,
        )
    uses.append(uses_temp)

phase_num = RECENT_PHASE
if da_mode:
    phase_num = phase_num + "_da"

with open("../char_results/" + phase_num + "/builds.json", "w") as out_file:
    out_file.write(json.dumps(uses, indent=2))
