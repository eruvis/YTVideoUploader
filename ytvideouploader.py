import logging
import multiprocessing
import random
import time

from pathlib import Path
from typing import Optional

from selenium.common import ElementNotInteractableException
from selenium.webdriver.common.by import By

import Constant
from firefox import Firefox


class YTVideoUploader:
    def __init__(self, task_n, video_path: str, video_title: Optional[str] = None,
                 hide_notify: bool = False,
                 headless: bool = False,
                 fullscreen: bool = False):
        self.task_n = str(task_n)
        self.video_path = str(Path.cwd() / video_path)
        self.video_title = video_title
        self.hide_notify = hide_notify
        self.headless = headless
        self.full_screen = fullscreen
        self.__init_logger()

        self.browser = Firefox(fullscreen=fullscreen, headless=headless)

    def upload_video(self):
        try:
            logging.info('Task start!')
            self.__login()
            return self.__upload()
        except ElementNotInteractableException as e:
            logging.error(e.msg)  # debug
            self.browser.screenshot()
            return False
        except Exception as e:
            logging.exception(e.__traceback__)  # debug
            if self.browser.driver.service.is_connectable():
                self.browser.screenshot()
            return False
        finally:
            self.__quit()

    def __init_logger(self):
        n_process = multiprocessing.current_process().name.split('-')[-1]
        if n_process == 'MainProcess':
            n_process = 1
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] [PROCESS №' + str(n_process) + '] [TASK №' + self.task_n + ']: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            force=True
        )  # debug

    def __login(self):
        self.browser.get(Constant.YOUTUBE_URL)
        self.__sleep()
        if self.browser.has_cookies_for_current_website():
            self.browser.load_cookies()
            self.__sleep()
            self.browser.refresh()
        else:
            logging.info('Please sign in and then press enter')  # debug
            input()
            self.browser.get(Constant.YOUTUBE_URL)
            self.__sleep()
            self.browser.save_cookies()

    def __upload(self):
        # open upload link
        self.browser.get(Constant.YOUTUBE_UPLOAD_URL)
        self.__sleep()

        # find upload element and upload send video
        file_data_input = self.browser.find_element(By.XPATH, Constant.FILE_DATA_INPUT)
        if file_data_input is None:
            return False

        self.browser.send_keys(file_data_input, self.video_path)
        logging.info(f'Attached video {self.video_path}')  # debug
        self.__sleep()

        # find title input element and write title
        if self.video_title:
            video_title_input = self.browser.find_element(By.XPATH, Constant.VIDEO_TITLE_INPUT)
            if video_title_input is None:
                return False
            self.browser.send_keys(video_title_input, self.video_title, True)
            logging.info(f'The video title was set to \"{self.video_title}\"')  # debug
            self.__sleep()

        # kids audience
        not_for_kids_rb = self.browser.find_element(By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
        if not not_for_kids_rb.get_attribute('checked'):
            self.browser.find_element(By.ID, 'radioLabel', not_for_kids_rb).click()
            logging.info(f'Selected \"{Constant.NOT_MADE_FOR_KIDS_LABEL}\"')  # debug

        if self.hide_notify:
            # advanced options
            ad_options = self.browser.find_element(By.ID, Constant.TOGGLE_BUTTON)
            ad_options.click()
            logging.info(f'Open advanced options')  # debug
            self.__sleep()

            # hide notify
            notify_subscribes = self.browser.find_element(By.ID, Constant.NOTIFY_SUBSCRIBERS)
            notify_subscribes.click()
            logging.info(f'Selected \"{Constant.NOTIFY_SUBSCRIBERS}\"')  # debug

        # next button
        for i in range(3):
            next_btn = self.browser.find_element(By.ID, Constant.NEXT_BUTTON)
            while True:
                if not self.__has_attribute(next_btn, Constant.DISABLED):
                    next_btn.click()
                    logging.info(f'Clicked {Constant.NEXT_BUTTON} {i + 1}')  # debug
                    self.__sleep()
                    break
                else:
                    self.__sleep()

        # publish video
        save_or_publish_rb = self.browser.find_element(By.NAME, Constant.SAVE_OR_PUBLISH_RADIO_BUTTON)
        if not self.__has_attribute(save_or_publish_rb, Constant.CHECKED):
            self.browser.find_element(By.ID, Constant.RADIO_LABEL, save_or_publish_rb).click()
            logging.info(f'Selected \"{Constant.SAVE_OR_PUBLISH_RADIO_BUTTON}\"')  # debug
            self.__sleep()

        public_rb = self.browser.find_element(By.NAME, Constant.PUBLIC_RADIO_BUTTON)
        if not self.__has_attribute(public_rb, Constant.CHECKED):
            self.browser.find_element(By.ID, Constant.RADIO_LABEL, public_rb).click()
            logging.info(f'Selected \"{Constant.PUBLIC_RADIO_BUTTON}\"')  # debug
            self.__sleep()

        # video link
        video_id = self.__get_video_id()

        # click upload
        self.browser.find_element(By.ID, Constant.DONE_BUTTON).click()
        logging.info(f"Published the video with video_id = {video_id}")
        self.__sleep()
        self.browser.get(Constant.YOUTUBE_URL)
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
        except Exception:
            logging.error('Video url not found!')
            pass

        return video_id

    def __quit(self):
        self.browser.driver.quit()
