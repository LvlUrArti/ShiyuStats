# ShiyuStats

Compile Shiyu Defense data using Python.

You can find the raw data in my [Hugging Face Dataset](https://huggingface.co/datasets/LvlUrArti/ShiyuData). You can also find the results of data compilation in another [Hugging Face Dataset](https://huggingface.co/datasets/LvlUrArti/ShiyuDataProcessed).

Feel free to analyze the data and post the findings. If you do, please credit me (LvlUrArti).

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q4IJ3P6)

# How to use

## Setup

1. Run `pip install -r requirements.txt`
2. In the `scripts/hf_data` folder, run `python fetch_data.py`
3. Change `past_phase` and `recent_phase` in `scripts/comp_rates_config.py`

## Compile for all gamemodes

Run `sh compile_all.sh`

Results can be found in the `results` folder.

## Compile for a specific gamemode

> By default, this compiles data for Shiyu Defense. Add the argument `-da` at the end of all python commands to compile data for Deadly Assault. For example, instead of `python comp_rates.py`, run `python comp_rates.py -da`.

1. In the `scripts` folder, run `python comp_rates.py`
2. Still in the `scripts` folder, run `python move.py`
3. In the `enka.network` folder, run `python stats.py`
