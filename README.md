# ShiyuStats

Compile Shiyu Defense data using Python.

You can find the raw data in my [Hugging Face Dataset](https://huggingface.co/datasets/LvlUrArti/ShiyuData). You can also find the results of data compilation in another [Hugging Face Dataset](https://huggingface.co/datasets/LvlUrArti/ShiyuDataProcessed).

Feel free to analyze the data and post the findings. If you do, please credit me (LvlUrArti).

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q4IJ3P6)

# How to use

## Setup

Run `pip install -r requirements.txt`

In the `scripts/hf_data` folder, run `python fetch_data.py`

Change past and recent phase in `scripts/comp_rates_config.py`

## Compile for all gamemodes

Run `sh compile_all.sh`

Results can be found in the `results` folder

## Compile specific gamemode

> By default, this compiles data for Shiyu Defense, add the argument `-da` at the end of all python commands to compile data for deadly assault. So instead of `python comp_rates.py`, run `python comp_rates.py -pf`.

In `scripts` folder, run `python comp_rates.py`

Still in `scripts` folder, run `python move.py`

In `enka.network` folder, run `python stats.py`
