"""Compile all ZZZ data."""

# pyright: reportUnknownVariableType=false, reportMissingTypeStubs=false
from __future__ import annotations

import csv
import time
from itertools import permutations
from os.path import isfile
from statistics import mean
from sys import exit as sys_exit
from typing import TYPE_CHECKING

import char_usage as cu
from comp_rates_config import (
    CHARACTERS,
    DEFAULT_ROUND,
    F2P_ONLY,
    PAST_PHASE,
    WHALE_ONLY,
    app_rate_threshold,
    app_rate_threshold_round,
    archetype,
    char_app_rate_threshold,
    char_infographics,
    da_mode,
    duo_dict_len,
    json,
    json_threshold,
    run_commands,
    sig_weaps,
)
from composition import Composition
from csv_to_pickle import PickleData, load_pickle_data  # noqa: TC002
from plyer import notification
from scipy.stats import skew, trim_mean
from slugify import slugify

if TYPE_CHECKING:
    from player_phase import PlayerPhase

with open("prydwen-slug.json") as slug_file:
    slug = json.load(slug_file)


start_time = time.time()
print("start")

da_filename = "_da" if da_mode else ""

loaded_data: PickleData = load_pickle_data("../data/pickle/data" + da_filename + ".pkl")

all_players: dict[str, PlayerPhase] = loaded_data.all_players
all_comps: list[Composition] = loaded_data.all_comps
avg_round_stage: dict[str, list[int]] = loaded_data.avg_round_stage
sample_size: dict[int | str, dict[str, int | float]] = loaded_data.sample_size
all_comps_json: dict[str, list[dict[str, str | float]]] = {}
all_comp_uids: set[str] = set()

if isfile("../../uids.csv"):
    with open("../../uids.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        self_uids = set(next(iter(reader)))
    with open("../../access.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        random_uids = {item for sublist in list(reader) for item in sublist}
    with open("../../collect/collected_interknot.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        interknot_uids = {item for sublist in list(reader) for item in sublist}
    with open("../../collect/collected_stardb.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        star_db_uids = {item for sublist in list(reader) for item in sublist}
    with open("../../collect/collected_hoyobuddy.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        hoyobuddy_uids = {item for sublist in list(reader) for item in sublist}
else:
    self_uids: set[str] = set()
    random_uids: set[str] = set()
    interknot_uids: set[str] = set()
    star_db_uids: set[str] = set()
    hoyobuddy_uids: set[str] = set()

if da_mode:
    three_stages = ["1-1", "1-2", "1-3"]
    three_double_stages = [["1-1", "1-2", "1-3"]]
    one_stage = ["1-1", "1-2", "1-3"]
    all_stages = ["1-1", "1-2", "1-3"]
else:
    three_stages = ["5-1", "5-2", "5-3"]
    three_double_stages = [["5-1", "5-2", "5-3"]]
    one_stage = ["5-1", "5-2", "5-3"]
    all_stages = ["5-1", "5-2", "5-3"]


def main() -> None:
    """Compile data."""
    if "Char usages all stages" in run_commands:
        char_usages(all_stages, filename="all")
        cur_time = time.time()
        print("done char: ", (cur_time - start_time), "s")

    if "Char usages 8 - 10" in run_commands:
        usage, boo_usage = char_usages(one_stage, filename="all")
        if not WHALE_ONLY and not F2P_ONLY:
            duo_usages(usage, archetype, one_stage)
        cur_time = time.time()
        print("done char 8 - 10: ", (cur_time - start_time), "s")

        if "Char usages for each stage" in run_commands:
            char_chambers: dict[str, dict[str, cu.CharUsageData]] = {
                "all": usage.copy(),
            }
            boo_chambers: dict[str, dict[str, cu.CharUsageData]] = {
                "all": boo_usage.copy(),
            }
            # for room in all_stages:
            for room in three_stages:
                char_chambers[room], boo_chambers[room] = char_usages(
                    [room],
                    filename=room,
                )

            appearances_write, rounds_write = compile_app_round(char_chambers)
            if not WHALE_ONLY and not F2P_ONLY:
                with open("../char_results/appearance.json", "w") as out_file:
                    out_file.write(json.dumps(appearances_write, indent=2))
                with open("../char_results/rounds.json", "w") as out_file:
                    out_file.write(json.dumps(rounds_write, indent=2))

            appearances_write, rounds_write = compile_app_round(boo_chambers)
            if not WHALE_ONLY and not F2P_ONLY:
                with open("../char_results/bangboo_appearance.json", "w") as out_file:
                    out_file.write(json.dumps(appearances_write, indent=2))
                with open("../char_results/bangboo_rounds.json", "w") as out_file:
                    out_file.write(json.dumps(rounds_write, indent=2))

            cur_time = time.time()
            print("done char stage: ", (cur_time - start_time), "s")

        if "Char usages for each stage (combined)" in run_commands:
            char_chambers = {"all": usage.copy()}
            boo_chambers = {"all": boo_usage.copy()}
            # for room in all_double_stages:
            for room in three_double_stages:
                char_chambers[room[0]], boo_chambers[room[0]] = char_usages(
                    room,
                    filename=room[0].split("-")[0],
                )

            appearances_write, rounds_write = compile_app_round(char_chambers)
            if not WHALE_ONLY and not F2P_ONLY:
                with open("../char_results/appearance_combine.json", "w") as out_file:
                    out_file.write(json.dumps(appearances_write, indent=2))
                with open("../char_results/rounds_combine.json", "w") as out_file:
                    out_file.write(json.dumps(rounds_write, indent=2))

            appearances_write, rounds_write = compile_app_round(boo_chambers)
            if not WHALE_ONLY and not F2P_ONLY:
                with open(
                    "../char_results/bangboo_appearance_combine.json",
                    "w",
                ) as out_file:
                    out_file.write(json.dumps(appearances_write, indent=2))
                with open(
                    "../char_results/bangboo_rounds_combine.json",
                    "w",
                ) as out_file:
                    out_file.write(json.dumps(rounds_write, indent=2))

            cur_time = time.time()
            print("done char stage (combine): ", (cur_time - start_time), "s")

    if "Comp usage all stages" in run_commands:
        comp_usages(all_stages, filename="all", floor=True)
        cur_time = time.time()
        print("done comp all: ", (cur_time - start_time), "s")

    if "Comp usage 8 - 10" in run_commands:
        comp_usages(one_stage, filename="top", floor=True)
        cur_time = time.time()
        print("done comp 8 - 10: ", (cur_time - start_time), "s")

    if "Comp usages for each stage" in run_commands:
        # for room in all_stages:
        for room in three_stages:
            comp_usages([room], filename=room)

        if not WHALE_ONLY and not F2P_ONLY:
            with open("../char_results/demographic.json", "w") as out_file:
                out_file.write(json.dumps(sample_size, indent=2))
        cur_time = time.time()
        print("done comp stage: ", (cur_time - start_time), "s")

    if "Character specific infographics" in run_commands:
        comp_usages(
            one_stage,
            filename=char_infographics,
            info_char=True,
            floor=True,
        )
        cur_time = time.time()
        print("done char infographics: ", (cur_time - start_time), "s")

    if (
        "Comp usage 8 - 10" in run_commands
        and "Comp usages for each stage" in run_commands
        and not WHALE_ONLY
        and not F2P_ONLY
    ):
        with open("../comp_results/json/all_comps.json", "w") as out_file:
            out_file.write(json.dumps(all_comps_json, indent=2))

    if __name__ == "__main__" and notification.notify:
        notification.notify(
            title="Finished",
            message="Finished executing comp_rates",
            # displaying time
            timeout=2,
        )
        # waiting time
        time.sleep(2)


def compile_app_round(
    char_chambers: dict[str, dict[str, cu.CharUsageData]],
) -> tuple[
    dict[str, dict[str, dict[str, float | str]]],
    dict[str, dict[str, dict[str, float | str]]],
]:
    """Compile appearance and round data."""
    appearances: dict[str, dict[str, cu.CharUsageData]] = {}
    rounds: dict[str, dict[str, cu.CharUsageData]] = {}
    appearances_write: dict[str, dict[str, dict[str, float | str]]] = {}
    rounds_write: dict[str, dict[str, dict[str, float | str]]] = {}
    for room, char_cham in char_chambers.items():
        appearances[room] = dict(
            sorted(char_cham.items(), key=lambda t: t[1].app, reverse=True),
        )
        appearances_write[room] = {}
        rounds_write[room] = {}
        rounds[room] = dict(
            sorted(char_cham.items(), key=lambda t: t[1].round, reverse=True),
        )
        for char in char_cham:
            appearances_write[room][char] = {
                "app": char_cham[char].app,
                "rarity": char_cham[char].rarity,
                "diff": char_cham[char].diff,
            }
            if char_cham[char].round == 0:
                continue
            rounds_write[room][char] = {
                "round": char_cham[char].round,
                "rarity": char_cham[char].rarity,
                "diff": char_cham[char].diff_rounds,
            }
    return (appearances_write, rounds_write)


def comp_usages(
    rooms: list[str],
    filename: str = "comp_usages",
    info_char: bool = False,
    floor: bool = False,
) -> None:
    """Comp usage."""
    global top_comps_app
    top_comps_app = {}
    comps_dict = used_comps(rooms, filename)
    rank_usages(comps_dict, rooms)
    comp_usages_write(comps_dict, filename, floor, info_char, True)
    comp_usages_write(comps_dict, filename, floor, info_char, False)


class CompUsage(Composition):
    """Comp usage class."""

    def __init__(self, comp: Composition) -> None:
        """Comp usage constructor."""
        self.__dict__.update(comp.__dict__)
        del self.player
        self.uses = 0
        self.owns = 0
        self.round_num = {str(i): list[int]() for i in range(1, 13)}
        self.whale_count = set[str]()
        self.players = set[Composition]()
        self.exc_comps = set[Composition]()
        self.boo_freq: dict[str, int] = {}
        self.bangboo: str
        self.is_count_round: bool
        self.is_count_round_print: bool
        self.app_rate: float
        self.round: float
        self.usage_rate: float
        self.own_rate: float
        self.app_rank: int


def used_comps(
    rooms: list[str],
    filename: str,
) -> dict[tuple[str, ...], CompUsage]:
    """Return the dictionary of all the comps used and how many times they were used."""
    comps_dict: dict[tuple[str, ...], CompUsage] = {}
    all_comp_uids.clear()
    all_comp_self_uids: set[str] = set()
    all_comp_random_uids: set[str] = set()
    all_comp_interknot_uids: set[str] = set()
    all_comp_star_db_uids: set[str] = set()
    all_comp_hoyobuddy_uids: set[str] = set()
    whale_count = 0
    f2p_count = 0

    for comp in all_comps:
        comp_tuple = tuple(comp.characters)
        cur_room = next(iter(str(comp.room).split("-")))
        # Check if the comp is used in the rooms that are being checked, and
        # if the clear is valid (reached 3 stars)
        if comp.room not in rooms or not comp.valid_clear:
            continue

        all_comp_uids.add(comp.player)
        if comp.player in self_uids:
            all_comp_self_uids.add(comp.player)
        if comp.player in random_uids:
            all_comp_random_uids.add(comp.player)
        if comp.player in interknot_uids:
            all_comp_interknot_uids.add(comp.player)
        if comp.player in star_db_uids:
            all_comp_star_db_uids.add(comp.player)
        if comp.player in hoyobuddy_uids:
            all_comp_hoyobuddy_uids.add(comp.player)
        if len(comp_tuple) < 3:
            continue

        whale_comp = False
        f2p_comp = True
        for char in range(3):
            if CHARACTERS[comp_tuple[char]]["availability"] == "Limited S":
                if comp.char_cons:
                    if comp.char_cons[comp_tuple[char]] > 0:
                        whale_comp = True
                elif (
                    comp_tuple[char] in all_players[comp.player].owned
                    and all_players[comp.player].owned[comp_tuple[char]].cons > 0
                ):
                    whale_comp = True
            if (
                comp_tuple[char] in all_players[comp.player].owned
                and all_players[comp.player].owned[comp_tuple[char]].weapon
                not in sig_weaps
            ):
                f2p_comp = False

        if whale_comp:
            whale_count += 1
        if f2p_comp:
            f2p_count += 1
        if (
            (WHALE_ONLY and not whale_comp)
            or (F2P_ONLY and (not f2p_comp or whale_comp))
        ):
            continue

        if comp_tuple not in comps_dict:
            comps_dict[comp_tuple] = CompUsage(comp)
        if comp.flag_cheat:
            if not whale_comp:
                comps_dict[comp_tuple].exc_comps.add(comp)
            continue

        comps_dict[comp_tuple].uses += 1

        if comp.bangboo:
            if comp.bangboo not in comps_dict[comp_tuple].boo_freq:
                comps_dict[comp_tuple].boo_freq[comp.bangboo] = 0
            comps_dict[comp_tuple].boo_freq[comp.bangboo] += 1

        if whale_comp:
            comps_dict[comp_tuple].whale_count.add(comp.player)
        if whale_comp == WHALE_ONLY and (not F2P_ONLY or f2p_comp):
            comps_dict[comp_tuple].round_num[cur_room].append(comp.round_num)
            comps_dict[comp_tuple].players.add(comp)
            avg_round_stage[cur_room].append(comp.round_num)

    for stage, round_stage in avg_round_stage.items():
        sample_size[stage]["avg_round"] = round(mean(round_stage or [0]), 2)

    chamber_num = list(str(filename).split("-"))
    if len(chamber_num) > 1 and chamber_num[1] == "1":
        sample_size[chamber_num[0]]["total"] = len(all_comp_uids)
        sample_size[chamber_num[0]]["prydwen"] = len(all_comp_self_uids)
        sample_size[chamber_num[0]]["random"] = len(all_comp_random_uids)
        sample_size[chamber_num[0]]["interknot"] = len(all_comp_interknot_uids)
        sample_size[chamber_num[0]]["star_db"] = len(all_comp_star_db_uids)
        sample_size[chamber_num[0]]["hoyobuddy"] = len(all_comp_hoyobuddy_uids)
    if WHALE_ONLY:
        print("Whale percentage: " + str(whale_count / len(all_comp_uids)))
    return comps_dict


def rank_usages(
    comps_dict: dict[tuple[str, ...], CompUsage],
    rooms: list[str],
) -> None:
    """Calculate the usage rate and sort the comps according to it."""
    # Calculate the usage rate and sort the comps according to it
    total = len(all_comp_uids) / 100.0
    rates: list[float] = []
    for cur_comp in comps_dict.values():
        if total == 0:
            print(cur_comp.uses)
        app = round(cur_comp.uses / total, 2)
        cur_comp.app_rate = app
        cur_comp.usage_rate = 0
        cur_comp.own_rate = 0
        rates.append(app)

        avg_round: list[float] = []
        uses_room: dict[int, int] = {}

        for room_num in range(1, 8):
            cur_round = cur_comp.round_num[str(room_num)]
            if cur_round:
                uses_room[room_num] = len(cur_round)
                if cur_comp.uses > 10:
                    skewness = skew(cur_round, axis=0, bias=True)
                    if abs(skewness) > 0.8:
                        avg_round.append(trim_mean(cur_round, 0.25))
                    else:
                        avg_round.append(mean(cur_round))
                else:
                    avg_round.append(mean(cur_round))

        list_round = [
            item for sublist in cur_comp.round_num.values() for item in sublist
        ]
        cur_comp.is_count_round = True
        cur_comp.is_count_round_print = True
        if rooms == one_stage:
            for uses_room_num in uses_room.values():
                if uses_room_num < 20:
                    cur_comp.is_count_round = False
                if uses_room_num < 3:
                    cur_comp.is_count_round_print = False
        elif len(rooms) == 1:
            if len(list_round) < 20:
                cur_comp.is_count_round = False
            if len(list_round) < 3:
                cur_comp.is_count_round_print = False

        rounded_avg_round: float
        rounded_avg_round = round(mean(avg_round)) if avg_round else DEFAULT_ROUND
        cur_comp.round = rounded_avg_round

        if cur_comp.boo_freq:
            # Find the bangboo with most usage
            cur_comp.bangboo = max(
                cur_comp.boo_freq,
                key=lambda k: cur_comp.boo_freq.get(k, 0),
            )
    rates.sort(reverse=True)
    for comp, cur_comp in comps_dict.items():
        comps_dict[comp].app_rank = rates.index(cur_comp.app_rate) + 1


def duo_usages(
    usage: dict[str, cu.CharUsageData],
    archetype: str,
    rooms: list[str],
) -> None:
    """Calculate duo usage."""
    duos_dict = used_duos(rooms, usage)
    duo_write(duos_dict, usage, "duo_usages", archetype)


def used_duos(
    rooms: list[str],
    usage: dict[str, cu.CharUsageData],
) -> dict[str, dict[str, cu.RoundApp]]:
    """Return dictionary of all the duos used and how many times they were used."""
    duos_dict: dict[tuple[str, str], cu.RoundApp] = {}

    for comp in all_comps:
        if len(comp.characters) < 2 or comp.room not in rooms:
            continue

        whale_comp = False
        cur_room = next(iter(str(comp.room).split("-")))
        for char in comp.characters:
            if CHARACTERS[char]["availability"] == "Limited S":
                if comp.char_cons:
                    if comp.char_cons[char] > 0:
                        whale_comp = True
                elif (
                    char in all_players[comp.player].owned
                    and all_players[comp.player].owned[char].cons > 0
                ):
                    whale_comp = True

        # Permutate the duos, for example if Ganyu and Xiangling are used,
        # two duos are used, Ganyu/Xiangling and Xiangling/Ganyu
        duos = list(permutations(comp.characters, 2))
        for duo in duos:
            is_triple_dps = False

            if duo not in duos_dict:
                duos_dict[duo] = cu.RoundApp()
            duos_dict[duo].app_flat += 1

            if is_triple_dps and "Duos check" in run_commands:
                continue
            if not whale_comp:
                duos_dict[duo].round_list[cur_room].append(comp.round_num)

    sorted_duos = sorted(duos_dict.items(), key=lambda t: t[1].app_flat, reverse=True)
    duos_dict = dict(sorted_duos)

    return_duos: dict[str, dict[str, cu.RoundApp]] = {}
    for duo in duos_dict:
        cur_duo = duos_dict[duo]
        if usage[duo[0]].app_flat > 0:
            # Calculate the appearance rate of the duo by dividing the appearance count
            # of the duo with the appearance count of the first character
            cur_duo.app = round(cur_duo.app_flat * 100 / usage[duo[0]].app_flat, 2)
            cur_duo.app_flat = 0
            avg_round: list[float] = []
            for room_num in range(1, 8):
                duo_round = cur_duo.round_list[str(room_num)]
                if duo_round:
                    cur_duo.app_flat += len(duo_round)
                    if len(duo_round) > 1:
                        skewness = skew(duo_round, axis=0, bias=True)
                        if abs(skewness) > 0.8:
                            avg_round.append(trim_mean(duo_round, 0.25))
                        else:
                            avg_round.append(mean(duo_round))
                    else:
                        avg_round.append(mean(duo_round))
            if avg_round:
                cur_duo.round = round(mean(avg_round))
            else:
                cur_duo.round = DEFAULT_ROUND
            if duo[0] not in return_duos:
                return_duos[duo[0]] = {}
            return_duos[duo[0]][duo[1]] = cur_duo

    return return_duos


def char_usages(
    rooms: list[str],
    filename: str = "char_usages",
    info_char: bool = False,
) -> tuple[
    dict[str, cu.CharUsageData],
    dict[str, cu.CharUsageData],
]:
    """Calculate character usage."""
    app = cu.appearances(all_players, chambers=rooms, info_char=info_char)
    chars_dict, boos_dict = cu.usages(app, PAST_PHASE, chambers=rooms)
    char_usages_write(chars_dict, filename, archetype)
    boo_usages_write(boos_dict, "bangboo_" + filename, archetype)
    return (chars_dict, boos_dict)


def comp_usages_write(
    comps_dict: dict[tuple[str, ...], CompUsage],
    filename: str,
    floor: int,
    info_char: bool,
    sort_app: bool,
) -> None:
    """Write comp usage."""
    out_json: list[dict[str, str | float]] = []
    out_comps: list[dict[str, str | int]] = []
    exc_comps: list[dict[str, str | int | float]] = []
    outvar_comps: list[dict[str, str | int]] = []
    var_comps: list[dict[str, str | int]] = []
    variations: dict[str, int] = {}
    threshold = app_rate_threshold if sort_app else app_rate_threshold_round

    if sort_app:
        comps_dict = dict(
            sorted(comps_dict.items(), key=lambda t: t[1].app_rate, reverse=True),
        )
    else:
        comps_dict = dict(
            sorted(comps_dict.items(), key=lambda t: t[1].round, reverse=True),
        )
    comp_names: list[str] = []
    dual_comp_names: list[str] = []

    for comp in comps_dict:
        if info_char and filename not in comp:
            continue
        cur_comp = comps_dict[comp]
        comp_name = cur_comp.comp_name
        dual_comp_name = cur_comp.dual_comp_name
        alt_comp_name = cur_comp.alt_comp_name
        # Only one variation of each comp name is included,
        # unless if it's used for a character's infographic
        if (
            (
                comp_name not in comp_names
                and comp_name not in dual_comp_names
                and dual_comp_name not in comp_names
                and alt_comp_name not in comp_names
                and cur_comp.round not in {1, 0}
            )
            or comp_name == "-"
            or info_char
        ):
            if sort_app:
                top_comps_app[comp_name] = cur_comp.app_rate
            if cur_comp.is_count_round and (
                cur_comp.app_rate >= threshold
                or (info_char and cur_comp.app_rate > char_app_rate_threshold)
            ):
                temp_comp_name = alt_comp_name if alt_comp_name != "-" else comp_name

                out_comps_append: dict[str, str | int] = {
                    "comp_name": temp_comp_name,
                    "char_1": comp[0],
                    "char_2": comp[1],
                    "char_3": comp[2],
                    "app_rate": str(cur_comp.app_rate) + "%",
                    "avg_round": str(cur_comp.round),
                }

                if info_char:
                    if comp_name not in comp_names:
                        variations[comp_name] = 1
                        out_comps_append["variation"] = variations[comp_name]
                    else:
                        variations[comp_name] += 1
                        out_comps_append["variation"] = variations[comp_name]

                out_comps_append["whale_count"] = str(len(cur_comp.whale_count))
                out_comps_append["uses"] = str(cur_comp.uses)

                if info_char:
                    if comp_name not in comp_names:
                        out_comps.append(out_comps_append)
                    else:
                        var_comps.append(out_comps_append)
                else:
                    out_comps.append(out_comps_append)

                if comp_name != "-":
                    comp_names.append(comp_name)
                if dual_comp_name != "-":
                    dual_comp_names.append(dual_comp_name)
                if alt_comp_name != "-":
                    comp_names.append(alt_comp_name)

        elif comp_name in comp_names:
            temp_comp_name = alt_comp_name if alt_comp_name != "-" else comp_name
            outvar_comps_append: dict[str, str | int] = {
                "comp_name": temp_comp_name,
                "char_1": comp[0],
                "char_2": comp[1],
                "char_3": comp[2],
            }
            outvar_comps_append["app_rate"] = str(cur_comp.app_rate) + "%"
            outvar_comps_append["avg_round"] = str(cur_comp.round)
            outvar_comps.append(outvar_comps_append)
        if not info_char and (
            cur_comp.is_count_round_print and (cur_comp.app_rate >= json_threshold)
        ):
            out = name_filter(list(comp), mode="out")
            for i in range(3):
                out[i] = slugify(out[i])
                if out[i] in slug:
                    out[i] = slug[out[i]]
            out_json_dict: dict[str, str | float] = {
                "char_one": out[0],
                "char_two": out[1],
                "char_three": out[2],
            }
            out_json_dict["bangboo"] = slugify(cur_comp.bangboo)
            out_json_dict["app_rate"] = cur_comp.app_rate
            out_json_dict["rank"] = cur_comp.app_rank
            out_json_dict["avg_round"] = cur_comp.round
            out_json.append(out_json_dict)

            for exc_comp in cur_comp.exc_comps:
                exc_comp_append = {
                    "player": exc_comp.player,
                    "char_one": exc_comp.characters[0],
                    "char_one_cons": exc_comp.char_cons[exc_comp.characters[0]],
                    "char_two": exc_comp.characters[1],
                    "char_two_cons": exc_comp.char_cons[exc_comp.characters[1]],
                    "char_three": exc_comp.characters[2],
                    "char_three_cons": exc_comp.char_cons[exc_comp.characters[2]],
                    "score": exc_comp.round_num,
                    "avg_score": cur_comp.round,
                    "app_rate": cur_comp.app_rate,
                    "stage": exc_comp.room,
                }
                exc_comps.append(exc_comp_append)

    if info_char:
        out_comps += var_comps

    if archetype != "all":
        filename = filename + "_" + archetype

    if not (sort_app):
        filename = filename + "_rounds"

    if WHALE_ONLY:
        filename = filename + "_C1"
    elif F2P_ONLY:
        filename = filename + "_E0S0"

    if floor:
        with open(
            "../comp_results/comps_usage_" + filename + ".csv",
            "w",
            newline="",
        ) as f:
            csv_writer = csv.writer(f)
            for comps in out_comps:
                csv_writer.writerow(comps.values())

    if not info_char:
        all_comps_json[filename] = out_json.copy()
        if (len(exc_comps) > 0) and sort_app:
            with open(
                "../comp_results/comps_usage_exc" + filename + ".csv",
                "w",
                newline="",
            ) as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(exc_comps[0].keys())
                for comps in exc_comps:
                    csv_writer.writerow(comps.values())
            with open("../comp_results/json/exc" + filename + ".json", "w") as out_file:
                out_file.write(json.dumps(exc_comps, indent=2))
        with open("../comp_results/json/" + filename + ".json", "w") as out_file:
            out_file.write(json.dumps(out_json, indent=2))


def duo_write(
    duos_dict: dict[str, dict[str, cu.RoundApp]],
    usage: dict[str, cu.CharUsageData],
    filename: str,
    archetype: str,
) -> None:
    """Write duo usage."""
    out_duos: list[dict[str, str | float]] = []
    for char, char_duo in duos_dict.items():
        duo_keys = list(char_duo.keys())
        if usage[char].app_flat > 0:
            out_duos_append = {
                "char": char,
                "app": usage[char].app,
            }
            for i in range(duo_dict_len):
                j = str(i + 1)
                if i < len(char_duo):
                    duo_char = char_duo[duo_keys[i]]
                    out_duos_append["char_" + j] = duo_keys[i]
                    out_duos_append["app_rate_" + j] = str(duo_char.app) + "%"
                    out_duos_append["avg_round_" + j] = duo_char.round
                    out_duos_append["app_flat_" + j] = duo_char.app_flat
                else:
                    out_duos_append["char_" + str(i + 1)] = "-"
                    out_duos_append["app_rate_" + str(i + 1)] = "0.00%"
                    out_duos_append["avg_round_" + str(i + 1)] = 0.00
                    out_duos_append["app_flat_" + str(i + 1)] = 0
            out_duos.append(out_duos_append)
    out_duos = sorted(out_duos, key=lambda t: t["app"], reverse=True)

    if archetype != "all":
        filename = filename + "_" + archetype
    count = 0
    out_duos_check: dict[str, dict[str, dict[str, str | float]]] = {}
    out_duos_exclu: dict[str, dict[str, dict[str, str | float]]] = {}

    with open("../char_results/" + filename + ".csv", "w", newline="") as f:
        csv_writer = csv.writer(f)
        for duos in out_duos:
            duo_char = str(duos["char"])
            out_duos_check[duo_char] = {}
            out_duos_exclu[duo_char] = {}
            if count == 0:
                temp_duos = ["char", "app"]
                for i in range(10):
                    temp_duos += [
                        "char_" + str(i + 1),
                        "app_rate_" + str(i + 1),
                        "avg_round_" + str(i + 1),
                    ]
                csv_writer.writerow(temp_duos)
                count += 1
            temp_duos = [duo_char, duos["app"]]
            for i in range(10):
                temp_duos += [
                    duos["char_" + str(i + 1)],
                    duos["app_rate_" + str(i + 1)],
                    duos["avg_round_" + str(i + 1)],
                ]
            csv_writer.writerow(temp_duos)
            for i in range(duo_dict_len):
                j = str(i + 1)
                duo_app_j = float(str(duos["app_rate_" + j])[:-1])
                duo_round_j = float(duos["avg_round_" + j])
                duo_j = str(duos["char_" + j])
                if (
                    duo_app_j >= 1
                    and float(duos["app_flat_" + j]) >= 10
                    and (
                        (duo_round_j < usage[duo_j].round)
                        or (duo_round_j < usage[duo_char].round)
                    )
                    and usage[duo_j].round != 1
                    and usage[duo_j].round != 0
                ):
                    out_duos_check[duo_char][duo_j] = {
                        "app": duo_app_j,
                        "avg_round": duo_round_j,
                    }

    if "Duos check" in run_commands:
        char_names = list(CHARACTERS.keys())
        out_dd: dict[frozenset[str], dict[str, str | float]] = {}
        out_dd_list: list[list[str]] = []
        for char_i in char_names:
            for char_j in char_names:
                is_char_i_dps = CHARACTERS[char_i][
                    "role"
                ] == "Damage Dealer" or char_i in [
                    "Sampo",
                    "Black Swan",
                    "Luka",
                    "Guinaifen",
                ]
                is_char_j_dps = CHARACTERS[char_j][
                    "role"
                ] == "Damage Dealer" or char_j in [
                    "Sampo",
                    "Black Swan",
                    "Luka",
                    "Guinaifen",
                ]
                if is_char_i_dps and is_char_j_dps:
                    if char_j not in out_duos_check:
                        continue
                    if char_i not in out_duos_check:
                        continue
                    if char_i in out_duos_check[char_j]:
                        out_dd_list.append([char_j, char_i])
                        out_i_j = out_duos_check[char_i][char_j]
                        out_j_i = out_duos_check[char_j][char_i]
                        if char_j in out_duos_check[char_i]:
                            out_dd[frozenset([char_i, char_j])] = {
                                "char_i": char_i,
                                "char_i_app": str(out_i_j["app"]),
                                "char_j": char_j,
                                "char_j_app": str(out_j_i["app"]),
                                "avg_round": str(out_i_j["avg_round"]),
                            }
                        elif char_j in out_duos_exclu[char_i]:
                            out_dd[frozenset([char_i, char_j])] = {
                                "char_i": char_i,
                                "char_i_app": str(
                                    out_duos_exclu[char_i][char_j]["app"],
                                ),
                                "char_j": char_j,
                                "char_j_app": str(out_j_i["app"]),
                                "avg_round": str(
                                    out_duos_exclu[char_i][char_j]["avg_round"],
                                ),
                            }

        sorted_out_dd = sorted(
            out_dd.items(),
            key=lambda t: t[1]["char_i"],
            reverse=True,
        )
        out_dd = dict(sorted_out_dd)

        with open("../char_results/duo_check.csv", "w", newline="") as f:
            csv_writer = csv.writer(f)
            for out_dd_print in out_dd_list:
                csv_writer.writerow(out_dd_print)
        for out_dd_print in out_dd:
            print(
                str(out_dd[out_dd_print]["char_i"])
                + ", "
                + str(out_dd[out_dd_print]["char_i_app"])
                + ", "
                + str(out_dd[out_dd_print]["char_j"])
                + ", "
                + str(out_dd[out_dd_print]["char_j_app"])
                + ", "
                + str(out_dd[out_dd_print]["avg_round"]),
            )
        if __name__ == "__main__" and notification.notify:
            notification.notify(
                title="Finished",
                message="Finished executing comp_rates",
                # displaying time
                timeout=2,
            )
            # waiting time
            time.sleep(1)
        sys_exit()

    for i in range(len(out_duos)):
        for duo_value in ["char"] + [f"char_{i}" for i in range(1, 31)]:
            if out_duos[i][duo_value]:
                out_duos[i][duo_value] = slugify(str(out_duos[i][duo_value]))
                if out_duos[i][duo_value] in slug:
                    out_duos[i][duo_value] = slug[out_duos[i][duo_value]]
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_duos, indent=2))


def boo_usages_write(
    chars_dict: dict[str, cu.CharUsageData],
    filename: str,
    archetype: str,
) -> None:
    """Write bangboos usage."""
    out_chars: list[dict[str, str | int | float]] = []
    out_chars_csv: list[dict[str, str | int | float]] = []
    chars_dict = dict(sorted(chars_dict.items(), key=lambda t: t[1].app, reverse=True))
    for char, cur_char in chars_dict.items():
        out_chars_append: dict[str, str | int | float] = {
            "char": char,
            "app_rate": str(cur_char.app) + "%",
            "avg_round": str(cur_char.round),
            "rarity": cur_char.rarity,
            "diff": str(cur_char.diff) + "%",
            "diff_rounds": str(cur_char.diff_rounds),
        }
        for i in ["app_rate", "diff", "diff_rounds"]:
            if out_chars_append[i] == "-%":
                out_chars_append[i] = "-"
        out_chars.append(out_chars_append)
        out_chars_csv.append(out_chars_append.copy())
        if char == filename:
            break

    if archetype != "all":
        filename = filename + "_" + archetype
    if WHALE_ONLY:
        filename = filename + "_C1"
    elif F2P_ONLY:
        filename = filename + "_E0S0"

    iterate_value_app = ["app_rate", "diff"]
    iterate_value_round = ["avg_round", "diff_rounds"]

    for i in range(len(out_chars)):
        out_chars[i]["char"] = slugify(str(out_chars[i]["char"]))
        if out_chars[i]["char"] in slug:
            out_chars[i]["char"] = slug[out_chars[i]["char"]]
        for value in iterate_value_app:
            if (
                str(out_chars[i][value])[:-1]
                .replace(".", "")
                .replace("-", "")
                .isnumeric()
            ):
                out_chars[i][value] = float(str(out_chars[i][value])[:-1])
            else:
                out_chars[i][value] = 0.00
        for value in iterate_value_round:
            if str(out_chars[i][value]).replace(".", "").replace("-", "").isnumeric():
                out_chars[i][value] = round(float(out_chars[i][value]))
            else:
                out_chars[i][value] = DEFAULT_ROUND
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_chars, indent=2))

    with open("../char_results/" + filename + ".csv", "w", newline="") as f:
        csv_writer = csv.writer(f)
        count = 0
        for chars in out_chars_csv:
            if count == 0:
                header = chars.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(chars.values())


def char_usages_write(
    chars_dict: dict[str, cu.CharUsageData],
    filename: str,
    archetype: str,
) -> None:
    """Write character usage."""
    out_chars: list[dict[str, str | int | float]] = []
    out_chars_csv: list[dict[str, str | int | float]] = []
    weap_len = 10
    arti_len = 10
    chars_dict = dict(sorted(chars_dict.items(), key=lambda t: t[1].app, reverse=True))
    for char, cur_char in chars_dict.items():
        out_chars_append: dict[str, str | int | float] = {
            "char": char,
            "app_rate": str(cur_char.app) + "%",
            "app_rate_m0": str(cur_char.app_exclude) + "%",
            "avg_round": str(cur_char.round),
            "std_dev_round": str(cur_char.std_dev_round),
            "q1_round": str(cur_char.q1_round),
            "role": cur_char.role,
            "rarity": cur_char.rarity,
            "diff": str(cur_char.diff) + "%",
            "diff_rounds": str(cur_char.diff_rounds),
        }
        for i in ["app_rate", "app_rate_m0", "diff", "diff_rounds"]:
            if out_chars_append[i] == "-%":
                out_chars_append[i] = "-"
        if list(cur_char.weapons):
            for i in range(weap_len):
                if i < len(list(cur_char.weapons)):
                    out_chars_append["weapon_" + str(i + 1)] = list(cur_char.weapons)[i]
                    out_chars_append["weapon_" + str(i + 1) + "_app"] = (
                        str(list(cur_char.weapons.values())[i].app) + "%"
                    )
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = str(
                        list(cur_char.weapons.values())[i].round,
                    )
                else:
                    out_chars_append["weapon_" + str(i + 1)] = ""
                    out_chars_append["weapon_" + str(i + 1) + "_app"] = "0.0"
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = str(
                        DEFAULT_ROUND,
                    )
            for i in range(arti_len):
                if i < len(list(cur_char.artifacts)):
                    arti_name = list(cur_char.artifacts)[i]
                    out_chars_append["artifact_" + str(i + 1)] = arti_name
                    arti_name = arti_name.split(", ")
                    out_chars_append["artifact_" + str(i + 1) + "_1"] = arti_name[0]
                    if len(arti_name) > 1:
                        out_chars_append["artifact_" + str(i + 1) + "_2"] = arti_name[1]
                        if len(arti_name) > 2:
                            out_chars_append["artifact_" + str(i + 1) + "_3"] = (
                                arti_name[2]
                            )
                        else:
                            out_chars_append["artifact_" + str(i + 1) + "_3"] = ""
                    else:
                        out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_app"] = (
                        str(list(cur_char.artifacts.values())[i].app) + "%"
                    )
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = str(
                        list(cur_char.artifacts.values())[i].round,
                    )
                else:
                    out_chars_append["artifact_" + str(i + 1)] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_1"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_3"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_app"] = "0.0"
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = str(
                        DEFAULT_ROUND,
                    )
            for i in range(7):
                out_chars_append["app_" + str(i)] = (
                    str(next(iter(list(cur_char.cons_usage.values())[i].values())))
                    + "%"
                )
                out_chars_append["round_" + str(i)] = str(
                    list(list(cur_char.cons_usage.values())[i].values())[3],
                )
                if out_chars_append["app_" + str(i)] == "-%":
                    out_chars_append["app_" + str(i)] = "-"
            out_chars_append["cons_avg"] = cur_char.cons_avg
            out_chars_append["sample"] = cur_char.sample
            out_chars_append["sample_app_flat"] = cur_char.sample_app_flat
        else:
            for i in range(weap_len):
                out_chars_append["weapon_" + str(i + 1)] = ""
                out_chars_append["weapon_" + str(i + 1) + "_app"] = "0.0"
                out_chars_append["weapon_" + str(i + 1) + "_round"] = str(DEFAULT_ROUND)
            for i in range(arti_len):
                out_chars_append["artifact_" + str(i + 1)] = ""
                out_chars_append["artifact_" + str(i + 1) + "_1"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_3"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_app"] = "0.0"
                out_chars_append["artifact_" + str(i + 1) + "_round"] = str(
                    DEFAULT_ROUND,
                )
            for i in range(7):
                out_chars_append["app_" + str(i)] = "0.0%"
                out_chars_append["round_" + str(i)] = str(DEFAULT_ROUND)
            out_chars_append["cons_avg"] = cur_char.cons_avg
            out_chars_append["sample"] = cur_char.sample
            out_chars_append["sample_app_flat"] = cur_char.sample_app_flat
        out_chars.append(out_chars_append)
        out_chars_csv.append(out_chars_append.copy())
        if char == filename:
            break

    if archetype != "all":
        filename = filename + "_" + archetype
    if WHALE_ONLY:
        filename = filename + "_C1"
    elif F2P_ONLY:
        filename = filename + "_E0S0"

    iterate_value_app = ["app_rate", "app_rate_m0", "diff"]
    iterate_value_round = ["avg_round", "std_dev_round", "q1_round", "diff_rounds"]
    iterate_name_arti: list[str] = []
    for i in range(weap_len):
        iterate_value_app.append("weapon_" + str(i + 1) + "_app")
        iterate_value_round.append("weapon_" + str(i + 1) + "_round")
    for i in range(arti_len):
        iterate_value_app.append("artifact_" + str(i + 1) + "_app")
        iterate_value_round.append("artifact_" + str(i + 1) + "_round")
    for i in range(7):
        iterate_value_app.append("app_" + str(i))
        iterate_value_round.append("round_" + str(i))

    for i in range(len(out_chars)):
        # for i in range(7):
        out_chars[i]["char"] = slugify(str(out_chars[i]["char"]))
        if out_chars[i]["char"] in slug:
            out_chars[i]["char"] = slug[out_chars[i]["char"]]
        for value in iterate_value_app:
            if (
                str(out_chars[i][value])[:-1]
                .replace(".", "")
                .replace("-", "")
                .isnumeric()
            ):
                out_chars[i][value] = float(str(out_chars[i][value])[:-1])
            else:
                out_chars[i][value] = 0.00
        for value in iterate_value_round:
            if str(out_chars[i][value]).replace(".", "").replace("-", "").isnumeric():
                out_chars[i][value] = round(float(out_chars[i][value]))
            else:
                out_chars[i][value] = DEFAULT_ROUND
        for value in iterate_name_arti:
            if out_chars[i][value]:
                out_chars[i][value] = (
                    str(out_chars[i][value]).replace(".", "").replace("-", "")
                )
            else:
                out_chars[i][value] = DEFAULT_ROUND
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_chars, indent=2))

    with open("../char_results/" + filename + ".csv", "w", newline="") as f:
        csv_writer = csv.writer(f)
        count = 0
        for chars in out_chars_csv:
            if count == 0:
                header = chars.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(chars.values())


def name_filter(comp: list[str], mode: str = "out") -> list[str]:
    """Filter names."""
    if mode == "out":
        return comp
    return []


main()
