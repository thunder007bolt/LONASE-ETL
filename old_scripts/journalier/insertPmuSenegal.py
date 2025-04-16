#!/usr/bin/env python
# coding: utf-8

# In[150]:


from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

import cx_Oracle


# In[151]:


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
start_date = end_date - delta

#print(start_date)
#start_date = datetime.date(2025, 3, 14)
#end_date = start_date+2*delta
#end_date = datetime.date(2024, 1, 10)


debut = start_date
fin = end_date-delta

generalDirectory = r"K:\\DATA_FICHIERS\\"

print(start_date)
#print(directory+f"**\\daily-modified-horse-racing-tickets-detailed_{str(start_date+delta).replace('-','')}.csv")


# In[152]:


def chargePmuSenegal():
    
    #pass
    import cx_Oracle

    #username = 'OPTIWARETEMP'
    #password = 'optiwaretemp'
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
    
    #suppression de la periode sur le fait vente
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux in (468)
AND  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 173)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime("%d/%m/%Y"))}' and '{str(fin.strftime("%d/%m/%Y"))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE idjeux in (468)
AND  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 173)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime("%d/%m/%Y"))}' and '{str(fin.strftime("%d/%m/%Y"))}' )
""")
    conn.commit()
    
    
    
    cur.execute("""
                
insert into USER_DWHPR.FAIT_VENTE (IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
(
SELECT   
    7181 AS IDVENDEUR,
    to_number(te.idterminal) AS IDTERMINAL,
    to_number(m.idtemps) AS IDTEMPS,
    468 AS IDJEUX, 
    to_number(COALESCE(trim(REPLACE(REPLACE(w.CA, '.', ','), ' ', '')), '0')) AS MONTANT,
    0 AS MONTANT_ANNULE,
    NULL AS TICKET_EMIS,
    NULL AS TICKET_ANNULE,
    m.ANNEEC AS ANNEE,
    m.MOISC AS MOIS,
    REPLACE(m.jour, '/', '') AS JOUR
FROM 
    OPTIWARETEMP.SRC_PRD_PMUSENEGAL_CA w
JOIN 
    USER_DWHPR.DIM_TERMINAL te
    ON upper(trim(w.PRODUIT)) = upper(trim(te.operateur))
JOIN 
    USER_DWHPR.DIM_TEMPS m
    ON m.jour = w.JOUR
WHERE 
    te.idsysteme = 173
) """) # vente
    conn.commit()



    cur.execute("""
INSERT INTO USER_DWHPR.FAIT_LOTS (IDVENDEUR, IDTERMINAL, IDTEMPS, IDJEUX, MONTANT, MONTANT_ANNULE, PAIEMENTS, ANNEE, MOIS, JOUR)
(
    SELECT 
        7181 AS IDVENDEUR,
        TO_NUMBER(te.idterminal) AS IDTERMINAL,
        TO_NUMBER(m.idtemps) AS IDTEMPS,
        468 AS IDJEUX,
        L.CA,
        0 AS MONTANT_ANNULE,
        L.PAIEMENTS,
        m.ANNEEC AS ANNEE,
        m.MOISC AS MOIS,
        REPLACE(m.jour, '/', '') AS JOUR
    FROM 
        (
            SELECT 
                JOUR, 
                produit, 
                CA, 
                PAIEMENTS
            FROM 
                (
                    SELECT 
                        w.JOUR, 
                        w.produit,
                        COALESCE(TO_NUMBER(TRIM(REPLACE(REPLACE(w.CA, '.', ','), ' ', ''))), 0) AS CA,
                        NULL AS PAIEMENTS
                    FROM OPTIWARETEMP.SRC_PRD_PMUSENEGAL_CA w

                    UNION ALL

                    SELECT 
                        l.JOUR, 
                        l.produit,
                        NULL AS CA,
                        COALESCE(TO_NUMBER(TRIM(REPLACE(REPLACE(l.Montant, '.', ','), ' ', ''))), 0) AS PAIEMENTS
                    FROM OPTIWARETEMP.SRC_PRD_PMUSENEGAL_LOTS l
                )
        ) L,
        USER_DWHPR.DIM_TERMINAL te,
        USER_DWHPR.DIM_TEMPS m
    WHERE 
        te.idsysteme = 173 
        AND UPPER(TRIM(L.PRODUIT)) = UPPER(TRIM(te.operateur))
        AND m.jour = L.JOUR
)
""")  # Lot
    conn.commit()

    
    cur.execute(f"""
        MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(COALESCE(F.MONTANT,0)) - SUM(COALESCE(F.MONTANT_ANNULE,0)) as CA_PMU_SENEGAL
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te

WHERE F.IDJEUX=J.IDJEUX 
  AND F.IDTEMPS=Te.IDTEMPS 
  AND F.IDJEUX=468
  AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_PMU_SENEGAL=R1.CA_PMU_SENEGAL

""")
    conn.commit()
    
    cur.execute(f"""
        MERGE INTO user_dwhpr.dtm_ca t
USING (
          SELECT F.ANNEE ANNEE, F.MOIS MOIS, SUM(COALESCE(MONTANT,0))-SUM(COALESCE(MONTANT_ANNULE,0)) CA_MINI_SHOP
          FROM USER_DWHPR.FAIT_VENTE F, USER_DWHPR.DIM_TERMINAL T,USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
WHERE Te.IDTEMPS=F.IDTEMPS
                  AND Te.ANNEEC in ('{str(debut.strftime('%Y'))}','{str(fin.strftime('/%Y'))}')
                  AND F.IDJEUX=J.IDJEUX
                  AND F.IDJEUX = 468
                  AND F.idterminal=T.idterminal
          GROUP BY F.ANNEE , F.MOIS
       ) g

ON (t.annee = g.annee and t.mois=g.mois)
    WHEN MATCHED THEN UPDATE SET t.CA_MINI_SHOP= g.CA_MINI_SHOP
""")
    conn.commit()
    
    
    
    
    cur.execute(f"""
        delete from OPTIWARETEMP.AR_PMUSEGAL_CA 
where jour in (select distinct jour from OPTIWARETEMP.SRC_PRD_PMUSENEGAL_CA)

""")
    conn.commit()
    
    cur.execute(f"""
        delete from OPTIWARETEMP.AR_PMUSEGAL_LOTS 
where jour in (select distinct jour from OPTIWARETEMP.SRC_PRD_PMUSENEGAL_LOTS)

""")
    conn.commit()
    
    cur.execute(f"""
        insert into OPTIWARETEMP.AR_PMUSEGAL_CA 
select *  from OPTIWARETEMP.SRC_PRD_PMUSENEGAL_CA

""")
    conn.commit()
    
    cur.execute(f"""
        insert into OPTIWARETEMP.AR_PMUSEGAL_LOTS 
select * from OPTIWARETEMP.SRC_PRD_PMUSENEGAL_LOTS

""")
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")


    
    cur.execute("""
    truncate table optiwaretemp.SRC_PRD_PMUSENEGAL_CA
    """)
    conn.commit()

    cur.execute("""
        truncate table optiwaretemp.SRC_PRD_PMUSENEGAL_LOTS
        """)
    conn.commit()
    
    
    cur.close()
    conn.close()


    


# In[153]:


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
    truncate table optiwaretemp.SRC_PRD_PMUSENEGAL_CA
    """)
conn.commit()

cur.execute("""
    truncate table optiwaretemp.SRC_PRD_PMUSENEGAL_LOTS
    """)
conn.commit()


# In[154]:


directory = generalDirectory+r"PMUSENEGAL\\"

while start_date<end_date:
    
    #print(f"virtuelAmabel{str(start_date)}.csv")
    #firstDay = datetime.date((end_date -  delta).year, (end_date -  delta).month, 1)
    #firstDay = date((end_date -  delta).year, (end_date -  delta).month, 1)
    
    file = glob.glob(directory+f"**\\Pmu_Senegal_ca_{str(start_date)}.csv",recursive=True)
    
    print( len( file ) )
    
    if len( file ) == 0:
        print(f"Le fichier Pmu_Senegal_ca du {start_date} n'a pas ete extrait ")
    else:
        file = file[0]
        
        data = pd.read_csv(file,sep=';',index_col=False)
        
        data = pd.DataFrame(data,columns=['PRODUIT','CA','SHARING','JOUR','ANNEE','MOIS'])
        
        #print(data.columns)
        
        data = data.replace(np.nan, '')
        #data = data.applymap(lambda x: str(x).replace('.',','))
        data=data.astype(str)
        data = list(data.to_records(index=False))

        
        cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_PMUSENEGAL_CA("PRODUIT", "CA", "SHARING", "JOUR", "ANNEE", "MOIS") VALUES(:1, :2, :3, :4, :5, :6)""", data)
        conn.commit()
    
    file = glob.glob(directory+f"**\\Pmu_Senegal_lots_{str(start_date)}.csv",recursive=True)
    
    print( len( file ) )
    
    if len( file ) == 0:
        print(f"Le fichier Pmu_Senegal_lots du {start_date} n'a pas ete extrait ")
    else:
        file = file[0]
        
        data = pd.read_csv(file, sep=';', index_col=False, encoding='latin1')

        data = pd.DataFrame(data,columns=['Joueur','Nombre de fois gagné','Montant','Type','Combinaison','Offre','produit','JOUR','ANNEE','MOIS'])
    
        #print(data.columns)
        
        data = data.replace(np.nan, '')
        #data = data.applymap(lambda x: str(x).replace('.',','))
        data=data.astype(str)
        data = list(data.to_records(index=False))

        
        cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_PMUSENEGAL_LOTS("JOUEUR", "NOMBRE_DE_FOIS_GAGNE", "MONTANT", "TYPE", "COMBINAISON", "OFFRE", "PRODUIT", "JOUR", "ANNEE", "MOIS") VALUES(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10)""", data)
        conn.commit()
    
        print(start_date)
        
    start_date+=delta
    


    
    


# In[155]:


cur.close()
conn.close()


# In[156]:


#break
chargePmuSenegal()


# In[157]:


#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


# In[159]:





# In[ ]:




