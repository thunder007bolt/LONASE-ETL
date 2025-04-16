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
#import shutil


import datetime

from datetime import date,timedelta

import time


# In[ ]:





# In[2]:


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

        a+=1
        if a <5:
            print(f"tentative numero {a+1} a echoue. Reessayons")
            continue


        sys.exit("Aucun WebDriver de navigateur ne fonctionne ou est installe")
    return browser


# In[ ]:





# In[3]:


def connectZeturf():
    
    
    #url = "https://bwinners-senegal-bo.impaladigital.com/Admin/Account/"
    url = 'https://a.bwinners.sn/oldbo/'
    browser.get(url)
    
    time.sleep(5)
    
    #usrname = wait2.until( EC.element_to_be_clickable(( By.ID, usernameId)) )
    #usrname.send_keys(username)
    usernameId="inputUsername"
    username = 'support1' 
    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    
    #browser.find_element(by=By.XPATH, value="/html/body/form/fieldset/input[1]").send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/form/fieldset/input[1]"))).send_keys(username)
    
    
    
    
    #pwd = wait2.until( EC.element_to_be_clickable(( By.ID, passwordId)) )
    #pwd.send_keys(password)
    passwordId = 'inputPassword'
    password = "1q2w3e8i9o0p"
    password = '1q2w3e8i9o0p'
    #browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    
    #browser.find_element(by=By.XPATH, value="/html/body/form/fieldset/input[2]").send_keys(password)
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/form/fieldset/input[2]"))).send_keys(password)
    
    
    
    #browser.find_element(by=By.ID, value="submit").click()
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.ID, "submit"))).click()
    
    #browser.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div/div/div/div[2]/div/form/input[2]").click()
    #driver.find_element_by_xpath("//button[@type='submit']").click()
    time.sleep(5) 
    
    print("la connection a la plateforme est un succes")
    
    generateBwinnersFiles()
    
    """
    for i in range(3):
        try:
            generateBwinnersFiles()
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
    
    #tryGenFiles()
    
    #for i in range(15):
        
        
    #generateBwinnersFiles()

    


# In[4]:


def generateBwinnersFiles():
    
    #url = "https://bwinners-senegal-bo.impaladigital.com/Admin/Reports/TotalTaxReport"
    url = 'https://a.bwinners.sn/oldbo/Reports/TotalTaxReport'
    
    #for i in glob.glob(r'C:\Users\CFAC\Documents\jules\Stage\ExtractedFiles\Bwinner\Total Tax Report*'): 
        #os.remove(i)
        
    #break
        
    
    browser.get(url)
    
    #time.sleep(5)
   
   #driver.find_element_by_class_name("form-control").click()
    #WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.CLASS_NAME, "form-control"))).click()
    
   #frmc = wait2.until( EC.element_to_be_clickable(( By.CLASS_NAME,"form-control")) )
   #frmc.click()
   #time.sleep(3)

    #WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "//option[@value='OperationHistory']"))).click()
   
   #driver.find_element_by_xpath("//option[@value='OperationHistory']").click()
    global generated
    
    global start_date
    
    global excl_list
    
    #start_date = datetime.date(2022, 1, 1)
    #end_date = datetime.date(2022, 2, 1)
    #delta = datetime.timedelta(days=1)
   
   #for day in range(start_date,end,1):
    global iterateur
    
    time.sleep(1)
        
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[5]/section/div[3]/div[2]/span[1]/span/span/span[1]"))).click()

    time.sleep(1)

    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[7]/div/ul/li[3]"))).click()

    time.sleep(1)

    browser.execute_script("window.scrollTo(document.body.scrollHeight,0)")

    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[5]/section/div[2]/span[1]/span/span[1]"))).click()

    time.sleep(1)

    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[11]/div/ul/li[1]"))).click()

    time.sleep(1)
        
    
    while start_date < end_date:
        
        for i in glob.glob(filesInitialDirectory+'Total Tax Report*'):
            os.remove(i)
    
        
        #lastMonth = date(start_date.year, start_date.month, calendar.monthrange(start_date.year, start_date.month)[1])
        
        #if end_date < lastMonth :
            
            #lastMonth = end_date - delta
            

        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "FromDate"))).clear()
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "FromDate"))).send_keys(str(start_date.strftime('%Y/%m/%d'))+" 00:00:00"+" - "+str(start_date.strftime('%Y/%m/%d'))+" 23:59:00")
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "FromDate"))).send_keys(str(start_date.strftime('%d/%m/%Y')))
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "FromDate"))).send_keys(Keys.ENTER)
        
        time.sleep(0.5)
        
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "ToDate"))).clear()
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "FromDate"))).send_keys(str(start_date.strftime('%Y/%m/%d'))+" 00:00:00"+" - "+str(start_date.strftime('%Y/%m/%d'))+" 23:59:00")
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "ToDate"))).send_keys(str(start_date.strftime('%d/%m/%Y')))
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "FromDate"))).send_keys(Keys.ENTER)
        
        time.sleep(0.5)
        
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "btnFilter"))).click()
        
        time.sleep(3)
        
        #return
        
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[5]/section/div[3]/div[1]/div/a"))).click()
        
        
        timer = 30
        
        while timer>=0:
            time.sleep(1)
            timer-=1
            p=glob.glob(filesInitialDirectory+'Total Tax Report*xlsx') 
            if len(p)>0:
                
                o = win32com.client.gencache.EnsureDispatch('Excel.Application')
                #o.Visible = False
                o.Visible = True
                
                wb = o.Workbooks.Open(p[0])
                o.ActiveWorkbook.SaveAs(p[0].replace('xlsx','csv'), FileFormat=24) #
                o.ActiveWorkbook.Close(SaveChanges=0) 
                o.Quit()
                
                df = pd.read_csv(p[0].replace('xlsx','csv'),sep=';')

                #print(df.dtypes)

                #print(df['Name'].unique())

                newdf= df[~df['Name'].isnull() ] #  &     ~df['Name'].str.contains(str("Totals"),case=False)  

                newdf= newdf[~newdf['Name'].str.contains(str("Totals"),case=False)  ]

                newdf['Report Date'] = [((datetime.datetime.strptime(str(i)[:10], '%d/%m/%Y'))+delta).strftime('%d/%m/%Y') for i in newdf['Report Date']]

                # bwinnerManipulation(newdf[["Report Date","Name","Total Stakes","Total Paid Win"]],start_date)
                
                #print(newdf.dtypes)

                #print(newdf['Name'].unique())

                #newdf.drop(columns=['Unnamed: 0', 'Ld'], axis=1)

                #print(newdf.columns)
                
                # start_date < end_date
                
                if os.path.exists(filesInitialDirectory+"Bwinner_"+str(start_date)+"_"+str(start_date)+".csv"):
                    os.remove(filesInitialDirectory+"Bwinner_"+str(start_date)+"_"+str(start_date)+".csv")

                newdf.to_csv(filesInitialDirectory+"Bwinner_"+str(start_date)+"_"+str(start_date)+".csv",index=False,sep=';',columns=['Report Date', 'Name','Total Stakes','Total Paid Win'])
                
                #excl_list.append(newdf[["Report Date","Name","Total Stakes","Total Paid Win"]])
                
                #excl_list.append(newdf[["Report Date","Name","Total Stakes","Total Paid Win"]])
                
                
                print(f"le fichier de la plateforme Bwinner du {start_date} au {start_date} a bien ete telecharge et deplace")
                
                start_date=start_date+delta
                

                

                break
                
        if timer < 0:
            print("le fichier n'a pas pu etre telecharge")
            continue
        
        
        
        
        
        #start_date=lastMonth+delta
        
        #i=0
        
    
     
    print("tous les fichiers ont bien ete telecharge")
    
    for i in glob.glob(filesInitialDirectory+'Total Tax Report*'):
        os.remove(i)
        
    #excl_merged = pd.concat(excl_list, ignore_index=True)
    
    #print(excl_merged.head())
    
    #print(excl_list.head())
    
    #if debut<fin:
        
        #excl_merged.to_csv(filesInitialDirectory+"MERGE\mergeBwinner_"+str(debut)+"_"+str(fin)+".csv" , index=False,sep=';',encoding='utf8')
    
    #bwinnerManipulation(excl_merged,debut,fin)
    
    
    
            
    
    
    


# In[ ]:





# In[5]:


excl_list = []

#start_date = datetime.date(2025, 4, 4)

#debut = datetime.date(2022, 5, 11)

#end_date = datetime.date(2025, 4, 5)


#delta = timedelta(days=1)

end_date = date.today()
delta = timedelta(days=1)
start_date = end_date - delta
delta = timedelta(days=1)


#↔debut = start_date
#fin = end_date-delta
#start_date = datetime.date(2025, 4, 4)
#end_date = datetime.date(2025, 4, 5)
#end_date = start_date+delta

#debut = datetime.date(2022, 9, 6)



"""
iterateur = int(22)

datee = '17/07/1997'

currentDate = ((datetime.datetime.strptime(datee, '%d/%m/%Y'))-delta).strftime('%d/%m/%Y')

#import datetime as dte

#dt = (datetime.datetime.strftime(str('17/07/1997')[:10], '%d/%m/%Y'))+delta
#dt = (dte.datetime.strftime(str('17/07/1997')[:10], '%d/%m/%Y'))+delta
#dt = (datetime.datetime.strftime(str('17/07/1997')[:10], '%d/%m/%Y'))+delta

#print(dt)


#path = "C:\\Users\\OPTIWARE-ENTERPRISE\\Downloads\\" CFAC
path = "C:\\Users\\CFAC\\Downloads\\" 
#filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\'
filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'
#filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\afitechAugust\\'

#generated = False

"""

filesInitialDirectory = r"K:\DATA_FICHIERS\BWINNERS\\"

#browser=openBrowser()
#connectZeturf()


#"""
for i in range(10):
    try:
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectZeturf()

        
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


# In[6]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_Bwinners.py").read())


# In[7]:


import gc
gc.collect()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




