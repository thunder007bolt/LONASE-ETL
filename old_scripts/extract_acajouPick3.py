#!/usr/bin/env python
# coding: utf-8

# In[40]:


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

from copy import copy, deepcopy
import copy
#import deepcopy

import warnings
warnings.simplefilter("ignore")


# In[41]:


from curses import KEY_ENTER
from unicodedata import name
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

#from datetime import date
#import datetime


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



# In[42]:


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
            chromeOptions.add_argument("--headless")
            chromeOptions.add_argument("--disable-gpu")
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


# In[43]:


def convert_float_to_str(val):
    from copy import copy, deepcopy
    if np.isnan(val):
        return str("")
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







# In[44]:



def convert_date_to_str(val):
    from copy import copy, deepcopy

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






# In[45]:



def transformFiles():
    
    #for i in range(len(attachments)):
    from copy import copy, deepcopy
    
    for i in glob.glob(filesInitialDirectory+'Listing_Tickets_Pick3*.xlsx'):
        
        nomFichier = i.split('\\')[-1]
    
        data = copy(pd.read_excel(i, header=2))


        #print(data.dtypes)
        #data = data [:10]

        #first_row = data.iloc[0]
        #first_row = data.columns
        #print(first_row)
        #print("jules")

        #my_data = []

        #for i in first_row:
        #    for  index,row in data.iterrows():
        

        print(f"le fichier {i} est en cours de formattage")
        for column in data.columns:

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

                data[column]=data[column].astype('str')

                #print(type(data[column]))
                #print("prolly un str deja")



        #data["Montant"] = np.where(data["Montant"] is float, "True", False)

        #print(data)

        #data.to_excel("Listing_Tickets_Pick3.xlsx", index=False)

        #print(ourDataFrame.shape)


        #print(ourDataFrame)
        print(f"le fichier {nomFichier} a ete formate et est en cours de conversion")
        
        #os.remove(attachments[i])
        
        #oldDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\pathFinal\\' #CFAC
        #oldDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\pathFinal\\'
        #destination = os.path.join(oldDirectory,nomFichier)
        #shutil.move(i,destination)

        data['Produit'] = str("Pick3")
        if os.path.exists(i.replace("xlsx","csv")):
            os.remove(i.replace("xlsx","csv"))
        data.to_csv(i.replace("xlsx","csv"), index=False, sep=";") #,encoding='utf-8', float_format='{:f}'.format
        
        os.remove(i)
        
        #attachments[i] = attachments[i].replace("xlsx","csv")
        #print(f"la conversion du fichier {attachments[i]} a ete un succes")
        
    print(f"Tous les fichiers ont bien ete formates et convertis")
        
    
    


# In[46]:




def connectToAcajouPlatform():
    
    
    username = "sfall"
    password = "OFwn1?)<"
    

    
    #browser=openBrowser()
    
    #browser.implicitly_wait(20)
    #browser.maximize_window()
    
    #browser.execute_script("window.open('about:blank', 'tab');")
    #browser.switch_to.window("tab")

    browser.get("https://analytics-cdr-portal.acajoue.sn/login")

    time.sleep(1)


    # Saisie du nom d'utilisateur
    #browser.find_element(by=By.NAME, value="username").send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.NAME, "username"))).send_keys(username)
    
    #Saisie du mot de passe
    #browser.find_element(by=By.NAME, value="password").send_keys(password)
    WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.NAME, "password"))).send_keys(password)
    
    #Submit button click
    #browser.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div/div/form/fieldset/div[4]/button").click()
    WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[2]/div[2]/div/div/div/form/fieldset/div[4]/button"))).click()
    
    time.sleep(5)
    
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/div[1]/header/div/div/div/ul[2]/li[4]/a/img")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    

    #print("La connexion a la plateforme est un succes")

    browser.get("https://analytics-cdr-portal.acajoue.sn/project/33/tab/155/reports")

    #Tab Creation

    #browser.execute_script("window.open('about:blank', 'firstTab' );") ##'firstTab'
    #browser.switch_to.window("firstTab")
    
    #browser.execute_script("window.open('about:blank', 'secondTab' );") ##'secondTab'
    #browser.switch_to.window("secondTab")
    
    #browser.execute_script("window.open('about:blank', 'thirdTab' );") ##'thirdTab'
    #browser.switch_to.window("thirdTab")

    ####getToDataPick3()
    #downloadAcajouFiles()
    #extractAcajouFiles()
    
    #"""
    for i in range(10):
        try:
            
            #verification = [0,0,0]
            
            extractAcajouFiles()
            #except SystemExit:
                #print("Program terminated with SystemExit exception")
                #sys.exit(" ")
            break
        except Exception as e:
            #print(e)
            print("nous avons rencontre un soucis lors de la phase de generation, nous allons reessayer")
            #tryGenFiles()
            #continue
        if i ==9:
            sys.exit("Impossible malgre 10 tentatives")
            
    #"""
    
    transformFiles()
    


# In[47]:



def extractAcajouFiles():
    
    
    #browser.switch_to.window("tab")
    
    
    global start_date
    #global liste
    #global verification
    #global end_date
    
    #start_date = datetime.date(2022, 2, 27)
    #end_date = datetime.date(2022, 3, 2)
    #delta = datetime.timedelta(days=1)
    while start_date < end_date:
    #while (start_date < end_date and len(liste)<11 ):
        
        #global verification
        
        """
        previous_day=getPreviousDate(start_date).split("/")
        previous_day[0],previous_day[1]=previous_day[1],previous_day[0]
        previous_day.reverse()
        previous_day = "".join(previous_day)
        """
        
        #date1 = getPreviousDate(start_date)
        
        """
        
        tableau = (
        ("firstTab" , name_TicketsReport , digitain_sports_betting_Tickets_report, "Listing_Tickets_Sports_betting "+previous_day+".xlsx"),
        ("secondTab", name_GrattageFR, listing_tickets_grattage_fr, "Listing_Tickets_Grattage "+previous_day+".xlsx"),
        ("thirdTab", name_Pick3FR, listing_tickets_pick3_fr, "Listing_Tickets_Pick3 "+previous_day+".xlsx")
                    )

        """
        
        
        #for i in range(1,len(tableau)):
            
        #if verification[i]==1:
            #continue
        #time.sleep(3)

        #url = browser.find_element(by=By.LINK_TEXT, value=tableau[i][1]).get_attribute("href")
        #url = browser.find_element(by=By.LINK_TEXT, value=name_Pick3FR).get_attribute("href")
        url = "https://analytics-cdr-portal.acajoue.sn/report/251?project=33&tab=155"
        
        #browser.switch_to.window(tableau[i][0])
        browser.get(url)

        #Date input
        #browser.find_element(by=By.ID, value="daterange-251").click()
        #browser.find_element(by=By.ID, value="daterange-251").clear()
        #browser.find_element(by=By.ID, value="daterange-251").send_keys(date1+" - "+date1)

        #time.sleep(3)




        #WebDriverWait(browser,timeout=60).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        
        try:
            WebDriverWait(browser,timeout=30).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        except:
            pass
        #WebDriverWait(browser,timeout=60).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        time.sleep(2)


        #browser.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div/app-report/div/div[3]/div[1]/div[1]/div/div/span/form/div/div/input").click()
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[2]/div[2]/div/div/app-report/div/div[3]/div[1]/div[1]/div/div/span/form/div/div/input"))).click()


        #browser.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div/app-report/div/div[3]/div[1]/div[1]/div/div/span/form/div/div/input").clear()
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[2]/div[2]/div/div/app-report/div/div[3]/div[1]/div[1]/div/div/span/form/div/div/input"))).clear()
        
        #browser.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div/app-report/div/div[3]/div[1]/div[1]/div/div/span/form/div/div/input").send_keys(date1+" - "+date1)
        
        date1 = str(start_date.strftime('%m/%d/%Y'))
        date2 = str((start_date+delta).strftime('%m/%d/%Y'))
        WebDriverWait(browser,timeout=20).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[2]/div[2]/div/div/app-report/div/div[3]/div[1]/div[1]/div/div/span/form/div/div/input"))).send_keys(date1+" - "+date2)


        time.sleep(2)


        heure = Select(browser.find_element(by=By.XPATH, value="/html/body/div[3]/div[3]/div[1]/div/div/select[1]"))


        heure.select_by_visible_text("0")

        time.sleep(1)

        minute = Select(browser.find_element(by=By.XPATH, value="/html/body/div[3]/div[3]/div[1]/div/div/select[2]"))
        minute.select_by_visible_text("00")


        time.sleep(1)

        #browser.find_element(by=By.XPATH, value="/html/body/div[3]/div[1]/div/button[1]").click()
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[3]/div[1]/div/button[1]"))).click()
        
        
        WebDriverWait(browser,timeout=60).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))


        time.sleep(2)

        #browser.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div/app-report/div/div[1]/div[3]/button").click()
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[2]/div[2]/div/div/app-report/div/div[1]/div[3]/button"))).click()


        time.sleep(1)

        #Click Excel
        #browser.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div/app-report/div/div[3]/div[2]/div[1]/ul/li[1]/a").click()
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[2]/div[2]/div/div/app-report/div/div[3]/div[2]/div[1]/ul/li[1]/a"))).click()


        time.sleep(1)

        #Click Include All
        #browser.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div[2]/div/div/label[1]").click()
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div/label[1]"))).click()

        time.sleep(1)

        #Click Export
        #browser.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div[3]/button[1]").click()
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[1]/div/div/div/div[3]/button[1]"))).click()

        time.sleep(1)
        
        

        #print(f"Le fichier {tableau[i][3]} est en cours d'exportation")

        #verification[i]=1

        #browser.switch_to.window("tab")


        #time.sleep(60)
        ####downloadDataPick3()
        #downloadAcajouFiles()

        """
        for i in range(3):
            try:
                
                time.sleep(3)
                
                downloadAcajouFiles()
                #except SystemExit:
                    #print("Program terminated with SystemExit exception")
                    #sys.exit(" ")
                break
            except Exception as e:
                print(e)
                print("nous avons rencontre un soucis, nous allons reessayer")
                #tryGenFiles()
                #continue
            if i ==2:
                sys.exit("Impossible malgre 3 tentatives")
        """
        #break
        #liste.append(start_date.strftime('%d/%m/%Y'))
        print(f"le fichier acajou  Pick3 du {start_date} a bien ete genere")
        
        #time.sleep(20)
        
        for i in range(10):
            try:

                #verification = [0,0,0]

                downloadAcajouFiles()
                #except SystemExit:
                    #print("Program terminated with SystemExit exception")
                    #sys.exit(" ")
                break
            except Exception as e:
                #print(e)
                print("nous avons rencontre un soucis lors de la phase de telechargement, nous allons reessayer")
                time.sleep(10)
                #tryGenFiles()
                #continue
            if i ==9:
                sys.exit("Impossible malgre 10 tentatives")


        
        
        
        start_date+=delta



# In[48]:



def downloadAcajouFiles():
    
    #time.sleep(2)
    nomFichier = "Listing_Tickets_Pick3 "+str(start_date).replace("-","")+".xlsx"
    #browser.switch_to.window("tab")
    
    #global verification
    
    #global downloaded
    
    #attachments = []
    
    """
    
    previous_day=getPreviousDate(start_date).split("/")
    previous_day[0],previous_day[1]=previous_day[1],previous_day[0]
    previous_day.reverse()
    previous_day = "".join(previous_day)
        
        
    date1 = getPreviousDate(start_date)
        
    tableau = (
        ("firstTab" , name_TicketsReport , digitain_sports_betting_Tickets_report, "Listing_Tickets_Sports_betting "+previous_day+".xlsx"),
        ("secondTab", name_GrattageFR, listing_tickets_grattage_fr, "Listing_Tickets_Grattage "+previous_day+".xlsx"),
        ("thirdTab", name_Pick3FR, listing_tickets_pick3_fr, "Listing_Tickets_Pick3 "+previous_day+".xlsx")
            )
        

    for i in range(1,len(tableau)):
        
        #print(i)
        
        if downloaded[i]==1:
            
            continue

        time.sleep(15)

        """
    
    
        #browser.switch_to.window(tableau[i][0])
    done = False
        
    #while done:
        
        
            
    browser.get("https://analytics-cdr-portal.acajoue.sn/file")

    #nom_fichier = browser.find_elements(by=By.PARTIAL_LINK_TEXT, value= tableau[i][2] + date_of_day )[-1].text
    #nom_fichier = tableau[i][2]+date_of_day+".xlsx"

    time.sleep(5)

    for i in glob.glob(filesInitialDirectory+'{str(nomFichier)}'):
        os.remove(i)

    #print(tableau[i][2])

    #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.PARTIAL_LINK_TEXT, tableau[i][2] + date_of_day)))
    #download_link = browser.find_elements(by=By.PARTIAL_LINK_TEXT, value= tableau[i][2] + date_of_day )[-1].get_attribute("href")

    #download_link = browser.find_elements(by=By.PARTIAL_LINK_TEXT, value= "Listing_Tickets_Pick3_-_FR_" + date_of_day )[-1].get_attribute("href")
    for i in browser.find_elements(by=By.PARTIAL_LINK_TEXT, value= "Listing_Tickets_Pick3_-_FR_" + date_of_day )[:-3:-1]:
        #data = requests.get(download_link)
        download_link = i.get_attribute("href")
        data = requests.get(download_link)

        #print(tableau[i][3])

        #with open(tableau[i][3], 'wb')as file:
        with open(filesInitialDirectory+nomFichier, 'wb')as file:
            file.write(data.content)

        #time.sleep(4)
        df =pd.read_excel(filesInitialDirectory+nomFichier,header=2)
        #print(str(df.iat[2, 0]))
        #if str(start_date) in str(df.iat[2, 0]):
        if str(start_date) in str(df.iat[0, 0]) and len(set([str(x).strip()[:10] for x in df.iloc[:,0]]))==1:

            #print("oh yeah")
            print(f"Le fichier {nomFichier} a bien ete telecharge")
            return
            done = True
            #break
        os.remove(filesInitialDirectory+nomFichier)
    
    #if not(done):
        #a = 1/0

        
        #if timer<0:
            #print("Le fichier n'a pas ete telecharge")
            #break

    

    #attachments.append(str(tableau[i][3]))

    #downloaded[i]=1

        
    #print(f"Les fichiers ACAJOU  du {start_date} ont bien ete telecharges")
    
    #time.sleep(10)
        
        
    #transformFiles(attachments)

    #sendMail(attachments)
    #\OPTIWARE-ENTERPRISE

    #filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\'
    #filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'


    """
    for filename in attachments:
            
        #filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\'
        dest = os.path.join(filesInitialDirectory,filename)


        shutil.move(filename,dest)

        print(f"le fichier {filename} a ete deplace")

    """
        
        
        
        
        
        

    #print(f"Les fichiers ACAJOU du {start_date} ont bien ete telecharges")
    
    #verification = [0,0,0]
    #downloaded = [0,0,0]
    
    #browser.switch_to.window("tab")
    
    #print("Tous les fichiers ont bien ete telecharges")
    
    #browser.quit()
    


# In[49]:


date_of_day = str(date.today()).replace("-","")
#global start_date
#start_date = datetime.date(2022, 7, 1)
#debut = datetime.date(2022, 7, 1)
#end_date = datetime.date(2022, 6, 1)
delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
delta = datetime.timedelta(days=1)
start_date = end_date - delta

#delta = datetime.timedelta(days=1)
#end_date = start_date+delta

#start_date = datetime.date(2024, 11, 7)
#end_date = start_date+delta

#end_date = datetime.date(2024, 11, 8)

liste = []

#path = "C:\\Users\\CFAC\\Downloads\\"
#filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'
#filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\premiersnSeptember\\'

filesInitialDirectory = r"K:\DATA_FICHIERS\ACAJOU\PICK3\\"


#os.system("taskkill /im chrome.exe /f")

time.sleep(2)
#global end_date

#browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

#connectToAcajouPlatform()
#break

#"""
for i in range(10):
    try:
        
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectToAcajouPlatform()
        
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

#"""

#time.sleep(5)
        
#browser.quit()






# In[50]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_Acajou_Pick3.py").read())


# In[51]:


import gc
gc.collect()


# In[52]:


#transformFiles()


# In[ ]:




