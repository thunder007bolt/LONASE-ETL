from curses import KEY_ENTER
from unicodedata import name
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select


from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


from selenium.webdriver.support.ui import Select



from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#options = Options()
#options.headless = True

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


# In[ ]:





# In[96]:


import pandas as pd
import numpy as np
import win32com.client
import os
import re
#import win32api
#import win32net



# Choisissez un repertoire sur votre machine comme indiqu� o� se trouve les fichiers xls � formatter
#path= '/Users/hp/Downloads/gitech/'
#/Users/hp/Documents/GITECH/ALR_MARS_2020/

# Choisissez un repertoire sur votre machine comme indiqu� o� vous souhaitez deposer les fichiers csv obtenus apr�s formattage 
#pathFinal='/Documents/CGFiles/depotdaily/'



# In[ ]:


#global start_date
#start_date = datetime.date(2022, 7, 1)
#debut = datetime.date(2022, 7, 1)
#end_date = datetime.date(2022, 6, 1)

end_date = datetime.date.today()
delta = datetime.timedelta(days=1)
start_date = end_date - delta



start_date = datetime.date(2025, 5, 4)
end_date = datetime.date(2025, 5,5 )
#end_date = start_date + delta

delta = datetime.timedelta(days=1)
#end_date = start_date+delta

#path = "C:\\Users\\OPTIWARE-ENTERPRISE\\Downloads\\" CFAC
#path = "C:\\Users\\CFAC\\Downloads\\" 
#filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\'
#filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'
#filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\premierSnAugust\\'

#filesInitialDirectory = r"K:\DATA_FICHIERS\GITECH\PMU_ONLINE_LOTS\\"

filesInitialDirectory = r"K:\DATA_FICHIERS\GITECH\PMU_ONLINE\\"

path = filesInitialDirectory




#global end_date



# In[97]:
def openBrowser():
    
    browser=0
    
    a=0
    #while True:
    for i in range(5):
        try:
            chromeOptions = webdriver.ChromeOptions()
            prefs = {"download.default_directory" : filesInitialDirectory}
            chromeOptions.add_experimental_option("prefs",prefs)
            chromedriver = r"‪C:\Users\optiware\Documents\jupyterNotebook\chromedriver.exe"
            browser = webdriver.Chrome(options=chromeOptions)
            
           
            break
        except:
            print("les drivers du navigateur Chrome semblent ne pas exister")

        a+=1
        if a <5:
            print(f"tentative numero {a+1} a echoue. Reessayons")
            continue


        sys.exit("Aucun WebDriver de navigateur ne fonctionne ou est installe")
    return browser




# In[98]:


def connectGitech():
    
    #url = "http://115.110.148.76/lonasemis/Lonase_administration/Login.aspx"
    url = "https://www.pmuonline.sn/lonasemis/lonase_administration/Login.aspx"
    
    
    browser.get(url)
    
    usernameId = "Username"
    username = 'khady'

    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
    
    
    passwordId = "Password"
    password = 'khady123#'
    
    #browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, passwordId))).send_keys(password)
    
    
    submit_buttonId = "btnSubmit"
    
    #browser.find_element(by=By.ID, value=submit_buttonId).click()
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, submit_buttonId))).click()
    
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/form/div[3]/table/tbody/tr/td/table[1]/tbody/tr[2]/td[3]/span")))
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    
    
    generateGitech()


# In[99]:

def generateGitech():
    
    #url = "http://115.110.148.76/lonasemis/Lonase_administration/HorseDrawWiseSales.aspx"
    #url = 'https://www.pmuonline.sn/lonasemis/lonase_administration/HorseDrawWiseSales.aspx'
    
    url = 'https://www.pmuonline.sn/lonasemis/lonase_administration/Playermanagementreport.aspx'
     
    global start_date
    #global end_date
    
    #start_date = datetime.date(2022, 2, 27)
    #end_date = datetime.date(2022, 3, 2)
    #delta = datetime.timedelta(days=1)
    while start_date < end_date:
        
        #for filename in os.listdir(path):
        for filename in glob.glob(filesInitialDirectory+'Rapport Gestion des joueurs*.*'):

            #if filename.startswith('Etat de la course') and ".xls" in filename:
            os.remove(filename)
        
        
        list = str(start_date).split("-")
        #print(list)
        annee = list[0]
        mois = list[1]
        jour = list[2]
        #print(jour)
        
        browser.get(url)
        
        Select(browser.find_element(By.ID, "OpsValidator_ContentPlaceHolder1_FDate_ddlDate")).select_by_visible_text(jour)
        Select(browser.find_element(By.ID, "OpsValidator_ContentPlaceHolder1_TDate_ddlDate")).select_by_visible_text(jour)
        Select(browser.find_element(By.ID, "OpsValidator_ContentPlaceHolder1_FDate_ddlMonth")).select_by_visible_text(mois)
        Select(browser.find_element(By.ID, "OpsValidator_ContentPlaceHolder1_TDate_ddlMonth")).select_by_visible_text(mois)
        Select(browser.find_element(By.ID, "OpsValidator_ContentPlaceHolder1_FDate_ddlYear")).select_by_visible_text(annee)
        Select(browser.find_element(By.ID, "OpsValidator_ContentPlaceHolder1_TDate_ddlYear")).select_by_visible_text(annee)

        WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.ID, "OpsValidator_ContentPlaceHolder1_btnSubmit"))).click()
        WebDriverWait(browser, 45).until(EC.element_to_be_clickable((By.ID, "OpsValidator_ContentPlaceHolder1_btnExcel"))).click()
        time.sleep(5)

        timer = 200
        downloaded_file = None
        while timer >= 0:
            time.sleep(1)
            files = glob.glob(os.path.join(filesInitialDirectory, 'Rapport Gestion des joueurs*.xls'))
            if files:
                downloaded_file = files[0]
                print(f" Fichier du {start_date} téléchargé : {downloaded_file}")
                break
            timer -= 1

        if not downloaded_file:
            print(f" Problème de téléchargement pour {start_date}.")
            start_date += delta
            continue
        try:
            tables = pd.read_html(downloaded_file, decimal=',', thousands=' ')
            print(f" Nbre de tableaux trouvés : {len(tables)}")

            df = None
            for i, table in enumerate(tables):
                first_col = table.columns[0]
                if table[first_col].astype(str).str.match(r'^\d+(\.0)?$').sum() >= 2:
                    df = table
                    print(f" Tableau sélectionné : index {i}")
                    break

            if df is None:
                raise Exception(" pas de tableau détécté.")

            df = df[df[df.columns[0]].astype(str).str.match(r'^\d+(\.0)?$')]
            df.columns = ['No', 'Date', 'NomJeu', 'Ventestotales', 'Gains', 'PourcentagePaiement', 'MontantNet']

            def nettoyer(val):
                val = str(val).replace('Â', '').replace('\xa0', '').strip()
                val = val.replace(' ', '').replace(',', '.')
                try:
                    return float(val)
                except:
                    return val

            colonnes_a_nettoyer = ['Ventestotales', 'Gains', 'MontantNet']
            for col in colonnes_a_nettoyer:
                df[col] = df[col].apply(nettoyer)
                
            df['No'] = df['No'].apply(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else str(x))
            df['Ventestotales'] = df['Ventestotales'].apply(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else str(x))
            df['Gains'] = df['Gains'].apply(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else str(x))
            df['MontantNet'] = df['MontantNet'].apply(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else str(x))


            print("\n Aperçu nouveau DataFrame :")
            print(df.head())

            #new_file_path = downloaded_file.replace('.xls', '_nettoye.xlsx')
            #df.to_excel(new_file_path, index=False)            
            new_file_path = downloaded_file.replace('.xls', '_nettoye.csv')
            df.to_csv(new_file_path, index=False, encoding='utf-8-sig',sep=';')

            os.remove(downloaded_file)

            #final_path = os.path.join(filesInitialDirectory, f"PmuOnline_{start_date}.csv")
            #final_path = os.path.join(filesInitialDirectory, f"GITECH_{start_date}.xlsx")

#------------------------------------supprimer l'ancien et renommer le nouveau ---------------------------------------#
            today_str = datetime.date.today().strftime('%Y-%m-%d')
            
            #final_path = os.path.join(filesInitialDirectory, f"GITECH_{start_date}.xlsx")
            final_path = os.path.join(filesInitialDirectory, f"PmuOnline_{start_date}.csv")

            if os.path.exists(final_path):
                os.remove(final_path)
                print(f" Ancien fichier supprimé : {final_path}")

            os.rename(new_file_path, final_path)
            print(f" Fichier normalisé et renommé : {final_path}")

        except Exception as e:
            print(f" Erreur de normalisation  {e}")
        start_date += delta

    print(" Terminé")
    


# In[ ]:





# In[100]:



#browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

#connectGitech()

#"""
for i in range(10):
    try:
        
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectGitech()
        
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
        
#"""


# In[ ]:


#exec(open("C:\Batchs\scripts_python\chargements\load_casino_gitech.py").read())


# In[ ]:


#d = dir()

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]
