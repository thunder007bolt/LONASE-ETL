#!/usr/bin/env python
# coding: utf-8

# In[14]:


import pandas as pd
import numpy as np
import pymssql
import glob
import shutil
import pyodbc
import os


# In[15]:


filesInitialDirectory = r"K:\DATA_FICHIERS\LONASEBET\GLOBAL\\"

dest = 'K:\DATA_FICHIERS\LONASEBET\GLOBAL\OLD\\'

SERVER = 'SRVSQLDWHPRD'
DATABASE = 'DWHPR_TEMP'
USERNAME = 'OPTIWARETEMP'
PASSWORD = 'optiwaretemp'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
conn = pyodbc.connect(connectionString)
cursor = conn.cursor()



# suppression de la table temporaire
cursor.execute("""truncate table [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_globalLonasebet]""")
conn.commit()
print("la table temporaire a ete videe")

for file in glob.glob(filesInitialDirectory+"globalLonasebet*csv"):
    #print(file)
    data = pd.read_csv(file,sep=';',index_col=False,encoding='latin1')
    
    #print(data.columns)
    
    
    #print(len(data.columns))
    #break
    
    #data = pd.DataFrame(data,columns=['AgentFirstName', 'TotalStake', 'TotalTickets', 'TotalWonAmount','date'])
    
    
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))

    #print(data)

    data = [tuple(i) for i in data]
        
    
    # Insertion au niveau de la table temporaire
    cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_globalLonasebet]("Nombre_de_paris","Nombre_de_tickets"
      ,"Mises"
      ,"Produit_brut_des_jeux"
      ,"Rentabilite"
      ,"Mises_en_cours"
      ,"Gains_Joueurs"
      ,"Montant_total_a_payer"
      ,"Montant_total_paye"
      ,"Montant_a_payer_expire"
      ,"Produit_bruts_des_jeux_Cashed_Out"
      ,"JOUR"
      ,"ANNEE"
      ,"MOIS"
      ,"CANAL"
      ,"CATEGORIE") VALUES(?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?)""", data)
    conn.commit()
    print("le fichier a ete insere au niveau de la table temporaire")
    
    #break
    
    namefile = file.split("\\")[-1]
    try:
        
        shutil.move(file,dest+namefile)
        
    except:
        os.remove(dest+namefile)
        shutil.move(file,dest+namefile)
    print(dest+namefile)
    
    

cursor.execute("""  
  delete from [DWHPR_TEMP].[OPTIWARETEMP].[ar_globalLonasebet]
  where cast(jour as date) in (select distinct cast(jour as date) from [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_globalLonasebet])
  
  """)
conn.commit()



cursor.execute("""
insert into [DWHPR_TEMP].[OPTIWARETEMP].[ar_globalLonasebet]
select * from [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_globalLonasebet]
               
""")
conn.commit()

cursor.close()
conn.close()  
    



# In[16]:


#d = dir()

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]

#import gc
#gc.collect()

#import gc
#gc.collect()

