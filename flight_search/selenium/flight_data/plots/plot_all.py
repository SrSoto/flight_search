import os

# simple python script for plotting every search fixed

f = open("../../searches/search_ryanair.txt","r")
for line in f:
    to_c, date = line.split(' ')[1:]
    date = date.replace('/','-')
    to_c = to_c.lower()
    os.system("./flight_plotter.sh %s %s" % (to_c, date))

