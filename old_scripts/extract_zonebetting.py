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








# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 19:52:56 2021

@author: JULES
"""

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



import pandas as pd
#import numpy as np
import win32com.client
#import win32com.client as win32
import os
from datetime import date,timedelta


import pandas as pd
#import numpy as np
import win32com.client
#import win32com.client as win32
import os
from datetime import date,timedelta



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





# In[ ]:





# In[4]:


def connectToZoneBetting():
    #print()
    zoneBetingLogin = "LONASE"
    zoneBetingPassword = "2#B@+Dy%"
    url = "https://premierbetzone.com/admin-console/login"
    
    browser.get(url)
    #time.sleep(5)
    
    #browser.find_element(by=By.ID, value = "login").send_keys(zoneBetingLogin)
    WebDriverWait(browser,timeout=15*10).until( EC.element_to_be_clickable(( By.ID, "login"))).send_keys(zoneBetingLogin)
    
    
    #/html/body/div/div[2]/div/form/div[2]/div/input
    #browser.find_element(by=By.ID, value = "password").send_keys(zoneBetingPassword)
    WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/div[2]/div/form/div[2]/div/input"))).send_keys(zoneBetingPassword)
    
    WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//form/button[@type='submit']"))).click()
    
    #time.sleep(15)

    #print("La connexion a la plateforme est un succes")
    
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        WebDriverWait(browser,timeout=10*4).until( EC.presence_of_element_located(( By.XPATH, "/html/body/div/div[2]/nav[1]/div/div/div[3]/div[1]")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    

    #browser.get("https://premierbetzone.com/admin-console/statistics/profits/BettingShopsOverall")
    
   #driver.maximize_window()
   #driver.find_element_by_id(usernameId).send_keys(username)
   #driver.find_element_by_id(passwordId).send_keys(password)
   #driver.find_element_by_xpath("//input[@type='password']").send_keys(password)
   
   #driver.find_element_by_xpath("//form/button[@type='submit']").click()
   #driver.get("https://premierbetzone.com/admin-console/statistics/profits/BettingShopsOverall")
    
    
    #login_zoneBetting(driver,, "login", zoneBetingLogin, "password", zoneBetingPassword,'daily',0,0) # 

    #generateZoneBetting()
    
    #return
    
    for i in range(3):
        try:
            generateZoneBetting()
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
    
    
    excl_merged = pd.concat(excl_list, ignore_index=True)
    
    if debut1<fin1:
    
        excl_merged.to_csv(filesInitialDirectory+"merge\\mergeZone_Betting"+str(debut1)+"_"+str(fin1)+".csv" , index=False,sep=';',encoding='utf8')
    
    '''
    for i in range(3):
        try:
            #generateParifootFiles(i)
            generateZoneBetting()
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
    '''


# In[5]:


def generateZoneBetting():
    
    url = "https://premierbetzone.com/admin-console/statistics/profits/BettingShopsOverall"
    
    browser.get(url)
    
    global start_date
    global excl_list
    #global delta

    #print("we did it")
    
    
    
    while start_date < end_date:
        
        #browser.get(url)
        
        """
        for filename in os.listdir(path): 
            if filename.endswith('.xls') and "BettingShopsOverall" in filename :
                os.remove(path+filename)
        """
        
        for i in glob.glob(filesInitialDirectory+'*BettingShopsOverall*xl*'): 
            os.remove(i)
        

        #time.sleep(10)
        
        dateFrom = WebDriverWait(browser,timeout=10*6).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='inputVisibilityFrom']//input[@name='date']")))
        time.sleep(1)
        dateFrom.click()
        #time.sleep(1)
        dateFrom.clear()
        #time.sleep(1)
        #time.sleep(7)
        #Keys.ENTER
        dateFrom.send_keys(str(start_date)+" 00:00")
        
        debut = "From: "+str(start_date)+" 00:00"
        
        #time.sleep(1)
        #time.sleep(7)
        dateFrom.send_keys(Keys.ENTER)

        time.sleep(1)


        dateTo = WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@name='date_time_to']//div[@id='inputVisibilityFrom']//input[@name='date']")))
        time.sleep(1)
        dateTo.click()
        #time.sleep(1)
        dateTo.clear()
        #time.sleep(1)
        #time.sleep(5)
        dateTo.send_keys(str(start_date)+" 23:59")
        
        fin = "To: "+str(start_date)+" 23:59"
        
        #time.sleep(1)
        dateFrom.send_keys(Keys.ENTER)



        """
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']"))).click()

        #time.sleep(25*2)
        timer = 60+50

        while timer>=0:
            time.sleep(10)
            timer-=10
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
            if  "loading..." not in browser.find_element(by=By.ID, value="reports-modal").text and "wait" not in browser.find_element(by=By.ID, value="reports-modal").text:
                break
        if timer<0:
            #btn btn-warning btn-sm
            #browser.find_element(by=By.CLASS_NAME, value="btn btn-warning btn-sm").click()
            # /html/body/div/div[5]/div[2]/div/button
            browser.find_element(by=By.XPATH, value ="/html/body/div/div[5]/div[2]/div/button").click()
            # /html/body/div/div[5]/div[2]/div/button
        
            print("Le chargement est anormalement long, nous allons recommencer")
            continue
        
        time.sleep(3)
        
        
        
        
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']"))).click()

        #time.sleep(25*2)
        timer = 60+50

        while timer>=0:
            time.sleep(10)
            timer-=10
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
            if  "loading..." not in browser.find_element(by=By.ID, value="reports-modal").text and "wait" not in browser.find_element(by=By.ID, value="reports-modal").text:
                break
        if timer<0:
            #btn btn-warning btn-sm
            #browser.find_element(by=By.CLASS_NAME, value="btn btn-warning btn-sm").click()
            # /html/body/div/div[5]/div[2]/div/button
            browser.find_element(by=By.XPATH, value ="/html/body/div/div[5]/div[2]/div/button").click()
            # /html/body/div/div[5]/div[2]/div/button
        
            print("Le chargement est anormalement long, nous allons recommencer")
            continue
        
        time.sleep(3)
        
        
        """
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']"))).click()
        
        #time.sleep(20)
        time.sleep(2)

        try:
            #print()
            #WebDriverWait(browser,timeout=120).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']")))
            
            #WebDriverWait(browser,timeout=120).until( EC.NoSuchElementException(( By.XPATH, "//button[@class='btn btn-warning btn-sm']")))
            
            WebDriverWait(browser,timeout=10*9).until( EC.invisibility_of_element(( By.XPATH, "//button[@class='btn btn-warning btn-sm']")))
            
            # btn btn-warning btn-sm
            # btn btn-warning btn-sm
        except:
            #print()
            print("Le chargement est anormalement long, nous allons recommencer")
            
            WebDriverWait(browser,timeout=2).until( EC.element_to_be_clickable(( By.XPATH, "//button[@class='btn btn-warning btn-sm']"))).click()
            time.sleep(1)
            browser.get(url)
            
            continue
        
        time.sleep(2)  
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']")))
        
        #time.sleep(10)
        
        #print("hi")
        
        #break
        
        
        
        
        
        
        '''
        time.sleep(2)
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']"))).click()
        
        #time.sleep(20)
        time.sleep(2)

        try:
            #print()
            #WebDriverWait(browser,timeout=120).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']")))
            
            WebDriverWait(browser,timeout=10*9).until( EC.invisibility_of_element(( By.XPATH, "//button[@class='btn btn-warning btn-sm']")))
            
            
            
            
        except:
            #print()
            print("Le chargement est anormalement long, nous allons recommencer")
            
            WebDriverWait(browser,timeout=2).until( EC.element_to_be_clickable(( By.XPATH, "//button[@class='btn btn-warning btn-sm']"))).click()
            time.sleep(1)
            browser.get(url)
            
            continue
            
        time.sleep(2)
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']")))   
        #time.sleep(10)
        '''
        
        
        
        
        
        
        
        
        
        
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//div[@class='form-group d-flex flex-row align-items-end']//button[@class='btn download_btn btn-primary']"))).click()
        
        #time.sleep(20)
        time.sleep(2)
        
        try:
            #print()
            #WebDriverWait(browser,timeout=120).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']")))
            
            WebDriverWait(browser,timeout=10*9).until( EC.invisibility_of_element(( By.XPATH, "//button[@class='btn btn-warning btn-sm']")))
            
        except:
            #print()
            print("Le chargement du fichier est anormalement long, nous allons recommencer")
            
            WebDriverWait(browser,timeout=2).until( EC.element_to_be_clickable(( By.XPATH, "//button[@class='btn btn-warning btn-sm']"))).click()
            time.sleep(1)
            browser.get(url)
            
            continue
            
        
        
        
        
        
        
        
        
        
        
        
        '''
        
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//div[@class='form-group d-flex flex-row align-items-end']//button[@class='btn download_btn btn-primary']"))).click()
        
        #time.sleep(20)
        time.sleep(2)
        
        try:
            #print()
            #WebDriverWait(browser,timeout=120).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']")))
            
            WebDriverWait(browser,timeout=10*3).until( EC.invisibility_of_element(( By.XPATH, "//button[@class='btn btn-warning btn-sm']")))
            
        except:
            #print()
            print("Le chargement est anormalement long, nous allons recommencer")
            
            WebDriverWait(browser,timeout=2).until( EC.element_to_be_clickable(( By.XPATH, "//button[@class='btn btn-warning btn-sm']"))).click()
            time.sleep(1)
            browser.get(url)
            
            continue
        
        '''
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        WebDriverWait(browser,timeout=30).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//button[@type='submit']")))   
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/div[2]/div[2]/div/div[2]/form/div/div[5]/button")))   
        time.sleep(2)
        
        


        """
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='main-view']//form//div[@class='form-row']//div[@class='form-group d-flex flex-row align-items-end']//button[@class='btn download_btn btn-primary']"))).click()

        #time.sleep(25)
        timer = 60+50

        while timer>=0:
            time.sleep(10)
            timer-=10
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
            if  "loading..." not in browser.find_element(by=By.ID, value="reports-modal").text and "wait" not in browser.find_element(by=By.ID, value="reports-modal").text:
                break
        if timer<0:
            browser.find_element(by=By.CLASS_NAME, value="btn btn-warning btn-sm").click()
            print("Le chargement est anormalement long, nous allons recommencer")
            continue
            
        """
        
        #time.sleep(3)


        #browser.find_elements(by=By.XPATH, value='//span[@title="Click to download the exported file report" and @class="download_btn"]')[0].click()
        
        downloaded = False
        
        for element in browser.find_elements(by=By.XPATH, value='//span[@title="Click to download the exported file report" and @class="download_btn"]')[:2]:
            #print("hey")
            #sibling = element.find_element(by=By.XPATH, value="//span[contains(text(),'" +element.text+ "')]/following-sibling::span")
            sibling = element.find_element(by=By.XPATH, value="..")
            parent = sibling.find_element(by=By.XPATH, value="..")
            
            filter1 = parent.find_element(by=By.XPATH, value="//span[contains(text(),'"+debut+ "')]")
            
            #print(filter1.text)
            
            filter2 = parent.find_element(by=By.XPATH, value="//span[contains(text(),'"+fin+ "')]")
            
            #print(filter2.text)
            
            #filter1 = 0
            #filter2 = 0
            
            if str(start_date) in filter1.text and str(filter1.text) in str(filter2.text):
            #if str(start_date) in filter1.text and str(start_date) in filter2.text:
                
                #print(filter1.text,filter2.text)
                #exported-generated exported-gray ml-3 mt-1
                #print(parent.find_element(by=By.CLASS_NAME, value="exported-generated exported-gray ml-3 mt-1").text)
                libelle = "generated:"
                print(parent.find_element(by=By.XPATH, value="//span[contains(text(),'"+libelle+ "')]").text)
                print(f"filtre: {filter1.text}")
                
                element.click()
                downloaded = True
                
                break
            
            
        #time.sleep(10)
        if not(downloaded):
            print("le fichier n'a pas ete telecharge")
            continue
        
        timer = 30

        while timer>=0:
            time.sleep(1)
            timer-=1

            #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            
            p=glob.glob(filesInitialDirectory+'*BettingShopsOverall*xls')
            if len(p)>0:
                #filename = p[0].split("\\")[-1]
                #shutil.move(path+filename,filesInitialDirectory+filename)
                
                #print(f"le fichier de la plateforme Premier SN du {start_date} a bien ete telecharge et deplace")
                
                final_file = 'zone betting '+str(start_date)+'.csv'
                
                df = pd.read_excel(p[0],skiprows=2,skipfooter=3,decimal=",", thousands="`")
                df = df.drop(['#','Cashback','Unsettled stake', 'Country'], axis=1)
                df['date']=start_date.strftime('%d/%m/%Y')
                
                if os.path.exists(filesInitialDirectory+final_file):
                    os.remove(filesInitialDirectory+final_file)
        
                
                df.to_csv(filesInitialDirectory+final_file,sep=';',index=False,decimal=",")
                excl_list.append(df)
                #df.to_csv(filesInitialDirectory+filename,sep=";",index=False)
                
                
                print(f"le fichier de la plateforme zone betting du {start_date} a bien ete telecharge")
                start_date+=delta
                # CFAC
                
                #renameToZoneBetting(downloadPath)
                
                for i in glob.glob(filesInitialDirectory+'*BettingShopsOverall*xl*'): 
                    os.remove(i)
        
                
                break
            
            
            #if  "block" not in browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"):
                #break
        if timer<0:
            print("Le chargement est anormalement long, nous allons recommencer")
            continue
            
        for i in glob.glob(filesInitialDirectory+'*BettingShopsOverall*xl*'): 
            os.remove(i)
        

        

        #print(f"le fichier de la plateforme zone betting du {start_date} a bien ete telecharge")

        #renameToZoneBetting(downloadPath)

        #start_date+=delta
    
    print("Tous les fichiers ont bien ete telecharge")
    #autoprocessZoneBetting(downloadPath)

        #/html/body/div/div[2]/div[2]/div/div[2]/form/div/div[6]/button[1]/svg



        #dateTo = ""


# In[ ]:





# In[6]:


excl_list = []

#global start_date
#global delta
#start_date = datetime.date(2022, 9, 1)
#debut = datetime.date(2022, 7, 1)
#e.

#end_date = datetime.date(2022, 10, 1)

end_date = datetime.date.today()
delta = datetime.timedelta(days=1)
delta = datetime.timedelta(days=1)
start_date = end_date - delta

start_date = datetime.date(2024, 4, 6)
end_date = datetime.date(2024, 5, 1)
#start_date = datetime.date(2023, 10, 1)
#end_date = start_date + delta


#end_date = start_date+delta



#global end_date
debut1 = start_date
fin1 = end_date-delta

filesInitialDirectory = r"K:\DATA_FICHIERS\VIRTUEL_EDITEC\ZONE BETTING\\"

#browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

#connectToZoneBetting()
        
#time.sleep(10)


#browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

#connectToZoneBetting()

#break


#"""
for i in range(5):
    try:
        
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectToZoneBetting()
        
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
    if i == 99 :
        sys.exit(f"Impossible d'executer ce programme malgre 10 tentatives")
        
#handleFinancialFile()
        
#browser.quit()

#"""




# In[7]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_ZoneBetting.py").read())


# In[8]:


import gc
gc.collect()


# In[ ]:





# In[ ]:




