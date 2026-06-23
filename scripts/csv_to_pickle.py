"""Compile all ZZZ data."""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pickle import dump as pickle_dump
from pickle import load as pickle_load
from time import time

from comp_rates_config import (
    CHARS_INFO,
    RECENT_PHASE,
    da_mode,
    skip_random,
    skip_self,
)
from composition import Composition
from player_phase import PlayerPhase


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
        "../results",
        "../results/comp_results",
        "../results/comp_results/json",
        "../enka.network",
        "../enka.network/results_real",
        "../results/char_results",
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

    da_filename = "_da" if da_mode else ""
    with (
        open("../data/raw_csvs_real/" + RECENT_PHASE + da_filename + ".csv")
        if os.path.exists("../data/raw_csvs_real/")
        else open("../data/raw_csvs/" + RECENT_PHASE + da_filename + ".csv")
    ) as f:
        stats = f
        reader = csv.reader(stats)
        next(reader)
        reader = list(reader)
    all_comps: list[Composition] = []
    all_chambers = ["1"] if da_mode else ["1", "2", "3", "4", "5", "6", "7"]

    # uid_freq_comp will help detect duplicate UIDs
    uid_freq_comp: dict[str, int] = {}
    last_uid = "0"
    skip_uid = False

    for line in reader:
        score = line[3] if da_mode else line[4]
        star_num = 0
        match str(line[3]):
            case "B":
                star_num = 1
            case "A":
                star_num = 2
            case "S":
                star_num = 3
            case _:
                if not (da_mode):
                    print("Unknown star num")
                else:
                    star_num = int(line[2])
        if skip_self and line[0] in self_uids:
            continue
        if skip_random and line[0] not in self_uids:
            continue
        if line[0] != last_uid:
            skip_uid = False
            if line[0] in uid_freq_comp:
                skip_uid = True
            else:
                uid_freq_comp[line[0]] = 1
        last_uid = line[0]
        if not skip_uid:
            stage = str(line[1])
            comp_chars_temp: list[str] = []
            cons_chars_temp: list[int] = []
            for i in [6, 8, 10] if da_mode else [5, 7, 9]:
                if line[i] != "" and line[i] in CHARS_INFO:
                    comp_chars_temp.append(line[i])
                    cons_chars_temp.append(int(float(line[i + 1])))
            if comp_chars_temp:
                comp = Composition(
                    line[0],
                    comp_chars_temp,
                    score,
                    star_num,
                    "1-" + stage if da_mode else stage + "-" + str(line[2]),
                    line[12] if da_mode else line[11],
                    cons_chars_temp,
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
        stats = f
        reader = csv.reader(stats)
        next(reader)
        reader = list(reader)

    all_players: dict[str, PlayerPhase] = {}
    player = PlayerPhase(last_uid)
    # uid_freq_char and last_uid will help detect duplicate UIDs
    last_uid = "0"
    uid_freq_char: set[str] = set()

    # Append lines
    for line in reader:
        line[1] = RECENT_PHASE
        if line[0] in uid_freq_comp:
            if line[0] != last_uid:
                skip_uid = False
                if line[0] in uid_freq_char:
                    skip_uid = True
                else:
                    uid_freq_char.add(line[0])
            if not skip_uid:
                if line[0] != last_uid:
                    all_players[last_uid] = player
                    last_uid = line[0]
                    player = PlayerPhase(last_uid)
                player.add_character(
                    line[2],
                    line[3],
                    line[4],
                    line[5],
                    line[6],
                    line[7],
                )
    all_players[last_uid] = player

    for comp in all_comps:
        if comp.player not in all_players:
            all_players[comp.player] = PlayerPhase(comp.player)
        all_players[comp.player].add_comp(comp)

    with open("../results/char_results/uids.csv", "w", newline="") as f:
        csv_writer = csv.writer(f)
        for uid in uid_freq_comp:
            csv_writer.writerow([uid])

    data = PickleData(
        all_players=all_players,
        all_comps=all_comps,
        avg_round_stage=avg_round_stage,
        sample_size=sample_size,
    )

    save_pickle_data("../data/pickle/data" + da_filename + ".pkl", data)

    cur_time = time()
    print("done csv: ", (cur_time - start_time), "s")


if __name__ == "__main__":
    main()
