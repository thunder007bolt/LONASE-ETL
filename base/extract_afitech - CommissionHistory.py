#!/usr/bin/env python
# coding: utf-8

# In[217]:


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




import pandas as pd
import numpy as np
import win32com.client
import os
import re
#import shutil


import pyotp


# In[218]:


#o = win32com.client.gencache.EnsureDispatch('Excel.Application')
#o.Visible = False


# In[ ]:





# In[219]:





# In[220]:


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


# In[221]:


def connectAfitech():
    
    
    url = "https://lonase-prod.afite.ch/login"
    browser.get(url)
    
    time.sleep(5)
    
    #usrname = wait2.until( EC.element_to_be_clickable(( By.ID, usernameId)) )
    #usrname.send_keys(username)
    usernameId="login" 
    username = 'Senghane_diouf' 
    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    
    #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/hg-root/hg-app-login/div/div[2]/div/div/div[1]/hg-authentication/form/div[1]/input'))).send_keys(username)
    
    
    #pwd = wait2.until( EC.element_to_be_clickable(( By.ID, passwordId)) )
    #pwd.send_keys(password)
    passwordId = 'password'
    password = "Senghane2021"
    #browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    
    #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/hg-root/hg-app-login/div/div/div[2]/div/div/div/div[2]/hg-authentication/div[2]/form/div[2]/div[1]/input'))).send_keys(password)
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, '/html/body/hg-root/hg-app-login/div/div[2]/div/div/div[1]/hg-authentication/form/div[2]/div[1]/input'))).send_keys(password)
    
    
    #browser.find_element(by=By.XPATH, value="//button[@type='submit']").click()
                                                                                    # /html/body/hg-root/hg-app-login/div/div/div[2]/div/div/div/div[2]/hg-authentication/div[2]/form/div[3]/button
    
    #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.XPATH, "//button[@type='submit']"))).click()
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "//button[@type='submit']"))).click()
    
    try:
                                                                                            #/html/body/hg-root/hg-app-login/div/div[2]/div/div/div[1]/hg-authentication/div[2]/p-dropdown/div/span
        WebDriverWait(browser,timeout=3).until( EC.presence_of_element_located(( By.XPATH, "/html/body/hg-root/hg-app-login/div/div[2]/div/div/div[1]/hg-authentication/div[1]/span")))
        WebDriverWait(browser,timeout=3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-app-login/div/div[2]/div/div/div[1]/hg-authentication/div[2]/p-dropdown/div/span"))).click()
        WebDriverWait(browser,timeout=3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/div/div/div/ul/p-dropdownitem[3]/li"))).click()
        
        time.sleep(1)

        #WebDriverWait(browser,timeout=3).until( EC.element_to_be_clickable(( By.TAG_NAME, "input"))).send_keys( pyotp.parse_uri('otpauth://totp/senghane_diouf?secret=7KMWXMWE56ZLBCBK&issuer=Lonase&algorithm=SHA256&digits=6&period=30').now() )
        
        # /html/body/hg-root/hg-app-login/div/div[2]/div/div/div[1]/hg-authentication/div[2]/div/hg-code/div/input[1]
        
        WebDriverWait(browser,timeout=3).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-app-login/div/div[2]/div/div/div[1]/hg-authentication/div[2]/div/hg-code/div/input[1]"))).send_keys( pyotp.parse_uri('otpauth://totp/senghane_diouf?secret=7KMWXMWE56ZLBCBK&issuer=Lonase&algorithm=SHA256&digits=6&period=30').now() )
        
        
    except:
        pass
    
    
    #driver.find_element_by_xpath("//button[@type='submit']").click()
    #time.sleep(10*3) 
    
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        
        # /html/body/hg-root/hg-layout/div/hg-topbar/header/div/div[2]/div[3]/button/span
        
        #WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/hg-root/hg-layout/div/hg-topbar/header/div/div[2]/div[4]/button/span")))
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/hg-root/hg-layout/div/hg-topbar/header/div/div[2]/div[5]/hg-profile-avatar/p-avatar/div/span")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    
    #print("la connection a la plateforme est un succes")
    #downloadAfitechFiles()
    #return
    
    #generateAfitechFiles()
    #return
    
    #"""
    for i in range(3):
        try:
            generateAfitechFiles()
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
            
    #excl_merged = pd.concat(excl_list, ignore_index=True)
    
    #print(excl_merged.head())
    
    #print(excl_list.head())
    
    #if debut1<fin1:
        
        #excl_merged.to_csv(filesInitialDirectory+"mergeAfitech_CommissionHistory"+str(debut1)+"_"+str(fin1)+".csv" , index=False,sep=';',encoding='utf8')
    
    #bwinnerManipulation(excl_merged,debut1,fin1)


    #"""
    
    #tryGenFiles()
    
    #for i in range(15):
        
        
    #generateAfitechFiles()

    


# In[ ]:





# In[222]:


def generateAfitechFiles():
    
    url = "https://lonase-prod.afite.ch/reports/create"
    
    #browser.get(url)
    
    #time.sleep(3)
   
   #driver.find_element_by_class_name("form-control").click()
    #WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.CLASS_NAME, "form-control"))).click()
    
   #frmc = wait2.until( EC.element_to_be_clickable(( By.CLASS_NAME,"form-control")) )
   #frmc.click()
   #time.sleep(3)

    #WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "//option[@value='OperationHistory']"))).click()
   
   #driver.find_element_by_xpath("//option[@value='OperationHistory']").click()
    global generated
    
    global start_date
    
    global lastMonth
    
    global excl_list
    
    global attempt
    
    #start_date = datetime.date(2022, 1, 1)
    #end_date = datetime.date(2022, 2, 1)
    #delta = datetime.timedelta(days=1)
   
   #for day in range(start_date,end,1):
    global i
    
    for i in glob.glob(filesInitialDirectory+'*CommissionHistory*.xls*'): 
        os.remove(i)
        
    #return
    
    while start_date < end_date:
        
        lastMonth = date(start_date.year, start_date.month, calendar.monthrange(start_date.year, start_date.month)[1])
        if end_date <= lastMonth :
            lastMonth = end_date - delta

        
        if generated is False:


            browser.get(url)
            
            time.sleep(1)
            #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.CLASS_NAME, "form-control"))).click()
            
            #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.CLASS_NAME, "form-control"))).send_keys("Daily Payment Activity")
            WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/div[2]/div/p-dropdown/div/span"))).click()
            
            WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/div/div/div/ul/p-dropdownitem[9]/li"))).click()
            #categorie = Select(browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/div/div/div/div/div/select"))
            #categorie.select_by_visible_text("23")
            #drpCountry.selectByValue("234")
            #categorie.select_by_value("DailyPaymentActivity")
            
            time.sleep(1)
            #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.XPATH, "//option[@value='OperationHistory']"))).click()
            #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.XPATH, "//option[@value='PaymentOperationHistory']"))).click()
            #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.XPATH, "//option[@value='PaymentOperationHistory']")))
            #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.XPATH, "//option[@value='PaymentOperationHistory']"))).send_keys("Payment Operations History")
            #time.sleep(1)

            start = str(start_date).split("-")
            start = start[2]+'/'+start[1]+'/'+start[0]


            #WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.CLASS_NAME, "ng-tns-c64-0.p-inputtext.p-component.ng-star-inserted"))).click()
            #time.sleep(1)
            
            
            #driver.find_element_by_class_name("ng-tns-c64-0.p-inputtext.p-component.ng-star-inserted").click()
            #time.sleep(4)

            #debut = browser.find_element(by=By.CLASS_NAME, value="ng-tns-c64-0.p-inputtext.p-component.ng-star-inserted")
            #debut = browser.find_element(by=By.CLASS_NAME, value="ng-tns-c77-0 p-inputtext p-component ng-star-inserted")
            debut = browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/hg-report-request-generator/div/div/form/div[1]/p-calendar/span/input")
            debut.clear()
            debut.send_keys(start+ Keys.ENTER)
            time.sleep(1)

            #driver.find_element_by_class_name("ng-tns-c64-0.p-inputtext.p-component.ng-star-inserted").clear()
            #driver.find_element_by_class_name("ng-tns-c64-0.p-inputtext.p-component.ng-star-inserted").send_keys(start+ Keys.ENTER)



            #driver.find_element_by_xpath("//*[@id="layout-wrapper"]/div/div/hg-create-report/div/div/div/div/div/hg-report-request-generator/div/form/div[1]/div/p-calendar/span/input").send_keys(start)
            # ng-tns-c64-0 p-inputtext p-component ng-star-inserted
            #driver.find_element_by_class_name("ng-tns-c64-0 p-inputtext p-component ng-star-inserted").send_keys(start)



            #firstCalendar = driver.

           #driver.find_element_by_xpath("//span[text()='"+str(start)+"']").click()
            # elt in driver.find_elements_by_xpath("//span[text()='"+str(start)+"']"):



            #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.CLASS_NAME, "ng-tns-c64-1.p-inputtext.p-component.ng-star-inserted"))).click()
            
            #time.sleep(1)
            
            
            
            #driver.find_element_by_class_name("ng-tns-c64-1.p-inputtext.p-component.ng-star-inserted").click()
            #time.sleep(4)

            #fin = browser.find_element(by=By.CLASS_NAME, value="ng-tns-c64-1.p-inputtext.p-component.ng-star-inserted")
            #fin = browser.find_element(by=By.CLASS_NAME, value="ng-tns-c77-1 p-inputtext p-component ng-star-inserted")
            start = str(lastMonth).split("-")
            start = start[2]+'/'+start[1]+'/'+start[0]
            fin = browser.find_element(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/hg-report-request-generator/div/div/form/div[2]/p-calendar/span/input")
            fin.clear()
            fin.send_keys(start+ Keys.ENTER)
            time.sleep(1)

            #driver.find_element_by_class_name("ng-tns-c64-1.p-inputtext.p-component.ng-star-inserted").clear()
            #driver.find_element_by_class_name("ng-tns-c64-1.p-inputtext.p-component.ng-star-inserted").send_keys(start+ Keys.ENTER)





            #driver.find_element_by_xpath("/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/div/div/div/div/hg-report-request-generator/div/form/div[2]/div/p-calendar/span/input").click().clear().send_keys(start)


           #driver.find_element_by_xpath("//span[text()='"+str(start)+"']").click()
            #time.sleep(4)


            #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.XPATH, "//div[@class='card-body']//button[@type='button']"))).click()#//*[@id="layout-wrapper"]/div/div/hg-create-report/div/div/div/div/div/hg-report-request-generator/div/form/div[8]/button

            #btn btn-primary btn-rounded

            #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.CLASS_NAME, "btn btn-primary btn-rounded"))).click()


            #browser.find_element(by=By.XPATH, value = "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/div/div/div/div/hg-report-request-generator/div/form/div[8]/button").click()
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            #time.sleep(1.5)
            WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/hg-report-request-generator/div/div/form/div[6]/hg-button/button"))).click()
            #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.CLASS_NAME, "btn btn-primary btn-rounded"))).click()
            #browser.find_element(by=By.XPATH, value = "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/div/div/div/div/hg-report-request-generator/div/form/div[8]/button").click()
            time.sleep(1)
            #/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/div/div/div/div/hg-report-request-generator/div/form/div[8]/button

            #element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//ngb-alert[contains(text(),'"+libelle+ "')]")))

            #generated = True
            
            #print(f"le fichier CommissionHistory de la plateforme AFITECH  du {start_date} au {lastMonth} a bien ete genere")
            
            try:
                element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'"+libelle+ "')]")))
                generated = True
                print(f"le fichier CommissionHistory de la plateforme AFITECH  du {start_date} au {lastMonth} a bien ete genere")
                attempt = 0
            except:
                attempt+=1
                if attempt==2:
                    print(f"le fichier CommissionHistory de la plateforme AFITECH  du {start_date} au {lastMonth} suite a {attempt+1} tentatives n'a malheuresement pas pu ete telecharge")
                    start_date = lastMonth+delta
                    attempt = 0

                continue
        


        '''
        try:
            element = WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.XPATH, "//ngb-alert[contains(text(),'"+libelle+ "')]")))
            #print('trouve')
            #browser.quit()
            #a = 2
        except:
            generateAfitechFiles()
            #start_date-=delta
        '''
            
        
        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "//div[@class='card-body']//button[@type='button']"))).click()
        #browser.find_element_by_xpath("//div[@class='card-body']//button[@type='button']").click()
        #driver.find_element_by_xpath("//div[@class='card-body']//button[@type='button']").click()
        #time.sleep(10)
        
        #downloadAfitechFiles()
        #return
        for i in range(3):
            try:
                #downloadAfitechFiles()
                downloadAfitechFiles()
                #return
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
        timer = 60+30

        while timer>=0:
            time.sleep(5)
            timer-=5

            #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            
            #p=glob.glob(f'C:\\Users\\OPTIWARE-ENTERPRISE\\Downloads\\*OperationHistory*') CFAC
            p=glob.glob(f'C:\\Users\\CFAC\\Downloads\\*OperationHistory*') 
            if len(p)>0:
                #print(p[0])
                break
        if timer<0:
            print("Le chargement est anormalement long, nous allons recommencer")
            continue
        
        """
        
        timer = 60

        while timer>=0:
            time.sleep(1)
            timer-=1

            #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            
            #p=glob.glob(f'C:\\Users\\OPTIWARE-ENTERPRISE\\Downloads\\*OperationHistory*.xlsx')
            #PaymentOperationHistory
            #p=glob.glob(f'C:\\Users\\OPTIWARE-ENTERPRISE\\Downloads\\*PaymentOperationHistory*.xlsx') CFAC
            p=glob.glob(filesInitialDirectory+'*CommissionHistory*.xlsx') 
            if len(p)>0:
                #print(p[0])
                #filename = p[0].split("\\")[-1]
                filename = "AFITECH_CommissionHistory "+str(start_date)+"_"+str(lastMonth)+".csv"
                #shutil.move(path+filename,filesInitialDirectory+filename)
                
                #print(f"le fichier de la plateforme Premier SN du {start_date} a bien ete telecharge et deplace")
                #print(f"le fichier de la plateforme zone betting du {start_date} a bien ete telecharge")
                
               
            
                #wb = o.Workbooks.Open(path+filename)
                """
                print(p[0])
                wb = o.Workbooks.Open(p[0])
                o.Sheets('Data').Select()
                #C:\\Users\\OPTIWARE\\Documents\\jules\\Stage\\ExtractedFiles\\
                #o.ActiveWorkbook.SaveAs('/Users/hp/website_login/'+filename.replace(".xlsx",".csv"), FileFormat=24) #
                #o.ActiveWorkbook.SaveAs('C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\AFITECH_2022_02_04\\'+filename.replace(".xlsx",".csv"), FileFormat=24) #
                o.ActiveWorkbook.SaveAs(filesInitialDirectory+filename, FileFormat=24) #
                o.ActiveWorkbook.Close(SaveChanges=0) 
                o.Quit()
                """
                #shutil.move(path+filename,filesInitialDirectory+filename)
                
                
                #df = pd.read_csv(filesInitialDirectory+filename,sep=";")
                df = pd.read_excel(p[0],sheet_name='Data')
                excl_list.append(df)
                #df.to_csv(filesInitialDirectory+filename,sep=";",index=False)
        
                if os.path.exists(filesInitialDirectory+filename):
                    os.remove(filesInitialDirectory+filename)
        
                df.to_csv(filesInitialDirectory+filename,sep=";",index=False)
                # "\\192.168.60.4\cg\DFP\AFITECH\CommissionHistory"
                
                generated = False
                os.remove(p[0])
                print(f"le fichier de la plateforme afitech CommissionHistory du {start_date} au {lastMonth} a bien ete telecharge")
                start_date=lastMonth+delta
                
                break
            
            
            #if  "block" not in browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"):
                #break
        #url = "https://editec.virtual-horizon.com/engine/backoffice/"
        
        #browser.get(url)
        
        if timer<0:
            print("Le telechargement est anormalement long, nous allons recommencer")
            continue

        
        
        i+=1
        #start_date+=delta
        #start_date=lastMonth+delta
        
        #for i in glob.glob(f'C:\\Users\\OPTIWARE-ENTERPRISE\\Downloads\\*PaymentOperationHistory*.xlsx'): CFAC
        for i in glob.glob(filesInitialDirectory+'*CommissionHistory*.xls*'): 
            os.remove(i)
        
        #time.sleep(4)
        
    #downloadAfitechFiles()
    print("tous les fichiers ont bien ete telecharge")
    
    for i in glob.glob(filesInitialDirectory+'*CommissionHistory*xls*'):
        os.remove(i)
        
    
    


# In[ ]:





# In[ ]:





# In[223]:


def downloadAfitechFiles():
    #timer = 60+30
    #while timer>=0:
    laDate1 = start_date.strftime('%d/%m/%Y')
    laDate2 = lastMonth.strftime('%d/%m/%Y')
    #print(laDate1,laDate2)
    #print(laDate)
    #global liste
    
    #while len(liste)>0:
        
    #laDate = liste[0]

    #print(laDate,liste[0])

    notDone  = True

    while notDone:

        #if timer



        #browser.maximize_window()



        url = "https://lonase-prod.afite.ch/reports/history"

        #time.sleep(10)
        
        browser.get(url)
        
        #return

        time.sleep(5)
                                                            # /html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div/div/div[3]/div/p-table/div/div/table/tbody/tr[1]
        #for tr in browser.find_elements(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div/div/div[3]/div/p-table/div/div/table/tbody/tr"):
        for tr in browser.find_elements(by=By.XPATH, value="/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div[3]/div/p-tabview/div/div[2]/p-tabpanel[1]/div/p-table/div/div/table/tbody/tr"):

            
            a=0
            #print(tr.text)
            #print('\n')
            listee=[]
            for td in tr.find_elements(by=By.TAG_NAME, value="td") :
                #print(a)

                #print(a,td.text)
                if a == 1 and "CommissionHistory" not in td.text:
                    break
                if (a == 2) and str(laDate1) not in td.text:
                    break
                if (a ==3) and str(laDate2) not in td.text:
                    break

                #print(td.text)
                listee.append(td.text)
                a+=1
                #print(listee,laDate1,laDate2)
            #print(listee,laDate1,laDate2)

                if a >4 and ("Available" in listee[4] or "Incomplete" in listee[4]):
                    #if listee[2]==listee[3] and str(laDate) in listee[3] :
                    if laDate1 in listee[2] and  laDate2 in listee[3]:
                        #print("oh yes")
                        #print(tr.text)
                        #tr.find_element(by=By.XPATH, value="//span[@class='download ng-star-inserted']").click()
                        tr.find_element(by=By.XPATH, value="*/span/span/i").click()
                        WebDriverWait(tr,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "*/span/span/i"))).click()
                        notDone = False
                        break

        
#print("Done")


# In[ ]:





# In[224]:


attempt = 0

excl_list = []
lastMonth = 0
i = 0

libelle = 'Report created successfully'

#start_date = datetime.date(2022, 8, 5)

#debut = datetime.date(2022, 5, 11)

#end_date = datetime.date(2022, 9, 1)
delta = datetime.timedelta(days=1)

end_date = datetime.date.today()
delta = datetime.timedelta(days=1)
#start_date = end_date -  delta
start_date = datetime.date((end_date -  delta).year, (end_date -  delta).month, 1)
#start_date = datetime.date(2023, 4, 18)

delta = datetime.timedelta(days=1)


#start_date = datetime.date(2025, 5, 21)
#end_date = start_date+delta
#end_date = datetime.date(2025, 5, 1)

#debut = datetime.date(2022, 9, 6)

filesInitialDirectory = r"K:\DATA_FICHIERS\AFITECH\CommissionHistory\\"


#filesInitialDirectory = 
debut1 = start_date
fin1 = end_date-delta

generated = False

#browser=openBrowser()
#connectAfitech()


#"""
for i in range(5):
    try:
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectAfitech()

        
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
        #sys.exit(f"Impossible d'executer ce programme malgre 10 tentatives")
        break

        

#browser = openBrowser()

#"""




#extract_afitech(driver,"https://lonase-prod.afite.ch/login","login", 'Senghane_diouf', "password", 'Senghane2021', "",'daily',0,0)


# In[ ]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_Afitech_CommissionHistory.py").read())


# In[ ]:


#import gc

#gc.collect()


# In[225]:


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


#downloadAfitechFiles()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




