import csv

from comp_rates_config import RECENT_PHASE
from send2trash import send2trash

char_data: dict[str, dict[str, list[str]]] = {}
print_data: list[list[str]] = []

# with open("char_data.csv", 'r') as f:
with open(
    "../enka.network/results_real/" + RECENT_PHASE + "/output1_char.csv",
    encoding="UTF8",
) as f:
    reader = csv.reader(f, delimiter=",")
    print_data += [next(reader)]
    char_data_temp = list(reader)
with open("../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv") as f:
    reader = csv.reader(f, delimiter=",")
    headers = next(reader)
    char_data_temp += list(reader)
    for line in char_data_temp:
        if line[0] not in char_data:
            char_data[line[0]] = {}
        if line[2] not in char_data[line[0]]:
            char_data[line[0]][line[2]] = line[3:]
for uid in char_data:
    for char in char_data[uid]:
        print_data += [[uid, "", char] + char_data[uid][char]]

send2trash("../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv")
csv_writer = csv.writer(
    open("../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv", "w", newline="")
)
csv_writer.writerows(print_data)
