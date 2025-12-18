#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


def edit_str(val):
    
    #print(val)
    
    #if np.isnan(val):
    
    if pd.isnull(val) or val == " " or val == "":
        #print("ceci est une chaine vide")
        return str("")
        #print("il s'agit d'un nan putain")
    
    #print(val)
    
    if "." in val:
        
        val = val.replace(".","")
        val = val.replace(",",".")
        
        #print(convert_float_to_str(val))
        
        return convert_float_to_str(val)
    return str(val)


# In[3]:













def convert_float_to_str(val):
    
    #if np.isnan(val):
    
        #print("il s'agit d'un nan putain")
    #print(val)
    new_val = str(val).split(".")
            #print(date1)
    #print(new_val)
    if int(new_val[1]) == 0:
        new_val = new_val[0]
    else:
        new_val = str(new_val[0]) + "," + str(new_val[1])
    #print("nouvelle valeur flottante")
    #print(new_val)
    return str(new_val)






def convert_date_to_str(val):
    
    date1 = copy(str(val)[:10])
            #print(date1)
    date1 = date1.split("-")
            #print(date1)
    date1[0],date1[2]= date1[2],date1[0]
            #print(date1)
    date1 = str(date1[0])+"/"+str(date1[1])+"/"+str(date1[2])
            #print(date1)
    #row[i] = copy(date1)
            #ligne.append(row[i])    
    #new_val = val.replace(',','').replace('$', '')
    #print(date1)
    return str(date1)








def transformFinancial(nomFichier):
    
    global excl_list
        

    data = copy(pd.read_csv(nomFichier , header=1,sep=";"))
    
    data = data.loc[:, data.columns!='Username']


    #print(data.dtypes)
    #data = data [:-1]

    #first_row = data.iloc[0]
    #first_row = data.columns
    #print(first_row)
    #print("jules")

    #my_data = []

    #for i in first_row:
    #    for  index,row in data.iterrows():


    for column in data.columns:
        
        #print(data[column])
        
        if  np.issubdtype(data[column].dtype, np.datetime64):
            
            #data[column] = np.where( pd.isna(data[column]), "jules", "dakho")
            #continue
            
            data[column]=data[column].apply(convert_date_to_str)
            
            #data[column].astype('str')
            
            #print("une date")
            #print(type(data[column]))
            
        elif  np.issubdtype(data[column].dtype, np.float_):
            
            
            
            #data[column] = np.where( pd.isna(data[column]), "jules", "dakho")
            #continue
            
            data[column]=data[column].apply(convert_float_to_str)
            
            #data[column]=data[column].apply(lambda x: '%.17f' % x)
            
            #data[column].astype('str')
            #data[column].astype(int)
            #data[column].astype('str')
            #print(type(data[column]))
            #print("un float")
            #pd.(df['Jan Units'], errors='coerce').fillna(0)
        else:
            
            #data[column] = np.where( pd.isna(data[column]), "jules", "dako")
            #continue
            
            #format_str(val)
            data[column]=data[column].apply(edit_str)
            #data[column]=data[column].astype('str')
            
            #print(type(data[column]))
            #print("prolly un str deja")
        #print(data[column])
        #print(data[column])
    #data['Name'] = 'jules'
    
    temp,i=0,0
    
    for dat in data['Name']:
        #print(f"i={i}")
        #print( type(dat))
        #print(len(dat))
        if dat == "" or pd.isnull(dat) or dat==str() or dat == " ":
            #a+=1
            #print("donnee vide")
            #print(temp)
            
            #data=temp
            #print(f"i={i}")
            data.at[i,'Name']=temp
            i+=1
            continue
        #data=temp
        #print(dat)
        temp = dat
        #print(temp)
        i+=1
        
    
        
    #data["Montant"] = np.where(data["Montant"] is float, "True", False)

    #print(data[:6])

    #data.to_excel("Listing_Tickets_Pick3.xlsx", index=False)

    #print(ourDataFrame.shape)


    #print(ourDataFrame)
    #nomFichier = nomFichier.split('/')[-1]
    #data.to_csv(nomFichier.split('/')[-1] , index=False, sep=";",encoding='utf-8')
    
    
    data["date"] = start_date.strftime('%d/%m/%Y')

    #data.to_csv(nomFichier , index=False, sep=";",encoding='utf-8')
    
    if os.path.exists(filesInitialDirectory+"Financial "+str(start_date)+".csv"):
        os.remove(filesInitialDirectory+"Financial "+str(start_date)+".csv")
        
    
    data.to_csv(filesInitialDirectory+"Financial "+str(start_date)+".csv" , index=False, sep=";",encoding='utf-8')
    #excl_list.append(data)
    # filesInitialDirectory


    print(f"le fichier du {start_date} a bien ete tranforme")



# In[4]:


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


# In[5]:


def generateFinancial():
    
    #url = "https://editec.virtual-horizon.com/engine/backoffice/"
        
    #browser.get(url)
    
    #jour = str(datetime.datetime.today()).split()[0]
    #jour = jour.split("-")[2]
    #"""
    dev = WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, "//img[@src='https://editec.virtual-horizon.com/engine/backoffice/backendUI/clear.cache.gif']")))
    #dev = wait2.until( EC.element_to_be_clickable(( By.XPATH, "//img[@src='https://editec.virtual-horizon.com/engine/backoffice/backendUI/clear.cache.gif']")) ) 


    #dev = wait2.until( EC.element_to_be_clickable(( By.CLASS_NAME, "")))
    dev.click()
    #time.sleep(60)

    #dr = WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "//div[text()='General Overview']")))

    #dr = wait2.until( EC.element_to_be_clickable(( By.XPATH, "//div[text()='General Overview']")))
    #driver.find_element_by_class_name("GA4RFAYIE.GA4RFAYOE")
    #dr.click() 

    WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div/div/table/tbody/tr[2]/td/div/div/div/div/div[1]/div[1]/div[2]/div/div[1]/div/div/div/div[2]/div/img"))).click()
    #"""
    
    for i in glob.glob(filesInitialDirectory+'*Financial Overview_All*cs*'):
        os.remove(i)

    
    weekDays = ["Mo","Tu","We","Th","Fr","Sa","Su"]
    
    global start_date
    #global end_date
    
    #start_date = datetime.date(2022, 2, 27)
    #end_date = datetime.date(2022, 3, 2)
    #delta = datetime.timedelta(days=1)
    while start_date < end_date:
        
        #url = "https://editec.virtual-horizon.com/engine/backoffice/"
        
        
        
        #print(start_date)
        
        #thatDay = start_date
        theDayAfter = start_date + delta
        jourAfter = str(theDayAfter).split("-")[2]
        
        jour = str(start_date).split("-")[2]
        #jour = jour.split("-")[2]
        #start_date += delta
        
        
        #browser.get("https://editec.virtual-horizon.com/engine/backoffice/index.htm#financial_overview:")

        #time.sleep(15)
        
        """

        dev = WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, "//img[@src='https://editec.virtual-horizon.com/engine/backoffice/backendUI/clear.cache.gif']")))
        #dev = wait2.until( EC.element_to_be_clickable(( By.XPATH, "//img[@src='https://editec.virtual-horizon.com/engine/backoffice/backendUI/clear.cache.gif']")) ) 


        #dev = wait2.until( EC.element_to_be_clickable(( By.CLASS_NAME, "")))
        dev.click()
        #time.sleep(60)
        
        #dr = WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "//div[text()='General Overview']")))

        #dr = wait2.until( EC.element_to_be_clickable(( By.XPATH, "//div[text()='General Overview']")))
        #driver.find_element_by_class_name("GA4RFAYIE.GA4RFAYOE")
        #dr.click() 
        
        WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div/div/table/tbody/tr[2]/td/div/div/div/div/div[1]/div[1]/div[2]/div/div[1]/div/div/div/div[2]/div/img"))).click()
        
        """
        
        #dev = WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "//img[@src='https://editec.virtual-horizon.com/engine/backoffice/backendUI/clear.cache.gif']")))
        #dev = wait2.until( EC.element_to_be_clickable(( By.XPATH, "//img[@src='https://editec.virtual-horizon.com/engine/backoffice/backendUI/clear.cache.gif']")) ) 


        #dev = wait2.until( EC.element_to_be_clickable(( By.CLASS_NAME, "")))
        #dev.click()
        
        #time.sleep(6)

        #browser.find_element(by=By.NAME, value=usernameId).send_keys(username)    
        WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div[3]/table/tbody/tr/td[2]/div/table/tbody/tr/td[2]/div/input"))).click()

        #browser.find_element(by=By.XPATH, value ="/html/body/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div[3]/table/tbody/tr/td[2]/div/table/tbody/tr/td[2]/div/input").click()
        #print("first click")
        
        # /html/body/div[3]/div/div/table/tbody/tr[2]/td[2]/div
        WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[3]/div/div/table/tbody/tr[2]/td[2]/div"))).click()
        
        while True:
            
            baliseDate = browser.find_element(by=By.XPATH, value = "/html/body/div[3]/div/div/table/tbody/tr[1]/td[1]").text
            #print(baliseDate)
            if theDayAfter.strftime("%B") in baliseDate and theDayAfter.strftime("%Y") in baliseDate :
                #print("first click1")
                break
            else : 
                browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[2]/td[1]/div").click()
        #print("first click2")
        #days = browser.find_elements(by=By.CLASS_NAME, value="days-table")


        #days = browser.find_elements(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[3]/td/table/tbody")


        #for day in days:
        
        """
        
        for td in browser.find_elements(by=By.TAG_NAME, value="td"):
            if td.text == str(int(jour)-0):
                #print("ceci est un str")
                td.click()

                time.sleep(6)
                #browser.find_element(by=By.CLASS_NAME, value = "switch-button switch-button-up").click()
                browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[4]/div").click()
                        #browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[4]/div/div")
                #a=1
                break
                
        """       #/html/body/div[3]/div/div/table/tbody/tr[3]/td/table/tbody


            
        #time.sleep(6)
        
        for balise in browser.find_elements(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[3]/td/table/tbody"):
            #print("in1")
            a=0

            #print(day.text)
            #print(type(day.text))

            for tr in balise.find_elements(by=By.TAG_NAME, value="tr"):
                #print("in2")
                for td in tr.find_elements(by=By.TAG_NAME, value="td"):
                    #print("in3")

                    #print(td.text)
                    #if td.text == "5":
                    
                    if td.text in weekDays:
                        continue
                    
                    #if td.get_attribute('class') == "disabled-day-cell":
                    if "disabled" in td.get_attribute('class'):
                        continue
                    
                    if td.text == str(int(jourAfter)):
                    #if int(td.text) == int(int(jour)-0):
                        #print("ceci est un str")
                        td.click()
                        
                        
                        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[1]/select"))).send_keys("00")
                        heure = Select(browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[1]/select"))
                        heure.select_by_visible_text("00")
            
                        #time.sleep(6)
                        #browser.find_element(by=By.CLASS_NAME, value = "switch-button switch-button-up").click()
                        
                        #browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[4]/div").click()
                        WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[4]/div"))).click()
                        #browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[4]/div/div")
                        a=1
                        break
                if a==1:
                    break
            if a==1:
                break
        





        #browser.find_element(by=By.XPATH, value = "/html/body/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div[3]/table/tbody/tr/td[1]/div/table/tbody/tr/td[2]/div/input").click()
        WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div[3]/table/tbody/tr/td[1]/div/table/tbody/tr/td[2]/div/input"))).click()
        #WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, ""))).click()
        
        # /html/body/div[3]/div/div/table/tbody/tr[2]/td[2]/div
        WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[3]/div/div/table/tbody/tr[2]/td[2]/div"))).click()


        while True:
            
            baliseDate = browser.find_element(by=By.XPATH, value = "/html/body/div[3]/div/div/table/tbody/tr[1]/td[1]").text
            if start_date.strftime("%B") in baliseDate and start_date.strftime("%Y") in baliseDate :
                break
            else : 
                #browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[2]/td[1]/div").click()
                
                WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[3]/div/div/table/tbody/tr[2]/td[1]/div"))).click()
 
        
        #time.sleep(3)
        
        for balise in browser.find_elements(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[3]/td/table/tbody"):
            a=0

            #print(day.text)
            #print(type(day.text))

            for tr in balise.find_elements(by=By.TAG_NAME, value="tr"):
                for td in tr.find_elements(by=By.TAG_NAME, value="td"):

                    #print(td.text)
                    #if td.text == "5":
                    if td.text in weekDays:
                        continue
                    #if td.get_attribute('class') == "disabled-day-cell":
                    if "disabled" in td.get_attribute('class'):
                        continue
                    if td.text == str(int(jour)):
                        #print("ceci est un str")
                        td.click()
                        
                        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[1]/select"))).send_keys("00")
                        heure = Select(browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[1]/select"))
                        heure.select_by_visible_text("00")
            

                        #time.sleep(6)
                        #browser.find_element(by=By.CLASS_NAME, value = "switch-button switch-button-up").click()
                        
                        #browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[4]/div/div").click()
                        WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[4]/div/div"))).click()
                        
                        #browser.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/table/tbody/tr[4]/td/table/tbody/tr/td[4]/div/div")
                        a=1
                        break
                if a==1:
                    break
            if a==1:
                break





            #tt = day.find_elements(by=By.)

            #for tt in browser.find_elements(by=By.)







        #zonetext.clear()
        #zonetext.send_keys("2022-04-05 00:00")

        #time.sleep(5)

        #browser.find_element(by=By.CLASS_NAME, value="GA4RFAYFBB").click()
        WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.CLASS_NAME, "GA4RFAYFBB"))).click()
        
        try:
            
            #libelle = f"Daily balance in currency on {str(start_date)}"
            libelle = f"Financial Overview report for agent All from {str(start_date)} 00:00 to {str(theDayAfter)} 00:00"
            #print(libelle)
            wantedDiv = WebDriverWait(browser,timeout=10).until( EC.presence_of_element_located(( By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div/div[2]/div[1][contains(text(), '" + libelle + "')]")))
        except:
            continue

        #time.sleep(2)
        #print("right here")

        #browser.find_elements(by=By.CLASS_NAME, value="gwt-Button")[-1].click()
        WebDriverWait(browser,timeout=5).until( EC.element_to_be_clickable(( By.CLASS_NAME, "gwt-Button")))#.click()
        browser.find_elements(by=By.CLASS_NAME, value="gwt-Button")[-1].click()
        #time.sleep(3)
        
        #time.sleep(2)
        

        #browser.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div/div[2]/div[2]/button[2]").click()

        #time.sleep(6)




        #list = browser.find_elements(by=By.CLASS_NAME, value="common-DatePicker") 
        
        timer = 20

        while timer>=0:
            time.sleep(1)
            timer-=1

            #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
            #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))
            
            p=glob.glob(filesInitialDirectory+'Financial Overview_All*csv')
            if len(p)>0:
                #filename = p[0].split("\\")[-1]
                #shutil.move(path+filename,filesInitialDirectory+filename)
                
                #print(f"le fichier de la plateforme Premier SN du {start_date} a bien ete telecharge et deplace")
                #print(f"le fichier de la plateforme zone betting du {start_date} a bien ete telecharge")
                
                transformFinancial(p[0])
                
                print(f"le fichier de la plateforme Financial du {start_date} a bien ete telecharge")
                
                #os.remove( p[0] )
                if os.path.exists(p[0]):
                    os.remove(p[0])
    
                
                start_date += delta
                
                break
            
            
            #if  "block" not in browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"):
                #break
        
        
        #url = "https://editec.virtual-horizon.com/engine/backoffice/"
        
        #browser.get(url)
        
        if timer<0:
            print("Le chargement est anormalement long, nous allons recommencer")
            continue
            
        for i in glob.glob(filesInitialDirectory+'*Financial Overview_All*cs*'):
            os.remove(i)




        #print(f"le fichier de la plateforme Financial du {start_date} a bien ete telecharge")
        
        #url = "https://editec.virtual-horizon.com/engine/backoffice/"
        
        #browser.get(url)
        
        #start_date += delta
        #browser.refresh()
        
        #url = "https://editec.virtual-horizon.com/engine/backoffice/"
        
        #browser.get(url)


    
    






# In[ ]:





# In[6]:


def connectToFinancialPlatform():
    
    global excl_list
    
    
    username = "editeclonasesenegal"
    #password = "EL16jT19"
    password = "EditecLonase22"

    
    #browser=openBrowser()
    
    #browser.implicitly_wait(20)
    #browser.maximize_window()
    
    #browser.execute_script("window.open('about:blank', 'tab');")
    #browser.switch_to.window("tab")
    
    url = "https://editec.virtual-horizon.com/engine/backoffice/"
    
    browser.get(url)

    #time.sleep(10)


    # Saisie du nom d'utilisateur
    usernameId = "username"
    #browser.find_element(by=By.NAME, value=usernameId).send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.NAME, usernameId))).send_keys(username)
    
    
    #Saisie du mot de passe
    passwordId = "password"
    #browser.find_element(by=By.NAME, value=passwordId).send_keys(password)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.NAME, passwordId))).send_keys(password)
    
    
    #Choisir administrator comme agent
    #browser.find_element(by=By.NAME, value="userType").send_keys("Administrator")
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.NAME, "userType"))).send_keys("Administrator")
    
    #browser.find_element_by_name("userType").send_keys("Administrator")
    
    #Submit button click
    login_button_id = "loginButton"
    #browser.find_element(by=By.NAME, value=login_button_id).click()
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.NAME, login_button_id))).click()
    
    #browser.find_element_by_name(login_button_id).click()
    #browser.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div/div/form/fieldset/div[4]/button").click()

    #time.sleep(5)

    #print("La connexion a la plateforme est un succes")
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/div[1]/div/div[1]/div/table[2]/tbody/tr/td[1]/div/span")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    
    
    #generateFinancial()
    #return
    
    
    #"""
    for i in range(3):
        
        try:
            generateFinancial()
            break
            
        except:
            print(f"la tentative numero {i} de generer le fichier a echoue")
            
        if i==2:
            
            #print("Impossible de generer le fichier")
            sys.exit("Impossible de generer le fichier malgre 3 tentatives")
            
            #try:
                #browser.quit()
            #except:
                #browser.close()
            #sys.exit("Impossible de generer le fichier")
    #"""
    
    #excl_merged = pd.concat(excl_list, ignore_index=True)
    
    #if debut1<fin1:
    
        #excl_merged.to_csv(filesInitialDirectory+"merge\\mergeFinancial"+str(debut1)+"_"+str(fin1)+".csv" , index=False,sep=';',encoding='utf8')
    
            
 
#print("executed")


# In[7]:


excl_list = []
#global start_date
#start_date = datetime.date(2022, 7, 1)
#debut = datetime.date(2022, 7, 1)
#end_date = datetime.date(2022, 6, 1)

end_date = datetime.date.today()
delta = datetime.timedelta(days=1)
start_date = end_date - delta

#start_date = datetime.date(2024, 4, 1)
#end_date = datetime.date(2024, 5, 1)
#end_date = start_date + delta

delta = datetime.timedelta(days=1)
#end_date = start_date+delta

filesInitialDirectory = r"K:\DATA_FICHIERS\VIRTUEL_EDITEC\FINANCIAL\\"

debut1 = start_date
fin1 = end_date-delta


#global end_date
#browser=openBrowser()
#connectToFinancialPlatform()

#"""
for i in range(10):
    try:
        
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectToFinancialPlatform()
        
        #time.sleep(1)
        
        #browser.quit()


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
        
browser.quit()

#"""






# In[8]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_Financial.py").read())


# In[9]:



d = dir()

#You'll need to check for user-defined variables in the directory
for obj in d:
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




