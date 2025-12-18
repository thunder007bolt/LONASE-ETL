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

from selenium import webdriver

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.action_chains import ActionChains


# In[30]:


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





# In[ ]:





# In[31]:


def connectSunubet():
    
    
    url = "https://new-admin-sunubet.sporty-tech.net/login"
    browser.get(url)
    
    time.sleep(5)
    
    #usrname = wait2.until( EC.element_to_be_clickable(( By.ID, usernameId)) )
    #usrname.send_keys(username)
    usernameId="inputUsername"
    #username = 'boubacar.mane' 
    #username = 'ndeyekhadyba.ly' 
    username = 'boubacar.mane'
    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    #browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-login/div/div[2]/form/div[1]/input").send_keys(username)
    #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.NAME, "username"))).send_keys(username)
    WebDriverWait(browser,timeout=10*3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-login/div/div[2]/form/div[1]/input"))).send_keys(username)
    
    
    
    
    #pwd = wait2.until( EC.element_to_be_clickable(( By.ID, passwordId)) )
    #pwd.send_keys(password)
    passwordId = 'inputPassword'
    #password = "H9$J7%W3fvgr"
    #password = "Lonase2021"
    password = "H9$J7%W3fvgr"
    #browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    #browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-login/div/div[2]/form/div[2]/input").send_keys(password)
    WebDriverWait(browser,timeout=45).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-login/div/div[2]/form/div[2]/input"))).send_keys(password)
    #browser.find_element(by=By.ID, value="submit").click()
    
    
    browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-login/div/div[2]/form/div[3]/button").click()
    WebDriverWait(browser,timeout=45).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-login/div/div[2]/form/div[3]/button"))).click()
    #driver.find_element_by_xpath("//button[@type='submit']").click()
    time.sleep(5) 
    
    #print("la connection a la plateforme est un succes")
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        WebDriverWait(browser,timeout=10*3).until( EC.presence_of_element_located(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/hg-header/div/div/hg-topbar-infos/div/div[2]/div[2]/button/div/span")))
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
    
    
    
    #downloadAlreadyGeneratedFiles()
    #print('hhhhhhhhhjjjjjjjjjjjjjjjfffffffff')
    
    #url = "https://new-admin-sunubet.sporty-tech.net/reports/create"

    #browser.get(url)

    #generateSunubet()
    #downloadAfitechFiles()
    
    #generateAllFiles()
    
    #downloadAlreadyGeneratedFiles()
    
    #return
    
    
    
    global start_date
    global liste
    
    while start_date < end_date:
        
        
        
        #liste = []
        
        for i in range(3):
            
            try:
                url = "https://new-admin-sunubet.sporty-tech.net/reports/create"

                browser.get(url)

                #time.sleep(5)

                #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[2]/div/button"))).click()
                # /html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[5]/div/button
                #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[5]/div/button"))).click()
                

                time.sleep(0.5)

                generateSunubet()
                #except SystemExit:
                #print("Program terminated with SystemExit exception")
                #sys.exit(" ")
                break
            except:
                print("nous avons rencontre un soucis lors de la generation du fichier, nous allons reessayer")
                #tryGenFiles()
                #continue
            if i ==2:
                sys.exit("Impossible malgre 3 tentatives")

    
        #generateSunubet()
        
        #print(liste)
        
        #downloadAfitechFiles()
        
        #break
    
    #"""
        for i in range(3):
            try:
                downloadAfitechFiles()
                #except SystemExit:
                    #print("Program terminated with SystemExit exception")
                    #sys.exit(" ")
                break
            except:
                print("nous avons rencontre un soucis lors du telechargement du fichier, nous allons reessayer")
                #tryGenFiles()
                #continue
            if i ==2:
                sys.exit("Impossible malgre 3 tentatives")
        #print(start_date)
        #print(liste)
                
    print("tous les fichiers ont bien ete telecharges")
    
    


# In[32]:


def generateSunubet():
    
    #global start_date
    global start_date
    global liste
    global attempt
    
    #url = "https://new-admin-sunubet.sporty-tech.net/reports/create"
    
    #for i in glob.glob(r'C:\Users\CFAC\Documents\jules\Stage\ExtractedFiles\Bwinner\Total Tax Report*'): 
        #os.remove(i)
            
        
    #browser.get(url)
    
    """
    time.sleep(5)
    
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[3]/div[1]/button"))).click()
    
    time.sleep(0.5)
    
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[3]/div[2]/div/hg-create-report-button/button"))).click()

    time.sleep(0.5)
    
    """
    
    #print(start_date,end_date,len(liste))
    
    while (start_date < end_date and len(liste)<11 ):
        
        #liste.append(start_date.strftime('%d/%m/%Y'))
        time.sleep(1)
        
        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[2]/div[2]/div/hg-create-report-button[2]/button"))).click()
        # /html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[5]/div[2]/div/hg-create-report-button/button
        WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[1]/div[2]/div/hg-create-report-button[4]/button"))).click()
        time.sleep(0.5)
        
        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[1]/button
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[1]/button"))).click()
        time.sleep(0.5)
        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[1]/div/button[2]
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[1]/div/button[2]"))).click()
        time.sleep(0.5)

    
    
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")

        #click on from input date

        time.sleep(0.5)
                                                                                        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/p-calendar/span/input
        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/p-calendar/span/input"))).click()
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar"))).click()
                                                                                        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar/span/input

        time.sleep(0.5)

        #click on year
                                                                                        #/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/p-calendar/span/div/div[1]/div/div[1]/div/button[2]
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar/span/div/div[1]/div/div[1]/div/button[2]"))).click()
                                                                                        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar/span/div/div[1]/div/div[1]/div/button[2]

        time.sleep(0.5)

        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[2]/span"))).click()

        #for i in WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[2]/span")))
        #for i in WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[2]/span")))

                                                            # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/p-calendar/span/div/div[2]
        for i in browser.find_elements(by=By.XPATH, value="/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar/span/div/div[2]/span"):
                                                            # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar/span/div/div[2]
            #print(i.text)
            if start_date.strftime('%Y') in i.text:
                i.click()
                break
        #time.sleep(5)
        for i in browser.find_elements(by=By.XPATH, value="/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar/span/div/div[2]/span"):
                                                            # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar/span/div/div[2]/span[6]
            #print(i.text)
            if start_date.strftime('%b') in i.text:
                i.click()
                break


        time.sleep(0.5)
        aa = 0
        
                                                        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/p-calendar/span/div/div[1]/div/div[2]/table/tbody
        for i in browser.find_elements(by=By.XPATH, value="/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar/span/div/div[1]/div/div[2]/table/tbody/*/*/span[not(contains(@class, 'p-disabled'))]"):
                                                        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[4]/hg-calendar/div/p-calendar/span/div/div[1]/div/div[2]/table/tbody/tr[1]/td[4]/span
            #print(i.text)
            
            if (str(0)+i.text.strip())[-2:] in start_date.strftime('%d'):
                aa = 1
                i.click()
                break
        
        time.sleep(0.5)

        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        
        time.sleep(0.5)

        #click on to input date
                                                                                        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/input
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar"))).click()

        time.sleep(0.5)
        
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar/span/div/div[2]/div[3]/button[1]"))).click()
        
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar/span/div/div[2]/div[1]/button[1]"))).click()


        #click on year
                                                                                        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[1]/div/div[1]/div/button[2]
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar/span/div/div[1]/div/div[1]/div/button[2]"))).click()

        time.sleep(0.5)
        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[2]/span"))).click()

        #for i in WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[2]/span")))
        #for i in WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[2]/span")))

                                                            # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[2]
        for i in browser.find_elements(by=By.XPATH, value="/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar/span/div/div[2]/span"):
            #print(i.text)
            if (start_date+delta).strftime('%Y') in i.text:
                i.click()
                break
                                                            # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[2]
        for i in browser.find_elements(by=By.XPATH, value="/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar/span/div/div[2]/span"):
            #print(i.text)
            if (start_date+delta).strftime('%b') in i.text:
                i.click()
                break


        time.sleep(0.5)
                                                        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/p-calendar/span/div/div[1]/div/div[2]/table/tbody
        for i in browser.find_elements(by=By.XPATH, value="/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar/span/div/div[1]/div/div[2]/table/tbody/*/*/span[not(contains(@class, 'p-disabled'))]"):
            #print(i.text)
            #if start_date.strftime('%d') in i.text:
            if (str(0)+i.text.strip())[-2:] in (start_date+delta).strftime('%d'):
                i.click()
                break

        # click generate button
                                                                                        # /html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/button
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/button"))).click()
      
        """
        try:
            libelle = 'Le rapport a été généré avec succès.'
            WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'"+libelle+ "')]")))
            #time.sleep(0.5)
            #browser.execute_script("window.scrollTo(document.body.scrollHeight,0)")
            #liste.append(start_date.strftime('%d/%m/%Y'))
            #print(f"le fichier sunubet DepositWithdrawalHistory du {start_date} a bien ete genere")
            #start_date+=delta
            #break
            attempt = 0
        except:
            #print(f"le fichier virtuel amabel du {start_date} n'a pas ete genere")
            #pass
            
            attempt+=1
            if attempt==2:
                attempt = 0
                start_date+=delta
                print(f"le fichier Online sunubet du {start_date} n'a malheuresement pas pu ete genere")
            url = "https://new-admin-sunubet.sporty-tech.net/reports/create"

            browser.get(url)
            
            continue

                                                                                            

        # loop to download

        #downloadAfitechFiles()
        
        """
        liste.append(start_date.strftime('%d/%m/%Y'))
        print(f"le fichier Online sunubet du {start_date} a bien ete genere")

        start_date+=delta

    
  
  
    
    


# In[33]:


def downloadAfitechFiles():
    #timer = 60+30
    #while timer>=0:
    #laDate = start_date.strftime('%d/%m/%Y')
    
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        WebDriverWait(browser,timeout=10*3).until( EC.presence_of_element_located(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/hg-header/div/div/hg-topbar-infos/div/div[2]/div[2]/button/div/span")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        #print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    
    
    global liste
    global start_date
    
    while len(liste)>0:
        
        laDate = liste[0]
        laDate1 = (datetime.datetime.strptime(str(laDate), "%d/%m/%Y")+delta).strftime('%d/%m/%Y')
        
        
        #print(laDate,liste[0])
        
        notDone  = True
        
        for i in glob.glob(filesInitialDirectory+'*GlobalBettingHistory*cs*'): 
            os.remove(i)
            

        while notDone:


            url = "https://new-admin-sunubet.sporty-tech.net/reports/history"

            browser.get(url)
                
            WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div/div/div[2]/table")))
            
            time.sleep(0.5)
            
            #break
                                                                
            for tr in browser.find_elements(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div/div/div[2]/table/tbody/tr"):
                a=0
                listee=[]
                for td in tr.find_elements(by=By.TAG_NAME, value="td") :
                    #print(a,td.text)
                    if a == 2 and "GlobalBettingHistory" not in td.text:
                        break
                    if (a ==3) and "CSV" not in td.text.upper():
                        break
                    if (a == 4) and str(laDate) not in td.text:
                        break
                    if (a ==5) and str(laDate1) not in td.text:
                        break

                    #print(td.text)
                    listee.append(td.text)
                    a+=1

                if a >5 and "Erreur" in listee[6]:
                    WebDriverWait(tr,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "td[9]/div/i"))).click()
                    
                    actions = ActionChains(browser) 

                    actions.send_keys(Keys.ENTER)

                    actions.perform()
                    
                    start_date-=delta
                    
                    liste.remove(laDate)
                    
                    return
                    
                
                if a >5 and "Disponible" in listee[6]:
                    #if listee[4]==listee[5] and str(laDate) in listee[4] :
                    if str(laDate) in listee[4] and str(laDate1) in listee[5] :
                    
                        #print("oh yes")
                        WebDriverWait(tr,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "*/div/div/i"))).click()
                        #break

                        timer = 60*30

                        while timer>=0:
                            time.sleep(3)
                            timer-=3
                            p=glob.glob(filesInitialDirectory+'*GlobalBettingHistory*csv') 
                            if len(p)>0:
                                #print(p[0])
                                
                                #'''
                                df = pd.read_csv(p[0],sep=';')#,index_col=False)
                                
                                df.to_csv(filesInitialDirectory+"OnlineSunubetTemp.csv",sep=';')
                                df = pd.read_csv(filesInitialDirectory+"OnlineSunubetTemp.csv",sep=';',index_col=False)#,index_col=None)
                                
                                df.columns = ['BetId', 'IssueDateTime', 'SettlementDateTime', 'Number', 'CustomerLogin', 'Stake','Freebet',
                                               'State', 'PaidAmount', 'InitalMaxPayout', 'CurrentMaxPayout',
                                               'InitialBonusAmount', 'FinalBonusAmount', 'BetCategory',
                                               'EventCategoryOrDrawGameType', 'SingleOrMultiple', 'BetLines',
                                               'bad1','bad2']

                                df = df.drop("bad1", axis='columns')
                                df = df.drop("bad2", axis='columns')
                                

                                #df['IssueDateTime'] = str(laDate)
                                
                                #'''
                                
                                #df = pd.read_csv(p[0],sep=';',index_col=False)
                                #df = pd.read_csv(p[0],sep=';')
                                
                                dd = datetime.datetime.strptime(str(laDate), "%d/%m/%Y")
                                #print(dd.strftime('%Y'))
                                df['JOUR'] = str(laDate)
                                df['ANNEE'] = str(dd.strftime('%Y'))
                                df['MOIS'] = str(dd.strftime('%m'))
                                
                                if os.path.exists(filesInitialDirectory+"OnlineSunubetTemp.csv"):
                                    os.remove(filesInitialDirectory+"OnlineSunubetTemp.csv")
        
                                
                                if os.path.exists(filesInitialDirectory+"onlineSunubet "+str((datetime.datetime.strptime(str(laDate), '%d/%m/%Y')))[:10]+".csv"):
                                    os.remove(filesInitialDirectory+"onlineSunubet "+str((datetime.datetime.strptime(str(laDate), '%d/%m/%Y')))[:10]+".csv")
        
                                
                                #df.to_csv(r"C:\Users\CFAC\Documents\jules\Stage\ExtractedFiles\sunubet\casinoLonasebet "+str((datetime.datetime.strptime(str(laDate), '%d/%m/%Y')))[:10]+".csv",index=False,sep=';',columns=["Id","Channel","State","Stake"])#,columns=['Report Date', 'Name','Total Stakes','Total Paid Win'])
                                #df.to_csv(r"C:\Users\CFAC\Documents\jules\Stage\ExtractedFiles\sunubet\OnlineSunubet "+str((datetime.datetime.strptime(str(laDate), '%d/%m/%Y')))[:10]+".csv",index=False,sep=';')#,columns=['Report Date', 'Name','Total Stakes','Total Paid Win'])
                                df.to_csv(filesInitialDirectory+"onlineSunubet "+str((datetime.datetime.strptime(str(laDate), '%d/%m/%Y')))[:10]+".csv",index=False,sep=';')#,columns=['Report Date', 'Name','Total Stakes','Total Paid Win'])
                                #df.to_csv(filesInitialDirectory+"onlineSunubet "+str((datetime.datetime.strptime(str(laDate), '%d/%m/%Y')))[:10]+".csv",sep=';')#,columns=['Report Date', 'Name','Total Stakes','Total Paid Win'])

                                #excl_list.append(df[["Id","Channel","State"]])

                                print(f"le fichier Online sunubet du {laDate} a bien ete telecharge")

                                os.remove(p[0])
                                #liste.remove(laDate)
                                try:
                                    liste.remove(laDate)
                                    laDate = liste[0]
                                except:
                                    pass
                                
                                
                                #excl_list.append(df[["JOUR","STAKE", "PAIDAMOUNT","BETCATEGORYTYPE", "FREEBET"]])
                                
                                #print(liste)
                                #print(len(liste))


                                notDone = False

                                break
                        if timer<0:
                            print("Le chargement est anormalement long, nous allons recommencer")
                            continue

        
        #liste.pop(0)
            for i in glob.glob(filesInitialDirectory+'*GlobalBettingHistory*cs*'): 
                os.remove(i)
                
            time.sleep(30)

        
    #print("Done")


# In[ ]:





# In[ ]:





# In[34]:


attempt = 0
aaaa=10

excl_list = []
#start_date = datetime.date(2022, 8, 5)

#debut = datetime.date(2022, 5, 11)

#end_date = datetime.date(2022, 9, 1)

liste = []
doneliste = []

delta = timedelta(days=1)

end_date = date.today()#- delta
delta = timedelta(days=1)
start_date = end_date - delta


delta = timedelta(days=1)




#start_date = date(2024, 12, 3)
#end_date = start_date+delta


#end_date = datetime.date(2024, 12, 1)

#debut = datetime.date(2022, 9, 6)

filesInitialDirectory = r"K:\DATA_FICHIERS\SUNUBET\ONLINE\\"


debut1 = start_date
fin1 = end_date-delta


#browser=openBrowser()
#browser.maximize_window()
#connectSunubet()


#"""
for i in range(5):
    try:
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectSunubet()

        
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


#browser = openBrowser()

#"""


# In[35]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_OnlineSunubet.py").read())


# In[36]:


#d = dir()

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




