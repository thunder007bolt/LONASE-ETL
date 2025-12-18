#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
import gc


# In[2]:


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


def bwinnerManipulation(data,debut,fin):
    
    import pymssql
    
    host = 'SRVSQLDWHPRD'
    database = 'DWHPR_TEMP'
    username = 'OPTIWARETEMP'
    password = 'optiwaretemp'
    conn = pymssql.connect(host, username, password, database)
    cursor = conn.cursor()
    encoding = 'UTF-8'

    #global start_date
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    data = [tuple(i) for i in data]
    
    #print(data)
    
    
    #vider la table temporaire optiwaretemp.SRC_PRD_SUNUBET
    
    cursor.execute("""truncate table optiwaretemp.SRC_PRD_SUNUBET""")
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.SRC_PRD_SUNUBET de donnees
    
    cursor.executemany("""INSERT INTO optiwaretemp.SRC_PRD_SUNUBET("NOM", "Total enjeu", "Total Ticket Virtuel", "Total Paiement","Date Vente") VALUES (%s, %s, %s, %s, %s)""", data)
    conn.commit()

    conn.close()
    print("La procedure d'insertion s'est bien deroulee")




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


def connectIpmu():
    
    url = "https://virtual-admin.virtustec.com/backoffice/login"
    browser.get(url)
    
    #time.sleep(5)
    
    #usrname = wait2.until( EC.element_to_be_clickable(( By.ID, usernameId)) )
    #usrname.send_keys(username)
    #usernameId="edit-name"
    username = 'sadio.fall' 
    #browser.find_element(by=By.ID, value=usernameId).send_keys(username)
    #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/ng-component/div/div[1]/div/div[2]/div[1]/form/div/div[3]/div/input"))).send_keys(username)
    
    
    #pwd = wait2.until( EC.element_to_be_clickable(( By.ID, passwordId)) )
    #pwd.send_keys(password)
    #passwordId = 'edit-pass'
    password = "Passer1234!"
    #browser.find_element(by=By.ID, value=passwordId).send_keys(password)
    #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, passwordId))).send_keys(password)
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/ng-component/div/div[1]/div/div[2]/div[1]/form/div/div[4]/div/p-password/div/input"))).send_keys(password)
    
    
    domain = "LONASE-CG"
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/ng-component/div/div[1]/div/div[2]/div[1]/form/div/div[2]/div/input"))).send_keys(domain)
    
    
    #browser.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div/div/div/div[2]/div/form/input[2]").click()
    #driver.find_element_by_xpath("//button[@type='submit']").click()
    #browser.find_element(by=By.ID, value="edit-submit").click()
    #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, "edit-submit"))).click()
    
                                                                                    # /html/body/app-root/app-logged-in/div/app-main-header-component/header/div/div[2]/ul/li/app-user-header/span/p-avatar/div/span
    WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/ng-component/div/div[1]/div/div[2]/div[1]/form/div/div[5]/div/button"))).click()
    #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-main-header-component/header/div/div[2]/ul/li/app-user-header/span/p-avatar/div/span"))).click()
    
    
    #time.sleep(5) 
    
    try:
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//div[contains(@style,'none') and contains(@class, 'dataTables_processing panel panel-default')]")))
        #WebDriverWait(browser,timeout=10*6).until( EC.presence_of_element_located(( By.XPATH, "//span[contains(@text,'senghane_diouf')]")))
        #WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-left-panel/div/div/app-sidebar-component/p-panel/div/div[1]/div[1]/div/strong")))
        
        WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-main-header-component/header/div/div[2]/ul/li/app-user-header/span/p-avatar/div/span")))
        
        #WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        print("la connection a la plateforme est un succes")
    except:
        print("la connection n'a pas pu etre etablie")
        browser.quit()
        
    """
        
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-main-header-component/header/div/div[2]/ul/li/app-entity-header/span"))).click()
    
    
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-right-panel/div/div/app-entities-tree-component/div/div[2]/p-tree/div/div/ul/p-treenode/li/div/span/span/div/div[1]"))).click()
    
    WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/app-left-panel/div/div/app-sidebar-component/p-panelmenu/div/div[1]/div[2]/div/p-panelmenusub/ul/li[1]/p-panelmenusub/ul/li[2]/a"))).click()
    
    """
    
    #/html/body/app-root/app-logged-in/div/app-right-panel/div[1]/div/app-entities-tree-component/div/div[2]/p-tree/div/div/ul/p-treenode/li/ul
    #print(browser.find_element(by=By.XPATH, value=usernameId).send_keys(username))
    
    #return
    
    generateVirtuelAmabel()
    
    print("tous les fichiers ont bien ete telecharges")
    
    return
    
    excl_merged = pd.concat(excl_list, ignore_index=True)
    
    #print(excl_list)
    
    #print(excl_list.head())
    
    #print("mergeZeturf"+str(debut)+"_"+str(fin)+".csv")
    #excl_merged.to_csv(r"C:\Users\CFAC\Documents\jules\Stage\ExtractedFiles\Bwinner\mergeBwinner"+str(debut)+"_"+str(fin)+".csv" , index=False,sep=';',encoding='utf8')
    if debut1<fin1:
        
        excl_merged.to_csv(filesInitialDirectory+"mergeVirtuelAmabel "+str(debut1)+"_"+str(fin1)+".csv" , index=False,sep=';',encoding='utf8')
    
    #print (excl_merged)
    bwinnerManipulation(excl_merged,debut1,fin1)
    
    
    #return


    
    """
    for i in range(3):
        try:
            generateIpmu()
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
        
        
    #generateAfitechFiles()

    


# In[6]:


def generateVirtuelAmabel():
    
    url = 'https://virtual-admin.virtustec.com/backoffice/manage/17828610/tickets/pivotTable'
    
    
    browser.get(url)
    
    
    global start_date
    global attemp
    
    #while start_date < end_date:
    while start_date < end_date:
        
        for file in glob.glob(filesInitialDirectory+'PivotTable_*.xlsx') :
            os.remove(file)
    


        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/div/div[1]/div[1]/p-button[1]/button"))).click()
        
        WebDriverWait(browser,timeout=20).until( EC.presence_of_element_located(( By.XPATH, "/html/body/div/div/form/div/div/div[1]/calendar-custom-fc-component/div/p-button/button"))).click()


        # yesterday
        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/div/div[1]/p-listbox/div/div/ul/li[2]/div"))).click()
        
        # current year and month
        
        #cym = browser.find_element(by=By.XPATH, value="//div[@class='p-datepicker-title ng-tns-c49-45']")
        # browser.find_elements(by=By.XPATH, value="//tr[@class='p-datepicker-title ng-tns-c49-45']")
        #cym = browser.find_element(by=By.XPATH, value="/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/div")
        #print(cym.text)
        
        dateNotPicked = True
        
        time.sleep(1)
        
        while(dateNotPicked):
            
                                                                                                            # /html/body/div[2]/div/div[2]/p-calendar/span/div/div/div[1]/div[1]
            #MonthYear = WebDriverWait(browser,timeout=20).until( EC.presence_of_element_located(( By.XPATH, "/html/body/div[2]/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/div"))).text

            MonthYear = browser.find_element(by=By.XPATH, value="/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/div").text
            #print(MonthYear," ", start_date.strftime('%B %Y'))
            #print(MonthYear == start_date.strftime('%B %Y'))
            #print(type(MonthYear), " ", type(start_date.strftime('%B %Y')))
            
            #date_string = "21 June 2018"
            #date_object = datetime.datetime.strptime(date_string, "%d %B %Y")

            #return
        

            #if MonthYear == start_date.strftime('%B %Y'):
            if datetime.datetime.strptime('01 '+str(MonthYear), "%d %B %Y") == datetime.datetime.strptime('01 '+start_date.strftime('%B %Y'), "%d %B %Y"):
                #print("hi")
                # to : choose date
                                                                                                                                                               # p-ripple p-element ng-tns-c49-101 ng-star-inserted
                #for tr in browser.find_elements(by=By.XPATH, value="/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[2]/table/tbody/*/*/span"):
                #for tr in browser.find_elements(by=By.XPATH, value="//span[@class='p-ripple p-element ng-tns-c49-124 ng-star-inserted']"):
                for tr in browser.find_elements(by=By.XPATH, value="/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[2]/table/tbody/*/*/span[not(contains(@class,'p-disabled'))]"):
        
                    #print(tr.text)
                    #print(('0'+str(tr.text).strip().lower())[-2:], " ",start_date.strftime("%d").lower() )
                    
                    if ('0'+str(tr.text).strip().lower())[-2:]==(start_date.strftime("%d").lower()):
                        tr.click()
                        tr.click()
                        dateNotPicked = False
                        break

                #time.sleep(0.1)

            elif datetime.datetime.strptime('01 '+str(MonthYear), "%d %B %Y") < datetime.datetime.strptime('01 '+start_date.strftime('%B %Y'), "%d %B %Y"):
                # pass
                WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/div/div[2]/p-calendar/span/div/div/div[2]/div[1]/button"))).click()
            
            elif datetime.datetime.strptime('01 '+str(MonthYear), "%d %B %Y") > datetime.datetime.strptime('01 '+start_date.strftime('%B %Y'), "%d %B %Y"):
                # /html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/button[1]
                                                                                                # /html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/button[1]
                WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/button[1]"))).click()

                
        #return

        #time.sleep(10)
        # validate
        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div/div/div[3]/div/p-button[1]/button"))).click()
                                                                                        # /html/body/div[2]/div/div[4]/div[2]/p-button[1]/button
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/div[2]/div/div[4]/div[2]/p-button[1]/button"))).click()

        #return
        # search
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/div/div[1]/div[1]/p-button[2]/button"))).click()
        
        
        #/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/div/div[2]/div/p-treetable/div/div[1]/div/spinnericon/svg
        '''
        try:
            WebDriverWait(browser,timeout=10).until( EC.presence_of_element_located(( By.XPATH, "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/div/div[2]/div/p-treetable/div/div[1]/div/spinnericon/svg")))
        except:
            pass
        '''
        
        #WebDriverWait(browser,timeout=10).until( EC.invisibility_of_element_located(( By.XPATH, "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/div/div[2]/div/p-treetable/div/div[1]/div/spinnericon/svg")))
        
        
        
        WebDriverWait(browser,timeout=60*5).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/div/div[1]/div[2]/div[3]/p-button[1]/button"))).click()
        
        WebDriverWait(browser,timeout=20).until( EC.presence_of_element_located(( By.XPATH, "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/p-dialog[2]/div/div/div[4]/p-button[1]/button"))).click()

        timer = 21 
        
        while timer>=0:
            time.sleep(1)
            timer-=1
            p=glob.glob(filesInitialDirectory+'PivotTable_*.xlsx')
            if len(p)>0:
                
                df = pd.read_excel(p[0],sheet_name=1,index_col=False)

                ##print(df)

                df['JOUR'] = start_date.strftime('%d/%m/%Y')
                df['ANNEE'] = str(start_date.strftime('%Y'))
                df['MOIS'] = str(start_date.strftime('%m'))
                
                filename = 'Amabel_jeux_virtuels_'+str(start_date)+".csv"
                
                if os.path.exists(filesInitialDirectory+filename):
                    os.remove(filesInitialDirectory+filename)
        
                df.to_csv(filesInitialDirectory+filename,sep=';',index=False)
                
                os.remove(p[0])
                
                print(f"le fichier amabel jeux virtuel du {start_date} a bien ete telecharge")
                
                #start_date-=delta
                start_date+=delta
                break

        
        #return

        
        """
        # deplier CFA
                                                                                        # /html/body/app-root/app-logged-in/div/div/div/app-turnover-component/div/div[2]/div/p-treetable/div/div/table/tbody/tr[2]/td[1]/p-treetabletoggler/button
                                                                                        # /html/body/app-root/app-logged-in/div/div/div/app-turnover-component/div/div[2]/div/p-treetable/div/div/table/tbody/tr[2]/td[1]/div/p-treetabletoggler/button
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/div/div/app-turnover-component/div/div[2]/div/p-treetable/div/div/table/tbody/tr[2]/td[1]/div/p-treetabletoggler/button"))).click()

        # deplier AmabelTech
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "/html/body/app-root/app-logged-in/div/div/div/app-turnover-component/div/div[2]/div/p-treetable/div/div/table/tbody/tr[3]/td[1]/div/p-treetabletoggler/button"))).click()

        


        #WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.CLASS_NAME, "paginator-node UNIT ng-star-inserted")))
        WebDriverWait(browser,timeout=10).until( EC.element_to_be_clickable(( By.XPATH, "//tr[@class='UNIT ng-star-inserted']")))
        data = []
        #time.sleep(1)
        for line in browser.find_elements(by=By.XPATH, value="//tr[@class='UNIT ng-star-inserted']"):
            #liste = []
            a = str(line.text)
            a = a.strip().replace('\u202f',' ')
            a = a.splitlines()
            #liste.append(a)
            data.append(a)

            #print(a)

            '''
            for element in line.find_elements(by=By.TAG_NAME, value="td"):


                a = str(element.text)
                a = a.strip().replace('\u202f',' ')
                a = a.splitlines()
                liste.append(a)

            print(liste)
            '''
            #print("fin liste")

        df = pd.DataFrame(data )#, columns = ['Name', 'Age']) 
        
        #print(df)

        df = df.iloc[:,[0,4,5,7]]
        
        print(df)
        

        df[2] = [str(i).split(' ')[-1] for i in df[2]]


        df.columns = ["AgentFirstName","TotalStake","TotalTickets","TotalWonAmount"]
        
        df = df.replace(',','', regex=True)
        #df = df.replace('.',',', regex=True)
        
        #df['TotalStake'] = df['TotalStake'].replace('.',',', regex=True)
        #df['TotalWonAmount'] = df['TotalWonAmount'].replace('.',',', regex=True)

        df['TotalStake'] = [str(i).replace('.',',') for i in df['TotalStake'] ]
        df['TotalWonAmount'] = [str(i).replace('.',',') for i in df['TotalWonAmount'] ]
        df['TotalTickets'] = [str(i).replace('.',',') for i in df['TotalTickets'] ]

        df['date'] = start_date.strftime('%d/%m/%Y')
        
        excl_list.append(df[["AgentFirstName","TotalStake","TotalTickets","TotalWonAmount","date"]])
        
        print(f"le fichier virtuel amabel du {start_date} a bien ete telecharge")
        

        df.to_csv(filesInitialDirectory+'virtuelAmabel'+str(start_date)+'.csv',sep=';',index=False)#,columns=["AgentFirstName","TotalTickets","TotalStake","TotalWonAmount"])
        
        start_date+=delta

        #time.sleep(2)
        
        #start_date+=delta
        
        """
        
        
        
        



    
    


# In[ ]:





# In[ ]:





# In[7]:


attemp = 0
excl_list = []
#global start_date
#start_date = datetime.date(2022, 7, 1)
#debut = datetime.date(2022, 7, 1)
#end_date = datetime.date(2022, 6, 1)
delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
#delta = datetime.timedelta(days=1)
start_date = end_date - delta

#start_date = datetime.date(2025, 4, 2)
#end_date = datetime.date(2025, 4, 6)

#delta = datetime.timedelta(days=1)
#end_date = start_date+delta

filesInitialDirectory = r"K:\DATA_FICHIERS\VIRTUEL_AMABEL\DETAILED\\"

#global end_date

debut1 = start_date
fin1 = end_date-delta

#browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

#connectIpmu()

#"""
for i in range(10):
    try:
        
        
        browser=openBrowser()

        #browser.implicitly_wait(20)
        #browser.maximize_window()

        connectIpmu()
        
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
        
#handleFinancialFile()

#"""

#time.sleep(5)
        
#browser.quit()




# In[8]:


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




