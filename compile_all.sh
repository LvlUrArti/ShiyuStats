#!/bin/bash

set -e # Stop on error

# Check for arguments, e.g. `sh compile_all.sh hello`
if [ -n "$1" ]; then
	cd scripts
else
	cd scripts
	python combine_raw_chars.py
	python csv_to_pickle.py &
	python csv_to_pickle.py -da &
	python hash.py
	cd hf_data
	python up_data.py -y
	python up_data.py -n
	cd ../
fi

echo ""
echo "SD"
python comp_rates.py -w &
python comp_rates.py -f &
python comp_rates.py -a
echo ""
echo "Move SD"
python move.py

echo ""
echo "DA"
python comp_rates.py -da -w &
python comp_rates.py -da -f &
python comp_rates.py -da -a
echo ""
echo "Move DA"
python move.py -da

echo ""
echo "SD stats"
cd ../enka.network
python stats.py
cd ../scripts
python move.py

echo ""
echo "DA stats"
cd ../enka.network
python stats.py -da
cd ../scripts
python move.py -da

cd compile_result
python combine_char.py
python combine_comp.py
python combine_comp.py -da

python copyfiles.py
python copyfiles.py -da

cd ../hf_data
python up_results.py
