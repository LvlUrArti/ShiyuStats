import csv
from os import path

from enka_config import RECENT_PHASE
from send2trash import send2trash

output: list[list[str]] = []
output_char: list[list[str]] = []

iteration = 0
while path.exists(
    "results_real/" + RECENT_PHASE + "/output" + str(iteration + 1) + ".csv"
):
    iteration += 1
uidlistchar = set[str]()
uidlist = set[str]()
uidcheck = set[int]()

for i in range(iteration):
    print(f"{i + 1} / {iteration}", end="")
    with open("results_real/" + RECENT_PHASE + "/output" + str(i + 1) + ".csv") as f:
        reader = csv.reader(f, delimiter=",")
        headers = next(reader)
        if i == 0:
            output += [headers]
            output_temp = list(reader)
            for j in output_temp:
                uidlistchar.add(j[0])
                output += [j]
        else:
            output_temp = list(reader)
            for j in output_temp:
                if j[0] not in uidlistchar:
                    output += [j]
        # np.concatenate((output, list(reader)), axis=1)

    with open(
        "results_real/" + RECENT_PHASE + "/output" + str(i + 1) + "_char.csv"
    ) as f:
        reader = csv.reader(f, delimiter=",")
        headers = next(reader)
        if i == 0:
            output_char += [headers]
            output_chartemp = list(reader)
            for j in output_chartemp:
                uidlist.add(j[0])
                output_char += [j]
        else:
            output_chartemp = list(reader)
            for j in output_chartemp:
                if j[0] not in uidlist:
                    output_char += [j]
                    uidcheck.add(int(j[0]))
        # np.concatenate((output_char, list(reader)), axis=1)
    send2trash("results_real/" + RECENT_PHASE + "/output" + str(i + 1) + ".csv")
    send2trash("results_real/" + RECENT_PHASE + "/output" + str(i + 1) + "_char.csv")
    print("\r", end="")

# print(uidcheck)
csv_writer = csv.writer(
    open("results_real/" + RECENT_PHASE + "/output1.csv", "w", newline="")
)
csv_writer.writerows(output)

csv_writer = csv.writer(
    open("results_real/" + RECENT_PHASE + "/output1_char.csv", "w", newline="")
)
csv_writer.writerows(output_char)
