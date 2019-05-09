#!/usr/bin/env python3
from src import *
import argparse
import configparser
import selenium
import time
import pprint
import os
import sqlite3
from decimal import Decimal
from tbselenium.utils import start_xvfb, stop_xvfb
from re import findall,sub
from urllib.request import urlopen

DATABASE_NAME = 'flight_data/flight_data_db.sqlite'
INTERNET_CHECK_URL = 'http://216.58.192.142'
INTERNET_CHECK_TIMEOUT = 30


def get_cheapest_flight(results):
    """Return the (ts, price) with the lowest price.

    Parameters
    ----------
    results : Map of timestamp and prices
        The results given by the search function.

    Returns
    -------
    (float, float)
        The cheapest flight found.
    """
    l = list(results.values())
    ps = []
    for spl in l:
        # why not checking for any other currency?
        # read the docs, chap.6
        spl = spl.replace(',','.').split('€')
        for tok in spl:
            if any(c.isdigit() for c in tok):
                ps.append(float(tok))
                break
    ts = time.time()
    ps = sorted(ps)
    p = ps[0]
    return ts, p

def internet_on():
    """Checks if Internet is on.
    The INTERNET_CHECK_URL can be specified in the .conf file

    Returns
    -------
    Boolean
        True if internet is on, false if the timeout was reached.
    """
    try:
        urlopen(INTERNET_CHECK_URL, timeout=INTERNET_CHECK_TIMEOUT)
        return True
    except:
        return False

def save_flight_to_text(results, prev_wd, args, v):
    """Saves cheapest flight in a generated .txt file.

    Parameters
    ----------
    results : Dict
        Dictionary of timestamps and prices.
    prev_wd : String
        Working directory previous to search the flight.
    args : Argparser struct
    v : Boolean
        verbosity.
    """
    os.chdir(prev_wd)
    # this is the .txt generated filename.
    file_name = "flight_data/"+args.company.lower()+"_"+args.fromc.lower()+"-"+args.to.lower()+"_"+args.date.replace('/','-')
    if args.nocookies:
        file_name+='_nocookies'
    elif args.tor:
        file_name+='_tor'
    file_name+='.txt'

    if os.path.exists(file_name):
        append_write = 'a' # append if already exists
    else:
        if v:
            print('Creating '+file_name+'...')
        append_write = 'w' # make a new file if not
    if v:
        print('Saving cheapest flight in %s...' % (file_name))
        ts, p = get_cheapest_flight(results)
        with open(file_name,append_write) as f:
            f.write(str(ts)+'\t'+str(p)+'\n')
    if v:
        print('Done.')

def save_flight_database(results,prev_wd,args,v):
    """Saves the cheapest flight in an SQL database.
        The DATABASE_NAME param can be specified in the .conf file.
    Parameters
    ----------
    results : Dict
        Dictionary of timestamps and prices.
    prev_wd : String
        Working directory previous to search the flight.
    args : Argparser struct
    v : Boolean
        verbosity.
    """
    os.chdir(prev_wd)
    if args.nocookies:
        typ = 'nocookies'
    elif args.tor:
        typ = 'tor'
    else:
        typ = 'cookies'
    if v:
        print('Saving cheapest flight in database...')
    ts, p = get_cheapest_flight(results)
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    # SQL query for inserting the cheapest flight
    cur.execute('INSERT INTO flights (company, from_c, to_c, date, type, price, ts) VALUES (?, ?, ?, ?, ?, ?, ?)',(args.company.lower(),args.fromc.lower(),args.to.lower(),args.date.replace('/','-'), typ,str(p),str(ts)))
    conn.commit()
    conn.close()
    if v:
        print('Done.')

def set_conf():
    """Reads the .conf file (config/flight_search.conf) and loads it.

    Returns
    -------
    Boolean
        True if loaded successfully, False if not.
    """
    config = configparser.ConfigParser()
    if not config.read('config/flight_search.conf'):
        print('Error: Config file not found. ¿Is it in config/flight_search.conf?')
        return False
    INTERNET_CHECK_URL = config['MAIN']['INTERNET_CHECK_URL']
    INTERNET_CHECK_TIMEOUT = int(config['MAIN']['INTERNET_CHECK_TIMEOUT'])
    DATABASE_NAME = config['MAIN']['DATABASE_NAME']
    Ryanair.SEARCH_WAIT = int(config['MAIN']['SEARCH_WAIT'])
    Iberia.SEARCH_WAIT = int(config['MAIN']['SEARCH_WAIT'])
    Ryanair.TOR_WAIT = int(config['MAIN']['TOR_WAIT'])
    Ryanair.TOR_TRIES = int(config['MAIN']['TOR_TRIES'])
    Driver.TOR_PATH = config['MAIN']['TOR_PATH']
    return True

def flight_search():
    parser = argparse.ArgumentParser(description="A headless flight searcher")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c","--nocookies",help="disables cookies", action='store_true')
    group.add_argument("-t","--tor",help="search using TOR", action='store_true')
    parser.add_argument("-f","--file",help="store (timestamp,depart hour,lowest price) in a generated archive in \'flight_data/\'",action='store_true')
    parser.add_argument("-v","--verbosity",help="program verbosity", action='store_true')
    parser.add_argument("-hd","--headless",help="use headless browser", action='store_true')
    parser.add_argument("company",help="select company of the flight", default="iberia")
    parser.add_argument("fromc",help="from (recommended city name or airport code)")
    parser.add_argument("to",help="to (airport code)")
    parser.add_argument("date",help="date (MM/DD/YYYY)")
    args = parser.parse_args()

    v = args.verbosity

    if not set_conf():
        return

    if not internet_on():
        print('Error: There is no Internet Connection')
        return

    if v:
        print('Init of search with %s: %s to %s, %s' % (args.company, args.fromc, args.to, args.date))

    comp = args.company.lower()
    prev_wd = os.getcwd()
    try:
        # prepare the driver
        driver,display,tor_process = Driver.prepare_driver(args.nocookies,args.tor,v,args.headless)
        if driver is None:
            return
        # select the company search function. This if/elif will grow.
        if(comp=='iberia'):
            results = Iberia.search(driver,args.fromc,args.to,args.date,args.nocookies,args.tor,v)
        elif(comp=='ryanair'):
            results = Ryanair.search(driver,args.fromc,args.to,args.date,args.nocookies,args.tor,v)
        else:
            print('Error: Company %s not supported' % (comp))
            return

        if not results or not len(results):
            print('No results for %s %s - %s ON DATE %s.' % (args.company.upper(), args.fromc.upper(), args.to.upper(), args.date))
            return
        else:
            print('%s SEARCH RESULTS OF %s - %s ON DATE %s:' % (args.company.upper(), args.fromc.upper(), args.to.upper(), args.date))
            pprint.pprint(results)
        if args.file:
            save_flight_to_text(results,prev_wd,args,v)
            save_flight_database(results,prev_wd,args,v)
    except selenium.common.exceptions.ElementNotInteractableException:
        print('Error: Website currently blocked or different from usual')
        raise
    finally:
        if driver:
            driver.close()
            if args.tor:
                if args.headless:
                    stop_xvfb(display)
                tor_process.kill()

if __name__ == '__main__':
    flight_search()
