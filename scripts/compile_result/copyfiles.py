"""Copy files to web directory."""

import shutil
from os import listdir, mkdir, path
from sys import path as sys_path

sys_path.append("../")
from comp_rates_config import (
    BOOS_RESULT_PATH,
    CHAR_RESULT_PATH,
    COMP_RESULT_PATH,
    DUOS_RESULT_PATH,
    RECENT_PHASE,
    da_mode,
    sd_mode,
)
from send2trash import send2trash

mode_sfx = "da" if da_mode else "sd"

source_dirs = [
    f"../../{BOOS_RESULT_PATH}",
    f"../../{CHAR_RESULT_PATH}",
    f"../../results/all_results/{RECENT_PHASE}",
    f"../../{DUOS_RESULT_PATH}",
    f"../../{COMP_RESULT_PATH}",
]

target_dir: str = ""
temp_target_dir: str = ""

if sd_mode and path.exists("../../results/web_results"):
    send2trash("../../results/web_results")
    mkdir("../../results/web_results")
mkdir("../../results/web_results/" + mode_sfx)

for source_dir in source_dirs:
    comp_mode = source_dir == f"../../{COMP_RESULT_PATH}"
    if comp_mode:
        target_dir = f"../../results/web_results/{mode_sfx}/comps"
    else:
        target_dir = f"../../results/web_results/{mode_sfx}/chars"

    file_names = listdir(source_dir)
    if path.exists(target_dir):
        send2trash(target_dir)
    mkdir(target_dir)
    for file_name in file_names:
        if (comp_mode and "combined" in file_name) or (
            file_name in {"duo_usages.json", "bangboo_all.json", "demographic.json"}
            or (file_name == "builds.json" and mode_sfx == "sd")
            or (
                file_name == "da_bosses_name.csv"
                and (RECENT_PHASE + "_da") not in source_dir
            )
        ):
            if file_name in ["builds.json", "da_bosses_name.csv"]:
                temp_target_dir: str = target_dir
                target_dir = "../../results/web_results"
            copyfrom = path.join(source_dir, file_name)
            copyto = path.join(target_dir, file_name)
            shutil.copyfile(copyfrom, copyto)
            if file_name in ["builds.json", "da_bosses_name.csv"]:
                target_dir = temp_target_dir


def copy_results() -> None:
    """Copy results to a specified location."""
    # Construct full destination path
    destination = f"../../results/final_results/{RECENT_PHASE}"

    # Check if destination already exists
    if path.exists(destination):
        overwrite = input(
            f"Warning: '{destination}' already exists. Overwrite? (y/n): ",
        )
        if overwrite != "y":
            print("Operation cancelled.")
            return

        # If it's a directory, remove it first
        if path.isdir(destination):
            try:
                shutil.rmtree(destination)
                print(f"Removed existing folder: {destination}")
            except Exception as e:
                print(f"Error removing existing folder: {e}")
                return

    # Perform the copy operation
    try:
        # Use copytree to copy entire folder
        shutil.copytree("../../results/web_results", destination)
        shutil.copy(
            "../../data/versions/config.json",
            "../../results/final_results/config.json",
        )

        print("✅ Folder copied successfully!")
        print(f"   Destination: {destination}")

    except Exception as e:
        print(f"Error during copy operation: {e}")


if da_mode:
    shutil.make_archive("../../results/results", "zip", "../../results/web_results")
    copy_results()
