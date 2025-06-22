#!/usr/bin/env python
# coding: utf-8

# In[67]:


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
#from datetime import date #,datetime,timedelta
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

#from datetime import date
#import datetime

import requests


#from datetime import date, timedelta
#import datetime

import sys
import os

#from datetime import date, timedelta, datetime
#from datetime import date, timedelta
#import datetime

import numpy as np
import csv
import pandas as pd
from copy import copy, deepcopy
#from datetime import date, timedelta, datetime
#import datetime
#from pandas.api.types import is_datetime64_any_dtype as is_datetime


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
######from datetime import date, timedelta, datetime
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
from openpyxl import Workbook
#import shutil


import datetime

from datetime import date,timedelta

import time


# In[68]:


def openBrowser():
    
    browser=0
    
    a=0
    #while True:
    for i in range(5):
        try:
            chromeOptions = webdriver.ChromeOptions()
            prefs = {"download.default_directory" : filesInitialDirectory}
            chromeOptions.add_experimental_option("prefs",prefs)
            chromedriver = r"C:\Users\optiware\Documents\jupyterNotebook\chromedriver.exe"
            #driver = webdriver.Chrome(executable_path=chromedriver, options=chromeOptions)
            browser = webdriver.Chrome(options=chromeOptions)
            
            #browser = webdriver.Chrome(chrome_options=options)
            
            
            #options = webdriver.ChromeOptions()
            #options = Options()           
            #prefs = {}
            #os.makedirs(downloadPath)
            #prefs["profile.default_content_settings.popups"]=0
            #prefs["download.default_directory"]=downloadPath
            #options.add_experimental_option("prefs", prefs)
            #browser = webdriver.Chrome(options=options)
            #browser = webdriver.Chrome()

            #filesInitialDirectory = 'C:\\Users\\OPTIWARE\\Documents\\jules\\Stage\\ExtractedFiles\\'
            #browser = webdriver.Chrome()
            break
        except:
            print("les drivers du navigateur Chrome semblent ne pas exister")

        a+=1
        if a <5:
            print(f"tentative numero {a+1} a echoue. Reessayons")
            continue


        sys.exit("Aucun WebDriver de navigateur ne fonctionne ou est installe")
    return browser


# In[ ]:





# In[ ]:





# In[69]:


def connectSunubet():
    
    
    url = "https://new-admin-lonase.sporty-tech.net/"
    browser.get(url)
    
    #time.sleep(5)
    
    #usrname = wait2.until( EC.element_to_be_clickable(( By.ID, usernameId)) )
    #usrname.send_keys(username)
    usernameId="inputUsername"
    #username = 'boubacar.mane' 
    username = 'boubacar.mane' 
    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    
    #browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-login/div/div[2]/form/div[1]/input").send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-login/div/div[2]/form/div[1]/input"))).send_keys(username)
    
    
    
    
    #pwd = wait2.until( EC.element_to_be_clickable(( By.ID, passwordId)) )
    #pwd.send_keys(password)
    passwordId = 'inputPassword'
    #password = "H9$J7%W3fvgr"
    password = "H9$J7%W3fvgr"
    #browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    
    #browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-login/div/div[2]/form/div[2]/input").send_keys(password)
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-login/div/div[2]/form/div[2]/input"))).send_keys(password)
    
    
    #browser.find_element(by=By.ID, value="submit").click()
    
    #browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-login/div/div[2]/form/div[3]/button").click()
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-login/div/div[2]/form/div[3]/button"))).click()
    
    #driver.find_element_by_xpath("//button[@type='submit']").click()
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/hg-header/div/div/hg-topbar-infos/div/div[2]/div[2]/button/div/span")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    
    """
    
    url = "https://new-admin-sunubet.sporty-tech.net/reports/create"
    
    browser.get(url)
    
    time.sleep(5)
    
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[3]/div[1]/button"))).click()
    
    time.sleep(0.5)
    
    """
    
    
    #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[3]/div[2]/div/hg-create-report-button/button"))).click()

    #time.sleep(0.5)
    
    
    
    
    
    
    
    global start_date
    global liste
    
    
    url = "https://new-admin-lonase.sporty-tech.net/analysis/bets"

    browser.get(url)
    
    time.sleep(5)
    
    while start_date < end_date:
        
        time.sleep(1)
        
        generateLonaseBet()

        start_date+=delta
        
    return

    #time.sleep(5)


# In[70]:


def click_masse_commune():
    global categorie_jeux
    categorie_jeux = 'Hippique masse commune internationale'
    
    browser.find_element(by=By.XPATH, value="/html/body/ng-dropdown-panel/div[2]/div[2]/div[1]/div").click()
    close_categorie()
    
def click_masse_separee():
    global categorie_jeux
    
    categorie_jeux = 'Hippique masse séparée'
    
    browser.find_element(by=By.XPATH, value="/html/body/ng-dropdown-panel/div[2]/div[2]/div[2]/div").click()
    close_categorie()
    
def click_sport():
    global categorie_jeux
    
    categorie_jeux = 'Sports'
    
    browser.find_element(by=By.XPATH, value="/html/body/ng-dropdown-panel/div[2]/div[2]/div[3]/div").click()
    close_categorie()
    
def click_virtuel():
    global categorie_jeux
    
    categorie_jeux = 'Virtuel'
                      
    browser.find_element(by=By.XPATH, value="/html/body/ng-dropdown-panel/div[2]/div[2]/div[4]/div").click()
    close_categorie()
    
def click_casino():
    global categorie_jeux
    
    categorie_jeux = 'Jeux instantanés'
    
    browser.find_element(by=By.XPATH, value="/html/body/ng-dropdown-panel/div[2]/div[2]/div[5]/div").click()
    close_categorie()
    
def click_date():
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-range/div/div/p-calendar/span/button").click()
                
def click_canal():
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-multi-select[2]/ng-select/div/div/div[2]").click()
            
def click_categorie():
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-multi-select[1]/ng-select/div/div/div[2]").click()
            
def click_canal_online():
    global type_canal
    
    type_canal = 'online'
    
    browser.find_element(by=By.XPATH, value="/html/body/ng-dropdown-panel/div[2]/div[2]/div[1]/div").click()
    close_canal()
    
def click_canal_retail():
    global type_canal
    
    type_canal = 'retail'
    
    browser.find_element(by=By.XPATH, value="/html/body/ng-dropdown-panel/div[2]/div[2]/div[2]/div").click()
    close_canal()

def pick_date():
    
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-range/div/div/p-calendar/span/button").click()

    pick_year()
    pick_month()
    pick_day()
    pick_day()
    
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-range/div/div/p-calendar/span/button").click()
    
def pick_year():
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-range/div/div/p-calendar/span/div/div[1]/div/div[1]/div/button[2]").click()
                        
    for i in browser.find_elements(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-range/div/div/p-calendar/span/div/div[2]/span"):
        #print(i.text)
        if start_date.strftime('%Y') in i.text:
            i.click()
            break

def pick_month():
    for i in browser.find_elements(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-range/div/div/p-calendar/span/div/div[2]/span"):
        #print(i.text)
        if start_date.strftime('%b') in i.text:
            i.click()
            break

def pick_day():
    for i in browser.find_elements(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-range/div/div/p-calendar/span/div/div[1]/div/div[2]/table/tbody/*/*/span[not(contains(@class, 'p-disabled'))]"):
        #print(i.text)
        if (str(0)+i.text.strip())[-2:] in start_date.strftime('%d'):
            i.click()
            #time.sleep(5)
            #i.click()
            break
    '''
    for i in browser.find_elements(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-range/div/div/p-calendar/span/div/div[1]/div/div[2]/table/tbody/*/*/span[not(contains(@class, 'p-disabled'))]"):
        #print(i.text)
        if (str(0)+i.text.strip())[-2:] in start_date.strftime('%d'):
            i.click()
            #time.sleep(5)
            #i.click()
            break
    '''
            
def close_categorie():
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-multi-select[1]/ng-select/div/span").click()

    
def close_canal():
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-multi-select[2]/ng-select/div/span").click()
    
    
def click_search():
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/div[2]/button[1]").click()

def extract_table():
    
    #print("Entering extract_table()")
    
    global excl_list
    global type_canal
    global categorie_jeux
    
    
    my_dict = {}
    for line in browser.find_elements(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[2]/div[1]/hg-betting-kpi/div[1]/div"):
        #print(line.text)
        #print(line.text.strip().split('\n'))
        #ligne = line.text.strip().replace("FCFA","").replace(" ","")
        #print(ligne)
        my_dict[line.text.strip().split('\n')[0]] = line.text.strip().split('\n')[-1].replace("FCFA","").replace(" ","")
        #print(1)
    #print(my_dict)



    # Transform the dictionary into a Pandas DataFrame
    df = pd.DataFrame([my_dict]) #,encoding='latin1'
    
    df['JOUR'] = str(start_date.strftime('%d/%m/%Y'))
    df['ANNEE'] = str(start_date.strftime('%Y'))
    df['MOIS'] = str(start_date.strftime('%m'))
    
    df['CANAL'] = type_canal
    
    df['CATEGORIE'] = categorie_jeux
    
    #print(type_canal,categorie_jeux)
                     
    #print(df)
    
    excl_list.append(df)
    
    #print(f"excl_list length after append: {len(excl_list)}")
    
    #print(11)
    
    #print(len(excl_list))
    
    
                                



    #print(df)

    

    


# In[71]:


def generateLonaseBet():
    
    global excl_list
    categorie_jeux = ''
    type_canal = ''
    excl_list = []

    categories = [click_masse_commune, click_masse_separee, click_sport, click_virtuel, click_casino]

    canaux = [click_canal_online, click_canal_retail]

    excl_list = []

    pick_date()

    for canal in canaux:

        click_canal()

        canal()

        for categorie in categories:

            click_categorie()

            categorie()

            #/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-multi-select[1]/ng-select/div/span

            #browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-betting-analysis/div[1]/div/form/hg-multi-select[1]/ng-select/div/span").click()

            click_search()

            time.sleep(2)

            extract_table()

            click_categorie()

            #time.sleep(0.5)

            categorie()

            #time.sleep(0.5)

        click_canal()

        canal()
        
    #print(len(excl_list))

    excl_merged = pd.concat(excl_list, ignore_index=True)

    excl_merged.to_csv(filesInitialDirectory+"globalLonasebet "+str(start_date)+".csv",index=False,sep=';',encoding='latin1')#,columns=["Id","Channel","State"])#,columns=['Report Date', 'Name','Total Stakes','Total Paid Win'])

    print(f"le fichier du {start_date} a bien ete telecharge")

    


# In[72]:


attempt = 0

excl_list = []

#start_date = datetime.date(2022, 8, 5)

#debut = datetime.date(2022, 5, 11)

#end_date = datetime.date(2022, 9, 1)

liste = []

delta = timedelta(days=1)

end_date = date.today()#-delta#-delta delta = timedelta(days=1) 

start_date = end_date - delta

delta = timedelta(days=1)

start_date = date(2025, 6, 15)

#end_date = start_date+delta

#end_date = date(2024, 1, 1)#datetime.date(2024, 1, 1)

#debut = datetime.date(2022, 9, 6)

filesInitialDirectory = r"K:\DATA_FICHIERS\LONASEBET\GLOBAL\\"

debut1 = start_date 
fin1 = end_date-delta

#browser=openBrowser()

#browser.maximize_window()

#connectSunubet()

#""" 
for i in range(10):
    try:
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectSunubet()


        #time.sleep(10)

        browser.quit()


        break

    except:

        #attachments = []

        try:
            browser.quit()
        except:
            print("nous n'avons pas pu quitte le navigateur precedemment ouvert")

        print(f"la tentative numero {i+1} a echoue")
        print("Nous allons reessayer")

        #continue
    if i == 9 :
        sys.exit(f"Impossible d'executer ce programme malgre 10 tentatives")

#browser = openBrowser()

#"""


# In[73]:


d = dir()

#You'll need to check for user-defined variables in the directory
for obj in d:
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


#import gc
#gc.collect()


# In[ ]:




