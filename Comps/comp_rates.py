import csv
import os
import statistics
import time

# from scipy.stats import skew, trim_mean
from itertools import permutations

import char_usage as cu
from archetypes import find_archetype, findchars, resetfind
from comp_rates_config import (
    CHARACTERS,
    RECENT_PHASE,
    alt_comps,
    app_rate_threshold,
    app_rate_threshold_round,
    archetype,
    char_app_rate_threshold,
    char_infographics,
    da_mode,
    duo_dict_len,
    f2pOnly,
    json,
    json_threshold,
    past_phase,
    run_commands,
    sigWeaps,
    skip_random,
    skip_self,
    whaleOnly,
)
from composition import Composition
from player_phase import PlayerPhase
from plyer import notification  # type: ignore
from slugify import slugify

with open("prydwen-slug.json") as slug_file:
    slug = json.load(slug_file)


def main() -> None:
    for make_path in [
        "../comp_results",
        "../comp_results/json",
        "../enka.network",
        "../enka.network/results_real",
        "../char_results",
        "../rogue_results",
    ]:
        if not os.path.exists(make_path):
            os.makedirs(make_path)

    start_time = time.time()
    print("start")

    global self_uids
    if os.path.isfile("../../uids.csv"):
        with open("../../uids.csv", encoding="UTF8") as f:
            reader = csv.reader(f, delimiter=",")
            self_uids = list(reader)[0]
    else:
        self_uids = []

    da_filename = ""
    if da_mode:
        da_filename = "_da"
    if os.path.exists("../data/raw_csvs_real/"):
        stats = open("../data/raw_csvs_real/" + RECENT_PHASE + da_filename + ".csv")
    else:
        stats = open("../data/raw_csvs/" + RECENT_PHASE + da_filename + ".csv")

    # uid_freq_comp will help detect duplicate UIDs
    reader = csv.reader(stats)
    next(reader)
    all_comps = []
    if da_mode:
        all_chambers = ["1"]
    else:
        all_chambers = ["1", "2", "3", "4", "5", "6", "7"]
    three_star_sample = {}
    for chamber_num in all_chambers:
        three_star_sample[chamber_num] = 0
    uid_freq_comp = {}
    self_freq_comp = {}
    # dps_freq_comp = {}
    last_uid = "0"
    skip_uid = False

    for line in reader:
        star_num = 0
        match str(line[3]):
            case "B":
                star_num = 1
            case "A":
                star_num = 2
            case "S":
                star_num = 3
        if skip_self and line[0] in self_uids:
            continue
        if skip_random and line[0] not in self_uids:
            continue
        if line[0] != last_uid:
            skip_uid = False
            if line[0] in uid_freq_comp:
                skip_uid = True
                # print("duplicate UID in comp: " + line[0])
            elif (not da_mode and star_num > 0) or (
                da_mode and int("".join(filter(str.isdigit, line[2]))) > 0
            ):
                uid_freq_comp[line[0]] = 1
                if line[0] in self_uids:
                    self_freq_comp[line[0]] = 1
            else:
                skip_uid = True
        # else:
        #     uid_freq_comp[line[0]] += 1
        last_uid = line[0]
        if not skip_uid:
            stage = str(line[1])
            comp_chars_temp = []
            cons_chars_temp = []
            if da_mode:
                for i in [6, 8, 10]:
                    if line[i] != "" and line[i] in CHARACTERS:
                        comp_chars_temp.append(line[i])
                        cons_chars_temp.append(line[i + 1])
            else:
                for i in [5, 7, 9]:
                    if line[i] != "" and line[i] in CHARACTERS:
                        comp_chars_temp.append(line[i])
                        cons_chars_temp.append(line[i + 1])
            if comp_chars_temp:
                if da_mode:
                    comp = Composition(
                        line[0],
                        comp_chars_temp,
                        RECENT_PHASE,
                        line[3],
                        line[2],
                        "1-" + stage,
                        alt_comps,
                        line[12],
                        cons_chars_temp,
                    )
                else:
                    comp = Composition(
                        line[0],
                        comp_chars_temp,
                        RECENT_PHASE,
                        line[4],
                        star_num,
                        stage + "-" + str(line[2]),
                        alt_comps,
                        line[10],
                        cons_chars_temp,
                    )
                # if int(stage) > 7:
                #     if line[0] not in dps_freq_comp:
                #         dps_freq_comp[line[0]] = set()
                #     if comp.dps == []:
                #         if comp.sub != []:
                #             dps_freq_comp[line[0]].add(frozenset([comp.sub[0]]))
                #     else:
                #         dps_freq_comp[line[0]].add(frozenset([comp.dps[0]]))
                all_comps.append(comp)
                if int(star_num) == 3:
                    three_star_sample[stage] += 1

    # len_dps_freq_comp = {}
    # for i in dps_freq_comp:
    #     if len(dps_freq_comp[i]) not in len_dps_freq_comp:
    #         len_dps_freq_comp[len(dps_freq_comp[i])] = 0
    #     len_dps_freq_comp[len(dps_freq_comp[i])] += 1
    #     if len(dps_freq_comp[i]) == 1:
    #         print(str(i) + ": " + str(dps_freq_comp[i]))
    # print(len_dps_freq_comp)
    # exit()

    global sample_size
    sample_size = {}
    for chamber_num in all_chambers:
        sample_size[chamber_num] = {}
    global avg_round_stage
    avg_round_stage = {}
    for chamber_num in all_chambers:
        avg_round_stage[chamber_num] = []
    global valid_duo_dps
    if os.path.exists("../char_results/duo_check.csv"):
        with open("../char_results/duo_check.csv", "r") as f:
            valid_duo_dps = list(csv.reader(f, delimiter=","))
    else:
        valid_duo_dps = []
    # max_weight = 0
    sample_size["all"] = {
        "total": len(uid_freq_comp),
        "self_report": len(self_freq_comp),
        "random": len(uid_freq_comp) - len(self_freq_comp),
    }

    # global stage_weight
    # stage_weight = {}
    # for stage in avg_round_stage:
    #     stage_weight[stage] = max_weight / sample_size[stage]["avg_round_stage"]
    #     sample_size[stage]["weight"] = stage_weight[stage]

    if os.path.exists("../data/raw_csvs_real/"):
        stats = open("../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv")
    else:
        stats = open("../data/raw_csvs/" + RECENT_PHASE + "_char.csv")

    # uid_freq_char and last_uid will help detect duplicate UIDs
    reader = csv.reader(stats)
    next(reader)
    all_players = {}
    all_players[RECENT_PHASE] = {}
    last_uid = "0"
    player = PlayerPhase(last_uid, RECENT_PHASE)
    uid_freq_char = []

    # Append lines
    for line in reader:
        line[1] = RECENT_PHASE
        if line[0] in uid_freq_comp:
            if line[0] != last_uid:
                skip_uid = False
                if line[0] in uid_freq_char:
                    skip_uid = True
                    # print("duplicate UID in char: " + line[0])
                else:
                    uid_freq_char.append(line[0])
            if not skip_uid:
                if line[0] != last_uid:
                    all_players[RECENT_PHASE][last_uid] = player
                    last_uid = line[0]
                    player = PlayerPhase(last_uid, RECENT_PHASE)
                player.add_character(
                    line[2], line[3], line[4], line[5], line[6], line[7]
                )
    all_players[RECENT_PHASE][last_uid] = player

    for comp in all_comps:
        if comp.player not in all_players[comp.phase]:
            all_players[comp.phase][comp.player] = PlayerPhase(comp.player, comp.phase)
        all_players[comp.phase][comp.player].add_comp(comp)

    csv_writer = csv.writer(open("../char_results/uids.csv", "w", newline=""))
    for uid in uid_freq_comp.keys():
        csv_writer.writerow([uid])

    cur_time = time.time()
    print("done csv: ", (cur_time - start_time), "s")

    global usage
    usage = {}
    global one_stage
    if da_mode:
        three_stages = ["1-1", "1-2", "1-3"]
        three_double_stages = [["1-1", "1-2", "1-3"]]
        one_stage = ["1-1", "1-2", "1-3"]
        all_stages = ["1-1", "1-2", "1-3"]
        # all_double_stages = [["1"], ["2"], ["3"], ["4"]]
    else:
        one_stage = ["7-1", "7-2"]
        # three_stages = ["5-1", "5-2", "6-1", "6-2", "7-1", "7-2"]
        # three_double_stages = [["5-1", "5-2"], ["6-1", "6-2"], ["7-1", "7-2"]]

        three_stages = [
            "1-1",
            "1-2",
            "2-1",
            "2-2",
            "3-1",
            "3-2",
            "4-1",
            "4-2",
            "5-1",
            "5-2",
            "6-1",
            "6-2",
            "7-1",
            "7-2",
        ]
        three_double_stages = [
            ["1-1", "1-2"],
            ["2-1", "2-2"],
            ["3-1", "3-2"],
            ["4-1", "4-2"],
            ["5-1", "5-2"],
            ["6-1", "6-2"],
            ["7-1", "7-2"],
        ]
        all_stages = [
            "1-1",
            "1-2",
            "2-1",
            "2-2",
            "3-1",
            "3-2",
            "4-1",
            "4-2",
            "5-1",
            "5-2",
            "6-1",
            "6-2",
            "7-1",
            "7-2",
        ]
        # all_double_stages = [["1-1", "1-2"], ["2-1", "2-2"], ["3-1", "3-2"], ["4-1", "4-2"], ["5-1", "5-2"], ["6-1", "6-2"], ["7-1", "7-2"]]

    if "Char usages all stages" in run_commands:
        char_usages(all_players, archetype, past_phase, all_stages, filename="all")
        cur_time = time.time()
        print("done char: ", (cur_time - start_time), "s")

    if "Duos check" in run_commands:
        usage = char_usages(
            all_players, archetype, past_phase, three_stages, filename="all"
        )
        duo_usages(
            all_comps, all_players, usage, archetype, three_stages, check_duo=True
        )

    if "Char usages 8 - 10" in run_commands:
        usage = char_usages(
            all_players, archetype, past_phase, one_stage, filename="all"
        )
        if not whaleOnly and not f2pOnly:
            duo_usages(
                all_comps, all_players, usage, archetype, one_stage, check_duo=False
            )
        # appearances = {}
        # rounds = {}
        # for star_num in usage:
        #     appearances[star_num] = dict(sorted(usage[star_num].items(), key=lambda t: t[1]["app"], reverse=True))
        #     rounds[star_num] = dict(sorted(usage[star_num].items(), key=lambda t: t[1]["round"], reverse=True))
        #     for char in usage[star_num]:
        #         appearances[star_num][char] = {
        #             "app": usage[star_num][char]["app"],
        #             "rarity": usage[star_num][char]["rarity"],
        #             "diff": usage[star_num][char]["diff"]
        #         }
        #         if usage[star_num][char]["round"] == 0.0:
        #             continue
        #         rounds[star_num][char] = {
        #             "round": usage[star_num][char]["round"],
        #             "rarity": usage[star_num][char]["rarity"],
        #             "diff": usage[star_num][char]["diff_rounds"]
        #         }
        # with open("../char_results/appearance_top.json", "w") as out_file:
        #     out_file.write(json.dumps(appearances,indent=2))
        # with open("../char_results/rounds_top.json", "w") as out_file:
        #     out_file.write(json.dumps(rounds,indent=2))
        cur_time = time.time()
        print("done char 8 - 10: ", (cur_time - start_time), "s")

    if "Char usages for each stage" in run_commands:
        char_chambers = {"all": {}}
        for star_num in usage:
            char_chambers["all"][star_num] = usage[star_num].copy()
        # for room in all_stages:
        for room in three_stages:
            char_chambers[room] = char_usages(
                all_players,
                archetype,
                past_phase,
                [room],
                filename=room,
                offset=(3 if da_mode else 2),
            )
        appearances = {}
        rounds = {}
        for room in char_chambers:
            appearances[room] = {}
            rounds[room] = {}
            for star_num in char_chambers[room]:
                appearances[room][star_num] = dict(
                    sorted(
                        char_chambers[room][star_num].items(),
                        key=lambda t: t[1]["app"],
                        reverse=True,
                    )
                )
                if da_mode:
                    rounds[room][star_num] = dict(
                        sorted(
                            char_chambers[room][star_num].items(),
                            key=lambda t: t[1]["round"],
                            reverse=True,
                        )
                    )
                else:
                    rounds[room][star_num] = dict(
                        sorted(
                            char_chambers[room][star_num].items(),
                            key=lambda t: t[1]["round"],
                            reverse=False,
                        )
                    )
                for char in char_chambers[room][star_num]:
                    appearances[room][star_num][char] = {
                        "app": char_chambers[room][star_num][char]["app"],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff"],
                    }
                    if char_chambers[room][star_num][char]["round"] == 0:
                        continue
                    rounds[room][star_num][char] = {
                        "round": char_chambers[room][star_num][char]["round"],
                        # "prev_round": prev_chambers[room][str(star_num)][char],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff_rounds"],
                    }
        if not whaleOnly and not f2pOnly:
            with open("../char_results/appearance.json", "w") as out_file:
                out_file.write(json.dumps(appearances, indent=2))
            with open("../char_results/rounds.json", "w") as out_file:
                out_file.write(json.dumps(rounds, indent=2))
        cur_time = time.time()
        print("done char stage: ", (cur_time - start_time), "s")

    if "Char usages for each stage (combined)" in run_commands:
        char_chambers = {"all": {}}
        for star_num in usage:
            char_chambers["all"][star_num] = usage[star_num].copy()
        # for room in all_double_stages:
        for room in three_double_stages:
            char_chambers[room[0]] = char_usages(
                all_players, archetype, past_phase, room, filename=room[0].split("-")[0]
            )
        appearances = {}
        rounds = {}
        for room in char_chambers:
            appearances[room] = {}
            rounds[room] = {}
            for star_num in char_chambers[room]:
                appearances[room][star_num] = dict(
                    sorted(
                        char_chambers[room][star_num].items(),
                        key=lambda t: t[1]["app"],
                        reverse=True,
                    )
                )
                if da_mode:
                    rounds[room][star_num] = dict(
                        sorted(
                            char_chambers[room][star_num].items(),
                            key=lambda t: t[1]["round"],
                            reverse=True,
                        )
                    )
                else:
                    rounds[room][star_num] = dict(
                        sorted(
                            char_chambers[room][star_num].items(),
                            key=lambda t: t[1]["round"],
                            reverse=False,
                        )
                    )
                for char in char_chambers[room][star_num]:
                    appearances[room][star_num][char] = {
                        "app": char_chambers[room][star_num][char]["app"],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff"],
                    }
                    if char_chambers[room][star_num][char]["round"] == 0:
                        continue
                    rounds[room][star_num][char] = {
                        "round": char_chambers[room][star_num][char]["round"],
                        # "prev_round": prev_chambers[room][str(star_num)][char],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff_rounds"],
                    }
        if not whaleOnly and not f2pOnly:
            with open("../char_results/appearance_combine.json", "w") as out_file:
                out_file.write(json.dumps(appearances, indent=2))
            with open("../char_results/rounds_combine.json", "w") as out_file:
                out_file.write(json.dumps(rounds, indent=2))
        cur_time = time.time()
        print("done char stage (combine): ", (cur_time - start_time), "s")

    global all_comps_json
    all_comps_json = {}
    if "Comp usage all stages" in run_commands:
        comp_usages(all_comps, all_players, all_stages, filename="all", floor=True)
        cur_time = time.time()
        print("done comp all: ", (cur_time - start_time), "s")

    if "Comp usage 8 - 10" in run_commands:
        comp_usages(all_comps, all_players, one_stage, filename="top", floor=True)
        cur_time = time.time()
        print("done comp 8 - 10: ", (cur_time - start_time), "s")

    if "Comp usages for each stage" in run_commands:
        # for room in all_stages:
        for room in three_stages:
            comp_usages(
                all_comps,
                all_players,
                [room],
                filename=room,
                offset=(3 if da_mode else 2),
            )

        if not whaleOnly and not f2pOnly:
            with open("../char_results/demographic.json", "w") as out_file:
                out_file.write(json.dumps(sample_size, indent=2))
        cur_time = time.time()
        print("done comp stage: ", (cur_time - start_time), "s")

    if "Character specific infographics" in run_commands:
        comp_usages(
            all_comps,
            all_players,
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
        and not whaleOnly
        and not f2pOnly
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


def comp_usages(
    comps,
    players,
    rooms,
    filename="comp_usages",
    offset=1,
    info_char=False,
    floor=False,
):
    global top_comps_app
    top_comps_app = {}
    comps_dict = used_comps(players, comps, rooms, filename)
    rank_usages(comps_dict, rooms, owns_offset=offset)
    comp_usages_write(comps_dict, filename, floor, info_char, True)
    comp_usages_write(comps_dict, filename, floor, info_char, False)


def used_comps(players, comps, rooms, filename, phase=RECENT_PHASE):
    # Returns the dictionary of all the comps used and how many times they were used
    comps_dict = [{}, {}, {}, {}, {}]
    # error_uids = []
    # lessFour = []
    # lessFourComps = {}
    global total_comps
    total_comps = 0
    global all_comp_uids
    all_comp_uids = set()
    total_self_comps = 0
    all_comp_self_uids = set()
    whale_count = 0
    f2p_count = 0
    # dual_dps = {}
    # total_char_comps = {}
    for comp in comps:
        comp_tuple = tuple(comp.characters)
        # Check if the comp is used in the rooms that are being checked
        if comp.room not in rooms:
            continue

        foundchar = resetfind()
        for char in comp.characters:
            findchars(char, foundchar)
        if find_archetype(foundchar):
            total_comps += 1
            all_comp_uids.add(comp.player)
            if comp.player in self_uids:
                total_self_comps += 1
                all_comp_self_uids.add(comp.player)
            if len(comp_tuple) < 3:
                #     lessFour.append(comp.player)
                continue

            whale_comp = False
            f2p_comp = True
            dps_count = 0
            for char in range(3):
                if CHARACTERS[comp_tuple[char]]["availability"] == "Limited S":
                    if comp.char_cons:
                        if comp.char_cons[comp_tuple[char]] > 0:
                            whale_comp = True
                    if comp_tuple[char] in players[phase][comp.player].owned:
                        # if players[phase][comp.player].owned[comp_tuple[char]]["level"] > 51:
                        #     whale_comp = True
                        # if comp_tuple[char] in players[phase][comp.player].owned and comp_tuple[char] == "Blade":
                        if (
                            players[phase][comp.player].owned[comp_tuple[char]]["cons"]
                            > 0
                            # ) or (
                            #     whaleSigWeap and players[phase][comp.player].owned[comp_tuple[char]]["weapon"] in sigWeaps
                        ):
                            whale_comp = True
                        if (
                            players[phase][comp.player].owned[comp_tuple[char]][
                                "weapon"
                            ]
                            not in sigWeaps
                        ):
                            f2p_comp = False
                # if comp_tuple[char] not in total_char_comps:
                #     total_char_comps[comp_tuple[char]] = 0
                # total_char_comps[comp_tuple[char]] += 1
                if CHARACTERS[comp_tuple[char]]["role"] == "Damage Dealer":
                    dps_count += 1
                for duo_dps in valid_duo_dps:
                    if set(duo_dps).issubset(comp_tuple):
                        dps_count = 1
                        break

            if whale_comp:
                whale_count += 1
            if whaleOnly and not whale_comp:
                continue
            if f2p_comp:
                f2p_count += 1
            if f2pOnly and (not f2p_comp or whale_comp):
                continue
            if da_mode:
                if not whale_comp and comp.round_num > 50000:
                    continue
            else:
                if whale_comp:
                    if comp.round_num < 10:
                        continue
                elif comp.round_num < 20:
                    continue
            # if dps_count > 1:
            #     for char in range (3):
            #         if comp_tuple[char] not in dual_dps:
            #             dual_dps[comp_tuple[char]] = 0
            #         dual_dps[comp_tuple[char]] += 1

            for star_threshold in range(1, 5):
                if star_threshold != 4 and comp.star_num != star_threshold:
                    continue
                if comp_tuple not in comps_dict[star_threshold]:
                    comps_dict[star_threshold][comp_tuple] = {
                        "uses": 0,
                        "owns": 0,
                        "S count": comp.fivecount,
                        "comp_name": comp.comp_name,
                        "alt_comp_name": comp.alt_comp_name,
                        "dual_comp_name": comp.dual_comp_name,
                        "star_num": comp.star_num,
                        "round_num": {
                            "1": [],
                            "2": [],
                            "3": [],
                            "4": [],
                            "5": [],
                            "6": [],
                            "7": [],
                            "8": [],
                            "9": [],
                            "10": [],
                            "11": [],
                            "12": [],
                        },
                        "whale_count": set(),
                        "players": set(),
                    }
                    for char in range(3):
                        comps_dict[star_threshold][comp_tuple][comp_tuple[char]] = {
                            "weapon": {},
                            "artifacts": {},
                            "cons": {},
                        }
                        for i in range(7):
                            comps_dict[star_threshold][comp_tuple][comp_tuple[char]][
                                "cons"
                            ][str(i)] = 0
                comps_dict[star_threshold][comp_tuple]["uses"] += 1
                # comps_dict[star_threshold][comp_tuple]["round_num"][list(str(comp.room).split("-"))[0]].append(comp.round_num)
                comps_dict[star_threshold][comp_tuple]["players"].add(comp.player)
                if whale_comp:
                    comps_dict[star_threshold][comp_tuple]["whale_count"].add(
                        comp.player
                    )
                if whale_comp == whaleOnly and (not f2pOnly or f2p_comp):
                    comps_dict[star_threshold][comp_tuple]["round_num"][
                        list(str(comp.room).split("-"))[0]
                    ].append(comp.round_num)
                    if star_threshold == 4 and dps_count == 1:
                        avg_round_stage[list(str(comp.room).split("-"))[0]].append(
                            comp.round_num
                        )
                        # if da_mode:
                        #     if "buff_" + comp.buff not in sample_size[list(str(comp.room).split("-"))[0]]:
                        #         sample_size[list(str(comp.room).split("-"))[0]]["buff_" + comp.buff] = 0
                        #     sample_size[list(str(comp.room).split("-"))[0]]["buff_" + comp.buff] += 1

    for stage in avg_round_stage:
        sample_size[stage]["avg_round"] = round(
            statistics.mean(avg_round_stage[stage] if avg_round_stage[stage] else [0]),
            2,
        )
        # "3_star": three_star_sample[stage]
        # if sample_size[stage]["avg_round_stage"] > max_weight:
        #     max_weight = sample_size[stage]["avg_round_stage"]

    chamber_num = list(str(filename).split("-"))
    if len(chamber_num) > 1:
        # if total_comps == 0:
        #     del sample_size[chamber_num[0]]
        if chamber_num[1] == "1":
            sample_size[chamber_num[0]]["total"] = len(all_comp_uids)
            sample_size[chamber_num[0]]["self_report"] = len(all_comp_self_uids)
            sample_size[chamber_num[0]]["random"] = len(all_comp_uids) - len(
                all_comp_self_uids
            )
    # print(error_uids)
    # print("Less than four: " + str(lessFour))
    # print("Less than four: " + str(len(lessFour)/total_comps))
    # for char in dual_dps:
    #     dual_percent = dual_dps[char]/total_char_comps[char]
    #     if char in ["Jingliu", "Dan Heng • Imbibitor Lunae", "Kafka", "Jing Yuan", "Seele", "Blade", "Qingque", "Himeko", "Sushang"]:
    #     # if dual_percent > 0.5:
    #         print("Char: " + str(char))
    #         print("    Dual DPS: " + str(dual_percent))
    #         print()
    if whaleOnly:
        print("Whale percentage: " + str(whale_count / len(all_comp_uids)))
    return comps_dict


def rank_usages(comps_dict, rooms, owns_offset=1):
    # Calculate the usage rate and sort the comps according to it
    total = len(all_comp_uids) / 100.0
    # print()
    # print(rooms)
    # print("uids: " + str(len(all_comp_uids)))
    # print("total_battle: " + str(total_comps))
    # print("total: " + str(total))
    for star_threshold in range(1, 5):
        rates = []
        # rounds = []
        for comp in comps_dict[star_threshold]:
            avg_round = []
            uses_room = {}

            for room_num in range(1, 8):
                if comps_dict[star_threshold][comp]["round_num"][str(room_num)]:
                    uses_room[room_num] = len(
                        comps_dict[star_threshold][comp]["round_num"][str(room_num)]
                    )
                    if comps_dict[star_threshold][comp]["uses"] > 1:
                        # skewness = skew(comps_dict[star_threshold][comp]["round_num"][str(room_num)], axis=0, bias=True)
                        # if abs(skewness) > 0.8:
                        #     avg_round.append(trim_mean(comps_dict[star_threshold][comp]["round_num"][str(room_num)], 0.25))
                        # else:
                        avg_round.append(
                            statistics.mean(
                                comps_dict[star_threshold][comp]["round_num"][
                                    str(room_num)
                                ]
                            )
                        )
                    else:
                        avg_round.append(
                            statistics.mean(
                                comps_dict[star_threshold][comp]["round_num"][
                                    str(room_num)
                                ]
                            )
                        )
                    # avg_round.append(statistics.mean(comps_dict[star_threshold][comp]["round_num"][str(room_num)]))
                    # avg_round += comps_dict[star_threshold][comp]["round_num"][str(room_num)]

            comps_dict[star_threshold][comp]["is_count_round"] = True
            comps_dict[star_threshold][comp]["is_count_round_print"] = True
            if (rooms == one_stage) or da_mode and rooms == ["1-1", "1-2", "1-3"]:
                for room_num in uses_room:
                    if uses_room[room_num] < 20:
                        comps_dict[star_threshold][comp]["is_count_round"] = False
                    if uses_room[room_num] < 3:
                        comps_dict[star_threshold][comp]["is_count_round_print"] = False
            elif len(rooms) == 1:
                if comps_dict[star_threshold][comp]["uses"] < 20:
                    comps_dict[star_threshold][comp]["is_count_round"] = False
                if comps_dict[star_threshold][comp]["uses"] < 3:
                    comps_dict[star_threshold][comp]["is_count_round_print"] = False

            if avg_round:
                avg_round = round(statistics.mean(avg_round))
            else:
                avg_round = 600
                if da_mode:
                    avg_round = 0

            app = round(comps_dict[star_threshold][comp]["uses"] / total, 2)
            # if comps_dict[star_threshold][comp]["uses"] > 0:
            #     print(comp)
            #     print("app_flat: " + str(comps_dict[star_threshold][comp]["uses"]))
            #     print(app)
            #     input()
            comps_dict[star_threshold][comp]["app_rate"] = app
            comps_dict[star_threshold][comp]["round"] = avg_round
            # rate = int(100.0 * comps_dict[star_threshold][comp]["uses"] / comps_dict[star_threshold][comp]["owns"] * 100 + .5) / 100.0
            comps_dict[star_threshold][comp]["usage_rate"] = 0
            # own = int(100.0 * comps_dict[star_threshold][comp]["owns"] / (total_comps * owns_offset) * 100 + .5) / 100.0
            comps_dict[star_threshold][comp]["own_rate"] = 0
            rates.append(app)
            # rounds.append(avg_round)
        rates.sort(reverse=True)
        # rounds.sort(reverse=True)
        for comp in comps_dict[star_threshold]:
            comps_dict[star_threshold][comp]["app_rank"] = (
                rates.index(comps_dict[star_threshold][comp]["app_rate"]) + 1
            )
            # comps_dict[star_threshold][comp]["round_rank"] = rounds.index(comps_dict[star_threshold][comp]["round"]) + 1


def duo_usages(
    comps, players, usage, archetype, rooms, check_duo=False, filename="duo_usages"
) -> None:
    duos_dict = used_duos(players, comps, rooms, usage, check_duo)
    duo_write(duos_dict, usage, filename, archetype, check_duo)


def used_duos(players, comps, rooms, usage, check_duo, phase=RECENT_PHASE):
    # Returns dictionary of all the duos used and how many times they were used
    duos_dict = {}

    for comp in comps:
        if len(comp.characters) < 2 or comp.room not in rooms:
            continue

        foundchar = resetfind()
        whale_comp = False
        for char in comp.characters:
            findchars(char, foundchar)
            if CHARACTERS[char]["availability"] == "Limited S":
                if comp.char_cons:
                    if comp.char_cons[char] > 0:
                        whale_comp = True
                elif char in players[phase][comp.player].owned:
                    if players[phase][comp.player].owned[char]["cons"] > 0:
                        whale_comp = True
        if not find_archetype(foundchar):
            continue

        # Permutate the duos, for example if Ganyu and Xiangling are used,
        # two duos are used, Ganyu/Xiangling and Xiangling/Ganyu
        duos = list(permutations(comp.characters, 2))
        for duo in duos:
            is_triple_dps = False
            # comp_diff_duo = list(set(comp.characters) - set(duo))
            # for char_diff_duo in comp_diff_duo:
            #     if CHARACTERS[char_diff_duo]["role"] == "Damage Dealer" or char_diff_duo in ["Sampo", "Black Swan", "Luka", "Guinaifen", "Ruan Mei"]:
            #         is_triple_dps = True
            #         break

            if duo not in duos_dict:
                duos_dict[duo] = {
                    "app_flat": 0,
                    "round_num": {
                        "1": [],
                        "2": [],
                        "3": [],
                        "4": [],
                        "5": [],
                        "6": [],
                        "7": [],
                        "8": [],
                        "9": [],
                        "10": [],
                        "11": [],
                        "12": [],
                    },
                }
            duos_dict[duo]["app_flat"] += 1

            if is_triple_dps and check_duo:
                continue
            if not whale_comp:
                duos_dict[duo]["round_num"][list(str(comp.room).split("-"))[0]].append(
                    comp.round_num
                )

    sorted_duos = sorted(
        duos_dict.items(), key=lambda t: t[1]["app_flat"], reverse=True
    )
    duos_dict = {k: v for k, v in sorted_duos}

    sorted_duos = {}
    for duo in duos_dict:
        if usage[4][duo[0]]["app_flat"] > 0:
            # Calculate the appearance rate of the duo by dividing the appearance count
            # of the duo with the appearance count of the first character
            duos_dict[duo]["uses"] = round(
                duos_dict[duo]["app_flat"] * 100 / usage[4][duo[0]]["app_flat"], 2
            )
            duos_dict[duo]["app_flat"] = 0
            avg_round = []
            for room_num in range(1, 8):
                if duos_dict[duo]["round_num"][str(room_num)]:
                    avg_round += duos_dict[duo]["round_num"][str(room_num)]
            if avg_round:
                duos_dict[duo]["round_num"] = round(statistics.mean(avg_round))
            else:
                duos_dict[duo]["round_num"] = 600
                if da_mode:
                    duos_dict[duo]["round_num"] = 0
            if duo[0] not in sorted_duos:
                sorted_duos[duo[0]] = []
            sorted_duos[duo[0]].append(
                [
                    duo[1],
                    duos_dict[duo]["uses"],
                    duos_dict[duo]["round_num"],
                    duos_dict[duo]["app_flat"],
                ]
            )

    return sorted_duos


def char_usages(
    players,
    archetype,
    past_phase,
    rooms,
    filename="char_usages",
    offset=1,
    info_char=False,
):
    # own = cu.ownership(players)
    app = cu.appearances(players, chambers=rooms, offset=offset, info_char=info_char)
    chars_dict = cu.usages(app, past_phase, chambers=rooms, offset=offset)
    # # Print the list of weapons and artifacts used for a character
    # if floor:
    #     print(app[RECENT_PHASE][filename])
    if (not da_mode and rooms == one_stage) or da_mode:
        char_usages_write(chars_dict[4], filename, archetype)
    return chars_dict


def comp_usages_write(comps_dict, filename, floor, info_char, sort_app):
    out_json = []
    out_comps = []
    outvar_comps = []
    var_comps = []
    # exc_comps = []
    variations = {}
    if sort_app:
        threshold = app_rate_threshold
    else:
        threshold = app_rate_threshold_round

    # Sort the comps according to their usage rate
    for star_threshold in range(1, 5):
        if sort_app:
            comps_dict[star_threshold] = dict(
                sorted(
                    comps_dict[star_threshold].items(),
                    key=lambda t: t[1]["app_rate"],
                    reverse=True,
                )
            )
        else:
            if da_mode:
                comps_dict[star_threshold] = dict(
                    sorted(
                        comps_dict[star_threshold].items(),
                        key=lambda t: t[1]["round"],
                        reverse=True,
                    )
                )
            else:
                comps_dict[star_threshold] = dict(
                    sorted(
                        comps_dict[star_threshold].items(),
                        key=lambda t: t[1]["round"],
                        reverse=False,
                    )
                )
        comp_names = []
        dual_comp_names = []

        for comp in comps_dict[star_threshold]:
            if info_char and filename not in comp:
                continue
            if star_threshold == 4:
                comp_name = comps_dict[star_threshold][comp]["comp_name"]
                dual_comp_name = comps_dict[star_threshold][comp]["dual_comp_name"]
                alt_comp_name = comps_dict[star_threshold][comp]["alt_comp_name"]
                # Only one variation of each comp name is included,
                # unless if it's used for a character's infographic
                if (
                    (
                        comp_name not in comp_names
                        and comp_name not in dual_comp_names
                        and dual_comp_name not in comp_names
                        and alt_comp_name not in comp_names
                        and comps_dict[star_threshold][comp]["round"] != 1
                        and comps_dict[star_threshold][comp]["round"] != 0
                    )
                    or comp_name == "-"
                    or info_char
                ):
                    if sort_app:
                        top_comps_app[comp_name] = comps_dict[star_threshold][comp][
                            "app_rate"
                        ]
                    # elif comp_name in top_comps_app:
                    #     if (
                    #         comps_dict[star_threshold][comp]["is_count_round"]
                    #         and comps_dict[star_threshold][comp]["app_rate"]
                    #         < top_comps_app[comp_name] / 3
                    #     ):
                    #         continue
                    if comps_dict[star_threshold][comp]["is_count_round"] and (
                        comps_dict[star_threshold][comp]["app_rate"] >= threshold
                        or (
                            info_char
                            and comps_dict[star_threshold][comp]["app_rate"]
                            > char_app_rate_threshold
                        )
                    ):
                        if alt_comp_name != "-":
                            temp_comp_name = alt_comp_name
                        else:
                            temp_comp_name = comp_name

                        out_comps_append = {
                            "comp_name": temp_comp_name,
                            "char_1": comp[0],
                            "char_2": comp[1],
                            "char_3": comp[2],
                            "app_rate": str(
                                comps_dict[star_threshold][comp]["app_rate"]
                            )
                            + "%",
                            "avg_round": str(comps_dict[star_threshold][comp]["round"]),
                            # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                            # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%"
                        }

                        if info_char:
                            if comp_name not in comp_names:
                                variations[comp_name] = 1
                                out_comps_append["variation"] = variations[comp_name]
                            else:
                                variations[comp_name] += 1
                                out_comps_append["variation"] = variations[comp_name]

                        out_comps_append["whale_count"] = str(
                            len(comps_dict[star_threshold][comp]["whale_count"])
                        )
                        out_comps_append["app_flat"] = str(
                            len(comps_dict[star_threshold][comp]["players"])
                        )
                        out_comps_append["uses"] = str(
                            comps_dict[star_threshold][comp]["uses"]
                        )

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

                    # elif floor:
                    #     if alt_comp_name != "-":
                    #         temp_comp_name = alt_comp_name
                    #     else:
                    #         temp_comp_name = comp_name
                    #     exc_comps_append = {
                    #         "comp_name": temp_comp_name,
                    #         "char_1": comp[0],
                    #         "char_2": comp[1],
                    #         "char_3": comp[2],
                    #         # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                    #         # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%",
                    #     }
                    #     exc_comps_append["app_rate"] = str(comps_dict[star_threshold][comp]["app_rate"]) + "%"
                    #     exc_comps_append["avg_round"] = str(comps_dict[star_threshold][comp]["round"])
                    #     exc_comps.append(exc_comps_append)
                elif comp_name in comp_names:
                    if alt_comp_name != "-":
                        temp_comp_name = alt_comp_name
                    else:
                        temp_comp_name = comp_name
                    outvar_comps_append = {
                        "comp_name": temp_comp_name,
                        "char_1": comp[0],
                        "char_2": comp[1],
                        "char_3": comp[2],
                        # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                        # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%"
                    }
                    outvar_comps_append["app_rate"] = (
                        str(comps_dict[star_threshold][comp]["app_rate"]) + "%"
                    )
                    outvar_comps_append["avg_round"] = str(
                        comps_dict[star_threshold][comp]["round"]
                    )
                    outvar_comps.append(outvar_comps_append)
                if not info_char and (
                    # comps_dict[star_threshold][comp]["app_rate"] >= json_threshold or da_mode or (not da_mode and filename not in ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2"])
                    comps_dict[star_threshold][comp]["is_count_round_print"]
                    and (comps_dict[star_threshold][comp]["app_rate"] >= json_threshold)
                ):
                    out = name_filter(comp, mode="out")
                    for i in range(0, 3):
                        out[i] = slugify(out[i])
                        if out[i] in slug:
                            out[i] = slug[out[i]]
                    out_json_dict = {
                        "char_one": out[0],
                        "char_two": out[1],
                        "char_three": out[2],
                    }
                    out_json_dict["app_rate"] = comps_dict[star_threshold][comp][
                        "app_rate"
                    ]
                    out_json_dict["rank"] = comps_dict[star_threshold][comp]["app_rank"]
                    out_json_dict["avg_round"] = comps_dict[star_threshold][comp][
                        "round"
                    ]
                    out_json_dict["star_num"] = str(star_threshold)
                    # out_json_dict["rank"] = comps_dict[star_threshold][comp]["round_rank"]
                    out_json.append(out_json_dict)

    if info_char:
        out_comps += var_comps

    if archetype != "all":
        filename = filename + "_" + archetype

    if not (sort_app):
        filename = filename + "_rounds"

    if whaleOnly:
        filename = filename + "_C1"
    elif f2pOnly:
        filename = filename + "_E0S0"

    # if floor and not info_char:
    #     # csv_writer = csv.writer(open("../comp_results/f2p_app_" + filename + ".csv", 'w', newline=''))
    #     # for comps in f2p_comps:
    #     #     csv_writer.writerow(comps.values())
    #     with open("../comp_results/var_" + filename + ".json", "w") as out_file:
    #         out_file.write(json.dumps(outvar_comps,indent=2))

    if floor:
        csv_writer = csv.writer(
            open("../comp_results/comps_usage_" + filename + ".csv", "w", newline="")
        )
        for comps in out_comps:
            csv_writer.writerow(comps.values())
        # with open("../comp_results/exc_" + filename + ".json", "w") as out_file:
        #     out_file.write(json.dumps(exc_comps,indent=2))

    if not info_char and sort_app:
        # csv_writer = csv.writer(open("../comp_results/csv/" + filename + ".csv", 'w', newline=''))
        # csv_writer.writerow(out_json[0].keys())
        # for comps in out_json:
        #     csv_writer.writerow(comps.values())

        # with open("../comp_results/exc_" + filename + ".json", "w") as out_file:
        #     out_file.write(json.dumps(exc_comps,indent=2))

        all_comps_json[filename] = out_json.copy()
        with open("../comp_results/json/" + filename + ".json", "w") as out_file:
            out_file.write(json.dumps(out_json, indent=2))


def duo_write(duos_dict, usage, filename, archetype, check_duo):
    out_duos = []
    for char in duos_dict:
        if usage[4][char]["app_flat"] > 0:
            out_duos_append = {
                "char": char,
                "app": usage[4][char]["app"],
            }
            for i in range(duo_dict_len):
                if i < len(duos_dict[char]):
                    out_duos_append["char_" + str(i + 1)] = duos_dict[char][i][0]
                    out_duos_append["app_rate_" + str(i + 1)] = (
                        str(duos_dict[char][i][1]) + "%"
                    )
                    out_duos_append["avg_round_" + str(i + 1)] = duos_dict[char][i][2]
                    out_duos_append["app_flat_" + str(i + 1)] = duos_dict[char][i][3]
                else:
                    out_duos_append["char_" + str(i + 1)] = "-"
                    out_duos_append["app_rate_" + str(i + 1)] = "0.00%"
                    out_duos_append["avg_round_" + str(i + 1)] = 0.00
                    out_duos_append["app_flat_" + str(i + 1)] = 0
            out_duos.append(out_duos_append)
    out_duos = sorted(out_duos, key=lambda t: t["app"], reverse=True)

    if archetype != "all":
        filename = filename + "_" + archetype
    csv_writer = csv.writer(
        open("../char_results/" + filename + ".csv", "w", newline="")
    )
    count = 0
    out_duos_check = {}
    out_duos_exclu = {}
    for duos in out_duos:
        out_duos_check[duos["char"]] = {}
        out_duos_exclu[duos["char"]] = {}
        if count == 0:
            # csv_writer.writerow(duos.keys())
            temp_duos = ["char", "app"]
            for i in range(10):
                temp_duos += [
                    "char_" + str(i + 1),
                    "app_rate_" + str(i + 1),
                    "avg_round_" + str(i + 1),
                ]
            csv_writer.writerow(temp_duos)
            count += 1
        # csv_writer.writerow(duos.values())
        temp_duos = [
            duos["char"],
            duos["app"],
        ]
        for i in range(10):
            temp_duos += [
                duos["char_" + str(i + 1)],
                duos["app_rate_" + str(i + 1)],
                duos["avg_round_" + str(i + 1)],
            ]
        csv_writer.writerow(temp_duos)
        # duos.pop("round")
        for i in range(duo_dict_len):
            duos["app_rate_" + str(i + 1)] = float(duos["app_rate_" + str(i + 1)][:-1])
            if (
                duos["app_rate_" + str(i + 1)] >= 1
                and duos["app_flat_" + str(i + 1)] >= 10
                and (
                    (
                        duos["avg_round_" + str(i + 1)]
                        < usage[4][duos["char_" + str(i + 1)]]["round"]
                    )
                    or (
                        duos["avg_round_" + str(i + 1)]
                        < usage[4][duos["char"]]["round"]
                    )
                )
                and usage[4][duos["char_" + str(i + 1)]]["round"] != 1
                and usage[4][duos["char_" + str(i + 1)]]["round"] != 0
            ):
                # out_duos_exclu[duos["char"]][duos["char_" + str(i + 1)]] = {
                #     "app": duos["app_rate_" + str(i + 1)],
                #     "avg_round": duos["avg_round_" + str(i + 1)]
                # }
                # duos.pop("char_" + str(i + 1))
                # duos.pop("app_rate_" + str(i + 1))
                # duos.pop("avg_round_" + str(i + 1))
                # continue
                out_duos_check[duos["char"]][duos["char_" + str(i + 1)]] = {
                    "app": duos["app_rate_" + str(i + 1)],
                    "avg_round": duos["avg_round_" + str(i + 1)],
                }
    if check_duo:
        char_names = list(CHARACTERS.keys())
        out_dd = {}
        out_dd_list = []
        csv_writer = csv.writer(open("../char_results/duo_check.csv", "w", newline=""))
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
                        if char_j in out_duos_check[char_i]:
                            out_dd[frozenset([char_i, char_j])] = {
                                "char_i": char_i,
                                "char_i_app": str(
                                    out_duos_check[char_i][char_j]["app"]
                                ),
                                "char_j": char_j,
                                "char_j_app": str(
                                    out_duos_check[char_j][char_i]["app"]
                                ),
                                "avg_round": str(
                                    out_duos_check[char_i][char_j]["avg_round"]
                                ),
                            }
                        elif char_j in out_duos_exclu[char_i]:
                            out_dd[frozenset([char_i, char_j])] = {
                                "char_i": char_i,
                                "char_i_app": str(
                                    out_duos_exclu[char_i][char_j]["app"]
                                ),
                                "char_j": char_j,
                                "char_j_app": str(
                                    out_duos_check[char_j][char_i]["app"]
                                ),
                                "avg_round": str(
                                    out_duos_exclu[char_i][char_j]["avg_round"]
                                ),
                            }

        sorted_out_dd = sorted(
            out_dd.items(), key=lambda t: t[1]["char_i"], reverse=True
        )
        out_dd = {k: v for k, v in sorted_out_dd}

        for out_dd_print in out_dd_list:
            csv_writer.writerow(out_dd_print)
            # print(out_dd_print)
        for out_dd_print in out_dd:
            print(
                out_dd[out_dd_print]["char_i"]
                + ", "
                + out_dd[out_dd_print]["char_i_app"]
                + ", "
                + out_dd[out_dd_print]["char_j"]
                + ", "
                + out_dd[out_dd_print]["char_j_app"]
                + ", "
                + out_dd[out_dd_print]["avg_round"]
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
        exit()

    for i in range(len(out_duos)):
        for duo_value in ["char"] + [f"char_{i}" for i in range(1, 31)]:
            if out_duos[i][duo_value]:
                out_duos[i][duo_value] = slugify(out_duos[i][duo_value])
                if out_duos[i][duo_value] in slug:
                    out_duos[i][duo_value] = slug[out_duos[i][duo_value]]
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_duos, indent=2))


def char_usages_write(chars_dict, filename, archetype):
    out_chars = []
    out_chars_csv = []
    weap_len = 10
    arti_len = 10
    chars_dict = dict(
        sorted(chars_dict.items(), key=lambda t: t[1]["app"], reverse=True)
    )
    for char in chars_dict:
        out_chars_append = {
            "char": char,
            "app_rate": str(chars_dict[char]["app"]) + "%",
            "avg_round": str(chars_dict[char]["round"]),
            # "prev_avg_round": str(prev_round.get(char, 1)),
            "std_dev_round": str(chars_dict[char]["std_dev_round"]),
            "q1_round": str(chars_dict[char]["q1_round"]),
            # "usage_rate": str(chars_dict[char]["usage"]) + "%",
            # "own_rate": str(chars_dict[char]["own"]) + "%",
            "role": chars_dict[char]["role"],
            "rarity": chars_dict[char]["rarity"],
            "diff": str(chars_dict[char]["diff"]) + "%",
            "diff_rounds": str(chars_dict[char]["diff_rounds"]),
        }
        for i in ["app_rate", "diff", "diff_rounds"]:
            if out_chars_append[i] == "-%":
                out_chars_append[i] = "-"
        if list(chars_dict[char]["weapons"]):
            for i in range(weap_len):
                if i < len(list(chars_dict[char]["weapons"])):
                    out_chars_append["weapon_" + str(i + 1)] = list(
                        chars_dict[char]["weapons"]
                    )[i]
                    out_chars_append["weapon_" + str(i + 1) + "_app"] = (
                        str(list(chars_dict[char]["weapons"].values())[i]["percent"])
                        + "%"
                    )
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = str(
                        list(chars_dict[char]["weapons"].values())[i]["avg_round"]
                    )
                else:
                    out_chars_append["weapon_" + str(i + 1)] = ""
                    out_chars_append["weapon_" + str(i + 1) + "_app"] = "0.0"
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = "600"
                    if da_mode:
                        out_chars_append["weapon_" + str(i + 1) + "_round"] = "0.0"
            for i in range(arti_len):
                if i < len(list(chars_dict[char]["artifacts"])):
                    arti_name = list(chars_dict[char]["artifacts"])[i]
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
                        str(list(chars_dict[char]["artifacts"].values())[i]["percent"])
                        + "%"
                    )
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = str(
                        list(chars_dict[char]["artifacts"].values())[i]["avg_round"]
                    )
                else:
                    out_chars_append["artifact_" + str(i + 1)] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_1"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_3"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_app"] = "0.0"
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = "600"
                    if da_mode:
                        out_chars_append["artifact_" + str(i + 1) + "_round"] = "0.0"
            # for i in range(7):
            #     out_chars_append["use_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[2]) + "%"
            #     if out_chars_append["use_" + str(i)] == "-%":
            #         out_chars_append["use_" + str(i)] = "-"
            #     out_chars_append["own_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[1]) + "%"
            #     if out_chars_append["own_" + str(i)] == "-%":
            #         out_chars_append["own_" + str(i)] = "-"
            for i in range(7):
                out_chars_append["app_" + str(i)] = (
                    str(
                        list(list(chars_dict[char]["cons_usage"].values())[i].values())[
                            0
                        ]
                    )
                    + "%"
                )
                out_chars_append["round_" + str(i)] = str(
                    list(list(chars_dict[char]["cons_usage"].values())[i].values())[3]
                )
                if out_chars_append["app_" + str(i)] == "-%":
                    out_chars_append["app_" + str(i)] = "-"
            out_chars_append["cons_avg"] = chars_dict[char]["cons_avg"]
            out_chars_append["sample"] = chars_dict[char]["sample"]
            out_chars_append["sample_app_flat"] = chars_dict[char]["sample_app_flat"]
        else:
            for i in range(weap_len):
                out_chars_append["weapon_" + str(i + 1)] = ""
                out_chars_append["weapon_" + str(i + 1) + "_app"] = "0.0"
                out_chars_append["weapon_" + str(i + 1) + "_round"] = "600"
                if da_mode:
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = "0.0"
            for i in range(arti_len):
                out_chars_append["artifact_" + str(i + 1)] = ""
                out_chars_append["artifact_" + str(i + 1) + "_1"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_3"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_app"] = "0.0"
                out_chars_append["artifact_" + str(i + 1) + "_round"] = "600"
                if da_mode:
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = "0.0"
            # for i in range(7):
            #     out_chars_append["use_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[2]) + "%"
            #     if out_chars_append["use_" + str(i)] == "-%":
            #         out_chars_append["use_" + str(i)] = "-"
            #     out_chars_append["own_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[1]) + "%"
            #     if out_chars_append["own_" + str(i)] == "-%":
            #         out_chars_append["own_" + str(i)] = "-"
            for i in range(7):
                out_chars_append["app_" + str(i)] = "0.0%"
                out_chars_append["round_" + str(i)] = "600"
                if da_mode:
                    out_chars_append["round_" + str(i)] = "0.0"
            out_chars_append["cons_avg"] = chars_dict[char]["cons_avg"]
            out_chars_append["sample"] = chars_dict[char]["sample"]
            out_chars_append["sample_app_flat"] = chars_dict[char]["sample_app_flat"]
        out_chars.append(out_chars_append)
        out_chars_csv.append(out_chars_append.copy())
        if char == filename:
            break

    if archetype != "all":
        filename = filename + "_" + archetype
    if whaleOnly:
        filename = filename + "_C1"
    elif f2pOnly:
        filename = filename + "_E0S0"

    iterate_value_app = ["app_rate", "diff"]
    iterate_value_round = ["avg_round", "std_dev_round", "q1_round", "diff_rounds"]
    iterate_name_arti = []
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
        out_chars[i]["char"] = slugify(out_chars[i]["char"])
        if out_chars[i]["char"] in slug:
            out_chars[i]["char"] = slug[out_chars[i]["char"]]
        for value in iterate_value_app:
            if out_chars[i][value][:-1].replace(".", "").replace("-", "").isnumeric():
                out_chars[i][value] = float(out_chars[i][value][:-1])
            else:
                out_chars[i][value] = 0.00
        for value in iterate_value_round:
            if out_chars[i][value].replace(".", "").replace("-", "").isnumeric():
                out_chars[i][value] = round(float(out_chars[i][value]))
            else:
                out_chars[i][value] = 600
                if da_mode:
                    out_chars[i][value] = 0
        for value in iterate_name_arti:
            if out_chars[i][value]:
                out_chars[i][value] = (
                    out_chars[i][value].replace(".", "").replace("-", "")
                )
            else:
                out_chars[i][value] = 600
                if da_mode:
                    out_chars[i][value] = 0
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_chars, indent=2))

    csv_writer = csv.writer(
        open("../char_results/" + filename + ".csv", "w", newline="")
    )
    count = 0
    for chars in out_chars_csv:
        if count == 0:
            header = chars.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(chars.values())


def name_filter(comp, mode="out"):
    filtered = []
    if mode == "out":
        for char in comp:
            # if CHARACTERS[char]["out_name"]:
            #     filtered.append(CHARACTERS[char]["alt_name"])
            # else:
            filtered.append(char)
    return filtered


main()
