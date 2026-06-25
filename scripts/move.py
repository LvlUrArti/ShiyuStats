"""Move files to correct directory."""

import shutil
from os import listdir, mkdir, path

from comp_rates_config import RECENT_PHASE, RECENT_PHASE_SFX

source_dirs = [
    "../results/char_results",
    "../results/comp_results",
    "../results/comp_results/json",
    "../enka.network",
    "../enka.network/results_real",
]

for source_dir in source_dirs:
    if source_dir == "../results/comp_results/json":
        target_dir = "../results/comp_results/" + RECENT_PHASE_SFX + "/json"
    elif source_dir == "../enka.network":
        target_dir = "../enka.network/results_real"
    elif source_dir == "../enka.network/results_real":
        target_dir = source_dir + "/" + RECENT_PHASE
    else:
        target_dir = source_dir + "/" + RECENT_PHASE_SFX

    file_names = listdir(source_dir)
    if not path.exists(target_dir):
        mkdir(target_dir)
    for file_name in file_names:
        if (source_dir == "../enka.network" and file_name.startswith("output")) or (
            source_dir != "../enka.network" and file_name.endswith((".json", ".csv"))
        ):
            shutil.move(path.join(source_dir, file_name), target_dir)
            if (
                source_dir == "../enka.network/results_real"
                and not file_name.startswith("output")
            ):
                if not path.exists(target_dir + "/" + RECENT_PHASE_SFX):
                    mkdir(target_dir + "/" + RECENT_PHASE_SFX)
                shutil.move(
                    path.join(target_dir, file_name),
                    target_dir + "/" + RECENT_PHASE_SFX,
                )
