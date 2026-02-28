#!/bin/bash

set -e # Stop on error

# Check for arguments, e.g. `sh compile_all.sh hello`
if [ -n "$1" ]; then
	cd Comps
else
	cd Comps
	python combine_raw_chars.py
	python csv_to_pickle.py &
	python csv_to_pickle.py -da &
	python hash.py
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
cd ../Comps
python move.py

echo ""
echo "DA stats"
cd ../enka.network
python stats.py -da
cd ../Comps
python move.py -da

python combine_char.py

python copyfiles.py
python copyfiles.py -da
