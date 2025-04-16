#!/usr/bin/env python
# coding: utf-8

# In[53]:


from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

import cx_Oracle
import shutil
import os


# In[54]:


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
start_date = end_date - delta

#print(start_date)
#start_date = datetime.date(2024, 6, 1)
#end_date = start_date+delta
#end_date = datetime.date(2024, 8, 1)

print(start_date)

debut = start_date
fin = end_date-delta

generalDirectory = r"K:\\DATA_FICHIERS\\"


# In[55]:


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






cur.execute(f"""
delete  from user_dwhpr.fait_lots 
WHERE idjeux in (25,26)
and  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 166)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' ) """)
conn.commit()

cur.execute(f"""
delete 
from user_dwhpr.fait_vente
where idjeux in (25,26)
and idterminal in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 166)
and idtemps in (select idtemps from user_dwhpr.dim_temps where user_dwhpr.dim_temps.jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'  ) """)
conn.commit()

            
cur.close()
conn.close()


# In[56]:


#dest = r"Z:\ALR_HONORE_GAMING\\"
dest = r"\\192.168.1.237\c$\Lonase\File_Production\ALR_HONORE_GAMING\\"

while start_date<end_date:

    directory = generalDirectory+r"HONORE_GAMING\\"

    file = glob.glob(directory+f"**\daily-modified-horse-racing-tickets-detailed_{str((start_date+delta).strftime('%Y%m%d'))}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier HonoreGaming du {start_date} n'a pas ete extrait ")
        start_date+=delta
        continue
    else:
        print(start_date)
        file = file[0]
        dest_file = dest+f"daily-modified-horse-racing-tickets-detailed_{str((start_date+delta).strftime('%Y%m%d'))}.csv"
        print(file)
        if os.path.exists(dest_file):
            os.remove(dest_file)
        
        #dest1 = os.path.join("Z:\ALR_HONORE_GAMING\\",f"daily-modified-horse-racing-tickets-detailed_{str((start_date+delta).strftime('%Y%m%d'))}.csv")
        #dest1 = os.path.join("Z:"+'/ALR_HONORE_GAMING/',f"daily-modified-horse-racing-tickets-detailed_{str((start_date+delta).strftime('%Y%m%d'))}.csv")
        
        #shutil.copy2(file, dest1)
        shutil.copy2(file, dest_file)
        start_date+=delta
                     
        # dest1 = os.path.join(pathDepot+'GITECH/',final_file)
        continue
        
    #break


# In[57]:


#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


# In[ ]:




