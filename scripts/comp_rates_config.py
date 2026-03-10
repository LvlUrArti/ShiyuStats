"""Config file for comp_rates.py."""

import argparse
import json
import os

from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-off", "--offline_collect", action="store_true")
parser.add_argument("-save", "--save_to_file", action="store_true")
parser.add_argument("-a", "--all", action="store_true")
parser.add_argument("-ca", "--comps_all", action="store_true")
parser.add_argument("-cha", "--chars_all", action="store_true")
parser.add_argument("-d", "--duos", action="store_true")
parser.add_argument("-t", "--top", action="store_true")
parser.add_argument("-cht", "--chars_top", action="store_true")
parser.add_argument("-ct", "--comps_top", action="store_true")
parser.add_argument("-w", "--whale", action="store_true")
parser.add_argument("-f", "--f2p", action="store_true")

parser.add_argument(
    "-sd",
    "--shiyu_defense",
    action="store_true",
)
parser.add_argument(
    "-da",
    "--deadly_assault",
    action="store_true",
)

args = parser.parse_args()

# For enka.network
offline_collect: bool = args.offline_collect
save_to_file: bool = args.save_to_file

with open(str(os.getenv("REPO_PATH")) + "/data/characters.json") as char_file:
    CHARACTERS = json.load(char_file)

with open(str(os.getenv("REPO_PATH")) + "/data/w-engine.json") as char_file:
    WENGINE = json.load(char_file)

RECENT_PHASE = "2.6.2"

# if no past phase, past_phase = "null"
PAST_PHASE = "2.6.1"
# if as: da_mode = True
da_mode: bool = args.deadly_assault

if not da_mode:
    da_mode = False

sd_mode: bool = not da_mode

DEFAULT_ROUND = 0
CONS_LIMIT = 2

suffix = ""
if da_mode:
    suffix = "_da"
RECENT_PHASE_PF = RECENT_PHASE + suffix
PAST_PHASE_PF = PAST_PHASE + suffix

char_infographics = {"Zhu Yuan", "Ben", "Nicole"}
char_infographics = next(iter(char_infographics))

# threshold for comps in character infographics, non-inclusive
char_app_rate_threshold = 0.25

# threshold for comps, not inclusive
app_rate_threshold = 0.1
app_rate_threshold_round = 0
json_threshold = 0
f2p_app_rate_threshold = 0.1
skew_num = 0.8
duo_dict_len = 30
duo_dict_len_print = 10

skip_self = False
skip_random = False
archetype = "all"
WHALE_ONLY: bool = args.whale
F2P_ONLY: bool = args.f2p

# Char infographics should be separated from overall comp rankings
run_commands = {
    # "Duos check",
    "Char usages 8 - 10",
    "Char usages for each stage",
    "Char usages for each stage (combined)",
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
        "Comp usage 8 - 10",
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
        "Char usages for each stage (combined)",
        "Comp usage 8 - 10",
        "Comp usages for each stage",
    }

elif args.chars_all:
    run_commands = {
        "Char usages 8 - 10",
        "Char usages for each stage",
        "Char usages for each stage (combined)",
    }

elif args.comps_all:
    run_commands = {
        "Comp usage 8 - 10",
        "Comp usages for each stage",
    }

elif args.duos:
    run_commands = {
        "Char usages 8 - 10",
        "Duos check",
    }

sig_weaps: set[str] = set()
for wengine in WENGINE:
    if WENGINE[wengine]["availability"] == "Limited S":
        sig_weaps.add(WENGINE[wengine]["name"])

alt_comps = "Character specific infographics" in run_commands
if alt_comps and char_app_rate_threshold > app_rate_threshold:
    app_rate_threshold = char_app_rate_threshold
