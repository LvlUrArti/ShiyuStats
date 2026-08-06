"""Compile all ZZZ data."""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pickle import dump as pickle_dump
from pickle import load as pickle_load
from time import time

from comp_rates_config import (
    BASE_RESULT_PATH,
    BOOS_RESULT_PATH,
    BUILD_RESULT_PATH,
    CHAR_RESULT_PATH,
    COMP_RESULT_PATH,
    DUOS_RESULT_PATH,
    RECENT_PHASE,
    RECENT_PHASE_SFX,
    all_stages,
    da_mode,
    mode_sfx,
    skip_random,
    skip_self,
)
from composition import Composition, Stage
from player_phase import OwnedChars, PlayerPhase


@dataclass
class PickleData:
    """Container for pickle data."""

    all_players: dict[str, PlayerPhase]
    all_comps: list[Composition]
    avg_round_stage: dict[str, list[int]]
    sample_size: dict[int | str, dict[str, int | float]]


def save_pickle_data(filename: str, data: PickleData) -> None:
    """Save data to a pickle file."""
    with open(filename, "wb") as f:
        pickle_dump(data, f)


def load_pickle_data(filename: str) -> PickleData:
    """Load data from a pickle file."""
    with open(filename, "rb") as f:
        return pickle_load(f)


def main() -> None:
    """Compile data."""
    start_time = time()
    print("start")

    for make_path in [
        f"../{BOOS_RESULT_PATH}",
        f"../{COMP_RESULT_PATH}",
        f"../{BUILD_RESULT_PATH}",
        f"../{CHAR_RESULT_PATH}",
        f"../{DUOS_RESULT_PATH}",
        "../data/pickle",
    ]:
        if not os.path.exists(make_path):
            os.makedirs(make_path)

    if os.path.isfile("../../uids.csv"):
        with open("../../uids.csv", encoding="UTF8") as f:
            reader = csv.reader(f, delimiter=",")
            self_uids = set(next(iter(reader)))
    else:
        self_uids: set[str] = set()

    filename = RECENT_PHASE_SFX.replace("_sd", "")
    with (
        open(f"../data/raw_csvs_real/{filename}.csv")
        if os.path.exists("../data/raw_csvs_real/")
        else open(f"../data/raw_csvs/{filename}.csv")
    ) as f:
        reader = list(csv.DictReader(f))
    all_comps: list[Composition] = []
    if da_mode:
        all_chambers = ["1", "2"] if "2-1" in all_stages else ["1"]
    else:
        all_chambers = ["1", "2", "3", "4", "5", "6", "7"]

    # uid_freq_comp will help detect duplicate UIDs
    uid_freq_comp: dict[str, int] = {}
    last_uid = "0"
    skip_uid = False
    sd_star_num = {
        "B": 1,
        "A": 2,
        "S": 3,
    }

    for line in reader:
        player = line["uid"]
        star_num = int(line["star"]) if da_mode else sd_star_num[line["rating"]]
        if skip_self and player in self_uids:
            continue
        if skip_random and player not in self_uids:
            continue
        if player != last_uid:
            skip_uid = False
            if player in uid_freq_comp:
                skip_uid = True
            else:
                uid_freq_comp[player] = 1
        last_uid = player
        if not skip_uid:
            if da_mode:
                adversity_mode = int(line["floor"]) > 3
                stage = 2 if adversity_mode else 1
                node = 1 if adversity_mode else int(line["floor"])
            else:
                stage = int(line["floor"])
                node = int(line["node"])

            comp_chars_temp: list[str] = []
            cons_chars_temp: list[int] = []
            for i in range(1, 4):
                if line[f"ch{i}"] != "":
                    comp_chars_temp.append(line[f"ch{i}"])
                    if "ch1_rank" in line:
                        cons_chars_temp.append(int(line[f"ch{i}_rank"]))
            if comp_chars_temp:
                comp = Composition(
                    player=player,
                    comp_chars=comp_chars_temp,
                    round_num=int(line["score"]),
                    star_num=star_num,
                    room=Stage(stage, node),
                    bangboo=line.get("bangboo", line.get("ch4")),
                    comp_chars_cons=cons_chars_temp,
                )
                all_comps.append(comp)

    sample_size: dict[int | str, dict[str, int | float]] = {}
    for chamber_num in all_chambers:
        sample_size[chamber_num] = {}
    avg_round_stage: dict[str, list[int]] = {}
    for chamber_num in all_chambers:
        avg_round_stage[chamber_num] = []

    with (
        open("../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv")
        if os.path.exists("../data/raw_csvs_real/")
        else open("../data/raw_csvs/" + RECENT_PHASE + "_char.csv")
    ) as f:
        reader = list(csv.DictReader(f))

    all_players: dict[str, PlayerPhase] = {}
    player = PlayerPhase(last_uid)
    # uid_freq_char and last_uid will help detect duplicate UIDs
    last_uid = "0"
    uid_freq_char: set[str] = set()

    # Append lines
    for line in reader:
        if line["uid"] in uid_freq_comp:
            if line["uid"] != last_uid:
                skip_uid = False
                if line["uid"] in uid_freq_char:
                    skip_uid = True
                else:
                    uid_freq_char.add(line["uid"])
            if not skip_uid:
                if line["uid"] != last_uid:
                    all_players[last_uid] = player
                    last_uid = line["uid"]
                    player = PlayerPhase(last_uid)
                player.add_character(
                    line["name"],
                    OwnedChars(
                        level=line["level"],
                        cons=line["cons"],
                        weapon=line["weapon"],
                        element=line["element"],
                        artifacts=line["artifacts"],
                    ),
                )
    all_players[last_uid] = player

    for comp in all_comps:
        if comp.player not in all_players:
            all_players[comp.player] = PlayerPhase(comp.player)
        all_players[comp.player].add_comp(comp)

    with open(f"../{BASE_RESULT_PATH}/uids.csv", "w", newline="") as f:
        csv_writer = csv.writer(f)
        for uid in uid_freq_comp:
            csv_writer.writerow([uid])

    data = PickleData(
        all_players=all_players,
        all_comps=all_comps,
        avg_round_stage=avg_round_stage,
        sample_size=sample_size,
    )

    save_pickle_data("../data/pickle/data" + mode_sfx + ".pkl", data)

    cur_time = time()
    print("done csv: ", (cur_time - start_time), "s")


if __name__ == "__main__":
    main()
