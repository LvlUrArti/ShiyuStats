"""Update data from hakushin."""

# ruff: noqa: N815, ANN401, D101

import json
import re
from io import StringIO
from typing import Any

import requests
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


with open("../../data/characters.json") as file:
    chars = json.load(file)
raw_chars: dict[str, dict[str, int | str]] = load_from_url(
    f"https://static.nanoka.cc/zzz/{live_version}/character.json",
)

for char_id, char in raw_chars.items():
    char_name = char["en"]
    if char_name not in chars and char["icon"] != "":
        add_char = input(f"Add {char_name}? (y/n): ")
        if add_char == "y":
            chars[char_name] = {
                "element": char["element"],
                "camp": char["camp"],
                "icon": char["icon"],
                "id": char_id,
                "name": char_name,
            }

            if char["rank"] == 3:
                chars[char_name]["availability"] = "A"
            elif char["rank"] == 4:
                chars[char_name]["availability"] = "Limited S"

            match str(char["type"]):
                case "1":
                    chars[char_name]["specialty"] = "Attack"
                    chars[char_name]["role"] = "Damage Dealer"
                case "2":
                    chars[char_name]["specialty"] = "Stun"
                    chars[char_name]["role"] = "Stun"
                case "3":
                    chars[char_name]["specialty"] = "Anomaly"
                    chars[char_name]["role"] = "Damage Dealer"
                case "4":
                    chars[char_name]["specialty"] = "Support"
                    chars[char_name]["role"] = "Support"
                case "5":
                    chars[char_name]["specialty"] = "Defense"
                    chars[char_name]["role"] = "Support"
                case "6":
                    chars[char_name]["specialty"] = "Rupture"
                    chars[char_name]["role"] = "Damage Dealer"
                case _:
                    print("Unknown character type: " + chars[char_name]["type"])

            match str(char["element"]):
                case "200":
                    chars[char_name]["element"] = "Physical"
                case "201":
                    chars[char_name]["element"] = "Fire"
                case "202":
                    chars[char_name]["element"] = "Ice"
                case "203":
                    chars[char_name]["element"] = "Electric"
                case "205":
                    chars[char_name]["element"] = "Ether"
                case _:
                    print("Unknown element: " + chars[char_name]["element"])

with open("../../data/characters.json", "w") as out_file:
    out_file.write(json.dumps(chars, indent=4))


with open("../../data/bangboos.json") as file:
    bangboos = json.load(file)
raw_bangboos: dict[str, dict[str, int | str]] = load_from_url(
    f"https://static.nanoka.cc/zzz/{live_version}/bangboo.json",
)

for bangboo_id, bangboo in raw_bangboos.items():
    bangboo_name = bangboo["en"]
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
        }

        if bangboo["rank"] == 3:
            bangboos[bangboo_name]["availability"] = "A"
        elif bangboo["rank"] == 4:
            bangboos[bangboo_name]["availability"] = "S"

with open("../../data/bangboos.json", "w") as out_file:
    out_file.write(json.dumps(bangboos, indent=4))


class EndgameConfig(BaseModel):
    versionTime: str


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
