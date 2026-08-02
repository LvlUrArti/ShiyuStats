"""Update data from hakushin."""

# ruff: noqa: N815, ANN401, D101

import json
import re
from io import StringIO
from typing import Any

import requests
from agent_scraper import scrape_wiki_chars
from merge_characters import merge_characters
from pydantic import BaseModel


def load_from_url(url: str) -> Any:
    """Load data from URL."""
    download = requests.get(url, timeout=10).content.decode("utf-8")
    return json.load(StringIO(download))


live_version: str = load_from_url(
    "https://static.nanoka.cc/manifest.json",
)["zzz"]["live"]

raw_drives: dict[str, dict[str, dict[str, str]]] = load_from_url(
    f"https://static.nanoka.cc/zzz/{live_version}/equipment.json",
)
drive_sets: dict[str, dict[str, str | list[str]]] = {}

with open("../../data/drive_affixes.json") as file:
    drive_affixes_data = json.load(file)

drive_affixes: dict[str, list[str]] = {}
for drive_id, drive in raw_drives.items():
    drive_sets[drive_id] = {}
    drive_sets[drive_id]["icon"] = str(drive["icon"])
    drive_sets[drive_id]["id"] = drive_id
    drive_sets[drive_id]["name"] = drive["en"]["name"]
    drive_sets[drive_id]["desc"] = [
        re.sub("<.*?>", "", drive["en"]["desc2"]),
        re.sub("<.*?>", "", drive["en"]["desc4"]),
    ]
    affix = drive_sets[drive_id]["desc"][0]

    if affix[-1] == ".":
        affix = affix[:-1]

    if "Increases " in affix:
        affix = affix.replace("Increases ", "")
        affix = affix.replace("by ", "+")
    if "Reduces " in affix:
        affix = affix.replace("Reduces ", "")
        affix = affix.replace("by ", "-")

    replacements = {
        "increases by ": "+",
        "DMG ": "",
        "CRIT Rate": "CR",
        "Anomaly Proficiency": "AP",
        "Physical": "Phys",
    }
    for old, new in replacements.items():
        affix = affix.replace(old, new)

    if affix not in drive_affixes:
        drive_affixes[affix] = []
    drive_affixes[affix].append(str(drive_sets[drive_id]["name"]))

for affix in list(drive_affixes.keys()):
    if len(drive_affixes[affix]) > 1:
        add_drive = "n"
        if affix not in drive_affixes_data:
            if len(affix) > 12:
                print("Set name too long: " + affix)
            else:
                add_drive = input("Add " + affix + "? (y/n): ")
        else:
            add_drive = "y"
        if add_drive == "y":
            drive_affixes_data[affix] = drive_affixes[affix]
    else:
        del drive_affixes[affix]

with open("../../data/drive_sets.json", "w") as out_file:
    out_file.write(json.dumps(drive_sets, indent=4))

with open("../../data/drive_affixes.json", "w") as out_file:
    out_file.write(json.dumps(drive_affixes_data, indent=4))

with open("../../data/w-engine.json") as file:
    wengine = json.load(file)
raw_wengine: dict[str, dict[str, int | str]] = load_from_url(
    f"https://static.nanoka.cc/zzz/{live_version}/weapon.json",
)

for weap_id, weap in raw_wengine.items():
    weap_name = weap["en"]
    if weap_name not in wengine:
        wengine[weap_name] = {
            "id": weap_id,
            "name": weap_name,
        }

        if weap["rank"] == 2:
            wengine[weap_name]["availability"] = "B"
        elif weap["rank"] == 3:
            wengine[weap_name]["availability"] = "A"
        elif weap["rank"] == 4:
            wengine[weap_name]["availability"] = "Limited S"

with open("../../data/w-engine.json", "w") as out_file:
    out_file.write(json.dumps(wengine, indent=4))


class RawCharInfo(BaseModel):
    """Character info from characters.json."""

    en: str
    rank: int
    type: int
    element: int
    camp: int
    icon: str


ELEMENT_MAP: dict[int, str] = {
    200: "Physical",
    201: "Fire",
    202: "Ice",
    203: "Electric",
    204: "Wind",
    205: "Ether",
    300: "Lumiflux",
}

SPECIALTY_MAP: dict[int, str] = {
    1: "Attack",
    2: "Stun",
    3: "Anomaly",
    4: "Support",
    5: "Defense",
    6: "Rupture",
}


with open("../../data/characters.json") as file:
    chars: dict[str, dict[str, int | str]] = json.load(file)
download = load_from_url(f"https://static.nanoka.cc/zzz/{live_version}/character.json")
raw_chars = {char_id: RawCharInfo(**item) for char_id, item in download.items()}

for char_id, char in raw_chars.items():
    if char.element not in ELEMENT_MAP:
        print(f"Unknown element: {char.element}")

    if char.type not in SPECIALTY_MAP:
        print(f"Unknown character type: {char.type}")

    char_name = char.en
    if char_name not in chars and char.icon != "":
        add_char = input(f"Add {char_name}? (y/n): ")
        if add_char == "y":
            chars[char_name] = {
                "id": char_id,
                "name": char_name,
                "slug": char_name.lower().replace(" ", "-"),
                "element": ELEMENT_MAP[char.element],
                "availability": "A" if char.rank == 3 else "Limited S",
                "specialty": SPECIALTY_MAP[char.type],
                "role": "support",
            }

            if char.type in {1, 3, 6}:
                is_sub_dps = input(f"Is {char_name} a sub-DPS? (y/n): ")
                chars[char_name]["role"] = "subdps" if is_sub_dps == "y" else "dps"

with open("../../data/characters.json", "w") as out_file:
    out_file.write(json.dumps(chars, indent=4))

wiki_characters = scrape_wiki_chars()
merge_characters(wiki_characters)

with open("../../data/bangboos.json") as file:
    bangboos = json.load(file)
raw_bangboos: dict[str, dict[str, int | str]] = load_from_url(
    f"https://static.nanoka.cc/zzz/{live_version}/bangboo.json",
)

for bangboo_id, bangboo in raw_bangboos.items():
    bangboo_name = str(bangboo["en"])
    if bangboo_name == "..." or "Bangboo_Name" in str(bangboo_name):
        continue
    if (
        bangboo_name not in bangboos
        and bangboo["icon"] != ""
        and "Bangboo_Name_" not in str(bangboo["icon"])
    ):
        bangboos[bangboo_name] = {
            "id": bangboo_id,
            "name": bangboo_name,
            "slug": bangboo_name.lower().replace(" ", "-"),
        }

        if bangboo["rank"] == 3:
            bangboos[bangboo_name]["availability"] = "A"
        elif bangboo["rank"] == 4:
            bangboos[bangboo_name]["availability"] = "S"

with open("../../data/bangboos.json", "w") as out_file:
    out_file.write(json.dumps(bangboos, indent=4))


class VersionEnemy(BaseModel):
    id: str
    type: int


class EndgameConfig(BaseModel):
    versionTime: str
    versionEnemies: list[VersionEnemy] | dict[str, Any]


enemies: dict[str, dict[str, str]] = load_from_url(
    "https://www.buhflipexplode.org/assets/zzz/enemies.json",
)


def add_endgame(versions_dict: dict[str, dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Add endgame versions."""
    versions: dict[str, dict[str, Any]] = {}
    for version, version_item in versions_dict.items():
        config = EndgameConfig(**version_item)
        version_time = config.versionTime
        if version_time != "xx/xx/20xx - xx/xx/20xx":
            versions[version] = {
                "time_start": version_time.split(" - ")[0],
                "time_end": version_time.split(" - ")[1],
            }

            if isinstance(config.versionEnemies, list):
                for i, enemy in enumerate(config.versionEnemies):
                    versions[version][f"boss_{i + 1}"] = enemies[enemy.id]["name"]
    return versions


# Endgame versions update
save_entries: dict[str, dict[str, dict[str, str]]] = {}

sd_data: list[dict[str, dict[str, dict[str, str]]]] = load_from_url(
    "https://www.buhflipexplode.org/zzz/sd/sd-versions.json",
)
for entry in sd_data:
    name = str(entry["name"])
    if name == "Critical Node":
        save_entries["Shiyu Defense"] = add_endgame(entry["versions"])

da_data: dict[str, dict[str, str]] = load_from_url(
    "https://www.buhflipexplode.org/zzz/da/da-versions.json",
)
save_entries["Deadly Assault"] = add_endgame(da_data)

with open("../../data/versions/endgame_versions.json", "w") as out_file:
    out_file.write(json.dumps(save_entries, indent=2))
