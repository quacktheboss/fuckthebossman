#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only

import os
import errno
import time
import tempfile
import getpass
import re
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

cookies = {}

def session(pw, login):
    global cookies
    url = 'https://login.microsoftonline.com'
    o = Options()
    o.binary_location = '/usr/bin/chromium-browser'
    o.add_argument('--disable-gpu')
    o.add_argument('--headless')
    #o.add_argument('--remote-debugging-port=9222')
    #o.add_argument('--remote-debugging-address=IP')
    o.add_argument('--window-size=1280,800')
    o.add_argument('--incognito')
    o.add_argument('--disable-extensions')
    ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    o.add_argument(f'--user-agent={ua}')
    s = Service(os.path.expanduser('/usr/bin/chromedriver'))
    driver = webdriver.Chrome(service=s, options=o)
    driver.get(url)
    time.sleep(2)
    driver.find_element(By.NAME, 'loginfmt').send_keys(login)
    driver.find_element(By.ID, 'idSIButton9').click()
    time.sleep(5)
    driver.find_element(By.NAME, 'passwd').send_keys(pw[0])
    driver.find_element(By.ID, 'idSIButton9').click()
    del pw
    time.sleep(5)
    sign = driver.find_element(By.ID, 'idRichContext_DisplaySign').text
    print(f'display sign: {sign}')
    time.sleep(30)
    driver.find_element(By.ID, 'idSIButton9').click()
    time.sleep(7)
    while True:
        try:
            url = 'https://developer.microsoft.com/en-us/graph/graph-explorer'
            driver.get(url)
            time.sleep(5)
            original_window = driver.current_window_handle
            t = driver.find_elements(By.TAG_NAME, 'button')
            for i in t:
                for attr in i.get_property('attributes'):
                    if attr['name'] == 'aria-label' and attr['value'] == 'Sign in':
                        #print('clicking on "Sign in" button..')
                        i.click()
                        time.sleep(5)
            another_window = list(set(driver.window_handles) - {driver.current_window_handle})
            if another_window:
                driver.switch_to.window(another_window[0])
            t = driver.find_elements(By.TAG_NAME, 'div')
            for i in t:
                if i.text == login:
                    #print('clicking on account button..')
                    i.click()
                    break
            driver.switch_to.window(original_window)
            time.sleep(5)
            t = driver.find_elements(By.TAG_NAME, 'span')
            for i in t:
                if 'Access token' in i.text:
                    #print('clicking on access token span button..')
                    i.click()
                    break
            t = driver.find_elements(By.TAG_NAME, 'div')
            for i in t:
                for attr in i.get_property('attributes'):
                    if attr['name'] == 'id' and attr['value'] == 'access-token':
                        with open('/tmp/graph' , 'w') as f:
                            #print('writing token to file...')
                            f.write(str(i.text))
                        break
            time.sleep(300)
        except StaleElementReferenceException as e:
            time.sleep(10)
        except Exception as e:
            print(e)
            time.sleep(10)
    return

def main():
    os.chdir(os.path.expanduser('~'))
    login = input('Login: ')
    pw = [getpass.getpass('Password: ')]
    session(pw, login)
    return

if __name__ == '__main__':
    main()
