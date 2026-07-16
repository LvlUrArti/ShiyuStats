"""Copy files to web directory."""

import shutil
from os import mkdir
from pathlib import Path
from sys import path as sys_path

sys_path.append("../")
from comp_rates_config import (
    BASE_RESULT_PATH,
    BOOS_RESULT_PATH,
    mode_sfx,
)
from utils.copy_json_files import copy_json_files

mode_sfx = mode_sfx.replace("_", "")

mkdir("../../results/web_results/" + mode_sfx)

source_dirs = {
    "": "/chars",
    "/duos": "/chars",
    "/comps": "/comps",
}

for source, target in source_dirs.items():
    source_dir = Path(f"../../{BASE_RESULT_PATH}{source}")
    target_dir = Path(f"../../results/web_results/{mode_sfx}{target}")
    copy_json_files(source_dir, target_dir)

shutil.copyfile(
    f"../../{BOOS_RESULT_PATH}/bangboo_all.json",
    f"../../results/web_results/{mode_sfx}/chars/bangboo_all.json",
)
