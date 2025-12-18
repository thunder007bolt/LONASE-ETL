#!/usr/bin/env python
# coding: utf-8

# In[56]:


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


# In[ ]:





# In[57]:


import pandas as pd
import numpy as np
import win32com.client
import os
import re
#import win32api
#import win32net



# Choisissez un repertoire sur votre machine comme indiqué où se trouve les fichiers xls à formatter
#path= '/Users/hp/Downloads/gitech/'
#/Users/hp/Documents/GITECH/ALR_MARS_2020/

# Choisissez un repertoire sur votre machine comme indiqué où vous souhaitez deposer les fichiers csv obtenus après formattage 
#pathFinal='/Documents/CGFiles/depotdaily/'



def autoprocessGitech(path):
# Tous les fichiers du repertoire path seront traités

    o = win32com.client.gencache.EnsureDispatch('Excel.Application')
    o.Visible = False


    #for path,dirs,files in os.walk(path):
    for filename in os.listdir(path):
        if "Etat de la course" in filename and filename.endswith('.xls'):
            #print(filename)
            #changer l'extension du fichier en xlsx
            
            output = path + filename.replace('.xls','.xlsx')
            #print(output)
            wb = o.Workbooks.Open(path+filename)
            wb.ActiveSheet.SaveAs(output,51)
            wb.Close(True)
            os.remove(path+filename)
            # lecture du fichier xls en ommettant les 5 premieres lignes (entete y compris)
            data = pd.read_excel(output,skiprows=range(1, 6))
            
            # recuperer la date dans le fichier
            dat1 = pd.read_excel(output) #,error_bad_lines=False
            date = dat1.iloc[1].str.replace("Date : Du:","").str.split(":")[0][0].replace("/","-").replace(" ","").replace("Au","")
            
            #print(date)
            
            # renommage des colonnes
            data.columns = ['No','Agences','Operateur','Vente','Annulation','Remboursement','Paiement','Resultat']
            
            # suppression de toutes les lignes comptenant Total et montant global
            data = data[data.Operateur != 'Total']
            data = data[data.Operateur != 'montant global']
            
            # suppression de la colonne No 
            data = data.drop('No',axis=1)
            
            
            # insertion et remplissage de la colonne date suivant la date indiquée dans le fichier xls
            date_serie = pd.Series(np.random.randn(len(data)), index=data.index)
            data.insert(2, "Date vente",date_serie, True)
            data['Date vente'] = data['Date vente'].apply(lambda x: str(x).replace(str(x),str(date.replace("-","/"))))
            
            # remplissage de la colonne Agence, les valeurs nulles sont remplies par leurs agences correspondantes 
            
            data = data.copy(deep=True)
            
            v_agence = data['Agences'].iloc[0]
            for i in range(0,len(data),1):
                #print(v_agence)
                if(pd.notnull(data['Agences'].iloc[i])):
                    v_agence = data['Agences'].iloc[i]
                else:
                    data['Agences'].iloc[i] = v_agence
            
            
            # Formattage des colonnes Vente, Annulation, Remboursement, Paiement, Resultat en numeric
            data['Resultat'] = data['Resultat'].map(lambda x: str(x).replace(u'\xa0',u''))
            data['Vente'] = data['Vente'].map(lambda x: str(x).replace(u'\xa0',u''))
            data['Annulation'] = data['Annulation'].map(lambda x: str(x).replace(u'\xa0',u''))
            data['Remboursement'] = data['Remboursement'].map(lambda x: str(x).replace(u'\xa0',u''))
            data['Paiement'] = data['Paiement'].map(lambda x: str(x).replace(u'\xa0',u''))
            
            
            data['Resultat'] = data['Resultat'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )
            data['Vente'] = data['Vente'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )
            
            data['Annulation'] = data['Annulation'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )
            data['Remboursement'] = data['Remboursement'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )
            data['Paiement'] = data['Paiement'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )
        
            
            data[['Vente','Annulation','Remboursement','Paiement','Resultat']] = data[['Vente','Annulation','Remboursement','Paiement','Resultat']].astype('int64')
            
            #print(data.head())
            #print(data.tail())
            
            #print(win32com.__gen_path__) C:\Users\hp\AppData\Local\Temp\gen_py\3.7
            namedfile = 'GITECH '+date.split('-')[2]+'-'+date.split('-')[1]+'-'+date.split('-')[0]+'.csv'
            
            if os.path.exists(path+'GITECH '+date.split('-')[2]+'-'+date.split('-')[1]+'-'+date.split('-')[0]+'.csv'):
                os.remove(path+'GITECH '+date.split('-')[2]+'-'+date.split('-')[1]+'-'+date.split('-')[0]+'.csv')
        
            
            data.to_csv(path+'GITECH '+date.split('-')[2]+'-'+date.split('-')[1]+'-'+date.split('-')[0]+'.csv', index=False,sep=';',encoding='utf8')
            
            print(f"le fichier {namedfile} a bien ete transforme")
            
            os.remove(path + filename.replace('.xls','.xlsx'))
    #print("tous les fichiers ont bien ete transformés")

#filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'
#autoprocessGitech(filesInitialDirectory)

from selenium.webdriver.chrome.service import Service
# In[58]:


def openBrowser():
    
    browser=0
    
    a=0
    #while True:
    for i in range(5):
        try:
            chromeOptions = webdriver.ChromeOptions()
            prefs = {"download.default_directory" : filesInitialDirectory}
            #prefs = {"download_restrictions" : 0}
            #prefs.put("download_restrictions", 3)
            chromeOptions.add_experimental_option("prefs",prefs)
            #chrome_options.add_argument("--allow-running-insecure-content")
            #chromeOptions.add_experimental_option("--allow-running-insecure-content")
            #chromeOptions.add_argument("--allow-running-insecure-content")
            
            chromeOptions.add_argument("--unsafely-treat-insecure-origin-as-secure=http://115.110.148.83/bwinnersmis/Administration/")
            chromeOptions.add_argument("--headless")
            chromeOptions.add_argument("--disable-gpu")
            #chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=http://exampleDomain1.com, http://exampleDomain2.com")
            #chromeOptions.add_experimental_option("prefs",prefs)
            
            #options.addArguments("--unsafely-treat-insecure-origin-as-secure=" + insecureOriginDominURL)
            
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


# In[59]:


def connectGitech():
    
    #url = "http://115.110.148.76/lonasemis/Lonase_administration/Login.aspx"
    url = "http://115.110.148.83/bwinnersmis/Administration/Login.aspx"
    
    
    browser.get(url)
    
    usernameId = "Username"
    username = 'ndeye.khady'

    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
    
    
    passwordId = "Password"
    password = 'dcg2024'
    
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
    
    #return
    
    generateGitech()
    


# In[60]:


import pandas as pd
import numpy as np
import win32com.client
import os
import re
#import win32api
#import win32net



# Choisissez un repertoire sur votre machine comme indiqué où se trouve les fichiers xls à formatter
#path= '/Users/hp/Downloads/gitech/'
#/Users/hp/Documents/GITECH/ALR_MARS_2020/

# Choisissez un repertoire sur votre machine comme indiqué où vous souhaitez deposer les fichiers csv obtenus après formattage 
#pathFinal='/Documents/CGFiles/depotdaily/'



def autoprocessGitech(path):
# Tous les fichiers du repertoire path seront traités

    o = win32com.client.gencache.EnsureDispatch('Excel.Application')
    o.Visible = False

    for filename in glob.glob(filesInitialDirectory+"Recette paiement Journalier*xls"):
        #print(filename)
        #changer l'extension du fichier en xlsx

        #output = path + filename.replace('.xls','.xlsx')
        output = filename.replace('.xls','.xlsx')
        #print(output)
        #wb = o.Workbooks.Open(path+filename)
        wb = o.Workbooks.Open(filename)
        wb.ActiveSheet.SaveAs(output,51)
        wb.Close(True)
        os.remove(filename)
        # lecture du fichier xls en ommettant les 5 premieres lignes (entete y compris)
        data = pd.read_excel(output,skiprows=range(0, 6), usecols="A:J")
        
        #print(data.columns)
        #print(data[:3])
        
        
        # recuperer la date dans le fichier
        dat1 = pd.read_excel(output) #,error_bad_lines=False
        #print(dat1)
        #date = dat1.iloc[2][0].replace("Du: ","").split(": ")[0].replace("/","-").replace(" ","").replace("Au","").replace(" ","")

        #print(date)

        # renommage des colonnes
        #data.columns = ['No','IdJeu','NomJeu','Vente','Paiement','PourcentagePaiement']
        
        #data.columns = ['No','Agences','Operateur','Vente','Annulation','Remboursement','Paiement','Resultat']

        data.columns = ['No','Agences','Operateurs','date de vente','Recette','Annulation','Ventes Resultant','comm vente','Paiements','Resultats']

        data = data[:-6]
        
        data['Operateurs'] = data['Operateurs'].replace(np.nan, '')

        
        #print(data[-4],data[-3],data[-2],data[-1])
        # Formattage des colonnes Vente, Annulation, Remboursement, Paiement, Resultat en numeric
        #data['Agences'] = data['Agences'].map(lambda x: str(x).replace(u'\xa0',u''))
        data['Operateurs'] = data['Operateurs'].map(lambda x: str(x).replace(u'\xa0',u''))
        data['date de vente'] = data['date de vente'].map(lambda x: str(x).replace(u'\xa0',u''))
        data['Recette'] = data['Recette'].map(lambda x: str(x).replace(u'\xa0',u''))
        data['Annulation'] = data['Annulation'].map(lambda x: str(x).replace(u'\xa0',u''))
        data['Recette'] = data['Recette'].map(lambda x: str(x).replace(u'\xa0',u''))
        data['Ventes Resultant'] = data['Ventes Resultant'].map(lambda x: str(x).replace(u'\xa0',u''))
        data['comm vente'] = data['comm vente'].map(lambda x: str(x).replace(u'\xa0',u''))
        data['Paiements'] = data['Paiements'].map(lambda x: str(x).replace(u'\xa0',u''))
        data['Resultats'] = data['Resultats'].map(lambda x: str(x).replace(u'\xa0',u''))
        
        data['date de vente'] = [ str(i)[:10] for i in data['date de vente'] ]
        
        
        
        if os.path.exists(filesInitialDirectory+'BWINNER_GAMBIE_'+str(start_date)+'.csv'):
            os.remove(filesInitialDirectory+'BWINNER_GAMBIE_'+str(start_date)+'.csv')
        
        data.to_csv(filesInitialDirectory+'BWINNER_GAMBIE_'+str(start_date)+'.csv', index=False,sep=';',encoding='utf8')
        #data.to_csv('C:\Users\cambe\Documents\Python Scripts\Final_file\GITECH '+date.split('-')[2]+'-'+date.split('-')[1]+'-'+date.split('-')[0]+'.csv', index=False,sep=';',encoding='utf8')
        
        print(f"le fichier a bien ete transforme")
        
        if os.path.exists(filename.replace('.xls','.xlsx')):
            os.remove(filename.replace('.xls','.xlsx'))
            
            #return
        

# In[61]:


def generateGitech():
    
    #url = "http://115.110.148.76/lonasemis/Lonase_administration/HorseDrawWiseSales.aspx"
    url = 'http://115.110.148.83/bwinnersmis/Administration/DatewisePa.aspx'
    
    #return
    
    # Recette paiement Journalier (par jour).xls
    
    #browser.get(url)
    
    global start_date
    #global end_date
    
    #start_date = datetime.date(2022, 2, 27)
    #end_date = datetime.date(2022, 3, 2)
    #delta = datetime.timedelta(days=1)
    while start_date < end_date:
        
        for i in glob.glob(filesInitialDirectory+'Recette paiement Journalier*xl*'):
            os.remove(i)
            
        browser.get(url)
        '''
        lastMonth = date(start_date.year, start_date.month, calendar.monthrange(start_date.year, start_date.month)[1])
        
        if end_date < lastMonth :
            
            lastMonth = end_date - delta
        '''
        
        
        
        
        """
        # Find id of option
        x = driver.find_element_by_id('RESULT_RadioButton-9')
        drop = Select(x)

        # Select by value
        drop.select_by_value("Radio-0")
        
        """
        
        #minute = Select(browser.find_element(by=By.XPATH, value="/html/body/div[3]/div[3]/div[1]/div/div/select[2]"))
        #minute.select_by_visible_text("59")
        
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_FDate_ddlDate"))).select_by_visible_text(str(start_date.strftime('%d')))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_TDate_ddlDate"))).select_by_visible_text(str(start_date.strftime('%d')))
        
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_FDate_ddlDate"))).send_keys(str(int(jour)))
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_TDate_ddlDate"))).send_keys(str(int(jour)))
        
        
        
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_FDate_ddlMonth"))).send_keys(str(mois))
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_TDate_ddlMonth"))).send_keys(str(mois))
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_FDate_ddlMonth"))).select_by_visible_text(str(mois))
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_TDate_ddlMonth"))).select_by_visible_text(str(mois))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_FDate_ddlMonth"))).select_by_visible_text(str(start_date.strftime('%m')))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_TDate_ddlMonth"))).select_by_visible_text(str(start_date.strftime('%m')))
        
        
        
        
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_FDate_ddlYear"))).send_keys(str(annee))
        #WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_TDate_ddlYear"))).send_keys(str(annee))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_FDate_ddlYear"))).select_by_visible_text(str(start_date.strftime('%Y')))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_TDate_ddlYear"))).select_by_visible_text(str(start_date.strftime('%Y')))
        
        
        #print("le mois")
        #print(str(mois))
        
        #break
        
        
        
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_btnSubmit"))).click()
        
        try:
            #WebDriverWait(browser,timeout=5).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'Aucun enregistrement trouv')]")))
            #WebDriverWait(browser,timeout=5).until( EC.presence_of_element_located(( By.ID, "OpsValidator_ContentPlaceHolder1_lblErrInfo")))
                                                                                                                                                                    # //*[contains(text(), 'My Button')]
            WebDriverWait(browser,timeout=5).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@id,'OpsValidator_ContentPlaceHolder1_lblErrInfo') and contains(text(),'Aucun enregistrement trouv')]")))
            
            print(f"le fichier de la plateforme BWINNER GAMBIE du {start_date} n'existe pas")
            start_date += delta
            continue
                
        except:
            #print("erreur")
            pass
        
        
        #time.sleep(10)
        
        WebDriverWait(browser,timeout=15*3).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_btnExcel"))).click()
        
        
        timer = 60*2

        while timer>=0:
            time.sleep(1)
            timer-=1
            
            p=glob.glob(filesInitialDirectory+'Recette paiement Journalier*xls') 
            if len(p)>0:
                
                #return
                #filename = p[0].split("\\")[-1]
                #shutil.move(path+filename,filesInitialDirectory+filename)
                
                #print(f"le fichier de la plateforme Premier SN du {start_date} a bien ete telecharge et deplace")
                print(f"le fichier de la plateforme BWINNER GAMBIE du {start_date} a bien ete telecharge")
                
                
                '''
                #src = os.path.join(path,filename)
                #src = os.path.join(p[0])
                filename = p[0].split("\\")[-1]
                
                src = os.path.join(path,filename)
                #final_file = 'SUNUBET '+str(start_date)+'.csv'
                
                final_file = filename
                
                dest = os.path.join(filesInitialDirectory,final_file) 
                #os.renames(src,dest) 

                shutil.move(src,dest) 

                """
                final_file = re.sub('\d*','', filename).replace('.csv',' '+str(start_date)+'.csv')
                # dest = os.path.join('/Users/hp/website_login/',final_file)
                #dest = os.path.join(path+'/ParifootOline/',final_file)
                dest = os.path.join(filesInitialDirectory,final_file)
                #os.renames(src,dest)
                shutil.move(src,dest)
                #print(final_file)
                """
                print(f"le fichier de la plateforme gitech du {start_date} a bien ete deplace")
                '''
                
                #renameToZoneBetting(downloadPath)
                autoprocessGitech(filesInitialDirectory)
                start_date += delta
                #start_date = lastMonth + delta
                
                break
            
            
            #if  "block" not in browser.find_element(by=By.CLASS_NAME, value="dataTables_processing").get_attribute("style"):
                #break
        if timer<0:
            
            print("Le telechargement est anormalement long, nous allons recommencer")
            continue

        
        
        
        #start_date += delta
        
    print("tous les fichiers ont bien ete telecharges")

    
    
    


# In[ ]:





# In[62]:


#global start_date
#start_date = datetime.date(2025,3, 1)
#debut = datetime.date(2022, 7, 1)
#end_date = datetime.date(2025, 3, 2)

end_date = datetime.date.today()
delta = datetime.timedelta(days=1)
start_date = end_date - delta


delta = datetime.timedelta(days=1)
#start_date = datetime.date(2025, 4, 4)
#end_date = datetime.date(2025, 4, 5)
#end_date = start_date+delta

#path = "C:\\Users\\OPTIWARE-ENTERPRISE\\Downloads\\" CFAC
#path = "C:\\Users\\CFAC\\Downloads\\" 
#filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\'
#filesInitialDirectory = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'
#filesInitialDirectory = 'C:\\Users\\OPTIWARE-ENTERPRISE\\Documents\\jules\\Stage\\ExtractedFiles\\premierSnAugust\\'

filesInitialDirectory = "K:\\DATA_FICHIERS\\BWINNERS_GAMBIE\\"

path = filesInitialDirectory


#global end_date

#browser=openBrowser() £µ877777



        #browser.implicitly_wait(20)
        #browser.maximize_window()

#connectGitech()

#"""
for i in range(5):
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


# In[63]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_ALR_GITECH.py").read())


# In[64]:


#d = dir()

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


# In[65]:


#C:\Windows\System32\cmd.exe /C python "C:\Batchs\scripts_python\extractions\journalier\try.py"


# In[66]:


#import sys
#print(sys.version)


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




