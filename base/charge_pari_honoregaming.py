import pandas as pd
import numpy as np
import pyodbc
import glob
import shutil


# In[20]:


filesInitialDirectory = r"K:\DATA_FICHIERS\HONORE_GAMING\PARI\Pari_avec_agence\\"

#dest = 'K:\DATA_FICHIERS\BWINNERS\OLD\\'
dest = filesInitialDirectory+"OLD\\"


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



# suppression de la table temporaire 
cursor.execute("""
delete from 
[DWHPR_TEMP].[OPTIWARETEMP].SRC_PRD_PARI_HONOREGAMING;
""")
conn.commit()

print("la table temporaire a ete videe")

for file in glob.glob(filesInitialDirectory+'HG_PARI*csv'):
    #print(file)
    data = pd.read_csv(file,sep=';',index_col=False)
    namefile = file.split("\\")[-1]
    #print(data.columns)
   
    data = pd.DataFrame(data,columns=['Year', 'Month', 'JOUR', 'RetailCategoryName', 'AGENCE', 
                                  'TerminalDescription', 'CATEGORIE_FINALE', 'GameName',
                                  'BetType','TotalStake', 'PayableAmount', 'ANNULATION', 
                                  'TICKET_VENDU', 'TICKET_ANNULE', 'CA','MinTotalStake','PaidAmount'])

    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))

    #print(data)
 
    data = [tuple(i) for i in data]
    #insertion de donnees
    cursor.executemany(
         """INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PARI_HONOREGAMING]
            ("Year", "Month","JOUR",  "RetailCategoryName", "AGENCE", "TerminalDescription", "CATEGORIE_FINALE", "GameName", "BetType", "TotalStake", "PayableAmount", "ANNULATION", "TICKET_VENDU", "TICKET_ANNULE", "CA","MinTotalStake","PaidAmount") 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)""",data) 

    conn.commit()
    print("le fichier a ete insere au niveau de la table temporaire")
    
    #namefile = file.split("\\")[-1]
    shutil.move(file,dest+namefile)
    print(dest+namefile)
    
cursor.close()
conn.close()  

# In[ ]:





# In[21]:



d = dir()

#You'll need to check for user-defined variables in the directory
for obj in d:
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


# In[ ]:





# In[ ]:




