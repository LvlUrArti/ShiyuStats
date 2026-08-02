"""An object that stores information about a player on a phase."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal, cast

if TYPE_CHECKING:
    from composition import Composition, Stage

# Set class constants in initialization
with open("../data/drive_affixes.json") as relic_file:
    articombinations = json.load(relic_file)


ElemLit = Literal[
    "Ice",
    "Fire",
    "Ether",
    "Electric",
    "Physical",
    "Wind",
    "Lumiflux",
]


class OwnedChars:
    """An object that stores information about owned characters."""

    def __init__(
        self,
        level: str,
        cons: str,
        weapon: str,
        element: str,
        artifacts: str,
    ) -> None:
        """Character constructor."""
        self.level: int = int(level)
        self.cons: int = int(cons)
        self.weapon: str = weapon
        self.element: ElemLit = cast("ElemLit", element)
        self.artifacts: str = artifacts


class PlayerPhase:
    """An object that stores information about a player on a phase."""

    """Has:
    player: a string for this player.
    phase: a string for the phase.
    chambers: a string->composition dict for the comps they used.
    owned: a string->dict (character) dict for the characters they owned:
        None if they don't own the character.
    """

    def __init__(self, player: str) -> None:
        """Composition constructor."""
        self.player = player
        self.chambers: dict[Stage, Composition] = {}
        self.owned: dict[str, OwnedChars] = {}

    def add_character(
        self,
        name: str,
        level: str,
        cons: str,
        weapon: str,
        element: str,
        artifacts: str,
    ) -> None:
        """Add in a character to the owned characters dict."""
        for arti in articombinations:
            articom: list[str] = []
            comarti: list[str] = []
            for artiset in articombinations[arti]:
                articom.append(artiset + ", ")
                comarti.append(", " + artiset)
            replaced = False
            arti_name = articombinations[arti][0]
            for arti_replace in comarti:
                if arti_replace in artifacts and "4p" not in artifacts:
                    artifacts = artifacts.replace(arti_replace, ", " + arti_name)
                    replaced = True
            if replaced:
                arti_name = articombinations[arti][1]
            for arti_replace in articom:
                if arti_replace in artifacts and "4p" not in artifacts:
                    artifacts = artifacts.replace(arti_replace, "")
                    artifacts = artifacts + ", " + arti_name

        if "Flex, " in artifacts:
            artifacts = artifacts.replace("Flex, ", "") + ", Flex"
        self.owned[name] = OwnedChars(level, cons, weapon, element, artifacts)

    def add_comp(self, composition: Composition) -> None:
        """Add a composition to the chambers dict."""
        if composition.player != self.player:
            return
        if composition.room in self.chambers:
            return
        self.chambers[composition.room] = composition

    def chars_owned(self, characters: list[str]) -> bool:
        """Take in an iter of character names. True if the player owned them all."""
        return all(self.owned[char] for char in characters)

    def chars_used(self, characters: list[str]) -> bool:
        """Take in an iter of character names. True if the player used them all."""
        if not self.chars_owned(characters):
            return False
        return all(self.char_used(char) for char in characters)

    def no_chars_owned(self, characters: list[str]) -> bool:
        """Take in a list of character names. True if the player owns none of them."""
        return all(not self.owned[char] for char in characters)

    def no_chars_used(self, characters: list[str]) -> bool:
        """Take in an iter of character names. True if the player used none of them."""
        return all(not self.char_used(char) for char in characters)

    def char_used(self, character: str) -> bool:
        """Take in a character name. True if the player used them."""
        if not self.owned[character]:
            return False
        for chamber in self.chambers.values():
            if chamber.char_presence[character]:
                return True
        return False
