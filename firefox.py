import datetime
import logging
import pickle
import os
import time

import tldextract

from typing import Optional

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

COOKIE_PATH = os.path.join(os.getcwd(), 'cookies')


class Firefox:
    def __init__(
            self,
            cookies_folder_path: str = COOKIE_PATH,
            language: str = 'ru',
            fullscreen: bool = True,
            private: bool = False,
            user_agent: str = None,
            headless: bool = False,
            host: str = None,
            port: int = None,
    ):
        self.cookies_folder_path = cookies_folder_path
        self.options = webdriver.FirefoxOptions()

        if language:
            self.__set_language(language)

        if private:
            self.__set_private()

        if user_agent:
            self.__set_user_agent(user_agent)

        if headless:
            self.__set_headless()

        if host and port:
            self.__set_proxy(host, port)

        self.__set_options()

        self.service = Service(executable_path='webdriver/geckodriver.exe', log_path='webdriver/geckodriver.log')

        firefoxProfile = webdriver.FirefoxProfile()
        firefoxProfile.set_preference('permissions.default.stylesheet', 2)
        firefoxProfile.set_preference('permissions.default.image', 2)
        firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
        firefoxProfile.set_preference("http.response.timeout", 20)
        firefoxProfile.set_preference("dom.max_script_run_time", 20)

        self.driver = webdriver.Firefox(service=self.service, firefox_profile=firefoxProfile, options=self.options)

        if fullscreen:
            self.__set_fullscreen()

    def get(self, url: str) -> bool:
        clean_current = self.driver.current_url.replace('https://', '').replace('http://', '').replace('www.', '').strip('/')
        clean_new = url.replace('https://', '').replace('http://', '').replace('www.', '').strip('/')

        if clean_current == clean_new:
            return False

        self.driver.get(url)

        return True

    def refresh(self) -> None:
        self.driver.refresh()

    def find_element(self, by: By, key: str, element: Optional = None, timeout: float = 15.0) -> Optional:
        if element is None:
            element = self.driver
        try:
            return WebDriverWait(driver=element, timeout=timeout).until(EC.presence_of_element_located((by, key)))
        except TimeoutException:
            logging.error(f'Dont find element with key: {key}')
            self.screenshot()
            return None

    def has_cookies_for_current_website(self) -> bool:
        return os.path.exists(self.__cookies_path())

    def save_cookies(self) -> None:
        pickle.dump(
            self.driver.get_cookies(),
            open(self.__cookies_path(), "wb")
        )

    def load_cookies(self) -> None:
        if not self.has_cookies_for_current_website():
            self.save_cookies()
            return

        cookies = pickle.load(open(self.__cookies_path(), "rb"))

        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def send_keys(self, field, string: str, overwrite=False):
        if overwrite:
            field.click()
            time.sleep(2)
            field.send_keys(Keys.CONTROL + 'a')
            time.sleep(2)
        field.send_keys(string)

    def get_attribute(self, element, key: str) -> Optional[str]:
        try:
            return element.get_attribute(key)
        except:
            return None

    def screenshot(self):
        if not os.path.isdir('media'):
            os.mkdir('media')
        self.driver.get_screenshot_as_file(f"media/" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f") + '.png')

    def __set_options(self):
        self.options.set_preference("marionette", False)
        self.options.set_preference("dom.webdriver.enabled", False)
        self.options.set_preference("media.peerconnection.enabled", False)
        self.options.set_preference("browser.aboutConfig.showWarning", False)

    def __set_fullscreen(self):
        self.driver.fullscreen_window()

    def __set_headless(self):
        self.options.add_argument("--headless")

    def __set_language(self, language):
        self.options.set_preference('intl.accept_languages', language)

    def __set_private(self):
        self.options.set_preference("browser.privatebrowsing.autostart", True)

    def __set_user_agent(self, user_agent):
        self.options.set_preference("general.useragent.override", user_agent)

    def __set_proxy(self, host, port):
        self.options.set_preference("network.proxy.type", 1)
        self.options.set_preference("network.proxy.http", host)
        self.options.set_preference("network.proxy.http_port", port)
        self.options.set_preference("network.proxy.ssl", host)
        self.options.set_preference("network.proxy.ssl_port", port)
        self.options.set_preference("network.proxy.ftp", host)
        self.options.set_preference("network.proxy.ftp_port", port)
        self.options.set_preference("network.proxy.socks", host)
        self.options.set_preference("network.proxy.socks_port", port)
        self.options.set_preference("network.proxy.socks_version", 5)
        self.options.set_preference("signon.autologin.proxy", True)

    def __cookies_path(self, create_folder_if_not_exists: bool = True) -> str:
        if not os.path.isdir(COOKIE_PATH) and create_folder_if_not_exists:
            try:
                os.mkdir(COOKIE_PATH)
            except OSError as e:
                print(e)

        url_comps = tldextract.extract(self.driver.current_url)
        formatted_url = url_comps.domain + '.' + url_comps.suffix

        return os.path.join(
            self.cookies_folder_path,
            formatted_url + '.pkl'
        )
