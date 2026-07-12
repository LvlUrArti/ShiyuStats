"""Copy files to web directory."""

import shutil
from os import mkdir, path
from pathlib import Path
from sys import path as sys_path

sys_path.append("../")
from comp_rates_config import (
    BASE_RESULT_PATH,
    BOOS_RESULT_PATH,
    RECENT_PHASE,
    da_mode,
    mode_sfx,
    sd_mode,
)
from send2trash import send2trash
from utils.copy_json_files import copy_json_files

mode_sfx = mode_sfx.replace("_", "")

if sd_mode and path.exists("../../results/web_results"):
    send2trash("../../results/web_results")
    mkdir("../../results/web_results")
mkdir("../../results/web_results/" + mode_sfx)

if da_mode:
    copy_json_files(
        Path(f"../../results/all_results/{RECENT_PHASE}"),
        Path("../../results/web_results"),
    )

    shutil.copyfile(
        f"../../results/all_results/{RECENT_PHASE}/da_bosses_name.csv",
        "../../results/web_results/da_bosses_name.csv",
    )

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


def copy_results() -> None:
    """Copy results to a specified location."""
    destination = f"../../results/final_results/{RECENT_PHASE}"

    if path.exists(destination):
        overwrite = input(
            f"Warning: '{destination}' already exists. Overwrite? (y/n): ",
        )
        if overwrite != "y":
            return

        shutil.rmtree(destination)

    shutil.copytree("../../results/web_results", destination)
    shutil.copy(
        "../../data/versions/config.json",
        "../../results/final_results/config.json",
    )


if da_mode:
    shutil.make_archive("../../results/results", "zip", "../../results/web_results")
    copy_results()
