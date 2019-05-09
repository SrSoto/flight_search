from . import Driver
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class Iberia:

    SEARCH_WAIT = 5

    @staticmethod
    def get_prices(driver,v=False):
        """Returns the flight prices given the driver with the search results
        URL loaded.

        Parameters
        ----------
        driver : Driver Struct
            A selenium webdriver.
        v : Boolean
            verbosity.

        Returns
        -------
        List
            List of flight prices.

        """
        ret = []
        PriceLabels = driver.find_elements_by_class_name('ib-box-mini-fare__box-price')
        for lbl in PriceLabels:
            ret.append(lbl.text)
        return ret

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
        ret_tuples = []
        ret_list = driver.find_elements_by_class_name('ib-info-journey__time')
        for i in range(0,len(ret_list),2):
            if not ':' in ret_list[i].text:
                break
            ret_tuples.append((ret_list[i].text,ret_list[i+1].text))
        return ret_tuples

    @staticmethod
    def search(driver,depart,arrive,date,disable_cookies=False,tor=False,v=False):
        """Searchs for a flight in Iberia.

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
        
        url='https://www.iberia.com/'
        if not disable_cookies and not tor:
            if v:
                print("Loading cookies...")
            driver = Driver.load_cookies('iberia',driver,url)
        # load the iberia url
        if not tor:
            driver.get(url)
        else:
            driver.load_url('https://www.iberia.com/')
        
        # close the cookies pop-up when disabled
        if disable_cookies:
            CookiesButtonElement = driver.find_elements_by_class_name('close')
            if not CookiesButtonElement:
                print('Error: Element "close" not found. Recommended executing with' +
                    ' --headless off for checking any possible HTML change.')
                return None
                
            action = webdriver.common.action_chains.ActionChains(driver)
            action.move_to_element_with_offset(CookiesButtonElement[0], 0, 0)
            action.click()
            action.perform()

        # fill the departure and arrival airports
        FromElement = driver.find_elements_by_id('flight_origin1')
        ToElement = driver.find_elements_by_id('flight_destiny1')
        if v:
            print('Inserting search parameters...')
        if(FromElement and ToElement):
            FromElement[0].clear()
            FromElement[0].send_keys(depart+Keys.RETURN)
            sleep(0.3)
            FromElement[0].send_keys(Keys.RETURN)
            ToElement[0].clear()
            ToElement[0].send_keys(arrive+Keys.RETURN)
            sleep(0.3)
            ToElement[0].send_keys(Keys.RETURN)
        else:
            print('Error: Elements of depart-arrival not found. Recommended executing with' +
                ' --headless off for checking any possible HTML change.')
            return None

        # only one way flights
        NoReturnButton = driver.find_elements_by_class_name('ui-selectmenu-text')
        if(NoReturnButton):
            NoReturnButton[0].click()
            sleep(0.5)
            options = driver.find_elements_by_class_name('ui-menu-item')
            solo_ida_option = options[-2] 
            solo_ida_option.click()
        else:
            print('Error: Element "no return" not found. Recommended executing with' +
                ' --headless off for checking any possible HTML change.')
            return None

        # fill in the date
        DateElement = driver.find_elements_by_id('flight_round_date1')
        MM,DD,YYYY = date.split('/')
        if(DateElement):
            DateElement[0].clear()
            sleep(1)
            DateElement = driver.find_elements_by_id('flight_round_date1')
            if(DateElement):
                DateElement[0].send_keys(MM)
                DateElement[0].send_keys(DD)
                DateElement[0].send_keys(YYYY)
            else: 
                print('Error: Element "date" not found. Recommended executing with' +
                    ' --headless off for checking any possible HTML change.')
                return None
            Date2Element = driver.find_elements_by_id('flight_return_date1')
            if(Date2Element):
                Date2Element[0].send_keys(str((int(MM)+1)%12))
                Date2Element[0].send_keys('01')
                Date2Element[0].send_keys(YYYY)
        else:
            print('Error: Element "date" not found. Recommended executing with' +
                ' --headless off for checking any possible HTML change.')
            return None

        # random click. Read the docs chap.6 for more info
        randomClick = driver.find_elements_by_xpath('//button[@type="close"]')
        if randomClick:
            randomClick[0].click()

        # click on Search
        SearchButton = driver.find_elements_by_id('buttonSubmit1')
        if not SearchButton:
            print('Error: Element "search button" not found. Recommended executing with' +
                ' --headless off for checking any possible HTML change.')
            return None

        SearchButton[0].click()
        if not disable_cookies and not tor:
            if v:
                print("Saving cookies...")
            Driver.save_cookies('iberia',driver)

        if v:
            print('Flight search queried, now waiting for results...')
        sleep(Iberia.SEARCH_WAIT * 3)

        # get and return results
        if v:
            print('Getting results...')
        prices = Iberia.get_prices(driver,v)
        hours = Iberia.get_hours(driver,v)

        return dict(zip(hours,prices))
