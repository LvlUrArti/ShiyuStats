"""Config file for comp_rates.py."""

import argparse
from datetime import datetime
from json import load
from os.path import dirname as path_dirname
from os.path import join as path_join
from sys import exit as sys_exit
from typing import Literal

from pydantic import BaseModel, field_validator

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", help="Version to compile")
parser.add_argument("-m", "--mode", help="Set which mode to compile (sd/da)")
parser.add_argument("-off", "--offline_collect", action="store_true")
parser.add_argument("-save", "--save_to_file", action="store_true")
parser.add_argument("-a", "--all", action="store_true")
parser.add_argument("-ca", "--comps_all", action="store_true")
parser.add_argument("-cha", "--chars_all", action="store_true")
parser.add_argument("-t", "--top", action="store_true")
parser.add_argument("-cht", "--chars_top", action="store_true")
parser.add_argument("-ct", "--comps_top", action="store_true")
parser.add_argument("-w", "--whale", action="store_true")
parser.add_argument("-f", "--f2p", action="store_true")
# Prompt for real data (hf data)
parser.add_argument("-y", "--yes", action="store_true")
parser.add_argument("-n", "--no", action="store_true")

args = parser.parse_args()

RECENT_PHASE: str = args.version or "3.1.1"


def relative_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    script_dir = path_dirname(__file__)
    return path_join(script_dir, relative_path)


class EndgameMode(BaseModel):
    """Endgame mode version info."""

    ver: str
    start: datetime
    end: datetime
    boss_1: str | None = None
    boss_2: str | None = None
    boss_3: str | None = None

    @field_validator("start", "end", mode="before")
    @classmethod
    def parse_date(cls, value: str) -> datetime:
        """Convert string to datetime."""
        return datetime.strptime(value, "%d/%m/%Y")


class EndgameConfig(BaseModel):
    """Endgame collect date and version info."""

    collect_date: datetime
    sd: EndgameMode | None = None
    da: EndgameMode | None = None

    @field_validator("collect_date", mode="before")
    @classmethod
    def parse_collect_date(cls, value: str) -> datetime:
        """Convert string to datetime."""
        return datetime.strptime(value, "%d/%m/%Y")


with open(relative_path("../data/versions/config.json")) as f:
    raw_config = load(f)
    ENDGAME_INFOS: dict[str, EndgameConfig] = {
        char_name: EndgameConfig(**item) for char_name, item in raw_config.items()
    }
    ENDGAME_INFO: EndgameConfig | None = ENDGAME_INFOS.get(RECENT_PHASE)

# For enka.network
offline_collect: bool = args.offline_collect
save_to_file: bool = args.save_to_file

RoleLit = Literal[
    "Attack",
    "Stun",
    "Anomaly",
    "Support",
    "Defense",
    "Rupture",
]


class BaseCharInfo(BaseModel):
    """Base character info."""

    id: str
    name: str
    slug: str
    availability: str


class CharInfo(BaseCharInfo):
    """Character info from characters.json."""

    full_name: str
    element: str
    specialty: RoleLit
    attack_type: str
    faction: str
    release_date: datetime
    role: str

    @field_validator("release_date", mode="before")
    @classmethod
    def parse_epoch(cls, value: int) -> datetime:
        """Convert epoch timestamp to datetime."""
        return datetime.fromtimestamp(value)


with open(relative_path("../data/characters.json")) as char_file:
    raw_characters = load(char_file)
    CHARS_INFO: dict[str, CharInfo] = {
        char_name: CharInfo(**item)
        for char_name, item in raw_characters.items()
        if (
            not ENDGAME_INFO
            or (
                datetime.fromtimestamp(item["release_date"]) < ENDGAME_INFO.collect_date
            )
        )
    }

with open(relative_path("../data/bangboos.json")) as char_file:
    raw_bangboos = load(char_file)
    BOOS_INFO: dict[str, BaseCharInfo] = {
        char_name: BaseCharInfo(**item) for char_name, item in raw_bangboos.items()
    }

with open(relative_path("../data/w-engine.json")) as char_file:
    WENGINE = load(char_file)

da_mode: bool = args.mode == "da"
sd_mode: bool = args.mode == "sd"
if not da_mode:
    da_mode = False

DEFAULT_ROUND = 0
CONS_LIMIT = 2

mode_sfx = "_da" if da_mode else "_sd"


class ModeConfig(BaseModel):
    """Configuration for a game mode."""

    all_stages: list[str]
    one_stage: list[str]
    star_num_threshold: int
    thresholds: list[tuple[datetime, list[str], list[str], int]]


# Mode configurations
mode_configs: dict[str, ModeConfig] = {
    "da": ModeConfig(
        all_stages=["1-1", "1-2", "1-3"],
        one_stage=["1-1", "1-2", "1-3"],
        star_num_threshold=3,
        thresholds=[
            # Adversity mode added in 3.1.1
            (
                datetime(2026, 7, 29),
                ["1-1", "1-2", "1-3", "2-1"],
                ["1-1", "1-2", "1-3"],
                3,
            ),
        ],
    ),
    "sd": ModeConfig(
        all_stages=["5-1", "5-2", "5-3"],
        one_stage=["5-1", "5-2", "5-3"],
        star_num_threshold=3,
        thresholds=[],
    ),
}

for config in mode_configs.values():
    # Apply thresholds if any
    if ENDGAME_INFO and config.thresholds:
        for date, stages, one_stages, star_num in config.thresholds:
            if ENDGAME_INFO.collect_date >= date:
                config.all_stages = stages
                config.one_stage = one_stages
                config.star_num_threshold = star_num
                break

cfg = mode_configs.get(args.mode)

if cfg is None:
    all_stages: list[str] = []
    one_stage: list[str] = []
    star_num_threshold = 3
else:
    # Check version exists
    if ENDGAME_INFO:
        mode_obj = getattr(ENDGAME_INFO, args.mode)
        if not mode_obj or not mode_obj.ver:
            sys_exit()

    all_stages = cfg.all_stages
    one_stage = cfg.one_stage
    star_num_threshold = cfg.star_num_threshold


RECENT_PHASE_SFX = RECENT_PHASE + mode_sfx
BASE_RESULT_PATH = f"results/all_results/{RECENT_PHASE}/{RECENT_PHASE_SFX}"
BOOS_RESULT_PATH = f"{BASE_RESULT_PATH}/boos"
CHAR_RESULT_PATH = f"{BASE_RESULT_PATH}/chars"
COMP_RESULT_PATH = f"{BASE_RESULT_PATH}/comps"
BUILD_RESULT_PATH = f"{BASE_RESULT_PATH}/builds"
DUOS_RESULT_PATH = f"{BASE_RESULT_PATH}/duos"

char_infographics = {"Zhu Yuan", "Ben", "Nicole"}
char_infographics = next(iter(char_infographics))

# threshold for comps in character infographics, non-inclusive
char_app_rate_threshold = 0.25

# threshold for comps, not inclusive
app_rate_threshold = 0.1
app_rate_threshold_round = 0
json_threshold = 0
skew_num = 0.8
duo_dict_len = 30
duo_dict_len_print = 10

skip_self = False
skip_random = False
WHALE_ONLY: bool = args.whale
F2P_ONLY: bool = args.f2p

# Char infographics should be separated from overall comp rankings
run_commands = {
    # "Duos check",
    "Char usages 8 - 10",
    "Char usages for each stage",
    # "Comp usage 8 - 10",
    # "Comp usages for each stage",
    # "Character specific infographics",
    # "Char usages all stages",
    # "Comp usage all stages",
}

if args.top or args.f2p:
    run_commands = {
        "Char usages 8 - 10",
        "Char usages for each stage",
    }

if args.whale:
    run_commands = {
        "Char usages 8 - 10",
        "Char usages for each stage",
        "Comp usage 8 - 10",
        "Comp usages for each stage",
    }

elif args.chars_top:
    run_commands = {
        "Char usages 8 - 10",
    }

elif args.comps_top:
    run_commands = {
        "Comp usage 8 - 10",
    }

elif args.all:
    run_commands = {
        "Char usages 8 - 10",
        "Char usages for each stage",
        "Comp usage 8 - 10",
        "Comp usages for each stage",
    }

elif args.chars_all:
    run_commands = {
        "Char usages 8 - 10",
        "Char usages for each stage",
    }

elif args.comps_all:
    run_commands = {
        "Comp usage 8 - 10",
        "Comp usages for each stage",
    }

sig_weaps: set[str] = set()
for wengine in WENGINE:
    if WENGINE[wengine]["availability"] == "Limited S":
        sig_weaps.add(WENGINE[wengine]["name"])

alt_comps = "Character specific infographics" in run_commands
if alt_comps and char_app_rate_threshold > app_rate_threshold:
    app_rate_threshold = char_app_rate_threshold
