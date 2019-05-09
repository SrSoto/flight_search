#!/bin/bash
echo "INICIO BÚSQUEDAS RYANAIR"
cd ..
while read p; do
	pkill -9 firefox.real
	pkill -9 Xvfb
	pkill -9 "tor -f"
	python3 flight_search.py -f --headless ryanair $p &
	pids[0]=$!
	python3 flight_search.py -f -c --headless ryanair $p & 
	pids[1]=$!
	python3 flight_search.py -f -t --headless ryanair $p 
	for pid in ${pids[*]}; do
		wait $pid
	done
done < searches/search_ryanair.txt
