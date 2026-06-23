"""Compile all HSR character data."""

# pyright: reportUnknownVariableType=false, reportMissingTypeStubs=false
import json
import warnings
from itertools import chain
from statistics import mean, stdev

from comp_rates_config import (
    BOOS_INFO,
    CHARS_INFO,
    CONS_LIMIT,
    DEFAULT_ROUND,
    F2P_ONLY,
    WHALE_ONLY,
    da_mode,
    sig_weaps,
)
from percentile import calculate_percentile
from player_phase import PlayerPhase
from scipy.stats import skew, trim_mean

warnings.filterwarnings("ignore", category=RuntimeWarning)
ONE_STAGE = ["1-1", "1-2", "1-3"] if da_mode else ["5-1", "5-2", "5-3"]
ROOMS = ONE_STAGE if da_mode else ["5-1", "5-2", "5-3"]
SKEW_LIMIT = 0.8
SKEW_APP_LIMIT = 10
gear_app_threshold = 0


class RoundApp:
    """Class for storing appearance data for each round."""

    def __init__(self) -> None:
        """Initialize RoundApp class."""
        self.app_flat: int = 0
        self.app_flat_all: int = 0
        self.app: float = 0
        self.round_list = {str(i): list[int]() for i in range(1, 13)}
        self.round: float = 0


class CharApp(RoundApp):
    """Class for storing appearance data for each character."""

    def __init__(self) -> None:
        """Initialize CharApp class."""
        super().__init__()
        self.app_flat_exclude: int = 0
        self.app_exclude: float = 0
        self.owned: int = 0
        self.std_dev_round: float = 0
        self.q1_round: float = 0
        self.weap_freq: dict[str, RoundApp] = {}
        self.arti_freq: dict[str, RoundApp] = {}
        self.cons_avg: float = 0
        self.sample: int = 0
        self.sample_app_flat: int = 0
        self.cons_freq = {i: RoundApp() for i in range(7)}


def appearances(
    users: dict[str, PlayerPhase],
    chambers: list[str] = ROOMS,
    info_char: bool = False,
) -> tuple[dict[str, CharApp], dict[str, CharApp]]:
    """Calculate appearance data for each character."""
    app: dict[str, CharApp] = {}
    user_chars: dict[str, set[str]] = {}
    app_boos: dict[str, CharApp] = {}
    user_boos: dict[str, set[str]] = {}

    all_uids = set[str]()
    cheated_uids = set[str]()

    for character in CHARS_INFO:
        user_chars[character] = set()
        app[character] = CharApp()
    for boo in BOOS_INFO:
        user_boos[boo] = set()
        app_boos[boo] = CharApp()

    # There's probably a better way to cache these things
    for user in users.values():
        for chamber, cur_user in user.chambers.items():
            if chamber not in chambers or not cur_user.valid_clear:
                continue
            whale_comp = False
            giga_whale = False
            f2p_comp = True

            for char in cur_user.characters:
                if (
                    CHARS_INFO[char].availability == "Limited S"
                    and cur_user.char_cons
                    and cur_user.char_cons[char] > 0
                ):
                    whale_comp = True
                    if cur_user.char_cons[char] > CONS_LIMIT:
                        giga_whale = True
                if char in user.owned and user.owned[char].weapon in sig_weaps:
                    f2p_comp = False
            if cur_user.flag_cheat:
                cheated_uids.add(user.player)
                continue

            all_uids.add(user.player)

            # >E2 clears should still be included to calculate
            # characters' average score for all eidolons
            if (WHALE_ONLY and (giga_whale or not whale_comp)) or (
                F2P_ONLY and (not f2p_comp or whale_comp)
            ):
                continue

            cur_chamber = next(iter(str(chamber).split("-")))
            for char in cur_user.characters:
                user_round = cur_user.round_num

                app[char].app_flat_all += 1
                if cur_user.char_cons and chambers == ONE_STAGE:
                    char_con = cur_user.char_cons[char]
                    app[char].cons_freq[char_con].app_flat += 1
                    app[char].cons_freq[char_con].round_list[cur_chamber].append(
                        user_round,
                    )
                    app[char].cons_avg += char_con

                if giga_whale:
                    continue

                # to print the amount of players using a character,
                # for char infographics
                if chambers == ONE_STAGE:
                    user_chars[char].add(user.player)

                app[char].app_flat += 1
                if whale_comp == WHALE_ONLY and (not F2P_ONLY or f2p_comp):
                    app[char].app_flat_exclude += 1

                if whale_comp == WHALE_ONLY and (not F2P_ONLY or f2p_comp):
                    if CHARS_INFO[char].availability == "Limited S":
                        app[char].cons_freq[0].round_list[cur_chamber].append(
                            cur_user.round_num,
                        )
                    app[char].round_list[cur_chamber].append(cur_user.round_num)
                # In case of character in comp data missing from character data
                if chambers != ONE_STAGE:
                    continue
                if char not in user.owned:
                    continue
                app[char].owned += 1

                weapon = user.owned[char].weapon
                if weapon != "":
                    if weapon not in app[char].weap_freq:
                        app[char].weap_freq[weapon] = RoundApp()
                    app[char].weap_freq[weapon].app_flat += 1
                    if not whale_comp:
                        app[char].weap_freq[weapon].round_list[cur_chamber].append(
                            cur_user.round_num,
                        )

                artifact = user.owned[char].artifacts
                if artifact != "":
                    if artifact not in app[char].arti_freq:
                        app[char].arti_freq[artifact] = RoundApp()
                    app[char].arti_freq[artifact].app_flat += 1
                    if not whale_comp:
                        app[char].arti_freq[artifact].round_list[cur_chamber].append(
                            cur_user.round_num,
                        )

            boo = cur_user.bangboo
            if boo:
                if chambers == ONE_STAGE:
                    user_boos[boo].add(user.player)
                app_boos[boo].app_flat += 1

                if whale_comp == WHALE_ONLY and (not F2P_ONLY or f2p_comp):
                    app_boos[boo].round_list[cur_chamber].append(cur_user.round_num)

    total = len(all_uids) / 100.0
    for char, char_item in chain(app.items(), app_boos.items()):
        if total > 0:
            char_item.app = round(char_item.app_flat / total, 2)
            char_item.app_exclude = round(char_item.app_flat_exclude / total, 2)
        if char_item.app_flat >= 20:
            avg_round: list[float] = []
            std_dev_round: list[float] = []
            q1_round: list[float] = []
            uses_room: dict[int, int] = {}

            for room_num in range(1, 8):
                round_list = char_item.round_list[str(room_num)]
                if round_list:
                    uses_room[room_num] = len(round_list)
                    if len(round_list) > 1:
                        std_dev_round.append(stdev(round_list))
                        q1_round.append(calculate_percentile(round_list, 75))

                        skewness = skew(round_list, axis=0, bias=True)
                        if abs(skewness) > SKEW_LIMIT:
                            avg_round.append(trim_mean(round_list, 0.25))
                        else:
                            avg_round.append(mean(round_list))
                    else:
                        std_dev_round.append(0)
                        q1_round.append(0)
                        avg_round.append(mean(round_list))

            is_count_cycles = True
            if not uses_room:
                is_count_cycles = False
            elif chambers == ONE_STAGE:
                char_item.sample_app_flat = uses_room[1 if da_mode else 5]
            for uses_room_num in uses_room.values():
                if uses_room_num < 10:
                    is_count_cycles = False
                    break

            # if avg_round:
            if is_count_cycles:
                char_item.round = round(mean(avg_round))
                char_item.std_dev_round = round(mean(std_dev_round))
                char_item.q1_round = round(mean(q1_round))
            else:
                char_item.round = DEFAULT_ROUND
                char_item.q1_round = DEFAULT_ROUND
        else:
            char_item.round = DEFAULT_ROUND
            char_item.q1_round = DEFAULT_ROUND

        char_item.sample = len(
            user_chars[char] if char in user_chars else user_boos[char],
        )

        if chambers != ONE_STAGE:
            continue
        # Calculate constellations
        if char_item.app_flat_all > 0:
            char_item.cons_avg = round(char_item.cons_avg / char_item.app_flat_all, 2)
        for cons_freq in char_item.cons_freq.values():
            if cons_freq.app_flat > 0:
                cons_freq.app = round(
                    cons_freq.app_flat / char_item.app_flat_all * 100,
                    2,
                )
                avg_round = []
                for room_num in range(1, 8):
                    if cons_freq.round_list[str(room_num)]:
                        if cons_freq.app_flat > SKEW_APP_LIMIT:
                            skewness = skew(
                                cons_freq.round_list[str(room_num)],
                                axis=0,
                                bias=True,
                            )
                            if abs(skewness) > SKEW_LIMIT:
                                avg_round.append(
                                    trim_mean(
                                        cons_freq.round_list[str(room_num)],
                                        0.25,
                                    ),
                                )
                            else:
                                avg_round.append(
                                    mean(cons_freq.round_list[str(room_num)]),
                                )
                        else:
                            avg_round.append(mean(cons_freq.round_list[str(room_num)]))
                if avg_round:
                    cons_freq.round = round(mean(avg_round))
                else:
                    cons_freq.round = DEFAULT_ROUND
            else:
                cons_freq.app = 0.00
                cons_freq.round = DEFAULT_ROUND

        app_flat = char_item.owned / 100.0
        # Calculate weapons
        sorted_weapons = sorted(
            char_item.weap_freq.items(),
            key=lambda t: t[1].app_flat,
            reverse=True,
        )
        char_item.weap_freq = dict(sorted_weapons)
        for weap_freq in char_item.weap_freq.values():
            # If a gear appears >15 times, include it
            # Because there might be 1* gears
            # If it's for character infographic, include all gears
            if (
                weap_freq.app_flat > gear_app_threshold
                or info_char
                or (weap_freq.app_flat / app_flat) > 20
            ):
                weap_freq.app = round(weap_freq.app_flat / app_flat, 2)
                avg_round = []
                for room_num in range(1, 8):
                    if weap_freq.round_list[str(room_num)]:
                        if weap_freq.app_flat > SKEW_APP_LIMIT:
                            skewness = skew(
                                weap_freq.round_list[str(room_num)],
                                axis=0,
                                bias=True,
                            )
                            if abs(skewness) > SKEW_LIMIT:
                                avg_round.append(
                                    trim_mean(
                                        weap_freq.round_list[str(room_num)],
                                        0.25,
                                    ),
                                )
                            else:
                                avg_round.append(
                                    mean(weap_freq.round_list[str(room_num)]),
                                )
                        else:
                            avg_round.append(mean(weap_freq.round_list[str(room_num)]))
                if avg_round:
                    weap_freq.round = round(mean(avg_round))
                else:
                    weap_freq.round = DEFAULT_ROUND
            else:
                weap_freq.app = 0
                weap_freq.round = DEFAULT_ROUND

        # Remove flex artifacts
        if "Flex" in char_item.arti_freq:
            del char_item.arti_freq["Flex"]
        # Calculate artifacts
        sorted_arti = sorted(
            char_item.arti_freq.items(),
            key=lambda t: t[1].app_flat,
            reverse=True,
        )
        char_item.arti_freq = dict(sorted_arti)
        for arti, arti_freq in char_item.arti_freq.items():
            # If a gear appears >15 times, include it
            # Because there might be 1* gears
            # If it's for character infographic, include all gears
            if (
                arti_freq.app_flat > gear_app_threshold or info_char
            ) and arti != "Flex":
                arti_freq.app = round(arti_freq.app_flat / app_flat, 2)
                avg_round = []
                for room_num in range(1, 8):
                    if arti_freq.round_list[str(room_num)]:
                        if arti_freq.app_flat > SKEW_APP_LIMIT:
                            skewness = skew(
                                arti_freq.round_list[str(room_num)],
                                axis=0,
                                bias=True,
                            )
                            if abs(skewness) > SKEW_LIMIT:
                                avg_round.append(
                                    trim_mean(
                                        arti_freq.round_list[str(room_num)],
                                        0.25,
                                    ),
                                )
                            else:
                                avg_round.append(
                                    mean(arti_freq.round_list[str(room_num)]),
                                )
                        else:
                            avg_round.append(mean(arti_freq.round_list[str(room_num)]))
                if avg_round:
                    arti_freq.round = round(mean(avg_round))
                else:
                    arti_freq.round = DEFAULT_ROUND
            else:
                arti_freq.app = 0
                arti_freq.round = DEFAULT_ROUND
    return (app, app_boos)


class CharUsageData(CharApp):
    """Class for storing usage data for each character."""

    def __init__(self, char_app: CharApp, char: str) -> None:
        """Initialize CharUsageData class."""
        if "solo-" in char:
            char = char.replace("solo-", "")
        if "supp-" in char:
            char = char.replace("supp-", "")
        super().__init__()
        self.__dict__.update(char_app.__dict__)
        self.usage = 0
        self.diff: str | int = "-"
        self.diff_rounds = "-"
        self.role = str(CHARS_INFO[char].role if char in CHARS_INFO else "")
        self.rarity = str(
            CHARS_INFO[char].availability
            if char in CHARS_INFO
            else BOOS_INFO[char].availability,
        )
        self.weapons: dict[str, RoundApp] = {}
        self.weapons_round: dict[str, RoundApp] = {}
        self.artifacts: dict[str, RoundApp] = {}
        self.artifacts_round: dict[str, RoundApp] = {}
        self.cons_usage = {i: dict[str, str]() for i in range(7)}
        self.rank: int


def usages(
    app: tuple[dict[str, CharApp], dict[str, CharApp]],
    past_phase: str,
    chambers: list[str] = ROOMS,
) -> tuple[dict[str, CharUsageData], dict[str, CharUsageData]]:
    """Calculate usage data for each character."""
    uses: dict[str, CharUsageData] = {}
    uses_boos: dict[str, CharUsageData] = {}
    past_usage: dict[str, dict[str, dict[str, float]]] = {}
    past_rounds: dict[str, dict[str, dict[str, float]]] = {}
    past_usage_boos: dict[str, dict[str, dict[str, float]]] = {}
    past_rounds_boos: dict[str, dict[str, dict[str, float]]] = {}
    rates: list[float] = []
    rates_boos: list[float] = []

    stage = "all" if chambers == ONE_STAGE else chambers[0]

    try:
        with open(
            "../results/char_results/" + past_phase + "/appearance.json",
        ) as stats:
            past_usage = json.load(stats)
        with open("../results/char_results/" + past_phase + "/rounds.json") as stats:
            past_rounds = json.load(stats)
    except FileNotFoundError:
        pass
    try:
        with open(
            "../results/char_results/" + past_phase + "/bangboo_appearance.json",
        ) as stats:
            past_usage = json.load(stats)
        with open(
            "../results/char_results/" + past_phase + "/bangboo_rounds.json",
        ) as stats:
            past_rounds = json.load(stats)
    except FileNotFoundError:
        pass

    app_chars, app_boos = app

    for boo, app_boo in app_boos.items():
        uses_boos[boo] = CharUsageData(app_boo, boo)
        rates_boos.append(uses_boos[boo].app)
        if stage not in past_usage_boos:
            continue
        if boo in past_usage_boos[stage]:
            uses_boos[boo].diff = str(
                round(app_boo.app - past_usage_boos[stage][boo]["app"], 2),
            )
        if boo in past_rounds_boos[stage]:
            uses_boos[boo].diff_rounds = str(
                round(app_boo.round - past_rounds_boos[stage][boo]["round"], 2),
            )
    rates_boos.sort(reverse=True)
    for uses_boo in uses_boos.values():
        # if owns[boo.app_flat > 0:
        uses_boo.rank = rates_boos.index(uses_boo.app) + 1

    for char, app_char in app_chars.items():
        uses[char] = CharUsageData(app_char, char)
        rates.append(uses[char].app)

        if stage in past_usage and char in past_usage[stage]:
            uses[char].diff = str(
                round(app_char.app - past_usage[stage][char]["app"], 2),
            )
        if stage in past_rounds and char in past_rounds[stage]:
            uses[char].diff_rounds = str(
                round(app_char.round - past_rounds[stage][char]["round"], 2),
            )

        for i in range(7):
            uses[char].cons_usage[i] = {"app": "-", "own": "-", "usage": "-"}

        if chambers != ONE_STAGE:
            continue

        weapons = list(app_char.weap_freq)
        for i in range(len(weapons)):
            uses[char].weapons[weapons[i]] = app_char.weap_freq[weapons[i]]

        artifacts = list(app_char.arti_freq)
        for i in range(len(artifacts)):
            uses[char].artifacts[artifacts[i]] = app_char.arti_freq[artifacts[i]]

        for i in range(7):
            uses[char].cons_usage[i]["app"] = str(app_char.cons_freq[i].app)
            uses[char].cons_usage[i]["round"] = str(app_char.cons_freq[i].round)
    rates.sort(reverse=True)
    for char, char_use in uses.items():
        uses[char].rank = rates.index(char_use.app) + 1

    return uses, uses_boos
