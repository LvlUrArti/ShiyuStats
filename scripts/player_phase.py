"""An object that stores information about a player on a phase."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal, cast

if TYPE_CHECKING:
    from composition import Composition, Stage

# Set class constants in initialization
with open("../data/drive_affixes.json") as relic_file:
    articombinations = json.load(relic_file)

# Affix groups in their JSON order, plus the set of all drives that belong to
# one of those groups.
AFFIX_GROUPS: list[list[str]] = list(articombinations.values())
GROUPED_DRIVES: set[str] = {drive for drives in AFFIX_GROUPS for drive in drives}


def _parse_artifacts(artifacts: str) -> tuple[list[list[str]], int]:
    """Split a drive combination string into [prefix, drive] slots.

    The prefix is either an empty string or the literal "4p", meaning that the
    slot holds the 4-piece set and must never be replaced. Slot order is kept.
    Any "Flex" tokens are counted separately since they are always placed last.
    """
    slots: list[list[str]] = []
    flex_count = 0
    for raw in artifacts.split(","):
        token = raw.strip()
        if not token:
            continue
        if token.lower() == "flex":
            flex_count += 1
            continue
        prefix = ""
        parts = token.split(None, 1)
        if len(parts) == 2 and parts[0].lower() == "4p":
            prefix = parts[0]
            token = parts[1].strip()
        slots.append([prefix, token])
    return slots, flex_count


def normalize_artifacts(artifacts: str) -> str:
    """Normalize a drive combination string using the affix groups.

    Drives that are not the 4-piece set are replaced by the earliest drive
    (in JSON order) of the same affix group that is still available. Names
    already used by a 4-piece set are never reused, and slots of the same
    group are reassigned in their original order, which keeps the output
    sorted by the group order.
    """
    slots, flex_count = _parse_artifacts(artifacts)

    # Fixed names that may never be handed out: 4-piece drives and drives that
    # do not belong to any affix group.
    used: set[str] = set()
    for prefix, drive in slots:
        if prefix or drive not in GROUPED_DRIVES:
            used.add(drive)

    for drives in AFFIX_GROUPS:
        slot_indices = [
            index
            for index, (prefix, drive) in enumerate(slots)
            if not prefix and drive in drives
        ]
        available = [drive for drive in drives if drive not in used]
        for index in slot_indices:
            if not available:
                break
            new_drive = available.pop(0)
            slots[index][1] = new_drive
            used.add(new_drive)

    parts = [f"{prefix} {drive}" if prefix else drive for prefix, drive in slots]
    parts.extend("Flex" for _ in range(flex_count))
    return ", ".join(parts)


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
        char: OwnedChars,
    ) -> None:
        """Add in a character to the owned characters dict."""
        char.artifacts = normalize_artifacts(char.artifacts)
        self.owned[name] = char

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
