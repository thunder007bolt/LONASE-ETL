#!/usr/bin/env python
# coding: utf-8

# In[13]:


from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

import cx_Oracle

# In[14]:


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
start_date = end_date - delta

#print(start_date)
#start_date = datetime.date(2024, 12, 19)
#end_date = start_date+delta
#end_date = datetime.date(2025, 1, 1)


debut = start_date
fin = end_date-delta

generalDirectory = r"K:\\DATA_FICHIERS\\"


# In[15]:


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

cur.execute("""
    truncate table OPTIWARETEMP.src_prd_sunubet_online
    """)
conn.commit()

cur.execute("""
    truncate table OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO
    """)
conn.commit()



while start_date<end_date:
    
    directory = generalDirectory+r"SUNUBET\CASINO\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    file = glob.glob(directory+f"**\\casinoSunubet {str(start_date)}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier sunubet casino du {start_date} n'a pas ete extrait ")
    else:
        file = file[0]

        data = pd.read_csv(file,sep=';',index_col=False)

        data = pd.DataFrame(data,columns=["JOUR","Stake", "PaidAmount"])


        data = data.replace(np.nan, '')
        data=data.astype(str)
        data = list(data.to_records(index=False))

        #print(data)

        cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO("ISSUEDATETIME","STAKE", "PAIDAMOUNT") VALUES(:1, :2, :3)""", data)
        conn.commit()


    directory = generalDirectory+r"SUNUBET\ONLINE\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    file = glob.glob(directory+f"**\\onlineSunubet {str(start_date)}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier sunubet online du {start_date} n'a pas ete extrait ")
    else:
        file = file[0]

        data = pd.read_csv(file,sep=';',index_col=False)

        data = pd.DataFrame(data,columns=["JOUR","Stake", "PaidAmount","BetCategory", "Freebet"])


        data = data.replace(np.nan, '')
        data=data.astype(str)
        data = list(data.to_records(index=False))


        cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_SUNUBET_ONLINE( "ISSUEDATETIME","STAKE", "PAIDAMOUNT","BETCATEGORYTYPE", "FREEBET") VALUES(:1, :2, :3, :4, :5)""", data[:len(data)//2])
        cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_SUNUBET_ONLINE( "ISSUEDATETIME","STAKE", "PAIDAMOUNT","BETCATEGORYTYPE", "FREEBET") VALUES(:1, :2, :3, :4, :5)""", data[len(data)//2:])
        conn.commit()
        
    print(start_date)
        
    #chargeAcajouPick3Grattage()
        
    start_date+=delta
        
#chargeAcajouPick3Grattage()


        
        


# In[16]:


#break


# In[17]:


cur.execute("""
    MERGE INTO user_dwhpr.DTM_MISE_SUNUBET_ONLINE t using
(
    select 
          m.idtemps as IDTEMPS,
          m.anneec as ANNEE,
          m.moisc as MOIS,
                  to_char(trim(substr(w.issuedatetime,1,10))) JOUR,
          sum ( case when upper(w.FREEBET) in ('FALSE') then to_number(regexp_replace(replace(w.stake,'.',','), '[^0-9,]+', '')) 
                       else to_number(0) 
                  end ) as CA,
          /*case when upper(w.BetCategoryType) like upper('%SPORTS%') then 'PARIFOOT'
                       else  'VIRTUEL'
                  end as CATEGORIE,*/
                  upper(w.BetCategoryType) as CATEGORIE,
          sum ( NVL(to_number(regexp_replace(replace(w.PAIDAMOUNT,'.',','), '[^0-9,]+', '')),0) ) as LOT,
          to_number(0) as MONTANT_ANNULE
          
    from optiwaretemp.src_prd_sunubet_online w ,user_dwhpr.dim_temps m
    where  m.jour = to_char( to_date(trim(substr(w.issuedatetime,1,10))),'DD/MM/YYYY')
    /* and to_date(trim(substr(w.JOUR,1,10))) BETWEEN '15/09/2023' AND '31/12/2023' */
    group by IDTEMPS, m.anneec, 
    m.moisc
    , to_char(trim(substr(w.issuedatetime,1,10))), upper(w.BetCategoryType)          
) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour AND T.CATEGORIE = G.CATEGORIE) 
WHEN MATCHED THEN UPDATE SET t.CA=g.CA, T.LOTS = G.LOT, t.MONTANT_ANNULE = 0 
WHEN NOT MATCHED THEN
    INSERT (IDTEMPS,ANNEE,MOIS,JOUR,CA,LOTS,CATEGORIE,MONTANT_ANNULE) 
    VALUES (G.IDTEMPS, G.ANNEE,G.MOIS,G.JOUR,G.CA,G.LOT,G.CATEGORIE,0)
    """)
conn.commit()




cur.execute("""
    MERGE INTO user_dwhpr.DTM_MISE_SUNUBET_ONLINE t using
(
    select 
          m.idtemps as IDTEMPS,
          m.anneec as ANNEE,
          m.moisc as MOIS,
          to_char(trim(substr(w.issuedatetime,1,10))) JOUR,
          sum (  NVL(to_number(regexp_replace(replace(w.stake,'.',','), '[^0-9,]+', '')),0) ) as CA,
                  upper('CASINO') as CATEGORIE,
          sum ( NVL(to_number(regexp_replace(replace(w.PAIDAMOUNT,'.',','), '[^0-9,]+', '')),0) ) as LOT,
          to_number(0) as MONTANT_ANNULE
          
    from optiwaretemp.SRC_PRD_SUNUBET_CASINO w ,user_dwhpr.dim_temps m
    where  m.jour = to_char( to_date(trim(substr(w.issuedatetime,1,10))),'DD/MM/YYYY')
    /* and to_date(trim(substr(w.issuedatetime,1,10))) BETWEEN '15/09/2023' AND '31/12/2023' */
    group by IDTEMPS, m.anneec, 
    m.moisc, to_char(trim(substr(w.issuedatetime,1,10)))          
) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour AND T.CATEGORIE = G.CATEGORIE) 
WHEN MATCHED THEN UPDATE SET t.CA=g.CA, T.LOTS = G.LOT, t.MONTANT_ANNULE = 0 
WHEN NOT MATCHED THEN
    INSERT (IDTEMPS,ANNEE,MOIS,JOUR,CA,LOTS,CATEGORIE,MONTANT_ANNULE) 
    VALUES (G.IDTEMPS, G.ANNEE,G.MOIS,G.JOUR,G.CA,G.LOT,G.CATEGORIE,0) 
    """)
conn.commit()


# In[ ]:


cur.execute("""
    truncate table OPTIWARETEMP.src_prd_sunubet_online
    """)
conn.commit()

cur.execute("""
    truncate table OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO
    """)
conn.commit()


# In[ ]:


cur.close()

conn.close()


# In[ ]:


#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]

