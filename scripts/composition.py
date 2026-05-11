"""An object that stores information about a particular composition."""

import json
from typing import Literal

from comp_rates_config import da_mode

# Set class constants in initialization
# Load the list of characters from their file
with open("../data/characters.json") as char_file:
    CHARACTERS = json.load(char_file)

RoleLit = Literal[
    "Attack",
    "Stun",
    "Anomaly",
    "Support",
    "Defense",
    "Rupture",
]


class Composition:
    """An object that stores information about a particular composition."""

    def __init__(
        self,
        uid: str,
        comp_chars: list[str],
        round_num: str,
        star_num: int,
        room: str,
        bangboo: str,
        comp_chars_cons: list[int],
    ) -> None:
        """Composition constructor."""
        self.player = str(uid)
        self.room = room
        self.round_num = int(round_num)
        self.star_num = int(star_num)
        self.char_structs(comp_chars, comp_chars_cons)
        self.bangboo = bangboo

    def char_structs(self, comp_chars: list[str], comp_chars_cons: list[int]) -> None:
        """Character structure creator."""
        self.char_presence: dict[str, bool] = {}
        self.char_cons: dict[str, int] = {}
        fives: list[str] = []
        self.dps: list[str] = []
        self.subdps: list[str] = []
        self.stun: list[str] = []
        self.support: list[str] = []
        len_elem: dict[str, int] = {
            "Ice": 0,
            "Fire": 0,
            "Ether": 0,
            "Electric": 0,
            "Physical": 0,
        }
        len_role: dict[RoleLit, int] = {
            "Attack": 0,
            "Stun": 0,
            "Anomaly": 0,
            "Support": 0,
            "Defense": 0,
            "Rupture": 0,
        }
        if comp_chars_cons:
            for char_iter in range(len(comp_chars)):
                self.char_cons[comp_chars[char_iter]] = int(comp_chars_cons[char_iter])
        comp_chars.sort()
        for character in comp_chars:
            char_data = CHARACTERS[character]
            self.char_presence[character] = True
            if char_data["availability"] in ["Limited S", "Standard S"]:
                fives.append(character)

            if character in [
                "Miyabi",
                "Zhu Yuan",
                "Ellen",
                "Soldier 11",
                "Evelyn",
                "Soldier 0 - Anby",
                "Hugo",
                "Yixuan",
                "Alice",
                "Manato",
                "Yidhari",
                "Banyue",
                "Ye Shunguang",
                "Aria",
                "Promeia",
            ]:
                self.dps.insert(0, character)
            if character in [
                "Corin",
                "Billy",
                "Nekomata",
                "Anton",
                "Harumasa",
                "Seed",
                "Orphie & Magus",
                "Cissia",
            ]:
                self.dps.append(character)
            elif character in [
                "Piper",
                "Jane",
                "Yanagi",
            ]:
                self.subdps.insert(0, character)
            elif character in [
                "Grace",
                "Burnice",
                "Vivian",
            ]:
                self.subdps.append(character)
            elif character in [
                "Anby",
                "Lycaon",
                "Koleda",
                "Qingyi",
                "Lighter",
                "Pulchra",
                "Trigger",
                "Ju Fufu",
                "Dialyn",
                "Nangong Yu",
            ]:
                self.stun.insert(0, character)
            elif character in [
                "Soukaku",
                "Nicole",
                "Rina",
                "Lucy",
                "Seth",
                "Astra Yao",
                "Pan Yinhu",
                "Yuzuha",
                "Lucia",
                "Zhao",
                "Sunna",
            ]:
                self.support.insert(0, character)
            elif character in [
                "Caesar",
                "Ben",
            ]:
                self.support.append(character)

            len_elem[char_data["element"]] += 1
            len_role[char_data["specialty"]] += 1
        self.fivecount = len(fives)
        self.characters = self.dps + self.subdps + self.stun + self.support

        self.flag_cheat = self.detect_cheat(len_elem, len_role)
        self.valid_clear = self.star_num == 3

        if not self.dps and not self.subdps and "Soukaku" in self.support:
            self.support.remove("Soukaku")
            self.dps.append("Soukaku")

        """Name structure creator.
        """
        self.comp_name = "-"
        self.alt_comp_name = "-"
        self.dual_comp_name = "-"

        if self.comp_name == "-":
            archetype = ""
            if len(self.dps) + len(self.subdps) > 1:
                if len(self.dps) + len(self.subdps) > 2:
                    archetype = " Triple Carry"
                else:
                    archetype = " Dual Carry"
                self.dual_comp_name = self.characters[1] + archetype
            elif len(self.support) > 1:
                archetype = " Dual Support"
            elif len(self.stun) > 0:
                archetype = " Stun"

            if self.dps or self.subdps or self.stun:
                self.comp_name = self.characters[0] + archetype
            else:
                self.comp_name = "Full Support"

    def detect_cheat(
        self,
        len_elem: dict[str, int],
        len_role: dict[RoleLit, int],
    ) -> bool:
        """Return a bool whether this comp is a cheat."""
        da_weak: list[bool] = []

        sd_weak: list[bool] = []

        cheat_conditions: list[bool] = [
            len_role["Anomaly"] > 0 and len_role["Attack"] + len_role["Rupture"] > 0,
            len(self.characters) < 3,
            any(sd_weak) and not da_mode,
            any(da_weak) and da_mode,
        ]

        high_score = self.round_num >= (50000 if da_mode else 45000)
        max_score = self.round_num >= (55000 if da_mode else 49000)
        return (any(cheat_conditions) and high_score) or max_score

    def contains_chars(self, chars: list[str]) -> bool:
        """Return a bool whether this comp contains all the chars in included list."""
        return all(self.char_presence[char] for char in chars)
