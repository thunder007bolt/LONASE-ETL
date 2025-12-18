#!/usr/bin/env python
# coding: utf-8

# In[1]:


from curses import KEY_ENTER
from unicodedata import name
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import calendar

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.date_utils import sleep

options = Options()
options.headless = True

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.keys import Keys

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import date  # ,datetime,timedelta
import calendar

from selenium.webdriver.chrome.options import Options

from curses import KEY_ENTER
from unicodedata import name
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
# from datetime import date
# import datetime


# from datetime import date, timedelta
# import datetime

import sys
import os

from datetime import date, timedelta, datetime
import datetime

import numpy as np
import csv
import pandas as pd
from copy import copy, deepcopy
# from datetime import date, timedelta, datetime
# import datetime
# from pandas.api.types import is_datetime64_any_dtype as is_datetime


from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from html.parser import HTMLParser
from email.mime.multipart import MIMEMultipart
import smtplib, os, sys
import mimetypes

from email import encoders

from selenium.webdriver.support.ui import WebDriverWait

import numpy as np
import csv
import pandas as pd
from copy import copy, deepcopy
from datetime import date, timedelta, datetime
import datetime

import zipfile
import shutil

import os
import sys

import warnings

warnings.simplefilter("ignore")

import os
import glob

# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 12:51:38 2022

@author: RAWANE
"""
import pandas as pd
import numpy as np
import win32com.client
import os
import re
import os
print("Dossier courant :", os.getcwd())

# import shutil


# In[ ]:


# In[2]:
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
def openBrowser():
    chromeOptions = Options()
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("--disable-dev-shm-usage")
    chromeOptions.add_argument('log-level=3')

    prefs = {"download.default_directory": r"K:\DATA_FICHIERS\ZETURF\\"}
    chromeOptions.add_experimental_option("prefs", prefs)

    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            service = ChromeService(ChromeDriverManager().install())
            browser = webdriver.Chrome(service=service, options=chromeOptions)
            print("ChromeDriver initialisé avec succès.")
            return browser
        except Exception as e:
            print(f"Échec (tentative {attempt + 1}/{max_attempts}): {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(4)
            else:
                print("Échec final. Arrêt du script.")

    return browser


# In[ ]:


# In[3]:


def connectZeturf():
    url = "https://ztat-extranet.zeturf.com/login"
    browser.get(url)

    # time.sleep(5)

    # usrname = wait2.until( EC.element_to_be_clickable(( By.ID, usernameId)) )
    # usrname.send_keys(username)
    usernameId = "inputUsername"
    username = 'LONASE'

    # browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    WebDriverWait(browser, timeout=10 * 9).until(EC.element_to_be_clickable((By.ID, usernameId))).send_keys(username)

    # pwd = wait2.until( EC.element_to_be_clickable(( By.ID, passwordId)) )
    # pwd.send_keys(password)
    passwordId = 'inputPassword'
    password = "LSFALudWin2022@"

    # browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    WebDriverWait(browser, timeout=10).until(EC.element_to_be_clickable((By.ID, passwordId))).send_keys(password)

    # browser.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div/div/div/div[2]/div/form/input[2]").click()
    WebDriverWait(browser, timeout=10).until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div[1]/div/div/div/div/div/div/div[2]/div/form/input[2]"))).click()

    # driver.find_element_by_xpath("//button[@type='submit']").click()
    time.sleep(5)

    print("la connection a la plateforme est un succes")

    generateZeturfFiles()

    """
    for i in range(3):
        try:
            generateZeturfFiles()
            #except SystemExit:
                #print("Program terminated with SystemExit exception")
                #sys.exit(" ")
            break
        except:
            print("nous avons rencontre un soucis, nous allons reessayer")
            #tryGenFiles()
            #continue
        if i ==2:
            sys.exit("Impossible malgre 3 tentatives")

    """

    # tryGenFiles()

    # for i in range(15):

    # generateAfitechFiles()


# In[4]:


def generateZeturfFiles():
    url = "https://ztat-extranet.zeturf.com/lonase/stats"

    browser.get(url)

    # time.sleep(3)

    # driver.find_element_by_class_name("form-control").click()
    # WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.CLASS_NAME, "form-control"))).click()

    # frmc = wait2.until( EC.element_to_be_clickable(( By.CLASS_NAME,"form-control")) )
    # frmc.click()
    # time.sleep(3)

    # WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "//option[@value='OperationHistory']"))).click()

    # driver.find_element_by_xpath("//option[@value='OperationHistory']").click()
    global generated

    global start_date

    # start_date = datetime.date(2022, 1, 1)
    # end_date = datetime.date(2022, 2, 1)
    # delta = datetime.timedelta(days=1)

    # for day in range(start_date,end,1):
    global i
    global excl_list

    # for i in glob.glob(f'C:\\Users\\CFAC\\Downloads\\Extranet ZEturf - prod*'):
    # os.remove(i)

    while start_date < end_date:

        for i in glob.glob(filesInitialDirectory + 'Extranet ZEturf - prod*'):
            os.remove(i)

        # print(start_date)

        start = str(start_date.strftime('%d/%m/%Y'))

        # print(start)

        debut = browser.find_element(by=By.ID, value="date_selector_form_ui_from")
        # debut.click()
        # debut.clear()
        # debut.send_keys(start) #+ Keys.ENTER
        """
        debut.send_keys(str('09'))
        time.sleep(5)
        debut.send_keys(str(19))
        time.sleep(5)
        debut.send_keys(str(2022))
        time.sleep(5)
        """
        debut.send_keys(start)
        time.sleep(1)

        fin = browser.find_element(by=By.ID, value="date_selector_form_ui_to")
        fin.click()
        fin.clear()
        fin.send_keys(start)  # + Keys.ENTER
        time.sleep(1)

        browser.find_element(by=By.ID, value="date_selector_form_ui_submit").click()

        # time.sleep(15)

        # downloadbut = browser.find_elements(by=By.XPATH, value='//*[@id="statsDatatable_wrapper"]/div/button[2]')[-1]

        # print(downloadbut.text)

        # downloadbut.click()

        WebDriverWait(browser, timeout=60).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]')))

        # time.sleep(60)
        # WebDriverWait(browser,timeout=120).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]/span'))).click()
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # time.sleep(3)
        WebDriverWait(browser, timeout=120).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]'))).click()

        # WebDriverWait(browser,timeout=60).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]'))).click()
        # WebDriverWait(browser,timeout=60).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/button[2]/span'))).click()

        # WebDriverWait(browser,timeout=60).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]'))).click()
        # browser.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]").click()

        # browser.find_elements(by=By.XPATH, value='//*[@id="statsDatatable_wrapper"]/div/button[2]')[-1].click()

        """
        for i in range(10):
            try:
                #browser.find_elements(by=By.XPATH, value='//*[@id="statsDatatable_wrapper"]/div/button[2]')[-1].click()
                browser.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]").click()

                break
            except:
                print("error")
                continue
        break
        """
        # WebDriverWait(browser,timeout=60).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]"))).click()
        # //*[@id="statsDatatable_wrapper"]/div/button[2]
        # WebDriverWait(browser,timeout=60).until( EC.element_to_be_clickable(( By.XPATH, '//*[@id="statsDatatable_wrapper"]/div/button[2]'))).click()
        # WebDriverWait(browser,timeout=60).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]'))).click()
        """
        timer = 15
        while timer>0:
            time.sleep(5)
            timer = timer - 5
            try:
                #WebDriverWait(browser,timeout=60).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]'))).click()
                browser.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div/div/div[2]/div/div/button[2]").click()
                break
            except:
                #print(i)
                print("le boutton n'a pas pu etre clicke")
                continue
        """

        timer = 30 * 2

        while timer >= 0:
            time.sleep(1)
            timer -= 1
            p = glob.glob(filesInitialDirectory + 'Extranet ZEturf - prod*')
            if len(p) > 0:
                # print(p[0])
                """

                filename = p[0].split("\\")[-1]
                #shutil.move(path+filename,filesInitialDirectory+filename)
                shutil.move(path+filename,filesInitialDirectory+"Extranet ZEturf - prod-"+str(start_date)+".csv")
                """
                df = pd.read_csv(p[0], delimiter=";")
                if len(df) == 0:
                    break

                enjeuxVertical = 0
                enjeuxVertical = browser.find_element(by=By.XPATH,
                                                      value="/html/body/div[1]/div[1]/div[1]/div[3]/div[2]/table/tbody/tr/td[1]").text
                margeVertical = 0
                margeVertical = browser.find_element(by=By.XPATH,
                                                     value="/html/body/div[1]/div[1]/div[1]/div[3]/div[2]/table/tbody/tr/td[5]").text

                Paris = df['Paris'][0]
                # Paris = str(start_date)
                start = str(start_date)

                # print(f"paris = {Paris}, margeVertical={margeVertical}, enjeuxVertical={enjeuxVertical}")
                # print(df.columns)

                # filename = "Extranet ZEturf - prod_"+str(start_date)+".csv"

                # df.append({'Paris':Paris,'Enjeux':enjeuxVertical,'Marge':margeVertical}, ignore_index=True)
                # df.loc[len(df.index)] = ["", "", "",str(Paris), str(enjeuxVertical), "",str(margeVertical), ""]
                # print(f"heyhey {start}")
                df.loc[len(df.index)] = ["", "", "", str(Paris), str(enjeuxVertical), "", str(margeVertical), start]

                df["Course"] = [str(i).replace(";", ",") for i in df["Course"]]

                df = df.replace(np.nan, '')
                df = df.astype(str)
                df['Date du départ'] = start_date.strftime('%d/%m/%Y')

                df['Date du dÃ©part'] = start_date.strftime('%d/%m/%Y')

                df['Annulations'] = ''

                if os.path.exists(filesInitialDirectory + "ZEturf " + str(start_date) + ".csv"):
                    os.remove(filesInitialDirectory + "ZEturf " + str(start_date) + ".csv")

                df.to_csv(filesInitialDirectory + "ZEturf " + str(start_date) + ".csv", sep=";", encoding='utf8',
                          index=False)

                excl_list.append(df)

                print(f"le fichier de la plateforme ZEturf du {start_date} a bien ete telecharge et deplace")

                start_date += delta

                break
        if timer < 0:
            print("Le chargement est anormalement long, nous allons recommencer")
            continue

        # start_date+=delta

    print("tous les fichiers ont bien ete telecharge")

    for i in glob.glob(filesInitialDirectory + 'Extranet ZEturf - prod*'):
        os.remove(i)


# In[5]:


excl_list = []
# start_date = datetime.date(2022, 8, 5)


# debut = datetime.date(2022, 5, 11)


delta = datetime.timedelta(days=1)
# """
end_date = datetime.date.today()
delta = datetime.timedelta(days=1)
start_date = end_date - delta

# start_date = datetime.date(2025, 4, 4)
# end_date = datetime.date(2025, 4, 6)
# """
delta = datetime.timedelta(days=1)

# start_date = datetime.date(2025, 3, 1)
# end_date = datetime.date(2025, 4, 1)
# end_date = start_date+delta
# debut = datetime.date(2022, 9, 6)


# path = "C:\\Users\\OPTIWARE-ENTERPRISE\\Downloads\\" CFAC
path = "C:\\Users\\CFAC\\Downloads\\"
# filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\'
# filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'
# filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\zeturf\\'
filesInitialDirectory = r"K:\DATA_FICHIERS\ZETURF\\"

generated = False
debut1 = start_date
fin1 = end_date - delta

# browser=openBrowser()
# connectZeturf()


# """
for i in range(10):
    try:

        browser = openBrowser()

        # browser.implicitly_wait(20)
        # browser.maximize_window()

        connectZeturf()

        time.sleep(1)

        browser.quit()

        break

    except:

        # attachments = []

        try:
            browser.quit()
        except:
            print("nous n'avons pas pu quitte le navigateur precedemment ouvert")

        print(f"la tentative numero {i + 1} a echoue")
        print("Nous allons reessayer")

        # continue
    if i == 9:
        sys.exit(f"Impossible d'executer ce programme malgre 10 tentatives")

# browser = openBrowser()

# """


# In[6]:


# exec(open("C:\Batchs\scripts_python\chargements\charge_zeturf.py").read())


# In[7]:


import gc

gc.collect()

# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:




