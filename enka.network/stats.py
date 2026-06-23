"""Calculate stats."""

from __future__ import annotations

import csv
import json
import operator
import os
import statistics
from dataclasses import dataclass
from sys import exit as sys_exit

import numpy as np
from enka_config import (
    RECENT_PHASE,
    da_mode,
    phase_num,
    skip_random,
    skip_self,
    substat_dict,
    to_snake_case,
)

from scripts.comp_rates_config import CHARS_INFO

with open(
    (
        "../data/raw_csvs_real/"
        if os.path.exists("../data/raw_csvs_real/")
        else "../data/raw_csvs/"
    )
    + phase_num
    + ".csv",
) as f:
    reader = csv.reader(f, delimiter=",")
    headers = next(reader)
    spiral = list(reader)

with open("../results/char_results/" + phase_num + "/all.csv") as f:
    reader = csv.reader(f, delimiter=",")
    headers = next(reader)
    builds = np.array(list(reader))


@dataclass
class CharacterData:
    """Stores all attributes from the CSV (except 'character')."""

    player_level: int
    char_level: int
    w_engine_level: int
    basic_atk: int
    special_atk: int
    dash: int
    ultimate: int
    core_skill: int
    assist: int
    base_hp: int
    base_atk: int
    base_def: int
    base_impact: int
    sheer_force: int
    crit_rate: float
    crit_dmg: float
    anomaly_mastery: int
    anomaly_proficiency: int
    pen_ratio: float
    pen: int
    base_energy_regen: int
    dmg_bonus: float
    percent_hp_sub: float
    percent_atk_sub: float
    percent_def_sub: float
    crit_rate_sub: float
    crit_dmg_sub: float
    pen_sub: int
    anomaly_proficiency_sub: int

    # Unused, but still needed for dictionary conversion
    element: str
    w_engine: str
    drive_slot_4: str
    drive_slot_5: str
    drive_slot_6: str
    drive_sets: str

    @classmethod
    def from_dict(cls, data: dict[str, str | int | float]) -> CharacterData:
        """Convert dictionary (from CSV row) to a CharacterData instance."""
        return cls(**data)  # pyright: ignore[reportArgumentType]


def transform_csv_data(file_path: str) -> dict[int, dict[str, CharacterData]]:
    """Transform the CSV data into a dictionary of UID → {character: CharacterData}."""
    result: dict[int, dict[str, CharacterData]] = {}

    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            # Get the character name (third column)
            uid = int(row.pop("uid"))
            character = row.pop("character")

            # Create a copy of the row without the character key
            processed_data = {k: v for k, v in row.items() if k != "character"}

            # Convert numeric values to appropriate types
            for key, value in processed_data.items():
                if value.replace(".", "", 1).isdigit():  # Check if numeric
                    if "." in value:  # Float
                        processed_data[key] = float(value)
                    else:  # Integer
                        processed_data[key] = int(value)
                elif value == "":  # Empty string to None
                    processed_data[key] = None

            # Group by UID → {character: CharacterData}
            if uid not in result:
                result[uid] = {}
            result[uid][character] = CharacterData.from_dict(processed_data)

    return result


if os.path.exists("../data/raw_csvs_real/"):
    filename = "../data/raw_csvs_real/" + RECENT_PHASE + "_build.csv"
else:
    filename = "../data/raw_csvs/" + RECENT_PHASE + "_build.csv"
data = transform_csv_data(filename)

type_hints = CharacterData.__annotations__
statkeys = [key for key, type_ in type_hints.items() if type_ != "str"]


class StatsChar:
    """Represent a character's stats."""

    def __init__(self, char: str) -> None:
        """Initialize. Takes in a character name, as a string."""
        self.name = char
        self.stats_count: dict[str, list[float]] = {key: [] for key in statkeys}
        self.stats_write: dict[str, float | str] = dict.fromkeys(statkeys, 0)
        self.sample_size = 0
        self.sample_size_players = 0


chars: list[str] = []
stats: dict[str, StatsChar] = {}
median: dict[str, dict[str, float]] = {}
mean: dict[str, dict[str, float]] = {}
mainstats: dict[str, dict[str, dict[str, float]]] = {}

spiral_rows: dict[int, dict[str, int]] = {}
for spiral_row in spiral:
    room_num = int(spiral_row[1])
    if (room_num > 4 or da_mode) and (
        spiral_row[3] == "S" or (da_mode and spiral_row[2] == "3")
    ):
        cur_uid = int(spiral_row[0])
        if int(cur_uid) not in spiral_rows:
            spiral_rows[int(cur_uid)] = {}
        for i in range(5 + (1 if da_mode else 0), 11, 2):
            char = spiral_row[i]
            if char not in spiral_rows[cur_uid]:
                spiral_rows[cur_uid][char] = 0
            spiral_rows[cur_uid][char] += 1

chars.extend(build[0] for build in builds)

for char in chars:
    stats[char] = StatsChar(char)
    mean[char] = dict.fromkeys(statkeys, 0)
    median[char] = mean[char].copy()
    mainstats[char] = {
        "drive_slot_4": {},
        "drive_slot_5": {},
        "drive_slot_6": {},
    }

count = 0
mainstatkeys: list[str] = list(mainstats[chars[0]].keys())
substatkeys: list[str] = [f"{to_snake_case(key)}_sub" for key in substat_dict.values()]

if os.path.isfile("../../uids.csv"):
    with open("../../uids.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        self_uids = next(iter(reader))
else:
    self_uids = []

for uid in data:
    cur_uid = uid
    if skip_self and str(cur_uid) in self_uids:
        continue
    if skip_random and str(cur_uid) not in self_uids:
        continue
    last_uid = cur_uid
    count += 1

    if cur_uid in spiral_rows:
        for char in data[uid]:
            if char not in chars:
                print(char, "not exist")
                sys_exit()
            if char in spiral_rows[cur_uid]:
                stats[char].sample_size_players += 1
                cur_char = data[uid][char]
                stats[char].sample_size += 1
                for key in statkeys:
                    value = getattr(cur_char, key)
                    value = 0 if value is None else value
                    if isinstance(value, str):
                        print(uid, char, key, value)
                        sys_exit()
                    stats[char].stats_count[key].append(value)
                for i in mainstats[char]:
                    if getattr(cur_char, i) in mainstats[char][i]:
                        mainstats[char][i][getattr(cur_char, i)] += 1
                    else:
                        mainstats[char][i][getattr(cur_char, i)] = 1

copy_chars = chars.copy()
for char in copy_chars:
    if stats[char].sample_size > 0:
        for stat in stats[char].stats_count:
            if not stats[char].stats_count[stat]:
                stats[char].stats_write[stat] = 0
            else:
                stats[char].stats_write[stat] = round(
                    statistics.mean(stats[char].stats_count[stat]),
                    2,
                )

        stats[char].stats_write["sample_size_players"] = stats[char].sample_size_players

        for stat in mainstats[char]:
            sorted_stats = sorted(
                mainstats[char][stat].items(),
                key=operator.itemgetter(1),
                reverse=True,
            )
            mainstats[char][stat] = dict(sorted_stats)
            for mainstat in mainstats[char][stat]:
                mainstats[char][stat][mainstat] = round(
                    mainstats[char][stat][mainstat] / stats[char].sample_size,
                    4,
                )
            mainstatlist = list(mainstats[char][stat])
            i = 0
            while i < 3:
                if i >= len(mainstatlist):
                    stats[char].stats_write[stat + "_" + str(i + 1)] = "-"
                    stats[char].stats_write[stat + "_" + str(i + 1) + "_app"] = "-"
                else:
                    stats[char].stats_write[stat + "_" + str(i + 1)] = mainstatlist[i]
                    stats[char].stats_write[stat + "_" + str(i + 1) + "_app"] = (
                        mainstats[char][stat][mainstatlist[i]]
                    )
                i += 1

    else:
        for stat in stats[char].stats_count:
            if not stats[char].stats_count[stat]:
                stats[char].stats_write[stat] = 0
            else:
                stats[char].stats_write[stat] = 0

        stats[char].stats_write["sample_size_players"] = 0
        for stat in mainstats[char]:
            i = 0
            while i < 3:
                stats[char].stats_write[stat + "_" + str(i + 1)] = "-"
                stats[char].stats_write[stat + "_" + str(i + 1) + "_app"] = "-"
                i += 1

exist_real = os.path.exists("results_real")
with (
    open(
        "results_real/chars.csv" if exist_real else "results/chars.csv",
        "w",
        newline="",
    ) as file1,
    open(
        "results_real/demographic.csv" if exist_real else "results/demographic.csv",
        "w",
        newline="",
    ) as file2,
):
    csv_writer = csv.writer(file1)
    csv_writer2 = csv.writer(file2)
    del stats[chars[0]].sample_size
    csv_writer.writerow(["name", *stats[chars[0]].stats_write.keys()])
    for char in chars:
        if char != chars[0]:
            del stats[char].sample_size
        csv_writer.writerow([stats[char].name, *stats[char].stats_write.values()])
        csv_writer2.writerow([char + ": " + str(stats[char].sample_size_players)])

temp_stats: list[str] = []
with open("../results/char_results/" + phase_num + "/all.json") as char_file:
    CHARACTERS = json.load(char_file)
with open(
    "../results/char_results/" + phase_num + "/appearance_combine.json",
) as app_char_file:
    APP = json.load(app_char_file)
with open(
    "../results/char_results/" + phase_num + "/rounds_combine.json",
) as round_char_file:
    ROUND = json.load(round_char_file)
for iter_char, char_value in enumerate(stats.values()):
    iterate_value_app: list[str] = []
    for i in range(3):
        iterate_value_app.append("drive_slot_4_" + str(i + 1) + "_app")
        iterate_value_app.append("drive_slot_5_" + str(i + 1) + "_app")
        iterate_value_app.append("drive_slot_6_" + str(i + 1) + "_app")
    for value in iterate_value_app:
        if isinstance(char_value.stats_write[value], float):
            char_value.stats_write[value] = round(
                float(char_value.stats_write[value]) * 100,
                2,
            )
        else:
            char_value.stats_write[value] = 0.00

    char_value.name = CHARS_INFO[char_value.name].slug
    if char_value.name == CHARACTERS[iter_char]["char"]:
        del char_value.name
    else:
        print(char_value.name)
        print(CHARACTERS[iter_char]["char"])
        sys_exit()

    temp_stats.append(CHARACTERS[iter_char] | char_value.stats_write)

if not os.path.exists("../results/char_results/" + phase_num):
    os.mkdir("../results/char_results/" + phase_num)

with open("../results/char_results/" + phase_num + "/all2.json", "w") as char_file:
    char_file.write(json.dumps(temp_stats, indent=2))
