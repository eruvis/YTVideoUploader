import logging
import random
import time

from pathlib import Path
from typing import Optional

from selenium.webdriver.common.by import By

import Constant
from firefox import Firefox


class YTVideoUploader:
    def __init__(self, video_path: str, video_title: Optional[str] = None, headless: bool = False,
                 fullscreen: bool = False):
        self.video_path = str(Path.cwd() / video_path)
        self.video_title = video_title
        self.headless = headless
        self.full_screen = fullscreen

        self.browser = Firefox(fullscreen=fullscreen, headless=headless)

        self.logger = logging.getLogger(__name__)  # debug
        self.logger.setLevel(logging.DEBUG)  # debug
        logging.basicConfig()  # debug

    def upload_video(self):
        try:
            self.__login()
            return self.__upload()
        except Exception as e:
            print(e)
            self.__quit()
            raise

    def __login(self):
        self.browser.get(Constant.YOUTUBE_URL)
        self.__sleep()
        if self.browser.has_cookies_for_current_website():
            self.browser.load_cookies()
            self.__sleep()
            self.browser.refresh()
        else:
            self.logger.info('Please sign in and then press enter')  # debug
            input()
            self.browser.get(Constant.YOUTUBE_URL)
            self.__sleep()
            self.browser.save_cookies()

    def __upload(self):
        # open upload link
        self.browser.get(Constant.YOUTUBE_UPLOAD_URL)
        self.__sleep()

        # find upload element and upload send video
        self.browser.find_element(By.XPATH, Constant.FILE_DATA_INPUT).send_keys(self.video_path)
        self.logger.debug('Attached video {}'.format(self.video_path))  # debug
        self.__sleep()

        # find title input element and write title
        if self.video_title:
            self.browser.send_keys(
                self.browser.find_element(By.XPATH, Constant.VIDEO_TITLE_INPUT),
                self.video_title,
                True
            )
            self.logger.debug(f'The video title was set to \"{self.video_title}\"')  # debug
            self.__sleep()

        # kids audience
        not_for_kids_rb = self.browser.find_element(By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
        if not not_for_kids_rb.get_attribute('checked'):
            self.browser.find_element(By.ID, 'radioLabel', not_for_kids_rb).click()
            self.logger.debug(f'Selected \"{Constant.NOT_MADE_FOR_KIDS_LABEL}\"')  # debug

        for i in range(3):
            next_btn = self.browser.find_element(By.ID, Constant.NEXT_BUTTON)
            while True:
                if not self.__has_attribute(next_btn, Constant.DISABLED):
                    next_btn.click()
                    self.logger.debug(f'Clicked {Constant.NEXT_BUTTON} {i+1}')  # debug
                    self.__sleep()
                    break
                else:
                    self.__sleep()

        # publish video
        save_or_publish_rb = self.browser.find_element(By.NAME, Constant.SAVE_OR_PUBLISH_RADIO_BUTTON)
        if not self.__has_attribute(save_or_publish_rb, Constant.CHECKED):
            self.browser.find_element(By.ID, Constant.RADIO_LABEL, save_or_publish_rb).click()
            self.logger.debug(f'Selected \"{Constant.SAVE_OR_PUBLISH_RADIO_BUTTON}\"')  # debug
            self.__sleep()

        public_rb = self.browser.find_element(By.NAME, Constant.PUBLIC_RADIO_BUTTON)
        if not self.__has_attribute(public_rb, Constant.CHECKED):
            self.browser.find_element(By.ID, Constant.RADIO_LABEL, public_rb).click()
            self.logger.debug(f'Selected \"{Constant.PUBLIC_RADIO_BUTTON}\"')  # debug
            self.__sleep()

        # video link
        video_id = self.__get_video_id()

        # click upload
        self.browser.find_element(By.ID, Constant.DONE_BUTTON).click()
        self.logger.debug(f"Published the video with video_id = {video_id}")
        self.__sleep()

        self.browser.get(Constant.YOUTUBE_URL)
        self.__quit()
        return True

    def __sleep(self):
        return time.sleep(random.uniform(Constant.MIN_DELAY, Constant.MAX_DELAY))

    def __has_attribute(self, element, attribute: str):
        if self.browser.get_attribute(element, attribute):
            return True
        else:
            return False

    def __get_video_id(self):
        video_id = None

        try:
            video_url_element = self.browser.find_element(By.XPATH, Constant.VIDEO_URL_ELEMENT)
            video_id = video_url_element.get_attribute('href').split('/')[-1]
        except:
            self.logger.warning('Video url not found!')
            pass

        return video_id

    def __quit(self):
        self.browser.driver.close()
        self.browser.driver.quit()
