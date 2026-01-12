"""Collects character data from Enka Network."""

from __future__ import annotations

import _thread
import asyncio
import sys
import traceback
from datetime import datetime
from pickle import dump as p_dump
from pickle import load as p_load
from typing import TYPE_CHECKING

import aiohttp
import enka  # pyright: ignore[reportMissingTypeStubs]
from enka.zzz import (  # pyright: ignore[reportMissingTypeStubs]
    AgentStatType,
    Element,
    SkillType,
)
from enka_config import (
    csv,
    desired_stats_dict,
    desired_stats_keys,
    drive_data,
    filename,
    json,
    output_keys,
    relics_data,
    substat_keys,
    uids,
)

sys.path.append("../Comps/")
from comp_rates_config import offline_collect, save_to_file

if TYPE_CHECKING:
    from enka.zzz import (  # pyright: ignore[reportMissingTypeStubs]
        AgentSkill,
        ShowcaseResponse,  # pyright: ignore[reportMissingTypeStubs]
    )

print(len(uids))


class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder."""

    def default(self, o: datetime | object) -> str | dict[str, str]:
        """Encode custom JSON."""
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return super().default(o)


def remove_nbsp(lines: list[str | int | float | None]) -> list[str]:
    """Remove non-breaking spaces."""
    return [str(line).replace("\xa0", " ") for line in lines]


def jprint(obj: dict[str, str]) -> None:
    """Create a formatted string of the Python JSON object."""
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def input_thread(input_list: list[bool]) -> None:
    """Input thread."""
    input()
    input_list.append(True)


async def main() -> None:
    """Compile character builds."""
    async with enka.ZZZClient(enka.zzz.Language.ENGLISH) as client:
        await client.start()
        is_update = input("Update assets? (y/n) ")
        if is_update == "y":
            await client.update_assets()

        writer = csv.writer(open(filename + ".csv", "w", encoding="UTF8", newline=""))
        writer.writerow(output_keys)

        header = [
            "uid",
            "phase",
            "name",
            "level",
            "cons",
            "weapon",
            "element",
            "artifacts",
            "potential",
        ]
        writer_chars = csv.writer(
            open(filename + "_char.csv", "w", encoding="UTF8", newline=""),
        )
        writer_chars.writerow(header)

        input_list: list[bool] = []
        _thread.start_new_thread(input_thread, (input_list,))
        uid_iter = -1
        while not input_list and uid_iter < len(uids) - 1:
            uid_iter += 1
            uid = uids[uid_iter]

            i: int = -1
            while i < 5:
                i += 1
                if i == 5:
                    print("error")
                try:
                    print(f"{uid_iter + 1} / {len(uids)} : {uid}, {i}")
                    if offline_collect:
                        with open("data.pkl", "rb") as f:
                            data = p_load(f)
                    else:
                        data: ShowcaseResponse = await client.fetch_showcase(uid)
                        if save_to_file:
                            with open("data.pkl", "wb") as f:
                                p_dump(data, f)
                            with open("data.json", "w") as f:
                                f.write(
                                    json.dumps(
                                        data.__dict__,
                                        cls=CustomEncoder,
                                        indent=2,
                                    ),
                                )

                    for character in data.agents:
                        element_name = character.elements[-1]
                        dmg_bonus: AgentStatType = AgentStatType.PHYSICAL_DMG_BONUS
                        match element_name:
                            case Element.PHYSICAL:
                                dmg_bonus = AgentStatType.PHYSICAL_DMG_BONUS
                            case Element.FIRE:
                                dmg_bonus = AgentStatType.FIRE_DMG_BONUS
                            case Element.ICE | Element.FIRE_FROST:
                                dmg_bonus = AgentStatType.ICE_DMG_BONUS
                            case Element.ELECTRIC:
                                dmg_bonus = AgentStatType.ELECTRIC_DMG_BONUS
                            case Element.ETHER | Element.AURIC_ETHER:
                                dmg_bonus = AgentStatType.ETHER_DMG_BONUS
                            case _:
                                dmg_bonus = AgentStatType.PHYSICAL_DMG_BONUS

                        if element_name == "Elec":
                            element_name = "Electric"
                        if element_name == "Physics":
                            element_name = "Physical"
                        line: list[str | int | float | None] = []
                        line_chars: list[str | int | float | None] = []
                        w_engine = character.w_engine
                        line.extend(
                            [
                                uid,
                                data.player.level,
                                character.name,
                                character.level,
                                element_name,
                                w_engine.name if w_engine else "",
                                w_engine.level if w_engine else "",
                            ],
                        )
                        line_chars.extend(
                            [
                                uid,
                                "",
                                character.name,
                                character.level,
                                character.mindscape,
                                w_engine.name if w_engine else "",
                                element_name,
                            ],
                        )

                        def find_skill(
                            skill_type: SkillType,
                            skills: list[AgentSkill],
                        ) -> int:
                            return next(
                                skill.level
                                for skill in skills
                                if skill.type == skill_type
                            )

                        skill_array = [
                            find_skill(SkillType.BASIC_ATK, character.skills),
                            find_skill(SkillType.SPECIAL_ATK, character.skills),
                            find_skill(SkillType.DASH, character.skills),
                            find_skill(SkillType.ULTIMATE, character.skills),
                            find_skill(SkillType.CORE_SKILL, character.skills),
                            find_skill(SkillType.ASSIST, character.skills),
                        ]
                        line.extend(skill_array)

                        desired_stats: dict[str, float] = dict.fromkeys(
                            desired_stats_keys,
                            0,
                        )

                        for stat in character.stats.values():
                            if stat.type in desired_stats_dict and (
                                "Bonus" not in stat.name or dmg_bonus == stat.type
                            ):
                                desired_stats[desired_stats_dict[stat.type]] = (
                                    stat.value / 100
                                    if "%" in stat.format
                                    else stat.value
                                )

                        line.extend(round(stat, 3) for stat in desired_stats.values())

                        mainstats = {
                            4: "",
                            5: "",
                            6: "",
                        }
                        substats: dict[str, float] = dict.fromkeys(substat_keys, 0)

                        artifacts: dict[str, int] = {}
                        for relic in character.discs:
                            set_id: int = drive_data["Items"][str(relic.id)]["SuitId"]
                            relic_name = relics_data[str(set_id)]["name"].replace(
                                "\xa0",
                                " ",
                            )
                            if relic.slot in mainstats:
                                mainstats[relic.slot] = relic.main_stat.name
                            if relic_name not in artifacts:
                                artifacts[relic_name] = 1
                            else:
                                artifacts[relic_name] += 1
                            for stat in relic.sub_stats:
                                stat_name = stat.name.replace("\xa0", " ")
                                if stat_name in substats:
                                    substats[stat_name] += (
                                        stat.value / 100
                                        if "%" in stat.format
                                        else stat.value
                                    )

                        line.extend(
                            round(substats[stat_key], 3)
                            for stat_key in list(substats.keys())
                        )

                        line.extend(
                            mainstats[stat_key] for stat_key in list(mainstats.keys())
                        )

                        char_set: None | str = None
                        len_artifacts = 0
                        for arti_set, arti_set_value in artifacts.items():
                            if arti_set_value >= 2:
                                char_set_name = arti_set
                                len_artifacts += 2
                                if arti_set_value >= 4:
                                    len_artifacts += 2
                                    char_set_name = "4p " + char_set_name
                                if char_set is not None:
                                    if char_set_name < char_set:
                                        char_set = char_set_name + ", " + char_set
                                    else:
                                        char_set += ", " + char_set_name
                                else:
                                    char_set = char_set_name
                        if len_artifacts < 6:
                            if char_set is not None:
                                char_set += ", Flex"
                            else:
                                char_set = "Flex"

                        line.append(char_set)
                        line_chars.append(char_set)
                        line_chars.append(character.potential)

                        writer.writerow(remove_nbsp(line))
                        writer_chars.writerow(remove_nbsp(line_chars))
                    break

                except enka.errors.PlayerDoesNotExistError:
                    print("Player does not exist.")
                    break

                except (
                    aiohttp.ClientConnectorError,
                    aiohttp.ClientConnectorDNSError,
                    aiohttp.ClientOSError,
                    aiohttp.ServerDisconnectedError,
                    enka.errors.APIRequestTimeoutError,
                    enka.errors.EnkaAPIError,
                ):
                    print("timeout")
                    await asyncio.sleep(10)

                except asyncio.exceptions.TimeoutError:
                    print("timeout")
                    await asyncio.sleep(10)

                except AttributeError:
                    print(f"{uid}: {traceback.format_exc()}")
                    await asyncio.sleep(1)

                except Exception as e:
                    if str(e) == "[429] Too Many Requests":
                        print("[429] Too Many Requests")
                        await asyncio.sleep(3)
                    elif "Cannot connect" in str(e):
                        print("Cannot connect")
                        i = 0
                        await asyncio.sleep(1)
                    elif str(e) == "User not found.":
                        print("User not found.")
                        break
                    else:
                        print(f"{uid}: {traceback.format_exc()}")
                        break

        print("\nFinished")
        await client.close()


asyncio.run(main())
