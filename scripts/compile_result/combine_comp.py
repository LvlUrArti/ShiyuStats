"""Combine JSON results."""

from __future__ import annotations

import json
from sys import path as sys_path

sys_path.append("../")
from comp_rates_config import RECENT_PHASE_SFX, da_mode

file_names = ["top"]
da_names = ["1-1", "1-2", "1-3"]
sd_names = ["5-1", "5-2", "5-3"]
exclude_value = 0

if da_mode:
    file_names.extend(da_names)
else:
    file_names.extend(sd_names)

for file_name in file_names:
    # Load the JSON files
    with open(
        f"../../results/comp_results/{RECENT_PHASE_SFX}/json/{file_name}.json",
    ) as f:
        team_data: list[dict[str, str | float]] = json.load(f)

    with open(
        f"../../results/comp_results/{RECENT_PHASE_SFX}/json/{file_name}_C1.json",
    ) as f:
        team_m1_data = json.load(f)

    # Create a dictionary to store the matched teams
    matched_teams: dict[tuple[str | float, ...], dict[str, str | float]] = {}
    matched_teams_m1: dict[tuple[str | float, ...], dict[str, str | float]] = {}
    output_teams: dict[tuple[str | float, ...], dict[str, str | float]] = {}

    # Iterate over the team_data and create a tuple key for each team
    for team in team_data:
        team_key = (
            team["char_one"],
            team["char_two"],
            team["char_three"],
        )
        matched_teams[team_key] = team

    for team in team_m1_data:
        team_key = (
            team["char_one"],
            team["char_two"],
            team["char_three"],
        )
        matched_teams_m1[team_key] = team

    # Iterate over the matched_teams_m1 and add the avg_round to the matched teams
    for team_key, matched_team in matched_teams.items():
        if team_key in matched_teams_m1:
            matched_team["avg_round_m1"] = matched_teams_m1[team_key]["avg_round"]
        else:
            matched_team["avg_round_m1"] = exclude_value

        if (
            matched_team["avg_round_m1"] == exclude_value
            and matched_team["avg_round"] == exclude_value
        ):
            continue

        output_teams[team_key] = matched_team.copy()

    team_data = list(output_teams.values())

    # Write the updated data back to the json file
    with open(
        f"../../results/comp_results/{RECENT_PHASE_SFX}/json/{file_name}_combined.json",
        "w",
    ) as f:
        json.dump(team_data, f, indent=2)
