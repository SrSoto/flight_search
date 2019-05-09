cd ..

sqlite3 flight_data_db.sqlite "SELECT ts,price from flights WHERE to_c='$1' AND date='$2' AND type='cookies';" > plots/cookies.txt
sqlite3 flight_data_db.sqlite "SELECT ts,price from flights WHERE to_c='$1' AND date='$2' AND type='nocookies';" > plots/nocookies.txt
sqlite3 flight_data_db.sqlite "SELECT ts,price from flights WHERE to_c='$1' AND date='$2' AND type='tor';" > plots/tor.txt

cd plots/

gnuplot << END_GNUPLOT
set datafile separator '|'
set title "Prices for $1 on $2"
set ylabel "Price (€)"
set xlabel "Time of search (Date)"
set xdata time
set timefmt "%s"
set format x "%d/%m"
set xtics rotate
set key right bottom
set grid
set term png
set output "$1_$2.png"
plot "cookies.txt" using 1:2 with linespoints lw 2 lc rgb "#4000FF00" title "Cookies", \
			"nocookies.txt" using 1:2 with linespoints lw 2 lc rgb "#400000FF" title "No Cookies", \
			"tor.txt" using 1:2 with linespoints lw 2 lc rgb "#40FF0000" title "Tor"
replot
quit
END_GNUPLOT

