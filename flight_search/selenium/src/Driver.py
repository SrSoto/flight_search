import pickle
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from tbselenium.tbdriver import TorBrowserDriver
import tbselenium.common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import launch_tbb_tor_with_stem
from tbselenium.utils import start_xvfb, stop_xvfb
import time
import os

class Driver:

    # The TOR_PATH must be set using the .conf file
    TOR_PATH = None 

    @staticmethod
    def save_cookies(company,driver):
        """Saves the cookies from a given company.

        Parameters
        ----------
        company : String
            Name of the flights company ('ryanair', 'iberia' ...)
        driver : Driver Struct
            A selenium webdriver.

        Returns
        -------
        WebDriver
            The given driver.

        """
        pickle.dump(driver.get_cookies(),open("cookie_data/"+company+"_cookies.pkl","wb"))

    @staticmethod
    def load_cookies(company,driver,url):
        """Loads the cookies from a given company.

        Parameters
        ----------
        company : String
            Name of the flights company ('ryanair', 'iberia' ...)
        driver : Driver Struct
            A selenium webdriver.
        url : String
            The main URL of the webpage (e.g. 'https://www.ryanair.com/').

        Returns
        -------
        WebDriver
            The given driver.

        """
        # default filename depending of the company 
        file_name = "cookie_data/"+company+"_cookies.pkl"
        if os.path.exists(file_name):
            # load robots.txt for getting to the company domain
            def_url = url+'/robots.txt'
            driver.get(def_url)
            # load the pickle
            cookies = pickle.load(open(file_name, "rb"))
            for cookie in cookies:
                try:
                    # add each cookie stored in the pickle
                    driver.add_cookie(cookie)
                except selenium.common.exceptions.InvalidCookieDomainException:
                    try:
                        # for secondary cookies from other domains
                        driver.get(cookie['domain'])
                        driver.add_cookie(cookie)
                        driver.get(def_url)
                    except:
                        print('Error: Invalid cookie:' + str(cookie))
                        cookies.remove(cookie)

        return driver

    @staticmethod
    def prepare_driver(disable_cookies=False,tor=False,v=False,headless=False):
        """Prepares a Selenium webdriver given multiple args.

        Parameters
        ----------
        disable_cookies : Boolean
            True to use a driver in incognito mode with cookies disables.
        tor : Boolean
            True to use a Tor webdriver.
        v : Boolean
            verbosity.
        headless : Boolean
            True to set the webdriver headless, which means not showing the
            Firefox window.

        Returns
        -------
        WebDriver
            A selenium or tbselenium webdriver.
        xvfb_display
            The Xvfb process for hiding the tbselenium webdriver.
        tor_process
            The Stem process for running the tbselenium webdriver.

        """
        options = Options()
        if headless and v:
            print("Setting headless mode...")
        options.headless = headless
        if disable_cookies:
            firefox_profile = webdriver.FirefoxProfile()
            # set incognito mode
            firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
            # disable cookies
            firefox_profile.set_preference("network.cookie.cookieBehavior",2)
            driver = webdriver.Firefox(options=options,firefox_profile=firefox_profile)
        elif not tor:
            driver = webdriver.Firefox(options=options)
        else:
            if v:
                print("Configuring tor browser...")
            tbb_dir =  Driver.TOR_PATH
            if headless:
                xvfb_display = start_xvfb()
            try:
                tor_process = launch_tbb_tor_with_stem(tbb_path=tbb_dir)
            except OSError as e:
                if 'timeout' in str(e):
                    print('Error: Tor connection timeout. Check URL or Internet connection')
                    return None, None, None
                else:
                    raise e

            # Tor driver constructor
            driver = TorBrowserDriver(tbb_dir, tor_cfg=cm.USE_STEM)
            if headless:
                return driver, xvfb_display, tor_process
            else:
                return driver, None, tor_process
        return driver, None, None
