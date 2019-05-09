#!/bin/bash
echo "INICIO BÚSQUEDAS IBERIA"
cd ..
while read p; do
	python3 flight_search.py -f --headless iberia $p 
	python3 flight_search.py -f -c --headless iberia $p 
	sleep $[ ( $RANDOM % 60 )  + 1 ]s
done < searches/search_iberia.txt
