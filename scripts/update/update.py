"""Update data from hakushin."""

import io
import json
import re

import requests

download = requests.get(
    "https://static.nanoka.cc/manifest.json",
    timeout=10,
).content.decode("utf-8")
live_version = json.load(io.StringIO(download))["zzz"]["live"]

download = requests.get(
    f"https://static.nanoka.cc/zzz/{live_version}/equipment.json",
    timeout=10,
).content.decode("utf-8")
artifacts = json.load(io.StringIO(download))

with open("../../data/drive_affixes.json") as artifact_file:
    artifacts2 = json.load(artifact_file)

artifacts_affixes: dict[str, list[str]] = {}
for artifact in artifacts:
    artifacts[artifact]["id"] = artifact
    artifacts[artifact]["name"] = artifacts[artifact]["en"]["name"]
    artifacts[artifact]["desc"] = [
        artifacts[artifact]["en"]["desc2"],
        artifacts[artifact]["en"]["desc4"],
    ]
    del artifacts[artifact]["en"]
    del artifacts[artifact]["ko"]
    del artifacts[artifact]["zh"]
    del artifacts[artifact]["ja"]
    artifacts[artifact]["desc"][0] = re.sub("<.*?>", "", artifacts[artifact]["desc"][0])
    artifacts[artifact]["desc"][1] = re.sub("<.*?>", "", artifacts[artifact]["desc"][1])
    affix = artifacts[artifact]["desc"][0]

    if affix[-1] == ".":
        affix = affix[:-1]
    for i in ["DMG "]:
        affix = affix.replace(i, "")

    affix = affix.replace("increases by ", "+")
    if "Increases " in affix:
        affix = affix.replace("Increases ", "")
        affix = affix.replace("by ", "+")
    if "Reduces " in affix:
        affix = affix.replace("Reduces ", "")
        affix = affix.replace("by ", "-")

    affix = affix.replace("CRIT Rate", "CR")
    affix = affix.replace("Anomaly Proficiency", "AP")
    affix = affix.replace("Physical", "Phys")

    if affix not in artifacts_affixes:
        artifacts_affixes[affix] = []
    artifacts_affixes[affix].append(artifacts[artifact]["name"])

for artifact in list(artifacts_affixes.keys()):
    if len(artifacts_affixes[artifact]) > 1:
        add_arti = "n"
        if artifact not in artifacts2:
            if len(artifact) > 12:
                print("Set name too long: " + artifact)
            else:
                add_arti = input("Add " + artifact + "? (y/n): ")
        else:
            add_arti = "y"
        if add_arti == "y":
            artifacts2[artifact] = artifacts_affixes[artifact]
    else:
        del artifacts_affixes[artifact]

with open("../../data/drive_sets.json", "w") as out_file:
    out_file.write(json.dumps(artifacts, indent=4))

with open("../../data/drive_affixes.json", "w") as out_file:
    out_file.write(json.dumps(artifacts2, indent=4))

with open("../../data/w-engine.json") as char_file:
    wengine1 = json.load(char_file)
download = requests.get(
    f"https://static.nanoka.cc/zzz/{live_version}/weapon.json",
    timeout=10,
).content.decode("utf-8")
wengine2 = json.load(io.StringIO(download))

for weap in wengine2:
    weap_name = wengine2[weap]["en"]
    if weap_name not in wengine1:
        wengine1[weap_name] = wengine2[weap].copy()
        wengine1[weap_name]["id"] = weap
        wengine1[weap_name]["name"] = weap_name

        if wengine2[weap]["rank"] == 2:
            wengine1[weap_name]["availability"] = "B"
        elif wengine2[weap]["rank"] == 3:
            wengine1[weap_name]["availability"] = "A"
        elif wengine2[weap]["rank"] == 4:
            wengine1[weap_name]["availability"] = "Limited S"

        match str(wengine1[weap_name]["type"]):
            case "1":
                wengine1[weap_name]["role"] = "Damage Dealer"
            case "2":
                wengine1[weap_name]["role"] = "Stun"
            case "3":
                wengine1[weap_name]["role"] = "Damage Dealer"
            case "4":
                wengine1[weap_name]["role"] = "Support"
            case "5":
                wengine1[weap_name]["role"] = "Stun"
            case "6": # Rupture
                wengine1[weap_name]["role"] = "Damage Dealer"
            case _:
                print("Unknown weapon type: " + str(wengine1[weap_name]["type"]))
                print(weap_name)

        del wengine1[weap_name]["rank"]
        del wengine1[weap_name]["type"]
        del wengine1[weap_name]["en"]
        del wengine1[weap_name]["ko"]
        del wengine1[weap_name]["zh"]
        del wengine1[weap_name]["ja"]

with open("../../data/w-engine.json", "w") as out_file:
    out_file.write(json.dumps(wengine1, indent=4))


with open("../../data/characters.json") as char_file:
    chars1 = json.load(char_file)
download = requests.get(
    f"https://static.nanoka.cc/zzz/{live_version}/character.json",
    timeout=10,
).content.decode("utf-8")
chars2 = json.load(io.StringIO(download))

for char, char2 in chars2.items():
    char_name = char2["en"]
    if char_name not in chars1 and char2["icon"] != "":
        add_char = input("Add " + char_name + "? (y/n): ")
        if add_char == "y":
            chars1[char_name] = {
                "element": char2["element"],
                "camp": char2["camp"],
                "icon": char2["icon"],
                "id": char,
                "name": char_name,
            }

            if char2["rank"] == 3:
                chars1[char_name]["availability"] = "A"
            elif char2["rank"] == 4:
                chars1[char_name]["availability"] = "Limited S"

            match str(char2["type"]):
                case "1":
                    chars1[char_name]["specialty"] = "Attack"
                    chars1[char_name]["role"] = "Damage Dealer"
                case "2":
                    chars1[char_name]["specialty"] = "Stun"
                    chars1[char_name]["role"] = "Stun"
                case "3":
                    chars1[char_name]["specialty"] = "Anomaly"
                    chars1[char_name]["role"] = "Damage Dealer"
                case "4":
                    chars1[char_name]["specialty"] = "Support"
                    chars1[char_name]["role"] = "Support"
                case "5":
                    chars1[char_name]["specialty"] = "Defense"
                    chars1[char_name]["role"] = "Support"
                case "6":
                    chars1[char_name]["specialty"] = "Rupture"
                    chars1[char_name]["role"] = "Damage Dealer"
                case _:
                    print("Unknown character type: " + chars1[char_name]["type"])

            match str(char2["element"]):
                case "200":
                    chars1[char_name]["element"] = "Physical"
                case "201":
                    chars1[char_name]["element"] = "Fire"
                case "202":
                    chars1[char_name]["element"] = "Ice"
                case "203":
                    chars1[char_name]["element"] = "Electric"
                case "205":
                    chars1[char_name]["element"] = "Ether"
                case _:
                    print("Unknown element: " + chars1[char_name]["element"])

            match str(char2["camp"]):
                case "1":
                    chars1[char_name]["camp"] = "Cunning Hares"
                case "2":
                    chars1[char_name]["camp"] = "Victoria Housekeeping Co."
                case "3":
                    chars1[char_name]["camp"] = "Belobog Heavy Industries"
                case "4":
                    chars1[char_name]["camp"] = "Sons of Calydon"
                case "5":
                    chars1[char_name]["camp"] = "Obol Squad"
                case "6":
                    chars1[char_name]["camp"] = "Hollow Special Operations Section 6"
                case "7":
                    chars1[char_name]["camp"] = "New Eridu Public Security"
                case "8":
                    chars1[char_name]["camp"] = "Stars of Lyra"
                case _:
                    chars1[char_name]["camp"] = str(chars1[char_name]["camp"])

with open("../../data/characters.json", "w") as out_file:
    out_file.write(json.dumps(chars1, indent=4))


with open("../../data/bangboos.json") as bangboo_file:
    bangboos1 = json.load(bangboo_file)
download = requests.get(
    f"https://static.nanoka.cc/zzz/{live_version}/bangboo.json",
    timeout=10,
).content.decode("utf-8")
bangboos2 = json.load(io.StringIO(download))

for bangboo in bangboos2:
    bangboo_name = bangboos2[bangboo]["en"]
    if bangboo_name == "..." or "Bangboo_Name" in bangboo_name:
        continue
    if (
        bangboo_name not in bangboos1
        and bangboos2[bangboo]["icon"] != ""
        and "Bangboo_Name_" not in bangboos2[bangboo]["icon"]
    ):
        bangboos1[bangboo_name] = bangboos2[bangboo].copy()
        bangboos1[bangboo_name]["id"] = bangboo
        bangboos1[bangboo_name]["name"] = bangboo_name

        if bangboos2[bangboo]["rank"] == 3:
            bangboos1[bangboo_name]["availability"] = "A"
        elif bangboos2[bangboo]["rank"] == 4:
            bangboos1[bangboo_name]["availability"] = "S"

        del bangboos1[bangboo_name]["codename"]
        del bangboos1[bangboo_name]["rank"]
        del bangboos1[bangboo_name]["en"]
        del bangboos1[bangboo_name]["ko"]
        del bangboos1[bangboo_name]["zh"]
        del bangboos1[bangboo_name]["ja"]

with open("../../data/bangboos.json", "w") as out_file:
    out_file.write(json.dumps(bangboos1, indent=4))


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
