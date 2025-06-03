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


from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

#from datetime import date
#import datetime


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


# In[3]:


#print(date.today())
#start_date = datetime.date(2022, 1, 1)

#end_date = datetime.date(2022, 1, 3)

#delta = datetime.timedelta(days=1)

#start_date = datetime.date(2022, 4, 2)
#print(start_date)


# In[4]:


# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 19:52:56 2021

@author: RAWANE
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


# In[5]:


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


# In[6]:


def connectParifoot():
    
    url = "https://agent.premierbet.com/"
    
    browser.get(url)
    
    #time.sleep(5)
    #driver.maximize_window()
    #driver.refresh()
    
    usernameId = 'Username'
    username = 'sn_lonase_cashier'
    #browser.find_element_by_id(usernameId).send_keys(username)
    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
    
    
    passwordId = 'Password'
    password = 'mS44MBxc46#O'
    #browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, passwordId))).send_keys(password)
    
    submit_buttonId = 'logon'
    #browser.find_element_by_id(submit_buttonId).click()
    #browser.find_element(by=By.ID, value=submit_buttonId).click()
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, submit_buttonId))).click()
    
    
    
    #time.sleep(5)

    #print("la connexion a la plateforme est un succes")
    
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/nav/div/div/ul[2]/li[2]/a/div/div[1]/span[3]")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    
    generateParifootFiles()
    
    return
    
    #'''
    for i in range(10):
        try:
            generateParifootFiles()
            #except SystemExit:
                #print("Program terminated with SystemExit exception")
                #sys.exit(" ")
            break
        except:
            print("nous avons rencontre un soucis, nous allons reessayer")
            #tryGenFiles()
            #continue
        if i ==9:
            sys.exit("Impossible malgre 3 tentatives")
    #'''
    
    
    
    
    
    #generateParifootFiles()
    


# In[7]:


def generateParifootFiles():
    
    global start_date
    
    lists = ['ID','Balance','Total Players','Total Players Date Range','SB Wins No.','SB Ref No.','Cas.Wins No.','Cas.Ref No.','Financial Deposits','Financial Withdrawals','Transaction Fee']
    
        
    while start_date < end_date:
        
        for i in glob.glob(filesInitialDirectory+'AgentCasinoAndBettingReport*'):
            os.remove(i)
    
        
        """
        for filename in os.listdir(path):
                if filename.startswith('AgentCasinoAndBettingReport') and ".csv" in filename:
                    os.remove(path+filename)
        """
        
        url = "https://agent.premierbet.com/Transaction?menu=accReport_index_agentCasinoAndBettingReport&actionCtrl=AgentCasinoAndBettingReport"
        
        browser.get(url)
        
        #time.sleep(5)
        
        start = str(start_date).split("-")
        start = start[2]+'/'+start[1]+'/'+start[0]+' 00:00'
        
        end = str(start_date+delta).split("-")
        end = end[2]+'/'+end[1]+'/'+end[0]+' 00:00'
        
        
        
            

        #url = "https://agent.premierbet.com/Transaction?menu=accReport_index_agentCasinoAndBettingReport&actionCtrl=AgentCasinoAndBettingReport"
        #browser.get(url)

        #wait_From = wait.until( EC.element_to_be_clickable(( By.ID, "tbFrom")) )
        WebDriverWait(browser,timeout=10*10).until( EC.element_to_be_clickable(( By.ID, "tbFrom"))).click()#.clear().send_keys(start+ Keys.ENTER)
        browser.find_element(by=By.ID, value="tbFrom").clear()
        browser.find_element(by=By.ID, value="tbFrom").send_keys(start+ Keys.ENTER)


        #wait_To = wait.until( EC.element_to_be_clickable(( By.ID, "tbTo")) )
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.ID, "tbTo"))).click()#.clear().send_keys(end+ Keys.ENTER)
        browser.find_element(by=By.ID, value="tbTo").clear()#.send_keys(end+ Keys.ENTER)
        browser.find_element(by=By.ID, value="tbTo").send_keys(end+ Keys.ENTER)
        
        
        
        WebDriverWait(browser,timeout=120).until( EC.element_to_be_clickable(( By.XPATH, "//div[@id='tblAgentCasinoAndBettingReport2356671_wrapper']//button[@class='ColVis_Button ColVis_MasterButton fa fa-th']"))).click()

        #div_checkboxes = driver.find_element_by_xpath("//ul[@class='ColVis_collection']") #//label//input[@type='checkbox']
        div_checkboxes = browser.find_element(by=By.XPATH, value="//ul[@class='ColVis_collection']")
        #checkboxes = div_checkboxes.find_elements_by_tag_name("li")
        checkboxes = div_checkboxes.find_elements(by=By.TAG_NAME, value="li")
        #lists = ['ID','Balance','Total Players','Total Players Date Range','SB Wins No.','SB Ref No.','Cas.Wins No.','Cas.Ref No.','Financial Deposits','Financial Withdrawals','Transaction Fee'] 
        for checkbox in checkboxes:
            if checkbox.text in lists:
                checkbox.click()
          
        mouse = ActionChains(browser).move_by_offset(242, 130)
        mouse.click()
        #ActionChains(driver).key_down(Keys.CONTROL)
        mouse.perform()
        #print (checkbox.text)
        
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.ID, "ReportCurrency"))).send_keys('West African CFA Franc')#.click()

        #time.sleep(60+20)
        timer = 60+60

        while timer>0:
            time.sleep(10)
            timer-=10
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
            if  "block" not in browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"):
                break
        if timer<=0:
            print("Le chargement est anormalement long, nous allons recommencer")
            continue
        
        time.sleep(3)

        
        WebDriverWait(browser,timeout=120).until( EC.element_to_be_clickable(( By.ID, "btnFilter"))).click()#.click()
        
        #time.sleep(40)
        timer = 60+60

        while timer>0:
            time.sleep(10)
            timer-=10

            #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            if  "block" not in browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"):
                break
        if timer<=0:
            print("Le chargement est anormalement long, nous allons recommencer")
            continue
            
        time.sleep(3)

        
        WebDriverWait(browser,timeout=120).until( EC.element_to_be_clickable(( By.ID, "ToolTables_tblAgentCasinoAndBettingReport2356671_0"))).click()#.click()
        
        #print(f"le fichier PARIFOOT du {start} est telecharge")
        
        #time.sleep(30)
        
        timer = 20
        while timer>=0:
            time.sleep(2)
            timer-=2
            p=glob.glob(filesInitialDirectory+'AgentCasinoAndBettingReport*cs*') 
            if len(p)>0:
                #print(p[0])
                break
        if timer<0:
            print("Le chargement est anormalement long, nous allons recommencer")
            continue
        
        
        timer = 60+60
        while timer>=0:
            time.sleep(2)
            timer-=2
            p=glob.glob(filesInitialDirectory+'AgentCasinoAndBettingReport*.csv') 
            if len(p)>0:
                
                #filename = p[0].split("\\")[-1]
                #shutil.move(path+filename,filesInitialDirectory+filename)
                
                #print(f"le fichier de la plateforme Premier SN du {start_date} a bien ete telecharge et deplace")
                #print(f"le fichier de la plateforme PARIFOOT du {start_date} a bien ete telecharge")
                
                df = pd.read_csv(p[0],sep=',',index_col=False)
                #df = df.apply(lambda s:s.str.replace('"', ""))
                df['date']=start_date.strftime('%d/%m/%Y')
                #df.to_csv(r'K:\DATA_FICHIERS\PARIFOOT_ONLINE\OLD\rama.csv',sep=';',index=False)
                
                if os.path.exists(filesInitialDirectory+"ParifootOnline "+str(start_date)+".csv"):
                    os.remove(filesInitialDirectory+"ParifootOnline "+str(start_date)+".csv")
        
                
                df.to_csv(filesInitialDirectory+"ParifootOnline "+str(start_date)+".csv",sep=';',index=False)
                os.remove(p[0])
                print(f"le fichier de la plateforme PARIFOOT du {start_date} a bien ete telecharge")
                start_date+=delta
                
                """
                #src = os.path.join(path,filename)
                src = os.path.join(p[0])
                
                print(src)
                
                filename = p[0].split("\\")[-1]
                #final_file = re.sub('\d*','', filename).replace('.csv',' '+str(start_date)+'.csv')
                final_file = "ParifootOnline "+str(start_date)+".csv" 
                # dest = os.path.join('/Users/hp/website_login/',final_file)
                #dest = os.path.join(path+'/ParifootOline/',final_file)
                dest = os.path.join(filesInitialDirectory,final_file)
                
                print(dest)
                #os.renames(src,dest)
                shutil.move(src,dest)
                #print(final_file)
                
                """
                #print(f"le fichier de la plateforme PARIFOOT du {start_date} a bien ete deplace")
                
                
                #renameToZoneBetting(downloadPath)
                
                break
            
            
        
        
        
        
        
        
        """
        while timer>=0:
            time.sleep(10)
            timer-=10
            
            #for i in 

            #if len(browser.find_elements(by=By.CLASS_NAME, value="infotext"))>0:
            #
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            
            for i in browser.find_elements(by=By.CLASS_NAME, value="infotext"):
                if "Something went wrong" in i.text or "Please come back later" in i.text:
                    print(i.text)
                    timer = -500
                    break
            
            p=glob.glob(f'C:\\Users\\CFAC\\Downloads\\AgentCasinoAndBettingReport*.csv')
            if len(p)>0:
                #filename = p[0].split("\\")[-1]
                #shutil.move(path+filename,filesInitialDirectory+filename)
                
                #print(f"le fichier de la plateforme Premier SN du {start_date} a bien ete telecharge et deplace")
                print(f"le fichier de la plateforme PARIFOOT du {start_date} a bien ete telecharge")
                
                
                #src = os.path.join(path,filename)
                src = os.path.join(p[0])
                filename = p[0].split("\\")[-1]
                final_file = re.sub('\d*','', filename).replace('.csv',' '+str(start_date)+'.csv')
                # dest = os.path.join('/Users/hp/website_login/',final_file)
                #dest = os.path.join(path+'/ParifootOline/',final_file)
                dest = os.path.join(filesInitialDirectory,final_file)
                #os.renames(src,dest)
                shutil.move(src,dest)
                #print(final_file)
                print(f"le fichier de la plateforme PARIFOOT du {start_date} a bien ete deplace")
                
                
                #renameToZoneBetting(downloadPath)
                
                break
            
            
            #if  "block" not in browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"):
                #break
        """
        
        
        
        
        if timer<0:
            
            print("Le telechargement est anormalement long, nous allons recommencer")
            continue

        
        
        """
        variable = 0
        
        for filename in os.listdir(path):
            if filename.startswith('AgentCasinoAndBettingReport') and ".csv" in filename:
                variable +=1
                break
                

        if variable ==0 : 
            #start_date-=delta
            print(f"le fichier PARIFOOT du {start} n'a pas ete telecharge")
            continue
            #if filename.startswith('AgentCasinoAndBettingReport'):
        print(f"le fichier PARIFOOT du {start} est telecharge")
        
        """
        
        #time.sleep(3)
        """
        for filename in os.listdir(path): 
            if filename.startswith('AgentCasinoAndBettingReport') and ".csv" in filename: 
                src = os.path.join(path,filename)
                final_file = re.sub('\d*','', filename).replace('.csv',' '+str(start_date)+'.csv')
                # dest = os.path.join('/Users/hp/website_login/',final_file)
                #dest = os.path.join(path+'/ParifootOline/',final_file)
                dest = os.path.join(filesInitialDirectory,final_file)
                #os.renames(src,dest)
                shutil.move(src,dest)
                print(final_file)
                
                time.sleep(3)
       """
        
        

        
        #start_date+=delta
        for i in glob.glob(filesInitialDirectory+'AgentCasinoAndBettingReport*'): 
            os.remove(i)
        #i=0
        #time.sleep(20)
    print("tous les fichiers ont ete telecharges")

        


# In[8]:


#start_date = datetime.date(2025, 3, 1)

#debut = datetime.date(2022, 5, 11)

#end_date = datetime.date(2025, 3, 2)

delta = datetime.timedelta(days=1)

end_date = datetime.date.today()#- delta
start_date = end_date - delta



#start_date = datetime.date(2022, 8, 6)
#end_date = datetime.date(2022, 8, 7)

#end_date = datetime.date(2023, 3, 5)

##delta = datetime.timedelta(days=1) #- delta


#end_date = start_date+delta


#start_date = datetime.date(2024, 11, 29)
#end_date = datetime.date(2023, 4, 1)

#end_date = datetime.date.today() - deltastart_date = end_date - delta

#start_date = datetime.date(2025, 4, 24)
#end_date = start_date + 3*delta
#end_date = datetime.date.today()
#end_date = datetime.date(2025, 4, 25)

#path = "C:\\Users\\CFAC\\Downloads\\"
#filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'

filesInitialDirectory = r"K:\DATA_FICHIERS\PARIFOOT_ONLINE\\"


#browser=openBrowser()
#connectParifoot()

#browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()
#connectParifoot()


#'''

for i in range(10):
    try:
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectParifoot()

        
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
    if i == 99 :
        sys.exit(f"Impossible d'executer ce programme malgre 10 tentatives")




#'''



#browser = openBrowser()
#connectParifoot()


# In[9]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_Parifoot_Online.py").read())


# In[10]:


d = dir()

#You'll need to check for user-defined variables in the directory
for obj in d:
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


# In[11]:


#import gc
#gc.collect()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




