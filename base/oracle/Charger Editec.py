#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os
import shutil
import glob


# In[2]:


username = 'USER_DWHPR'
password = 'optiware2016'

#dsn = '192.168.1.237/OPTIWARE_TEMP'
#'''
import cx_Oracle
dsn = cx_Oracle.makedsn('192.168.1.237', 1521, service_name='DWHPR')
port = 1521
encoding = 'UTF-8'

try:
    cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_6")
except:
    print("La base de donnee a deja ete initialisee")

conn = cx_Oracle.connect(username,password,dsn)
cur = conn.cursor() #creates a cursor object

#'''

directory = r'K:\DATA_FICHIERS\EDITEC\\'


# In[7]:


file = r"K:\DATA_FICHIERS\EDITEC\OLD\RECAP_EDITEC_JANVIER_2025.csv"


df1 = pd.read_csv(file,index_col=False, sep=';')
df1 = df1[df1['DATE'] == '01/01/2025']
#df1['DATE'] = pd.to_datetime(df1['DATE'], errors='coerce')
#df1_filtered = df1[df1['DATE'].dt.date == pd.to_datetime('2025-01-01').date()]
df1 = df1[df1['PRODUIT'] == 'LOTO']

montant  = df1['PAYABLE'].sum()

print(df1.columns)

data = df1.replace(np.nan, '')
data=data.astype(str)
data = list(data.to_records(index=False))
cur.executemany("""INSERT INTO optiwaretemp.src_prd_temp_editec("RETAILER","DATE_VENTE", "TERMINAL", "VENTES","TICKET_EMIS","TICKET_ANNULE", "ANNULATIONS" ,"PAID" ,"PRODUIT","PAYABLE") VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)""", data)
conn.commit()

'''
file = "K:\DATA_FICHIERS\EDITEC\OLD\EDITEc.xlsx"
df1 = pd.read_excel(file,index_col=False, sheet_name=0)

df1[ df['DATE'] =  ]
#print(df1)
print(df1.groupby(['PRODUIT'])['VENTES','ANNULATIONS','PAYABLE','Paid'].sum())
#'''



# In[8]:


#break