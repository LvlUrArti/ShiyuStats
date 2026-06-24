"""Combine data from multiple CSV files."""

import csv

from comp_rates_config import RECENT_PHASE
from send2trash import send2trash

char_data: dict[str, dict[str, list[str]]] = {}
print_data: list[list[str]] = [
    [
        "uid",
        "name",
        "level",
        "cons",
        "weapon",
        "element",
        "artifacts",
        "potential",
    ],
]

char_data_path = "../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv"
enka_char_path = "../data/raw_csvs_real/" + RECENT_PHASE + "_build_char.csv"

# with open("char_data.csv", 'r') as f:
with open(enka_char_path, encoding="UTF8") as f:
    reader = list(csv.DictReader(f))
    char_data_temp: list[dict[str, str]] = list(reader)
with open(char_data_path) as f:
    reader = list(csv.DictReader(f))
    char_data_temp += list(reader)
    for line in char_data_temp:
        if line["uid"] not in char_data:
            char_data[line["uid"]] = {}
        if line["name"] not in char_data[line["uid"]]:
            char_data[line["uid"]][line["name"]] = [
                line["level"],
                line["cons"],
                line["weapon"],
                line["element"],
                line["artifacts"],
                line["potential"],
            ]
for uid, uid_char in char_data.items():
    for char in uid_char:
        print_data += [[uid, "", char] + uid_char[char]]

send2trash(char_data_path)
send2trash(enka_char_path)
with open(char_data_path, "w", newline="") as f:
    csv_writer = csv.writer(f)
    csv_writer.writerows(print_data)
