#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os
import shutil
import glob
import cx_Oracle


# In[2]:


username = 'USER_DWHPR'
password = 'optiware2016'

#dsn = '192.168.1.237/OPTIWARE_TEMP'
dsn = cx_Oracle.makedsn('192.168.1.237', 1521, service_name='DWHPR')
port = 1521
encoding = 'UTF-8'

try:
    cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_6")
except:
    print("La base de donnee a deja ete initialisee")

conn = cx_Oracle.connect(username,password,dsn)
cur = conn.cursor() #creates a cursor object

file = r"K:\DATA_FICHIERS\EDITEC\RECAP EDITEC MAI 25.xlsx"

#PARIFOOT
df1 = pd.read_excel(file,index_col=False, sheet_name=0)
#LOTO
df2 = pd.read_excel(file,index_col=False, sheet_name=1)
#YAAKAAR
df3 = pd.read_excel(file,index_col=False, sheet_name=2)

cur.execute("""truncate table optiwaretemp.src_prd_temp_editec""")
conn.commit()


#'''
#PARIFOOT

data = df1.replace(np.nan, '')
data=data.astype(str)
data = list(data.to_records(index=False))
print(len(data))
cur.executemany("""INSERT INTO optiwaretemp.src_prd_temp_editec("RETAILER","DATE_VENTE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAYABLE","DATE_PAIEMENT" ,"PAID","PRODUIT") VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11)""", data)
conn.commit()
print('Données PARIFOOT insérées')

#LOTO
data = df2.replace(np.nan, '')
data=data.astype(str)
data = list(data.to_records(index=False))
print(len(data))

cur.executemany("""INSERT INTO optiwaretemp.src_prd_temp_editec("RETAILER","DATE_VENTE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAYABLE","DATE_PAIEMENT" ,"PAID","PRODUIT") VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11)""", data)
conn.commit()
print('Données LOTO insérées')

#YAAKAAR
data = df3.replace(np.nan, '')
data=data.astype(str)
data = list(data.to_records(index=False))
print(len(data))

cur.executemany("""INSERT INTO optiwaretemp.src_prd_temp_editec("RETAILER","DATE_VENTE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAYABLE","DATE_PAIEMENT" ,"PAID","PRODUIT") VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11)""", data)
conn.commit()
print('Données YAAKAAR insérées')

#UPDATES
cur.execute(""" update  optiwaretemp.src_prd_temp_editec
set payable = paid 
where 'VOUCHER' in upper(produit) """)
conn.commit()
cur.execute(""" update  optiwaretemp.src_prd_temp_editec
set date_vente = to_char(to_date(date_vente,'YYYY-MM-DD'),'DD/MM/YYYY') """)
conn.commit()

cur.close()
conn.close()