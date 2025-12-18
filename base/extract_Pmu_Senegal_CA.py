#!/usr/bin/env python
# coding: utf-8

# In[25]:


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
import gc


# In[26]:


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



# In[27]:


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


# In[28]:


def connectPmuSenegal():
    
    url = "https://backoffice.pmu.sn/"
    browser.get(url)
    
    WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/jhi-main/div[1]/jhi-navbar/nav/div/ul/li[3]/a"))).click()

    WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/jhi-main/div[1]/jhi-navbar/nav/div/ul/li[3]/ul"))).click()
    
    
    username = 'bmane' 
    WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-modal-window/div/div/jhi-login-modal/div[2]/div/div[2]/form/div[1]/input"))).send_keys(username)
    
    
    password = "L0n@se2024#"
    WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-modal-window/div/div/jhi-login-modal/div[2]/div/div[2]/form/div[2]/input"))).send_keys(password)
    
    
    WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-modal-window/div/div/jhi-login-modal/div[2]/div/div[2]/form/button"))).click()
    
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        #WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-left-panel/div/div/app-sidebar-component/p-panel/div/div[1]/div[1]/div/strong")))
        
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/jhi-main/div[1]/jhi-navbar/nav/div/ul/li[2]/a/span/span")))
        
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
        
    """
        
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-main-header-component/header/div/div[2]/ul/li/app-entity-header/span"))).click()
    
    
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-right-panel/div/div/app-entities-tree-component/div/div[2]/p-tree/div/div/ul/p-treenode/li/div/span/span/div/div[1]"))).click()
    
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-left-panel/div/div/app-sidebar-component/p-panelmenu/div/div[1]/div[2]/div/p-panelmenusub/ul/li[1]/p-panelmenusub/ul/li[2]/a"))).click()
    
    """
    
    #/html/body/app-root/app-logged-in/div/app-right-panel/div[1]/div/app-entities-tree-component/div/div[2]/p-tree/div/div/ul/p-treenode/li/ul
    #print(browser.find_element(by=By.XPATH, value=usernameId).send_keys(username))
    
    #return
    
    #generatePmuSenegal()
    
    time.sleep(5)
    
    extractPartenaires()
    
    print("tous les fichiers ont bien ete telecharges")
    
    return
    
    


# In[29]:


def extractPartenaires():
    url = 'https://backoffice.pmu.sn/partner/view'
    browser.get(url)
    
    global start_date
    
    tentatives = 0
    
    #while start_date > end_date:
    while start_date < end_date:
        
        
        browser.get(url)
    
        month = int(start_date.strftime('%#m'))

        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, f"/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[2]/div[2]/div/div[2]/div[{month}]"))).click()
        
        time.sleep(5)

        #browser.find_element(by=By.XPATH, value='/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[3]/div[2]/div/div/div[contains(., "07-05-2024")]').click()

        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, f"/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[3]/div[2]/div/div/div[contains(., '07-05-2024')]"))).click()

        #browser.find_element(by=By.XPATH, value=f"/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[3]/div[2]/div/div/div[contains(., '{start_date.strftime('''%d-%m-%Y''')}')]").click() 

        dd = start_date.strftime('%d-%m-%Y')
        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, f"/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[3]/div[2]/div/div/div[contains(., '{dd}')]"))).click()


        try:
            #pass
            WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, f"/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[3]/div[2]/div/div/div[contains(., '{dd}')]"))).click()
            tentatives = 0
        except:
            #pass
            #try:
                #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, f"/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[3]/div[2]/div/div/div[contains(., '{dd}')]"))).click()
            #except:
                #print(f" fichier PMU Senegal du {start_date} non genere")
            tentatives += 1 
            if tentatives == 3:
                print(f" fichier PMU Senegal du {start_date} non genere")
                start_date-=delta
                tentatives = 0
            continue

        
        time.sleep(5)


        WebDriverWait(browser,timeout=10).until( EC.presence_of_element_located(( By.XPATH, f"/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[2]/div[1]/div/div[1]/span[contains(., '{dd}')]")))#.click()

        time.sleep(5)

        table = WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[2]/div[1]/div/div[2]/table")))
        dfs = pd.read_html(table.get_attribute('outerHTML')) #latin1
        df = dfs[0].dropna(axis=0, thresh=4)


        table = WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/jhi-main/div[2]/div/jhi-partner-view/div/div[3]/div[1]/div/div[2]/table")))
        dfs = pd.read_html(table.get_attribute('outerHTML')) #latin1
        dfa = dfs[0].dropna(axis=0, thresh=4)



        df_concatenated = pd.concat([df.transpose(), dfa.transpose()], axis=1)


        df_concatenated = df_concatenated.set_axis(['CA', 'SHARING'], axis=1) #, 'Z'

        df_concatenated.index.name = 'PRODUIT'

        #df_concatenated['JOUR'] = str(start_date.strftime('%d/%m/%Y')
        #df_concatenated['ANNEE'] = str(start_date.strftime('%Y'))
        #df_concatenated['MOIS'] = str(start_date.strftime('%m'))

        for index, row in df_concatenated.iterrows():
            for column in df_concatenated.columns:
                df_concatenated.at[index, column] = str(row[column]).strip().replace('\u202f',' ').lstrip("CA :")

        df_concatenated = pd.DataFrame(data=df_concatenated);

        df_concatenated['JOUR'] = str(start_date.strftime('%d/%m/%Y'))
        df_concatenated['ANNEE'] = str(start_date.strftime('%Y'));
        df_concatenated['MOIS'] = str(start_date.strftime('%m'));


        filename = "Pmu_Senegal_ca_"+str(start_date)+".csv"
        df_concatenated[:-2].to_csv(filesInitialDirectory+filename,sep=';',encoding='utf-8')#,index=False)#,encoding='latin1')

        print(f"le fichier PMU senegal du {start_date} est telecharge")
        #start_date-=delta
        start_date+=delta



                                    


# In[30]:


#start_date -= delta 

#start_date = datetime.date(2024, 5, 22)
#end_date = datetime.date(2024, 5, 21)

#print(start_date)

#extractPartenaires()

#print(dd)


# In[31]:


#print(start_date)

#start_date-=delta


# In[32]:


def extractGagnants():
    url = 'https://backoffice.pmusenegal.sn/winner'
    browser.get(url)
    
    WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/jhi-main/div[2]/div/jhi-winner/div/div[1]/div/div/div/form/div/div[5]/div/div/input"))).clear()
    WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/jhi-main/div[2]/div/jhi-winner/div/div[1]/div/div/div/form/div/div[5]/div/div/input"))).send_keys(str(start_date))

    
    
    pass


# In[33]:


def generatePmuSenegal():
    global start_date
    global attemp
    
    #while start_date < end_date:
    while start_date > end_date:
        
        for file in glob.glob(filesInitialDirectory+'PivotTable_*.xlsx') :
            os.remove(file)
    
    
    pass


# In[34]:


attemp = 0
excl_list = []
#global start_date
#start_date = datetime.date(2022, 7, 1)
#debut = datetime.date(2022, 7, 1)
#end_date = datetime.date(2022, 6, 1)
delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
#delta = datetime.timedelta(days=1)
start_date = end_date - delta

#start_date = datetime.date(2025, 4, 21)
#end_date = datetime.date(2025, 4, 2)

#delta = datetime.timedelta(days=1)
#end_date = start_date+delta

filesInitialDirectory = r"K:\DATA_FICHIERS\PMUSENEGAL\\"

#global end_date

debut1 = start_date
fin1 = end_date-delta

#browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

#connectPmuSenegal()

#"""
for i in range(10):
    try:
        
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectPmuSenegal()
        
        time.sleep(1)
        
        browser.quit()


        break
    
    except Exception as e:
        
        #attachments = []
        
        try:
            browser.quit()
        except Exception as e:
            print("nous n'avons pas pu quitte le navigateur precedemment ouvert")
    
        print(f"la tentative numero {i+1} a echoue")
        print(f"Nous allons reessayer {e}")
        
        #continue
    if i == 9 :
        sys.exit(f"Impossible d'executer ce programme malgre 10 tentatives")
        
#handleFinancialFile()

#"""

#time.sleep(5)
        
#browser.quit()


#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


