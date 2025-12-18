# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 11:25:40 2024

@author: optiware
"""

#!/usr/bin/env python
# coding: utf-8

# In[17]:

from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select



from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC



from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True


from selenium.webdriver.common.keys import Keys

from selenium.webdriver.firefox.options import Options



from selenium.webdriver.common.keys import Keys


import os
from datetime import date #,datetime,timedelta



from selenium.webdriver.chrome.options import Options



#


#from datetime import date, timedelta
#import datetime

import sys

import datetime
import re
import numpy as np
import csv
import pandas as pd
from copy import copy, deepcopy
#from datetime import date, timedelta, datetime
#import datetime
#from pandas.api.types import is_datetime64_any_dtype as is_datetime


import shutil



import warnings
warnings.simplefilter("ignore")


import glob
import pandas as pd

# In[ ]:





# In[18]:


import win32com.client as win32



def autoprocessPMU(path):

    # Créer une instance de Excel (en arrière-plan)
    o =  win32.Dispatch('Excel.Application')
    o.Visible = False
    #print("Excel lancé en arrière-plan.")
    
    for filename in glob.glob(path+'Rapport Gestion des joueurs.xl*'):

        output =filename.replace('.xls', '.xlsx')
        wb = o.Workbooks.Open(filename)
        wb.ActiveSheet.SaveAs(output, 51)  # 51 correspond au format .xlsx
        wb.Close(True)
        # Suppression du fichier .xls après conversion
        #os.remove(filename)

        # Traitement des données avec pandas (si nécessaire)

        # Lire le fichier .xlsx avec pandas
        data = pd.read_excel(output,skiprows=range(1, 6))
        data.columns = ['No', 'Date', 'Nomjeu', 'Ventestotales', 'Gains', 'PourcentagePaiement', 'MontantNet']
        # Sppression des lignes contenant 'Total' 
        data = data[~data['Nomjeu'].isin(['TOTAL'])]
            # Suppression de la colonne 'No'
        data = data.drop('No', axis=1)

        # Fonction de nettoyage
        def nettoyer_montant(valeur):
            if isinstance(valeur, str):
                # Supprimer tous les caractères non numériques sauf la virgule
                return valeur.replace('Â', '').replace(' ', '').replace(',', '.')
            return valeur

        # Appliquer le nettoyage sur les colonnes de montant
        for col in ["Ventestotales", "Gains", "PourcentagePaiement", "MontantNet"]:
            data[col] = data[col].apply(nettoyer_montant)

        # Convert cleaned strings to numeric types
        data["Ventestotales"] = pd.to_numeric(data["Ventestotales"], errors='coerce')
        data["Gains"] = pd.to_numeric(data["Gains"], errors='coerce')
        data["PourcentagePaiement"] = pd.to_numeric(data["PourcentagePaiement"], errors='coerce')
        data["MontantNet"] = pd.to_numeric(data["MontantNet"], errors='coerce')

        dat1 = pd.read_excel(output)
        cell_value = dat1.iloc[1, 0]
        if isinstance(cell_value, str):  
         # Nettoyer et extraire la date du texte
            date = (
                cell_value.replace("Du", " ")
                .split(": ")[0]
                .replace("/", "-")
                .replace(" ", "")
                .replace("Au", "_")
               # .replace(" ", "")
            )
        #print("Date extraite :", date)
        data.to_csv(path+'pmu'+' '+date+'.csv', index=False, sep=';', encoding='latin-1')
        print(f"Le fichier  a été sauvegardé en CSV.")

        if os.path.exists(filename.replace('.xls','.xlsx')):
                os.remove(filename.replace('.xls','.xlsx'))
        os.remove(filename) 

    

    



# In[19]:


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


# In[20]:


def connectPMU():
    
 
    
    url = "https://www.pmuonline.sn/lonasemis/lonase_administration/Login.aspx"
    
    
    browser.get(url)
    
    usernameId = "Username"
    username = 'khady'

    
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
    
    
    passwordId = "Password"
    password = 'khady123#'
    
    
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, passwordId))).send_keys(password)
    
    
    submit_buttonId = "btnSubmit"
    
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, submit_buttonId))).click()
    
    try:
        
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/form/div[3]/table/tbody/tr/td/table[1]/tbody/tr[2]/td[3]/span")))

        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
    
    
    
    generatePMU()
    


# In[ ]:





# In[21]:


def generatePMU():
    
    
    url = 'https://www.pmuonline.sn/lonasemis/lonase_administration/Playermanagementreport.aspx'
    
    
    global start_date
    
    while start_date < end_date:
        
        for filename in os.listdir(path):
            if filename.startswith('Rapport Gestion des joueurs') and ".xls" in filename:
                os.remove(path+filename)
        
        
        list = str(start_date).split("-")
        
        annee = list[0]
        mois = list[1]
        jour = list[2]
        #print(jour)
        
        browser.get(url)
        
        
        
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_FDate_ddlDate"))).select_by_visible_text(str(jour))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_TDate_ddlDate"))).select_by_visible_text(str(jour))
        
        
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_FDate_ddlMonth"))).select_by_visible_text(str(mois))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_TDate_ddlMonth"))).select_by_visible_text(str(mois))
        
        
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_FDate_ddlYear"))).select_by_visible_text(str(annee))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_TDate_ddlYear"))).select_by_visible_text(str(annee))
        
        
        #print("le mois")
        #print(str(mois))
        
        #break
        
        
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_btnSubmit"))).click()
        
        #time.sleep(10)
        
        WebDriverWait(browser,timeout=15*3).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_btnExcel"))).click()
        
        
        timer = 60+60+30

        while timer>=0:
            time.sleep(10)
            timer-=1
            
           
            p=glob.glob(filesInitialDirectory+'Rapport Gestion des joueurs.xls') 
            if len(p)>0:
                
                print(f"le fichier de la plateforme gitech du {start_date} a bien ete telecharge")
                
                
                filename = p[0].split("\\")[-1]
                
                src = os.path.join(path,filename)
                
                
                final_file = filename
                
                dest = os.path.join(filesInitialDirectory,final_file) 
               

                shutil.move(src,dest) 
                print(f"le fichier de la plateforme gitech du {start_date} a bien ete deplace")

                try:
                    autoprocessPMU(filesInitialDirectory)
                except Exception as e:
                    print(f"Informations {e}")
                break
            
        if timer<0:
            
            print("Le telechargement est anormalement long, nous allons recommencer")
            continue

        
        
        
        start_date += delta
        
    print("tous les fichiers ont bien ete telecharges")

    
    
    


# In[ ]:





# In[22]:



end_date = datetime.date.today()
delta = datetime.timedelta(days=1)
start_date = end_date - delta
 
start_date = datetime.date(2024, 11, 5)
end_date = datetime.date(2024, 11, 6)
#end_date = start_date + delta

delta = datetime.timedelta(days=1)
#end_date = start_date+delta


filesInitialDirectory = r"K:\DATA_FICHIERS\GITECH\PMU_ONLINE_LOTS\\"

path = filesInitialDirectory



for i in range(3):
    try:
        browser = openBrowser()
        connectPMU()
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
    if i == 2 :
        sys.exit(f"Impossible d'executer ce programme malgre 10 tentatives")



# In[24]:


#d = dir()

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]






