import os
import time

from selenium import webdriver

from webdriver.firefox import Firefox

if __name__ == '__main__':
    # browser = Firefox()
    # browser.get('https://www.youtube.com/')
    # # login
    # browser.get('https://www.youtube.com/upload')

    # options = webdriver.FirefoxOptions()
    # options.set_preference("marionatte", False)
    # options.set_preference("dom.webdriver.enabled", False)
    # options.set_preference("media.peerconnection.enabled", False)
    # options.set_preference('useAutomationExtension', False)
    # options.set_preference("general.warnOnAboutConfig", False)
    # driver = webdriver.Firefox(options=options)
    # driver.get('https://www.youtube.com/upload')

    # time.sleep(5)
    # browser.driver.quit()
    print("HELLO")

# search_box = driver.find_element(By.NAME, 'q')
search_box.send_keys('ChromeDriver')
# search_box.submit()
# time.sleep(5)  # Let the user actually see something!
