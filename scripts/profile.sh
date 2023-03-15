#!/bin/bash

profile=$1

export LORREM_CONFIG=conf/lorrem.conf

mkdir -p .profiling

python -m memray run -f -o .profiling/$profile-memray.bin app.py
python -m memray flamegraph -f .profiling/$profile-memray.bin -o .profiling/$profile-memray.html

python -m cProfile -o .profiling/$profile-cprofile.pstats app.py
python -m gprof2dot -f pstats .profiling/$profile-cprofile.pstats > .profiling/$profile-cprofile.dot

{ time python app.py; } 2> .profiling/$profile-time.txt
