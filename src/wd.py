#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only

import os, time, getpass, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# change to your workday URL
URL = 'https://wdX.myworkday.com/XXXXXXX/'

def wd_refresh(driver):
    url = URL
    driver.get(url)
    time.sleep(30)

def verify(driver):
    t = driver.find_elements(By.TAG_NAME, 'button')
    for i in t:
        if i.text == 'Time':
            t = i
            break
    if t.text != 'Time':
        print('could not find the Time app')
        driver.quit()
    t.click()
    time.sleep(10)
    d = driver.find_elements(By.TAG_NAME, 'div')
    for i in d:
        if (i.text.count('\n') > 0):
            continue
        if (i.text.startswith('This Week') or i.text.startswith('Last Week')):
            print(i.text)
        if (i.text.startswith('Checked In at') or i.text.startswith('Checked Out at')):
            print(i.text)
            break

def do_punch(driver, out, comment):
    t = driver.find_elements(By.TAG_NAME, 'button')
    for i in t:
        if i.text == 'Time':
            t = i
            break
    if t.text != 'Time':
        print('could not find the Time app')
        driver.quit()
    t.click()
    time.sleep(10)
    b = driver.find_elements(By.TAG_NAME, 'button')
    for i in b:
        if out:
            if (i.text == 'Check Out'):
                i.click()
                break
        else:
            if (i.text == 'Check In'):
                i.click()
                break
    time.sleep(10)
    if out:
        if comment:
            driver.find_element(By.CSS_SELECTOR, "textarea[data-automation-id='textAreaField']").send_keys(comment)
    time.sleep(10)
    b = driver.find_elements(By.TAG_NAME, 'button')
    for i in b:
        if (i.text == 'OK'):
            i.click()
            break
    time.sleep(5)
    if out:
        print("punched out.")
    else:
        print("punched in..")
    wd_refresh(driver)
    verify(driver)

def wd_login(login, pw, comment, hours):
    url = URL
    o = Options()
    o.binary_location = '/usr/bin/chromium-browser'
    o.add_argument('--disable-gpu')
    o.add_argument('--headless')
    o.add_argument('--incognito')
    o.add_argument('--disable-extensions')
    ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
    o.add_argument(f'--user-agent={ua}')
    s = Service(os.path.expanduser('/usr/bin/chromedriver'))
    driver = webdriver.Chrome(service=s, options=o)
    driver.set_page_load_timeout(60)
    driver.get(url)
    time.sleep(7)
    driver.find_element(By.NAME, 'loginfmt').send_keys(login)
    driver.find_element(By.ID, 'idSIButton9').click()
    time.sleep(5)
    driver.find_element(By.NAME, 'passwd').send_keys(pw[0])
    driver.find_element(By.ID, 'idSIButton9').click()
    del pw
    time.sleep(7)
    sign = driver.find_element(By.ID, 'idRichContext_DisplaySign').text
    print(f'display sign: {sign}')
    time.sleep(30)
    driver.find_element(By.ID, 'idSIButton9').click()
    time.sleep(7)
    t = driver.find_elements(By.TAG_NAME, 'a')
    for i in t:
        if i.text == 'Skip':
            t = i
            break
    if t.text != 'Skip':
        print('could not find the Skip button')
        driver.quit()
    t.click()
    time.sleep(10)

    wd_refresh(driver)
    time.sleep(10)

    do_punch(driver, False, '')

    i = 0
    cycles = hours * 3600 / 120
    print(f'now sleep for {hours} hours..')
    while True:
        try:
            time.sleep(90)
            i += 1
            wd_refresh(driver)
            if i > cycles:
                break
        except Exception as e:
            print(e)

    do_punch(driver, True, comment)
    driver.quit()

def main():
    comment = ''
    hours = 8
    argc = len(sys.argv)
    if argc == 3:
        hours = int(sys.argv[1])
        comment = sys.argv[2]
    if argc == 2:
        hours = int(sys.argv[1])
    os.chdir(os.path.expanduser('~'))
    print()
    print(f'will check out with comment: {comment}')
    login = input('Login: ')
    pw = [getpass.getpass('Password: ')]
    wd_login(login, pw, comment, hours)

if __name__ == '__main__':
    main()
