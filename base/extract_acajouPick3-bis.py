#!/usr/bin/env python
# coding: utf-8

# In[1]:


from curses import KEY_ENTER
from unicodedata import name
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from soupsieve import select

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC






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
from datetime import date #,datetime,timedelta
import calendar





from selenium.webdriver.chrome.options import Options

from curses import KEY_ENTER
from unicodedata import name
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from soupsieve import select

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

from datetime import date, timedelta#, datetime
import datetime

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
from datetime import date, timedelta#, datetime
import datetime

import zipfile
import shutil

import os
import sys


import warnings
warnings.simplefilter("ignore")


import os
import glob


#from datetime import datetime


# In[2]:


from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from datetime import date,timedelta #,datetime
import calendar
import shutil
#import yaml
import time
import os
import re


# In[3]:


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





# In[4]:


def connectPick3Acajou():
    
    url = "https://cms.acajou.sn/Account/Login"
    
    browser.get(url)
    
    #time.sleep(5)
    #driver.maximize_window()
    #driver.refresh()
    
    usernameId = 'Input_Email'
    username = 'bmane'
    #browser.find_element_by_id(usernameId).send_keys(username)
    
    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
    
    
    passwordId = 'Input_Password'
    password = '2L*pIF9s'
    
    #browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.ID, passwordId))).send_keys(password)
    
    
    #submit_buttonId = 'logon'
    #browser.find_element_by_id(submit_buttonId).click()
    #browser.find_element(by=By.ID, value=submit_buttonId).click()
    
    #browser.find_element(by=By.XPATH, value='/html/body/div/main/div/div[2]/div/form/div[3]/div[2]/button').click()
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/main/div/div[2]/div/form/div[3]/div[2]/button"))).click()
    
    
    time.sleep(5)

    print("la connexion a la plateforme ACAJOU Pick3 est un succes")
    
    generatePick3AcajouFiles()
    
    
    
    
    
    
    
    #generateParifootFiles()
    


# In[5]:


def generatePick3AcajouFiles():
    #print('hey')
    
    #for i in glob.glob(f'C:\\Users\\CFAC\\Downloads\\Accounting*csv'): 
            #os.remove(i)
    
    url = 'https://cms.acajou.sn/Accounting/AccountingReport'
    
    browser.get(url)
    
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.NAME, "game"))).send_keys("PICKTHREE")
    
    global start_date
    #global end_date
    
    #start_date = datetime.date(2022, 2, 27)
    #end_date = datetime.date(2022, 3, 2)
    #delta = datetime.timedelta(days=1)
    while start_date < end_date:
        
        for i in glob.glob(filesInitialDirectory+'Accounting*csv'): 
            os.remove(i)

        
        #lastMonth = date(start_date.year, start_date.month, calendar.monthrange(start_date.year, start_date.month)[1])
        
        #if end_date < lastMonth :
            
            #lastMonth = end_date - delta
        
        #date = 0
        #print(str(start_date.strftime('%m/%d/%Y')))
        print(str(start_date.strftime('%Y/%m/%d'))+" 00:00:00"+" - "+str((start_date).strftime('%Y/%m/%d'))+" 23:59:59")
        
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.NAME, "dateCreated"))).clear()
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.NAME, "dateCreated"))).send_keys(str(start_date.strftime('%Y/%m/%d'))+" 00:00:00"+" - "+str((start_date).strftime('%Y/%m/%d'))+" 23:59:59")
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.NAME, "dateCreated"))).send_keys(Keys.ENTER)
        
        
        #WebDriverWait(browser,timeout=15).until( EC.text_to_be_present_in_element_attribute(( By.NAME, "dateCreated"))).send_keys(Keys.ENTER)
        
        #locator = (by=By.ID, value="results-jackpot_processing")
        nom = "none"
        
        #WebDriverWait(browser,timeout=15).until(EC.text_to_be_present_in_element_attribute((by=By.ID, value="results-jackpot_processing")))
        
        WebDriverWait(browser,timeout=15).until( EC.text_to_be_present_in_element_attribute(( By.ID, "results-jackpot_processing"),"style", nom))
        
        #WebDriverWait(browser,timeout=15).until( EC.text_to_be_present_in_element_attribute())
        
        # /html/body/div[1]/div[1]/section[2]/div/div/div/div/div[3]/button
        
        time.sleep(1)
        
        
        WebDriverWait(browser,timeout=60).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[1]/div[1]/section[2]/div/div/div/div/div[3]/button"))).click()
        
        try:
            WebDriverWait(browser,timeout=60*5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[1]/div[1]/section[2]/div/div/div/div/div[3]/button")))
        except:
            pass
        
        timer = 60*2
        while timer>=0:
            time.sleep(2)
            timer-=2
            p=glob.glob(filesInitialDirectory+'Accounting*csv') 
            if len(p)>0:
                
                #final_file = "acajouDigitain"+str(start_date)+".csv"
                final_file = "Listing_Tickets_Pick3 "+str(start_date.strftime('%Y%m%d'))+'_'+str((start_date).strftime('%Y%m%d'))+".csv" #20221030
                
                #dest = os.path.join(filesInitialDirectory,final_file)
                #os.renames(src,dest)
                #shutil.move(p[0],dest)
                df = pd.read_csv(p[0],delimiter=",")
                
                #print(df['Date Created'])
                
                df = df.replace(np.nan, '')
                df=df.astype(str)
                
                """
                df['Date Created'] = [i[:10] for i in df['Date Created'] ]
                
                print(df['Date Created'])
                
                
                df['Date Created'] = [str(datetime.strptime(str(i.rstrip(" AM").rstrip(" PM")), "%m-%d-%Y %H:%M:%S"))[:10] for i in df['Date Created'] ]
                """
                format = '%Y-%m-%d'
                df['Date Created'] = [datetime.strptime(i[:10], format).strftime('%d/%m/%Y') for i in df['Date Created'] ]
                
                df['Produit'] = str("Pick3")

                if os.path.exists(filesInitialDirectory+final_file):
                    os.remove(filesInitialDirectory+final_file)
        
                
                df.to_csv(filesInitialDirectory+final_file,sep=';', index=False,encoding='utf8',columns=["Date Created","Ticket ID","Msisdn","Purchase Method","Collection","Gross Payout","Status","Produit"])
                #excl_list.append(df[["Date Created","Ticket ID","Msisdn","Purchase Method","Collection","Gross Payout","Status"]])
                print(f"le fichier de la plateforme PICK3 du {start_date} au {start_date} a bien ete telecharge")
                start_date=start_date+delta
                break
        if timer < 0:
            print("le fichier n'a pas pu etre telecharge")
            continue
    
    print("tous les fichiers ont bien ete telecharge")
    
    for i in glob.glob(filesInitialDirectory+'Accounting*csv'): 
        os.remove(i)
    
    
    
                
        
        
                #break
        
        


# In[6]:


from datetime import date
import datetime
from datetime import date, timedelta
from datetime import datetime


excl_list = []
#start_date = datetime.date(2022, 2, 1)

#debut = datetime.date(2022, 5, 11)

#end_date = datetime.date(2022, 2, 4)

delta = timedelta(days=1)
#start_date = datetime.date(2024, 11, 29)
#end_date = datetime.date(2024, 12, 1)
#end_date = date.today()
#end_date = datetime.date(2022, 5, 7)
#"""
delta = timedelta(days=1) #- delta


end_date = date.today() #- delta
start_date = end_date - delta
#"""
#start_date = date(2024, 11,29)
#end_date = date(2024, 12, 1)


#start_date = end_date - 2*delta
#end_date = datetime.date.today() - delta
#start_date = end_date - delta

#end_date = start_date+delta


#start_date = datetime.date(2024, 11, 29) 
 #end_date = start_date + 2delta 
#end_date = datetime.date(2024, 12, 1)

#end_date = start_date + delta

#start_date = datetime.date(2023, 1, 1)
#end_date = datetime.date(2023, 2, 1)

#path = "C:\\Users\\CFAC\\Downloads\\"
#filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\AcajouParifoot\\'
filesInitialDirectory = r"K:\DATA_FICHIERS\ACAJOU\PICK3\\"

#debut = start_date
#fin = end_date-delta

#browser=openBrowser()
#connectParifoot()

#browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()
#connectDigitainAcajou()


#'''

for i in range(10):
    try:
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectPick3Acajou()

        
        time.sleep(1)
        
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
        break
        #sys.exit(f"Impossible d'executer ce programme malgre 10 tentatives")




#'''



#browser = openBrowser()
#connectParifoot()


# In[7]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_DigitainAcajou.py").read())


# In[8]:


import gc
gc.collect()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




