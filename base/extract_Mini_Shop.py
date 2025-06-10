from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

from functools import reduce



delta = datetime.timedelta(days=1)
end_date = datetime.date.today()- delta
start_date = end_date - delta

start_date = datetime.date(2025, 6, 6)
#debut = datetime.date(2022, 7, 1)
#end_date = datetime.date(2025, 4, 5)


#print(start_date)
currentYear = end_date.strftime("%Y")
#currentYear = '2024'
currentDay = end_date.strftime("%d/%m/%y")
#print(currentYear)
#print(currentDay)

#print(datetime.datetime.now())


# In[803]:


import pyodbc
SERVER = '192.168.1.160'
DATABASE = 'db_Lonasse_Def'
USERNAME = 'USER_BI'
PASSWORD = 'L0n@seBI2022'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
conn2 = pyodbc.connect(connectionString)
cursor2 = conn2.cursor()

#print(start_date,end_date)
while start_date < end_date:
    day=start_date.strftime("%d/%m/%Y")
    query_gac = f"""
    select  convert (date, DateSituation) DATE, E.Caption ETABLISSEMENT, J.Caption JEU, T.CodeTerminalVirtuel TERMINAL, V.CodeVendeur VENDEUR, H.MontantAVerser 'MONTANT A VERSER' ,H.MontantARembourser 'MONTANT A PAYER'
    from THPCCHISTORIQUESITUATION H, TETABLISSEMENT E, THPCPTERMINAL_VIRTUEL T, THPCPVENDEUR V, THPCPJEUX J 
    where  H.oidEtablissement = E.oid
    and H.oidTerminal = T.oid and T.oidVendeur = V.oid and H.oidJeu = J.oid 
    and  J.Caption not like 'SOLIDICON'
    and V.CodeVendeur in('VD3692','VD3693','VD3694','VD3695','VD3696')
    and CONVERT(date,DateSituation)= '{day}'
   -- order by DateOp desc
    
    UNION ALL
    
    select  convert (date, DateSituation) DATE, E.Caption ETABLISSEMENT, J.Caption JEU, T.CodeTerminalVirtuel TERMINAL, V.CodeVendeur VENDEUR, H.MontantAVerser 'MONTANT A VERSER' ,H.MontantARembourser 'MONTANT A PAYER'
    from THPCCHISTORIQUESITUATION H, TETABLISSEMENT E, THPCPTERMINAL_VIRTUEL T, THPCPVENDEUR V, THPCPJEUX J 
    where  H.oidEtablissement = E.oid
    and H.oidTerminal = T.oid and T.oidVendeur = V.oid and H.oidJeu = J.oid 
    and  J.Caption  like 'SOLIDICON'
    and CONVERT(date,DateSituation)= '{day}'
    --order by DateOp desc
    
    """

    
    df_gac = pd.read_sql_query(query_gac, conn2)
    if len(df_gac)>0:
    
        df_gac.to_csv(f"K:\DATA_FICHIERS\MINI_SHOP\minishop_{start_date}.csv", sep= ';',index=False)
        print(f"le fichier du {day} a bien ete extrait")
        
    else:
        print(f"le fichier du {day} n'a pas de donnees")
    start_date += delta
#print(df_gac)
#df_gac..to_csv("K:\DATA_FICHIERS\MINI_SHOP_BIS\minishop")

# In[805]:


cursor2.close()
conn2.close() 



#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]