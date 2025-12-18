#!/usr/bin/env python
# coding: utf-8

# In[1]:


d = dir()

#You'll need to check for user-defined variables in the directory
for obj in d:
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


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
from selenium.webdriver.common.action_chains import ActionChains




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
            
            chromeOptions.add_argument(r"--user-data-dir=C:\\Users\\optiware3\\AppData\\Local\\Google\\Chrome\\User Data\\")

            chromeOptions.add_argument(r"--profile-directory=Default")

            prefs = {"download.default_directory" : filesInitialDirectory}
            chromeOptions.add_experimental_option("prefs",prefs)
            chromedriver = r"C:\Users\optiware3\Documents\jupyterNotebook\chromedriver.exe"
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

        if a <5:
            print(f"tentative numero {a+1} a echoue. Reessayons")
            continue


        sys.exit("Aucun WebDriver de navigateur ne fonctionne ou est installe")
    return browser


# In[4]:


#"""
def autoprocessPremierSN(path):
    
    #path = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\'

#import shutil


#o = win32com.client.gencache.EnsureDispatch('Excel.Application')

    o = win32.Dispatch("Excel.Application")
    o.Visible = False
    
    # Tous les fichiers du repertoire path seront traités
    for filename in os.listdir(path):
        
        if "Premier SN" in filename and filename.endswith(".xlsx"):
            
            print(f"le fichier {filename} est en cours de transformation")
            
            
            
            #shutil.copy(os.path.join(path,filename),os.path.join(os.getcwd(),filename))
            
            #print(filename)
            '''
            output = path + filename.replace('.xlsx','.xlsxx')
            wb = o.Workbooks.Open(path+filename)
            wb.ActiveSheet.SaveAs(output,51)
            wb.Close(True)
            os.remove(path+filename)'''
            
            
            #changer l'extension du fichier en xlsx
           
            #print(filename)
            output = path + filename.replace('.xls','.xlsx')
        
            #print(output)
            #break
            #print(path+filename)
            
            wb = o.Workbooks.Open(path+filename)
            wb.ActiveSheet.SaveAs(output,51)
            wb.Close(True)

            
            
            #data = pd.read_excel(path+filename,sep=';',skiprows=range(0, 1))
            #data = pd.read_excel(path+filename,skiprows=range(0, 1))
            #data = copy(pd.read_excel(path+'2022-04-13-Premier SN.xlsx'))
            
            
            #data = pd.read_excel(str(filename),header=1)
            
            #data = data[:-7]
            #data = data.fillna("")
            
            
            data = pd.read_excel(output,skiprows=1)
            #data = pd.read_excel(filename,skiprows=1)
            #data = pd.read_excel(path+filename,sep=';',skiprows=range(0, 1))
            data = data[:-7]
            data = data.fillna("")
            
            
            
            data['Sales'] = data['Sales'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
            data['Redeems'] = data['Redeems'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
            data['SB Unpaid'] = data['SB Unpaid'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
            data['Balance'] = data['Balance'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
            data['Commission Base'] = data['Commission Base'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
            data['Voided'] = data['Voided'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
            data['#Bets Sold'] = data['#Bets Sold'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
            data['#Bets Redeemed'] = data['#Bets Redeemed'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
            
            data = data[data.Currency != ""]
            
                 
            #print(data.head())
            #print(data.tail())
            
            
            os.remove(path+filename)
            os.remove(output)
            
            filename = filename.replace('.xlsx','.csv')
            
            #break
            data.to_csv(filename, index=False,sep=';',encoding='utf8')
            
            dest = os.path.join(path,filename)
            
            print(f"le fichier {filename} a bien ete transforme")

            
            
            #shutil.move(os.getcwd(),filename,dest)
            shutil.move(os.path.join(os.getcwd(),filename),os.path.join(path,filename))
            
            #os.remove(filename)
            
            
            #, index=False, sep=";"
            
            #print("fini")
    print("tous les fichiers ont bien ete transformes")
            
    
#"""


# In[5]:



def autoprocessPremierSN(a):
    
    
    #path = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\'

#import shutil


#o = win32com.client.gencache.EnsureDispatch('Excel.Application')

    filename = a
    o = win32.Dispatch("Excel.Application")
    o.Visible = False
    
    # Tous les fichiers du repertoire path seront traités
    #for filename in os.listdir(path):
        
    #if "Premier SN" in filename and filename.endswith(".xlsx"):

    print(f"le fichier {filename} est en cours de transformation")



    #shutil.copy(os.path.join(path,filename),os.path.join(os.getcwd(),filename))

    #print(filename)
    '''
    output = path + filename.replace('.xlsx','.xlsxx')
    wb = o.Workbooks.Open(path+filename)
    wb.ActiveSheet.SaveAs(output,51)
    wb.Close(True)
    os.remove(path+filename)
    '''


    #changer l'extension du fichier en xlsx

    #print(filename)
    
    #output = path + filename.replace('.xls','.xlsx')
    output = a.replace('.xls','.xlsx')

    #print(output)
    #break
    #print(path+filename)

    #wb = o.Workbooks.Open(path+filename)
    wb = o.Workbooks.Open(a)
    wb.ActiveSheet.SaveAs(output,51)
    wb.Close(True)



    #data = pd.read_excel(path+filename,sep=';',skiprows=range(0, 1))
    #data = pd.read_excel(path+filename,skiprows=range(0, 1))
    #data = copy(pd.read_excel(path+'2022-04-13-Premier SN.xlsx'))


    #data = pd.read_excel(str(filename),header=1)

    #data = data[:-7]
    #data = data.fillna("")


    data = pd.read_excel(output,skiprows=1)
    #data = pd.read_excel(filename,skiprows=1)
    #data = pd.read_excel(path+filename,sep=';',skiprows=range(0, 1))
    data = data[:-7]
    data = data.fillna("")



    data['Sales'] = data['Sales'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
    data['Redeems'] = data['Redeems'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
    data['SB Unpaid'] = data['SB Unpaid'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
    data['Balance'] = data['Balance'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
    data['Commission Base'] = data['Commission Base'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
    data['Voided'] = data['Voided'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
    data['#Bets Sold'] = data['#Bets Sold'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
    data['#Bets Redeemed'] = data['#Bets Redeemed'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )

    data = data[data.Currency != ""]
    
    data['Reported']= str(start_date.strftime('%d/%m/%Y'))


    #print(data.head())
    #print(data.tail())


    #os.remove(path+filename)
    #os.remove(output)
    os.remove(a)
    os.remove(output)

    
    
    #filename = filename.replace('.xlsx','.csv')

    #break
    #data.to_csv(filename, index=False,sep=';',encoding='utf8')
    filename = a.split("\\")[-1]
    filename = filename.replace('.xlsx','.csv')
    filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'
    
    if os.path.exists(filesInitialDirectory+filename):
        os.remove(filesInitialDirectory+filename)
        
    
    data.to_csv(filesInitialDirectory+filename, index=False,sep=';',encoding='utf8')

    
    #dest = os.path.join(path,filename)

    print(f"le fichier {filename} a bien ete transforme")



        #shutil.move(os.getcwd(),filename,dest)
        #shutil.move(os.path.join(os.getcwd(),filename),os.path.join(path,filename))

        #os.remove(filename)


        #, index=False, sep=";"

        #print("fini")
#print("tous les fichiers ont bien ete transformes")

            
            
#path = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'
#autoprocessPremierSN(path)


# In[6]:


def connectToPremierSn():
    
    #browser=openBrowser()
    
    #browser.session_id = "443adf7953d44e05a0a5fb04acd740c2"
    
    
    username = "sadio.fall@lonase.sn"
    password = "S@dio1234#"
    

    
    #browser=openBrowser()
    
    #browser.implicitly_wait(20)
    #browser.maximize_window()
    
    #browser.execute_script("window.open('about:blank', 'tab');")
    #browser.switch_to.window("tab")
    
    url = "http://soliditymanagement.mine.nu:86/SolidAdmin/Account/Login"
    
    browser.get(url)

    #time.sleep(10)
    
    #browser.session_id = "443adf7953d44e05a0a5fb04acd740c2"


    # Saisie du nom d'utilisateur
    usernameId = "UserName"
    #browser.find_element(by=By.NAME, value=usernameId).send_keys(username)
    WebDriverWait(browser,timeout=15*9).until( EC.element_to_be_clickable(( By.NAME, usernameId))).send_keys(username)
    
    
    
    #Saisie du mot de passe
    passwordId = "Password"
    #browser.find_element(by=By.NAME, value=passwordId).send_keys(password)
    WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.NAME, passwordId))).send_keys(password)
    
    #Choisir administrator comme agent
    
    #browser.find_element(by=By.NAME, value="userType").send_keys("Administrator")
    
    #browser.find_element_by_name("userType").send_keys("Administrator")
    
    #Submit button click
    #login_button_id = "loginButton"
    #browser.find_element(by=By.NAME, value=login_button_id).click()
    
    #browser.find_element(by=By.XPATH, value="/html/body/main/div/form/table/tbody/tr[4]/td/button").click()
    WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/main/div/form/table/tbody/tr[4]/td/button"))).click()
    
    #browser.find_element_by_name(login_button_id).click()
    #browser.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div/div/form/fieldset/div[4]/button").click()

    #time.sleep(5)

    #print("La connexion a la plateforme est un succes")
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        # /html/body/header/div/div[4]/form/a[1]
        #WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/hg-root/hg-layout/div/div/hg-header/div/div/hg-topbar-infos/div/div[2]/div[2]/button/div/span")))
        WebDriverWait(browser,timeout=10*4).until( EC.presence_of_element_located(( By.XPATH, "/html/body/header/div/div[4]/form/a[1]")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    
    
    generateFinancial()
   
    return
    
    
    #'''
    for i in range(3):
        
        try:
            generateFinancial()
            break
            
        except:
            print(f"erreur numero {i} a echoue")
            
        if i==3:
            try:
                browser.quit()
                connectToFinancialPlatform()
            except:
                browser.close()
                connectToFinancialPlatform()
            #sys.exit("Impossible de generer le fichier")
    #''' 
    
    return
    
    excl_merged = pd.concat(excl_list, ignore_index=True)
    
    if debut1<fin1:
    
        excl_merged.to_csv(filesInitialDirectory+"merge\\mergePremierSN"+str(debut1)+"_"+str(fin1)+".csv" , index=False,sep=';',encoding='utf8')
    
 
#print("executed")


# In[7]:


def generateFinancial():
    
    url = "http://soliditymanagement.mine.nu:86/SolidReports/Reports#"
    
    global start_date
    #global excl_list
    #global end_date
    
    #start_date = datetime.date(2022, 2, 27)
    #end_date = datetime.date(2022, 3, 2)
    #delta = datetime.timedelta(days=1)
    
    theFiles = ["Premier Sat","Premier","Express","Cloud"] # Premier sat
    
    browser.get(url)
    
    
    while start_date < end_date:
        
        for i in glob.glob(filesInitialDirectory+'*["Premier Sat","Premier","Express","Cloud"] SN*xls*'):
            os.remove(i)
    

        #browser.get(url)

        #delta = datetime.timedelta(days=1)
        #/html/body/main/section/div/div/div[1]/table[1]/tbody/tr[2]/td[1]/input
        #/html/body/main/section/div/div/div[1]/table[1]/tbody/tr[2]/td[1]/input

        time.sleep(3)

        browser.find_element(by=By.XPATH, value="/html/body/main/section/div/div/div[1]/table[1]/tbody/tr[2]/td[1]/input").click()
        #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/main/section/div/div/div[1]/table[1]/tbody/tr[2]/td[1]/input']"))).click()

        time.sleep(0.5)

        browser.find_element(by=By.ID, value="datepicker").click()
        #WebDriverWait(browser,timeout=25).until( EC.element_to_be_clickable(( By.ID, "datepicker"))).click()


        time.sleep(1)

        browser.find_element(by=By.ID, value="datepicker").send_keys(Keys.CONTROL + 'a')

        time.sleep(1)

        browser.find_element(by=By.ID, value="datepicker").send_keys(str(start_date.strftime('%d/%m/%Y')))

        time.sleep(1)

        browser.find_element(by=By.ID, value="datepicker").send_keys(Keys.ENTER)
        browser.find_element(by=By.ID, value="datepicker").send_keys(Keys.ENTER)

        #time.sleep(60)
        
        for fichier in theFiles:
            
            #browser.find_element(by=By.XPATH, value="/html/body/main/section/div/div/div[1]/table[2]/tbody/tr[1]/td[2]/span/span/span[1]").click()
            
            WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/main/section/div/div/div[1]/table[2]/tbody/tr[1]/td[2]/span/span/span[1]"))).click()
            
            time.sleep(1)

            
            if "Premier" == fichier:
                
                #time.sleep(0.5)
                
                #browser.find_element(by=By.XPATH, value="/html/body/main/section/div/div/div[1]/table[2]/tbody/tr[1]/td[2]/span/span/span[1]").click()

                
                #time.sleep(0.5)
                                                                        # /html/body/div[6]/div/ul/li[5]
                drp_element = browser.find_element(by=By.XPATH, value="/html/body/div[6]/div/ul/li[5]").click()
                #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[6]/div/ul/li[4]"))).click()
                                                        # /html/body/div[6]/div/ul/li[4]
            elif "Express" == fichier:
                
                #time.sleep(0.5)

                #browser.find_element(by=By.XPATH, value="/html/body/main/section/div/div/div[1]/table[2]/tbody/tr[1]/td[2]/span/span/span[1]").click()

                #time.sleep(0.5)

                drp_element = browser.find_element(by=By.XPATH, value="/html/body/div[6]/div/ul/li[3]").click()
            elif "Cloud" == fichier:
                
                #time.sleep(0.5)

                #browser.find_element(by=By.XPATH, value="/html/body/main/section/div/div/div[1]/table[2]/tbody/tr[1]/td[2]/span/span/span[1]").click()

                #time.sleep(0.5)

                drp_element = browser.find_element(by=By.XPATH, value="/html/body/div[6]/div/ul/li[2]").click()
            elif "Premier Sat" == fichier:
                
                #time.sleep(0.5)

                #browser.find_element(by=By.XPATH, value="/html/body/main/section/div/div/div[1]/table[2]/tbody/tr[1]/td[2]/span/span/span[1]").click()

                #time.sleep(0.5)

                drp_element = browser.find_element(by=By.XPATH, value="/html/body/div[6]/div/ul/li[4]").click()
                #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[6]/div/ul/li[3]"))).click()
                
                # WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "excelExportButton"))).click()

            #drp_element = browser.find_element(by=By.XPATH, value="/html/body/div[6]/div/ul/li[4]")
            action = ActionChains(browser)
            action.click(on_element=drp_element).perform()

                
            #timer = 60+30
            
            #print(1)
            time.sleep(5)
            #print(2)
            
            WebDriverWait(browser,timeout=60+30).until( EC.invisibility_of_element(( By.CLASS_NAME, "k-loading-mask")))
            
            time.sleep(1)
            
            #print(browser.find_element(by=By.XPATH, value='/html/body/main/section/div/div/div[3]/div[1]/div/div[2]/table/tbody/tr').text)
            
            if len(browser.find_elements(by=By.XPATH, value='/html/body/main/section/div/div/div[3]/div[1]/div/div[2]/table/tbody/tr'))==0:
               
                print(f"le fichier {fichier} SN de la plateforme Premier SN du {start_date} ne contient aucune donnee")
                continue


            time.sleep(2)
            #browser.find_element(by=By.ID, value="excelExportButton").click()
            WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "excelExportButton"))).click()


            #time.sleep(20)

            #path = "C:\\Users\\OPTIWARE-ENTERPRISE\\Downloads\\"
            #filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\'


            timer = 30+30

            while timer>=0:
                time.sleep(1)
                timer-=1

                #if len(browser.find_elements(by=By.CLASS_NAME, value="dataTables_processing"))==0:
                #print(browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"))

                #p=glob.glob(f'C:\\Users\\CFAC\\Downloads\\*{start_date}*Premier SN.xlsx')
                p=glob.glob(filesInitialDirectory+f'{start_date.strftime("%d_%m_%Y")}*["Premier Sat","Premier","Express","Cloud"] SN.xlsx')
                if len(p)>0:
                    filename = p[0].split("\\")[-1]
                    
                    #autoprocessPremierSN(p[0])
                    #data = pd.read_excel(r"K:\DATA_FICHIERS\VIRTUEL_EDITEC\07_12_2023-Premier SN.xlsx",skiprows=1,skipfooter=7,index_col=False)
                    data = pd.read_excel(p[0],skiprows=1,skipfooter=7,index_col=False)

                    data = data.fillna("")
                    data['Sales'] = data['Sales'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
                    data['Redeems'] = data['Redeems'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
                    data['SB Unpaid'] = data['SB Unpaid'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
                    data['Balance'] = data['Balance'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
                    data['Commission Base'] = data['Commission Base'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
                    data['Voided'] = data['Voided'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
                    data['#Bets Sold'] = data['#Bets Sold'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )
                    data['#Bets Redeemed'] = data['#Bets Redeemed'].map(lambda x: str("%.1f" % float(x)).replace(".",",").replace(",0","") if(re.search(r'.[0-9]',str(x))) else str(x) )

                    data = data[data.Currency != ""]
                            
                    filename = str(filename.replace('.xlsx','.csv'))
                    
                    data.to_csv(filesInitialDirectory+filename, index=False,sep=';',encoding='utf8')
                            
                    os.remove(p[0])
                    
                    print(f"le fichier {fichier} de la plateforme Premier SN du {start_date} a bien ete telecharge et deplace")
                    

                    break


                #if  "block" not in browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"):
                    #break
            if timer<0:
                print("Le chargement est anormalement long, nous allons recommencer")
                continue


        excl_list = []
        p=glob.glob(filesInitialDirectory+f'{start_date.strftime("%d_%m_%Y")}*["Premier Sat","Premier","Express","Cloud"] SN.csv')
        for i in p:
            excl_list.append(pd.read_csv(i, sep=';'))
            os.remove(i)
        excl_merged = pd.concat(excl_list, ignore_index=True)
        filename = str(start_date)+"-Premier SN.csv"
        excl_merged.to_csv(filesInitialDirectory+filename, index=False,sep=';',encoding='utf8')
                    
                    
        print(f"\n le fichier Premier SN du {start_date} a bien ete telecharge \n")

        
        start_date += delta
        for i in glob.glob(filesInitialDirectory+'*["Premier Sat","Premier","Express","Cloud"] SN.xls*'):
            os.remove(i)
        #for i in glob.glob(filesInitialDirectory+'*["Premier Sat","Premier","Express"] SN.cs*'):
            #os.remove(i)
        
                            
        '''
        for i in glob.glob(f'C:\\Users\\CFAC\\Downloads\\*{start_date}*Premier SN*xlsx'):
            os.remove(i)
        '''
    print("tous les fichiers ont bien ete telecharges")
    
    
    #autoprocessPremierSN(filesInitialDirectory)
    


        #Tab Creation

        #browser.execute_script("window.open('about:blank', 'firstTab' );") ##'firstTab'
        #browser.switch_to.window("firstTab")

        #browser.execute_script("window.open('about:blank', 'secondTab' );") ##'secondTab'
        #browser.switch_to.window("secondTab")

        #browser.execute_script("window.open('about:blank', 'thirdTab' );") ##'thirdTab'
        #browser.switch_to.window("thirdTab")
        #print("generated")


# In[ ]:





# In[8]:


#excl_list = []
#global start_date
#start_date = datetime.date(2022, 7, 1)
#debut = datetime.date(2022, 7, 1)
#end_date = datetime.date(2022, 6, 1)
delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
delta = datetime.timedelta(days=1)
start_date = end_date - delta

#start_date = datetime.date(2024, 6, 15)
#end_date = datetime.date(2024, 8, 1)

delta = datetime.timedelta(days=1)
#end_date = start_date+delta

filesInitialDirectory = r'K:\DATA_FICHIERS\VIRTUEL_EDITEC\PREMIERSN\\'

os.system("taskkill /im chrome.exe /f")

time.sleep(2)
#global end_date

browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

connectToPremierSn()
#break

#"""
for i in range(5):
    try:
        
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectToPremierSn()
        
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
        
#handleFinancialFile()

#"""

#time.sleep(5)
        
#browser.quit()






# In[9]:



d = dir()

#You'll need to check for user-defined variables in the directory
for obj in d:
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]

