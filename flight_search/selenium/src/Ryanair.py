from . import Driver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class Ryanair:

    SEARCH_WAIT = 5
    TOR_WAIT = 3*SEARCH_WAIT
    TOR_TRIES = 1

    @staticmethod
    def get_prices(driver,v=False, t=False):
        """Returns the flight prices given the driver with the search results
        URL loaded.

        Parameters
        ----------
        driver : Driver Struct
            A selenium webdriver.
        v : Boolean
            verbosity.
        t : Boolean
            True if using Tor

        Returns
        -------
        List
            List of flight prices.

        """
        PriceLabel = driver.find_elements_by_xpath("//span[@class='flights-table-price__price']")
        tries = Ryanair.TOR_TRIES
        while not PriceLabel:
            if not tries:
                if t:
                    print('Error: This Tor Path is blocked.')
                else:
                    print('Error: The website is currently blocked.')
                return None
            driver.refresh()
            sleep(Ryanair.TOR_WAIT)
            PriceLabel = driver.find_elements_by_xpath("//span[@class='flights-table-price__price']")
            tries-=1
        money_text = PriceLabel[0].get_attribute("textContent")
        return [money_text]

    @staticmethod
    def get_hours(driver,v=False):
        """Returns the flight hours.

        Parameters
        ----------
        driver : Driver Struct
            A selenium webdriver.
        v : Boolean
            verbosity.

        Returns
        -------
        List
            List of flight hours.

        """
        StartLabel = driver.find_elements_by_xpath("//div[@class='start-time']")
        EndLabel = driver.find_elements_by_xpath("//div[@class='end-time']")
        return [(StartLabel[0].text,EndLabel[0].text)]

    @staticmethod
    def shortcut(driver,depart,arrive,date,tor,v):
        """Search with Ryanair using the URL shorcut (read the docs for more info).

        Parameters
        ----------
        driver : Driver Struct
            A selenium webdriver.
        depart : String
            Airport of departure
        arrive : String
            Airport of arrival
        date : String
            Day of departure (MM-DD-YYYY)
        disable_cookies : Boolean
            Search with no cookies in incognito mode
        tor : Boolean
            Search using Tor.
        v : Boolean
            verbosity.

        Returns
        -------
        Dict
            Dictionary of hours and prices.

        """
        MM,DD,YYYY = date.split('/')
        uri_date = YYYY+'-'+MM+'-'+DD
        def_url = 'https://www.ryanair.com/'
        # shortcurt URL
        shortcut_url = 'booking/home/'+depart+'/'+arrive+'/'+uri_date+'//1/0/0/0'
        
        # load the full URL
        if tor:
            driver.load_url(def_url)
            sleep(Ryanair.SEARCH_WAIT)
            url = driver.current_url + shortcut_url
            if v:
                print('Searching in '+ url + ' ...')
            driver.load_url(url)
            sleep(Ryanair.TOR_WAIT)
        else:
            url = def_url+'es/es/'+shortcut_url
            if v:
                print('Searching in '+ url + ' ...')
            driver.get(url)
            sleep(Ryanair.SEARCH_WAIT)

        # wait for, get and return results
        if v:
            print('Getting results...')
        prices = Ryanair.get_prices(driver,v)
        if not prices:
            return None
        hours = Ryanair.get_hours(driver,v)

        return dict(zip(hours,prices))

    @staticmethod
    def search(driver,depart,arrive,date,disable_cookies=False,tor=False,v=False):
        """Searchs for a flight in Ryanair.

        Parameters
        ----------
        driver : Driver Struct
            A selenium webdriver.
        depart : String
            Airport of departure
        arrive : String
            Airport of arrival
        date : String
            Day of departure (MM-DD-YYYY)
        disable_cookies : Boolean
            Search with no cookies in incognito mode
        tor : Boolean
            Search using Tor.
        v : Boolean
            verbosity.
        Returns
        -------
        Dict
            Dictionary of hours and prices.
        """

        url='https://www.ryanair.com/'
        if not disable_cookies and not tor:
            if v:
                print("Loading cookies...")
            driver = Driver.load_cookies('ryanair',driver,url)
            driver.get(url)
        # if in incognito mode or using Tor, we use the URL shortcut
        else:
            return Ryanair.shortcut(driver,depart,arrive,date,tor,v)


        # fill the departure and arrival airports
        FromElement = driver.find_elements_by_xpath("//input[@placeholder='Departure airport']")
        ToElement = driver.find_elements_by_xpath("//input[@placeholder='Destination airport']")
        if v:
            print('Inserting search parameters...')
        if FromElement and ToElement:
            FromElement[0].clear()
            ToElement[0].clear()
            FromElement[0].send_keys(depart+'\r\n')
            ToElement[0].send_keys(arrive)
            sleep(0.01)
            ToElement[0].clear()
            ToElement[0].send_keys(arrive+Keys.RETURN)
        else:
            print('Fallo en la búsqueda de elementos')

        # click on No Return
        NoReturnButton = driver.find_elements_by_id('flight-search-type-option-one-way')
        if(NoReturnButton):
            NoReturnButton[0].click()
        else:
            print('Fallo en la búsqueda de elementos')

        sleep(1)
 
        # fill in the date
        DDElement = driver.find_elements_by_xpath("//input[@aria-label='Fly out: - DD']")
        MMElement = driver.find_elements_by_xpath("//input[@aria-label='Fly out: - MM']")
        YYYYElement = driver.find_elements_by_xpath("//input[@aria-label='Fly out: - YYYY']")
        MM,DD,YYYY = date.split('/')
        if(DDElement and MMElement and YYYYElement):
            YYYYElement[0].send_keys(YYYY)
            sleep(0.1)
            MMElement[0].clear()
            MMElement[0].send_keys(MM)
            sleep(0.1)
            DDElement[0].clear()
            DDElement[0].send_keys(DD)
        else:
            print('Fallo en la búsqueda de elementos')

        # random click
        randomClick = driver.find_elements_by_xpath('//button[@type="close"]')
        if randomClick:
            randomClick[0].click()
        sleep(0.5)

        # click on Search
        SearchButton = driver.find_elements_by_xpath("//button[@ng-click='searchFlights()']")
        SearchButton[0].click()
        if not disable_cookies:
            if v:
                print("Saving cookies...")
            Driver.save_cookies('ryanair',driver)
        if v:
            print('Flight search queried, now waiting for results...')

        # wait for, get and return results
        sleep(Ryanair.SEARCH_WAIT)
        if v:
            print('Getting results...')
        prices = Ryanair.get_prices(driver,v)
        if not prices:
            return None
        hours = Ryanair.get_hours(driver,v)

        return dict(zip(hours,prices))
