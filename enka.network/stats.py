"""Calculate stats."""

from __future__ import annotations

import csv
import json
import operator
import os
import statistics
import sys
from dataclasses import dataclass
from sys import exit as sys_exit

from enka_config import (
    RECENT_PHASE,
    skip_random,
    skip_self,
    substat_dict,
    to_snake_case,
)
from send2trash import send2trash

sys.path.append("../scripts/")
from typing import TYPE_CHECKING

from comp_rates_config import (
    BUILD_RESULT_PATH,
    CHAR_RESULT_PATH,
    CHARS_INFO,
    mode_sfx,
)
from csv_to_pickle import PickleData, load_pickle_data

if TYPE_CHECKING:
    from player_phase import PlayerPhase

with open(f"../{CHAR_RESULT_PATH}/all.csv") as f:
    builds = list(csv.DictReader(f, delimiter=","))


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

    # Rupture class released in 2.0
    sheer_force: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, str | int | float]) -> CharacterData:
        """Convert dictionary (from CSV row) to a CharacterData instance."""
        return cls(**data)  # pyright: ignore[reportArgumentType]


def transform_csv_data(file_path: str) -> dict[str, dict[str, CharacterData]]:
    """Transform the CSV data into a dictionary of UID → {character: CharacterData}."""
    result: dict[str, dict[str, CharacterData]] = {}

    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            # Get the character name (third column)
            uid = str(row.pop("uid"))
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
try:
    data = transform_csv_data(filename)
except FileNotFoundError:
    print("No build data found.")
    data = {}

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

loaded_data: PickleData = load_pickle_data("../data/pickle/data" + mode_sfx + ".pkl")

all_players: dict[str, PlayerPhase] = loaded_data.all_players
spiral_rows: dict[str, dict[str, int]] = {}
for cur_uid, cur_player in all_players.items():
    spiral_rows[cur_uid] = {}
    for player_comp in cur_player.chambers.values():
        for char in player_comp.characters:
            if char not in spiral_rows[cur_uid]:
                spiral_rows[cur_uid][char] = 0
            spiral_rows[cur_uid][char] += 1

chars.extend(build["char"] for build in builds)

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
                msg = f"Unknown character: {char}"
                raise ValueError(msg)
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
                    mainstat = getattr(cur_char, i)
                    if mainstat:
                        if mainstat in mainstats[char][i]:
                            mainstats[char][i][mainstat] += 1
                        else:
                            mainstats[char][i][mainstat] = 1

for char, stat_char in stats.items():
    if stat_char.sample_size > 0:
        for stat, stat_count in stat_char.stats_count.items():
            if not stat_count:
                stat_char.stats_write[stat] = 0
            else:
                stat_char.stats_write[stat] = round(statistics.mean(stat_count), 2)

        stat_char.stats_write["sample_size_players"] = stat_char.sample_size_players

        for stat in mainstats[char]:
            sorted_stats = sorted(
                mainstats[char][stat].items(),
                key=operator.itemgetter(1),
                reverse=True,
            )
            mainstats[char][stat] = dict(sorted_stats)
            for mainstat in mainstats[char][stat]:
                mainstats[char][stat][mainstat] = round(
                    mainstats[char][stat][mainstat] / stat_char.sample_size,
                    4,
                )
            mainstatlist = list(mainstats[char][stat])
            i = 0
            while i < 3:
                if i >= len(mainstatlist):
                    stat_char.stats_write[stat + "_" + str(i + 1)] = "-"
                    stat_char.stats_write[stat + "_" + str(i + 1) + "_app"] = "-"
                else:
                    stat_char.stats_write[stat + "_" + str(i + 1)] = mainstatlist[i]
                    stat_char.stats_write[stat + "_" + str(i + 1) + "_app"] = mainstats[
                        char
                    ][stat][mainstatlist[i]]
                i += 1

    else:
        for stat, stat_count in stat_char.stats_count.items():
            if not stat_count:
                stat_char.stats_write[stat] = 0
            else:
                stat_char.stats_write[stat] = 0

        stat_char.stats_write["sample_size_players"] = 0
        for stat in mainstats[char]:
            i = 0
            while i < 3:
                stat_char.stats_write[stat + "_" + str(i + 1)] = "-"
                stat_char.stats_write[stat + "_" + str(i + 1) + "_app"] = "-"
                i += 1

with (
    open(
        f"../{BUILD_RESULT_PATH}/chars.csv",
        "w",
        newline="",
    ) as file1,
    open(
        f"../{BUILD_RESULT_PATH}/demographic.csv",
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
with open(f"../{CHAR_RESULT_PATH}/all.json") as char_file:
    CHARACTERS = json.load(char_file)
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

send2trash(f"../{CHAR_RESULT_PATH}/all.json")
with open(f"../{CHAR_RESULT_PATH}/all.json", "w") as char_file:
    char_file.write(json.dumps(temp_stats, indent=2))
