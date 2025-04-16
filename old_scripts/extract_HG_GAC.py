#!/usr/bin/env python
# coding: utf-8

# In[5]:


# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 15:58:27 2022

@author: RAWANE
"""
import os
from ftplib import FTP
#import pandas as pd
#import os
#import time
from datetime import date #,datetime,timedelta

today = date.today()
#path = '/Users/cambe/Downloads/'
#path = 'C:\\Users\\CFAC\\Documents\\jules\\Stage\\ExtractedFiles\\'
path = r"K:\DATA_FICHIERS\MINI_SHOP\HG_GAC_FILE\\"

username = "bi_user"
password = "TeamOpti@22"
server   = "192.168.1.103"
date = str(today).replace("-","")
#path_to_file = "daily-modified-horse-racing-tickets-detailed_{date}.csv"
#/LONASEBET
#/SUNUBET
#

def extract_honore_gaming():
    ftp = FTP(server)
    ftp.login(user = username,passwd= password)
    
    dirName = '/HONOREGAMING/'
    #dirName = 'HONOREGAMING\\'
    
    '''
    if filetype == 'honore gaming':
        dirName = '/HONOREGAMING/'
    elif filetype == 'lonase.bet':
        dirName = '/LONASEBET/'
    elif filetype == 'sunubet online':
        dirName = '/SUNUBET/'
    '''
    
    ftp.cwd(dirName)
    
    files = ftp.nlst()
    
    for filename in files:
        
        if filename.startswith('HG_GAC_FILE'+date+'.csv'):
            
            #data = pd.read_csv(filename,sep=';') #,skiprows=range(0, 1)
            #print(data.head())
            
            if os.path.exists(path+filename):
                
                os.remove(path+filename)

            
            
            print("Downloading HG GAC File...")
            #ftp.retrbinary("RETR %s" %filename, open("/Users/cambe/Documents/Python Scripts/Final_file/"+filename,'wb').write)
            ftp.retrbinary("RETR %s" %filename, open(path+filename,'wb').write)
            print(filename)
            
    ftp.close()

def extract_LonaseBet():
    ftp = FTP(server)
    ftp.login(user = username,passwd= password)
    
    dirName = '/LONASEBET/'
    #dirName = 'LONASEBET\\'
    ftp.cwd(dirName)
    
    files = ftp.nlst()
    
    for filename in files:
        
        if filename.startswith('daily-created-settled-customers-bets_'+date+'.csv'):
            
            
            print("Downloading LONASEBET File...")
            #ftp.retrbinary("RETR %s" %filename, open("/Users/cambe/Downloads/lonaseBet/"+filename,'wb').write)
            ftp.retrbinary("RETR %s" %filename, open(path+'LONASEBET\\'+filename,'wb').write)
            print(filename)
            
    ftp.close()

def extract_SunuBet():
    ftp = FTP(server)
    ftp.login(user = username,passwd= password)
    
    dirName = '/SUNUBET/'
    #dirName = 'SUNUBET\\'
    ftp.cwd(dirName)
    
    files = ftp.nlst()
    
    for filename in files:
        
        if filename.startswith('daily-created-settled-customers-bets_'+date+'.csv'):
            
            print("Downloading SUNUBET File...")
            #ftp.retrbinary("RETR %s" %filename, open("/Users/cambe/Downloads/sunubet/online/"+filename,'wb').write)
            ftp.retrbinary("RETR %s" %filename, open(path+'SUNUBET\\'+filename,'wb').write)
            print(filename)
            
    ftp.close()
    
        
extract_honore_gaming()

#extract_LonaseBet()

#extract_SunuBet()

print("tous les fichiers ont bien ete extraits")


# In[6]:


#exec(open("C:\Batchs\scripts_python\chargements\charge_HonoreGaming.py").read())


# In[7]:


#d = dir()

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]

