from requests import get
import requests
import json
from requests.exceptions import RequestException
from contextlib import closing

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def print_req(req):
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

#print(simple_get("https://www.iberia.com/web/dispatchSearchFormHOME.do"))
#print(simple_get("https://www.ryanair.com/es/es/booking/home/MAD/PMI/2019-03-30/2019-04-7/1/0/0/0?Discount=0"))
#req = requests.Request('GET','https://www.ryanair.com/es/es/booking/home/MAD/PMI/2019-03-30/2019-04-7/1/0/0/0?Discount=0')
#prepared = req.prepare()
#print(print_req(prepared))


FLIGHT_URL="https://desktopapps.ryanair.com/en-gb/availability?"
#FLIGHT_URL="https://desktopapps.ryanair.com/en-gb/availability?ADT=1&CHD=0&DateIn="
#+ DATEIN + "&DateOut=" + DATEOUT + "&Destination=" + DESTINATION +
#"&FlexDaysIn=6&FlexDaysOut=4&INF=0&Origin=" + ORIGIN + "&RoundTrip=true&TEEN=0"

API_URL="https://api.ryanair.com/aggregate/3/common?embedded=airports&market=en-gb"
#API_URL="http://localhost:8080/airports.json"

requests.packages.urllib3.disable_warnings()

## Print flights
#def printFlights(origin, destination, datein, dateout, type_of_flight="regularFare"):
#    url = FLIGHT_URL + "ADT=1&CHD=0&DateIn=" + datein + "&DateOut=" + dateout + "&Destination=" + destination + "&FlexDaysIn=6&FlexDaysOut=4&INF=0&Origin="+ origin + "&RoundTrip=true&TEEN=0"
#    r = requests.get(url)
#    j = json.loads(r.content)
#
#    for trip in j['trips']:
#        print (trip['origin'] + "->" + trip['destination'])
#        for day in trip['dates']:
#             for flight in day['flights']:
#                 print ("-- " + flight['flightKey'].split("~")[5] + " - " + flight['flightKey'].split("~")[7] + " - " + str(flight[type_of_flight]['fares'][0]['amount']) + "" + j['currency'])

#printFlights("MAD","PMI","2019-05-31","2019-06-07")

def printFlights(origin, destination, datein, dateout, type_of_flight="regularFare"):
    url = FLIGHT_URL + "ADT=1&CHD=0&DateIn=" + datein + "&DateOut=" + dateout + "&Destination=" + destination + "&FlexDaysIn=6&FlexDaysOut=4&INF=0&Origin="+ origin + "&RoundTrip=true&TEEN=0"
    print(url)
    r = requests.get(url)
    print(r)

#printFlights("MAD","PMI","2019-05-31","2019-06-07")
