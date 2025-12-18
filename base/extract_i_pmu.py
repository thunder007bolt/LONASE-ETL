#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options


# import Action chains
from selenium.webdriver.common.action_chains import ActionChains
 
# import KEYS
from selenium.webdriver.common.keys import Keys



import os
import glob


# In[2]:


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

from datetime import date, timedelta, datetime
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

#import Options




import pandas as pd
import numpy as np
import win32com.client
import os
#import re
from datetime import date
import re
#import calendar
import copy

import shutil
import win32com.client as win32



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
            chromeOptions.add_argument("--headless")
            chromeOptions.add_argument("--disable-gpu")
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

        try:
            browser = webdriver.Safari()
            break
        except:
            print("les drivers du navigateur Safari semblent ne pas exister")

        try:
            browser = webdriver.Edge()
            break
        except:
            print("les drivers du navigateur Edge semblent ne pas exister/fonctionner")

        try:
            browser = webdriver.Firefox()
            break
        except:
            print("les drivers du navigateur Firefox semblent ne pas exister/fonctionner")
        a+=1
        if a <5:
            print(f"tentative numero {a+1} a echoue. Reessayons")
            continue


        sys.exit("Aucun WebDriver de navigateur ne fonctionne ou est installe")
    return browser


# In[4]:


def connectIpmu():
    
    url = "https://i-pmu.pmu.fr"
    browser.get(url)
    
    #time.sleep(5)
    
    #usrname = wait2.until( EC.element_to_be_clickable(( By.ID, usernameId)) )
    #usrname.send_keys(username)
    usernameId=":r0:"
    username = 'Mthiam' 
    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
    
    
    #pwd = wait2.until( EC.element_to_be_clickable(( By.ID, passwordId)) )
    #pwd.send_keys(password)
    passwordId = ':r1:'
    password = "S@l@mdiam2024"
    #browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, passwordId))).send_keys(password)
    
    
    #browser.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div/div/div/div[2]/div/form/input[2]").click()
    #driver.find_element_by_xpath("//button[@type='submit']").click()
    #browser.find_element(by=By.ID, value="edit-submit").click()
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/div/div/div/div[2]/div/div[2]/div/form/div/div[3]/div[2]/button"))).click()
    
    
    
    #time.sleep(5) 
    
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/div/div/div[1]/header/div/div[2]/div[2]/h6")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    
    generateIpmu()
    
    """
    for i in range(3):
        try:
            generateIpmu()
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
    
    return
    
    excl_merged = pd.concat(excl_list, ignore_index=True)
    
    #print(excl_list)
    
    #print(excl_list.head())
    
    #print("mergeZeturf"+str(debut)+"_"+str(fin)+".csv")
    #excl_merged.to_csv(r"C:\Users\CFAC\Documents\jules\Stage\ExtractedFiles\Bwinner\mergeBwinner"+str(debut)+"_"+str(fin)+".csv" , index=False,sep=';',encoding='utf8')
    if debut1<fin1:
        excl_merged.to_csv(filesInitialDirectory+"merge_I_PMU"+str(debut1)+"_"+str(fin1)+".csv" , index=False,sep=';',encoding='utf8')
    
    #print (excl_merged)
    
    return

    #bwinnerManipulation(excl_merged,debut1,fin1)
    
    
    #tryGenFiles()
    
    #for i in range(15):
        
        
    #generateAfitechFiles()

    


# In[5]:


def generateIpmu():
    #print("")
    url = 'https://i-pmu.pmu.fr/courses-pmu'
    
    for i in glob.glob(f"{filesInitialDirectory}BALAN*PMU_LONASE*CSV"):
        os.remove(i)
        
    #browser.get(url)
        
    global start_date
    global attemp
    global excl_list
    
    while start_date < end_date:
        
        browser.get(url)
        
        #time.sleep(0.1)
        #WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[2]/div/div/input'))).clear()
        
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[2]/div/div/input'))).click()
        
        time.sleep(0.1)
    
        
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[2]/div/div/input'))).send_keys(str(start_date.strftime("%d%m%Y")))
        
        #WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/input'))).clear()
        
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/input'))).click()
        
        time.sleep(0.1)
        
        
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/input'))).send_keys(str(start_date.strftime("%d%m%Y")))
        
            
        #'''
        try:
            
            #libelle = f"Daily balance in currency on {str(start_date)}"
            libelle = f'{str(start_date.strftime("%d/%m/%Y"))}'
            
            WebDriverWait(browser,timeout=10).until( EC.presence_of_element_located(( By.XPATH, "/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/table/tbody/tr[1]/td[contains(text(), '" + libelle + "')]")))
                                                                                            # /html/body/div[2]/div[2]/div/section/div/section/div/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div[3]/div/div/a[2]/div[2]/div
        except:
            attemp+=1
            if attemp==2:
                print(f"le fichier i_pmu du {start_date} n'a malheuresement pas pu ete telecharge")
                start_date+=delta
                attemp = 0
            continue
        #'''
        
        
        
        
        
        notAvailable = False
        
        for tr in browser.find_elements(By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/table/tbody/tr'):
            
            
            
            #print(tr.text)
            
            if start_date.strftime("%d/%m/%Y") in tr.text :#and ("€" in tr.text or '€' in tr.text or r"€" in tr.text or r'€' in tr.text   ):
                
                
                WebDriverWait(tr,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "td[3]"))).click()
                notAvailable = True
                break

        if notAvailable is False:
            print(f"le fichier i_pmu du {start_date} n'a malheuresement pas pu ete telecharge")
            start_date+=delta
            attemp = 0
            continue
        
        
        
        filename = 'i_pmu '+str(start_date)+'.csv'
        timer = 20
        while timer>=0:
            time.sleep(1)
            timer-=1
            #p=glob.glob(f"{path+str(start_date)}*LONASE-daily*csv")  #BALAN_3212023_PMU_LONASE.CSV
            #for i in glob.glob(f"{path}BALAN*PMU_LONASE.CSV"):
            p=glob.glob(f"{filesInitialDirectory}BALAN*PMU_LONASE*CSV")
            if len(p)>0:
                #df = pd.read_csv(p[0],sep=",",index_col=False)
                
                
                df = pd.read_csv(p[0],sep=";",index_col=False,skipfooter=1,engine='python',encoding='latin-1')#,header=0,skiprows=1)
                #df = pd.read_csv(p[0],sep=";",index_col=False,skipfooter=1,engine='python',encoding='latin-1')
                
                df = df[1:]
                
                #df=df.astype(str)
                #df = df.applymap(lambda x: str(x).replace('.',','))
                
                #df['MeetingDate'] = start_date.strftime('%d/%m/%Y')
                
                excl_list.append(df)
                
                df.to_csv(filesInitialDirectory+filename,sep=";",index=False)
                
                os.remove(p[0])
                print(f"le fichier i_pmu du {start_date} a bien ete telecharge")
                start_date+=delta
                for i in glob.glob(f"{filesInitialDirectory}BALAN*PMU_LONASE.CSV"):
                    os.remove(i)
    
                attemp = 0
                break
            
        for i in glob.glob(f"{filesInitialDirectory}BALAN*PMU_LONASE*CSV"):
            os.remove(i)
            
        '''
        # send_keys(Keys.CONTROL + 'a')
        
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[2]/div/div/input'))).send_keys(Keys.CONTROL + 'a')
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[2]/div/div/input'))).clear()
        
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/input'))).send_keys(Keys.CONTROL + 'a')
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/input'))).clear()
        
        
        
        
        #WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[2]/div/div/input'))).clear()
        #WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/input'))).clear()
        '''
        


# In[ ]:





# In[6]:


excl_list = []

attemp = 0
#global start_date
#start_date = datetime.date(2022, 7, 1)
#debut = datetime.date(2022, 7, 1)
#end_date = datetime.date(2022, 6, 1)
delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
#delta = datetime.timedelta(days=1)
start_date = end_date - delta

#start_date = datetime.date(2024, 9, 16)
#end_date = datetime.date(2023, 11, 1)

start_date = end_date - 8*delta
end_date = start_date+delta


#delta = datetime.timedelta(days=1)
#end_date = start_date+delta


filesInitialDirectory = r"K:\DATA_FICHIERS\I-PMU\\"


#global end_date

debut1 = start_date
fin1 = end_date-delta

#browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

#connectIpmu()

#"""
for i in range(5):
    try:
        
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectIpmu()

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
        sys.exit(f"Impossible d'executer ce programme malgre 10 tentatives")
        
#handleFinancialFile()

#"""

#time.sleep(5)
        
#browser.quit()




# In[7]:


import gc

gc.collect()


# In[8]:


#d = dir()

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


# In[ ]:





# In[9]:


#browser = webdriver.Chrome()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




