#!/usr/bin/env python
# coding: utf-8

# In[19]:


import pandas as pd
import numpy as np
import pyodbc
import glob
import shutil

# In[20]:


filesInitialDirectory = r"K:\DATA_FICHIERS\EDITEC\\"

# dest = 'K:\DATA_FICHIERS\BWINNERS\OLD\\'
dest = filesInitialDirectory + "OLD\\"

"""
host = '192.168.1.59'#as the database is on my local machine
database = 'DWHPR'
database = 'DWHPR_TEMP'
#username = 'LONASE\\dwh_sqlserveur_svc'
username = "LONASE\dwh_sqlserveur_svc"
password = 'Bisql@221'

conn = pymssql.connect(host, username, password, database)
cursor = conn.cursor()
"""

SERVER = 'SRVSQLDWHPRD'
DATABASE = 'DWHPR_TEMP'
USERNAME = 'OPTIWARETEMP'
PASSWORD = 'optiwaretemp'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
conn = pyodbc.connect(connectionString)
cursor = conn.cursor()

# suppression de la table temporaire [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_temp_editec]
'''
cursor.execute("""
delete from 
[DWHPR_TEMP].[OPTIWARETEMP].[TEMP_EDITEC]
""")
conn.commit()
#'''

print("la table temporaire a ete videe")
'''
for file in glob.glob(filesInitialDirectory + '*["parifoot","loto","5_90","590","voucher","YAAKAAR"]*csv'):
    # print(file)
    data = pd.read_csv(file, sep=';', index_col=False)
    namefile = file.split("\\")[-1]
    # print(data.columns)

    data = pd.DataFrame(data, columns=['RETAILER', 'DATE', 'TERMINAL', 'VENTES', 'ANNULATIONS', 'TICKET_EMIS',
                                       'TICKET_ANNULE', 'Paid', 'PRODUIT'])

    data = data.replace(np.nan, '')
    data = data.astype(str)
    data = list(data.to_records(index=False))

    # print(data)

    data = [tuple(i) for i in data]
    # print(data[:5])

    # cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_temp_editec]("RETAILER","DATE_VENTE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAYABLE","DATE_PAIEMENT" ,"PAID","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?,?,?)""", data)
    # cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[TEMP_EDITEC]("RETAILER_SALE","T_DATE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAIEMENTS","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?)""", data)
    conn.commit()
    print("le fichier a ete insere au niveau de la table temporaire")

    # namefile = file.split("\\")[-1]
    shutil.move(file, dest + namefile)
    print(dest + namefile)

    # if 'Pick3' in namefile:

    # data = pd.DataFrame(data,columns=['Date&Heure', 'Moblie', 'Operateur', 'NumeroJouer', 'ReferenceTicket','Montant', 'Statut', 'GainaPayer', 'Produit'])
'''

######################### CSV ###################
for file in glob.glob(filesInitialDirectory + '*RECAP*csv'):
    # print(file)
    data = pd.read_csv(file, sep=';', index_col=False)
    namefile = file.split("\\")[-1]
    # print(data.columns)

    data = pd.DataFrame(data, columns=['RETAILER', 'DATE', 'TERMINAL', 'VENTES', 'ANNULATIONS', 'TICKET_EMIS',
                                       'TICKET_ANNULE', 'Paid', 'PRODUIT'])

    data = data.replace(np.nan, '')
    data = data.astype(str)
    data = list(data.to_records(index=False))

    # print(data)

    data = [tuple(i) for i in data]
    # print(data[:5])

    #cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_temp_editec]("RETAILER","DATE_VENTE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAYABLE","DATE_PAIEMENT" ,"PAID","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?,?,?)""", data)
    cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[TEMP_EDITEC]("RETAILER_SALE","T_DATE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAIEMENTS","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?)""", data)
    conn.commit()
    print("le fichier a ete insere au niveau de la table temporaire")

    # namefile = file.split("\\")[-1]
    shutil.move(file, dest + namefile)
    print(dest + namefile)

######################### EXECL #######################3
#'''
for file in glob.glob(filesInitialDirectory + "*RECAP*.xlsx"):
    data1 = pd.read_excel(file, index_col=False, sheet_name=0)
    data2 = pd.read_excel(file, index_col=False, sheet_name=1)
    data3 = pd.read_excel(file, index_col=False, sheet_name=2)

    data1 = pd.DataFrame(data1, columns=['RETAILER', 'DATE', 'TERMINAL', 'VENTES', 'ANNULATIONS', 'TICKET_EMIS',
                                         'TICKET_ANNULE', 'Paid', 'PRODUIT'])
    data2 = pd.DataFrame(data2, columns=['RETAILER', 'DATE', 'TERMINAL', 'VENTES', 'ANNULATIONS', 'TICKET_EMIS',
                                         'TICKET_ANNULE', 'Paid', 'PRODUIT'])
    data3 = pd.DataFrame(data3, columns=['RETAILER', 'DATE', 'TERMINAL', 'VENTES', 'ANNULATIONS', 'TICKET_EMIS',
                                         'TICKET_ANNULE', 'Paid', 'PRODUIT'])

    # print(file)
    # data = pd.read_csv(file,sep=';',index_col=False)
    namefile = file.split("\\")[-1]
    # print(data.columns)

    data1 = data1.replace(np.nan, '')
    data1 = data1.astype(str)
    data1 = list(data1.to_records(index=False))

    # print(data)

    data1 = [tuple(i) for i in data1]

    data2 = data2.replace(np.nan, '')
    data2 = data2.astype(str)
    data2 = list(data2.to_records(index=False))

    # print(data)

    data2 = [tuple(i) for i in data2]

    data3 = data3.replace(np.nan, '')
    data3 = data3.astype(str)
    data3 = list(data3.to_records(index=False))

    # print(data)

    data3 = [tuple(i) for i in data3]

    # cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_temp_editec]("RETAILER","DATE_VENTE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAYABLE","DATE_PAIEMENT" ,"PAID","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?,?,?)""", data1)
    # cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_temp_editec]("RETAILER","DATE_VENTE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAYABLE","DATE_PAIEMENT" ,"PAID","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?,?,?)""", data2)
    # cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_temp_editec]("RETAILER","DATE_VENTE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAYABLE","DATE_PAIEMENT" ,"PAID","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?,?,?)""", data3)

    cursor.executemany(
        """INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[TEMP_EDITEC]("RETAILER_SALE","T_DATE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAIEMENTS","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?)""",
        data1)
    cursor.executemany(
        """INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[TEMP_EDITEC]("RETAILER_SALE","T_DATE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAIEMENTS","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?)""",
        data2)
    cursor.executemany(
        """INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[TEMP_EDITEC]("RETAILER_SALE","T_DATE", "TERMINAL", "VENTES", "ANNULATIONS","TICKET_EMIS","TICKET_ANNULE" ,"PAIEMENTS","PRODUIT") VALUES(?,?,?,?,?,?,?,?,?)""",
        data3)

    conn.commit()
    print("le fichier a ete insere au niveau de la table temporaire")

    # namefile = file.split("\\")[-1]
    shutil.move(file, dest + namefile)
    print(dest + namefile)
#'''
cursor.close()
conn.close()

# In[ ]:


# In[21]:


d = dir()

# You'll need to check for user-defined variables in the directory
for obj in d:
    # checking for built-in variables/functions
    if not obj.startswith('__'):
        # deleting the said obj, since a user-defined function
        del globals()[obj]

# In[ ]:


# In[ ]:




