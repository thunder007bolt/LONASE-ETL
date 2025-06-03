from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

import cx_Oracle

#from datetime import  date,datetime,timedelta


#chargeAFITECHDailyPaymentActivity


import pause
from datetime import  date,datetime,timedelta
delta = timedelta(days=1)    


#nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=0, minute=10, second=0, microsecond=0)

#pause.until(nextday)



import shutil
import gc
import pause
import time
#import datetime


import pandas as pd
import numpy as np

import glob
    


# In[2]:

#while not(datetime.now() >= datetime.now().replace(hour=4, minute=24, second=0, microsecond=0) and datetime.now() <= datetime.now().replace(hour=22, minute=59, second=0, microsecond=0)) :
#while False:
    #time.sleep(60)
    

#delta = timedelta(days=1)
#delta = datetime.timedelta(days=1)
#end_date = date(2024,6,30)#datetime.date.today()
#start_date = date(2024,6,17) #end_date - delta

#end_date = datetime.date.today()
end_date = date.today() #- delta

start_date = end_date - delta

#start_date = date(2025,4,12) #end_date - delta


end_date = start_date+delta

print(start_date,end_date)

debut = start_date
fin = end_date #-delta

#generalDirectory = r"X:\\DATA_FICHIERS\\"
generalDirectory = r"K:\\DATA_FICHIERS\\"

# In[3]:

import cx_Oracle
username = 'USER_DWHPR'
password = 'optiware2016'

#dsn = '192.168.1.237/OPTIWARE_TEMP'
dsn = cx_Oracle.makedsn('192.168.1.237', 1521, service_name='DWHPR')
port = 1521
encoding = 'UTF-8'

try:
    cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_6")
    print("successfuly connected")
except:
    print("La base de donnee a deja ete initialisee")

conn = cx_Oracle.connect(username,password,dsn)
cur = conn.cursor() #creates a cursor object


# In[4]:





def chargeBwinner(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data=data.astype(str)
    data = list(data.to_records(index=False))

    
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

        
    #vider la table temporaire optiwaretemp.SRC_PRD_BWINNERS
    
    cur.execute("""truncate table optiwaretemp.SRC_PRD_BWINNERS""")
    #conn.commit()
    
    #print(1)

    
    #remplir la table temporaire optiwaretemp.SRC_PRD_BWINNERS de donnees
    
    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_BWINNERS(CREATE_TIME,PRODUCT,STAKE,"MAX PAYOUT") VALUES(:1,:2,:3,:4)""", data)
    conn.commit()
    
    #print(2)
    
    #return

    
    # mettre a jour le status
    
    cur.execute("""update optiwaretemp.SRC_PRD_BWINNERS set status = 'LOST'""")
    conn.commit()

    #a = 1
    #b = 1+"f"
    
    #suppression de la periode sur le fait vente
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 312
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE idjeux = 312
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #insertion de la periode sur le fait vente
    
    cur.execute("""insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            312 IDJEUX, 
            case when to_number(replace(trim(w.stake),'.',',')) is not null then to_number(replace(trim(w.stake),'.',','))
                else 0 
            end as MONTANT,
            0  MONTANT_ANNULE,
            null TICKET_EMIS,
            null TICKET_ANNULE,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
            
    from optiwaretemp.src_prd_bwinners w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    
    where upper(trim(te.operateur)) = case when upper(trim(w.product))='SN.BWINNERS.NET' then 'BWINNERS ONLINE' else 'BWINNERS PHYSIQUE' end  
        and te.idsysteme=170 
        and m.jour = to_date(w.CREATE_TIME,'DD/MM/YYYY')
)
""")
    conn.commit()

    
    #insertion de la periode sur le fait lots
    
    cur.execute("""insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            312 IDJEUX, 
            case when to_number(replace(trim(w.stake),'.',',')) is not null then to_number(replace(trim(w.stake),'.',','))
                else 0 
            end as MONTANT,
            0  MONTANT_ANNULE,
            case when to_number(replace(trim(w."MAX PAYOUT"),'.',',')) is not null then to_number(replace(trim(w."MAX PAYOUT"),'.',','))
                else 0 
            end as PAIEMENTS,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
            
    from optiwaretemp.src_prd_bwinners w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    
    where upper(trim(te.operateur)) = case when upper(trim(w.product))='SN.BWINNERS.NET' then 'BWINNERS ONLINE' else 'BWINNERS PHYSIQUE' end
        and m.jour = to_date(w.CREATE_TIME,'DD/MM/YYYY')
)
""")
    conn.commit()

    
    #vider la table temporaire optiwaretemp.SRC_PRD_BWINNERS
    
    cur.execute("""truncate table optiwaretemp.SRC_PRD_BWINNERS""")
    conn.commit()
    
    #mise a jour dtm_ca_daily
    
    
    cur.execute(f"""MERGE INTO user_dwhpr.dtm_ca_daily t  
USING ( 
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_BWINNERS_ONLINE
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 312 
            AND F.idterminal=T.idterminal 
            AND upper(trim(T.operateur)) like 'BWINNERS ONLINE'
            AND T.idsysteme  = 170 
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR  
    ) g 
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour) 
WHEN MATCHED THEN UPDATE SET t.CA_BWINNERS_ONLINE=g.CA_BWINNERS_ONLINE 
""")
    
    
    #BWINNERS ONLINE   
    
    
    
    cur.execute(f"""MERGE INTO user_dwhpr.dtm_ca_daily t  
USING ( 
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_BWINNERS_PHYSIQUE
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR  between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 312
            AND F.idterminal=T.idterminal 
            AND upper(trim(T.operateur)) like 'BWINNERS PHYSIQUE'
            AND T.idsysteme  = 170 
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR  
    ) g 
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour) 
WHEN MATCHED THEN UPDATE SET t.CA_BWINNERS_PHYSIQUE=g.CA_BWINNERS_PHYSIQUE      
""")
    
    
    conn.commit()
    
    
    #print('hey')
    
    
    #merge dtm_mise_bwinner
    
    
    cur.execute(f"""MERGE INTO user_dwhpr.DTM_MISE_BWINNER t  
USING ( 
    SELECT F.IDTEMPS TEMPS,Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR,upper(trim(T.operateur)) OPERATEUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA, SUM(NVL(PAIEMENTS,0)) LOT
        FROM user_dwhpr.FAIT_LOTS F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 312 
            AND F.idterminal=T.idterminal 
            /* AND upper(trim(T.operateur)) like 'BWINNERS ONLINE' */
            AND T.idsysteme  = 170 
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR,F.IDTEMPS, upper(trim(T.operateur))  
    ) g 
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour AND T.CATEGORIE = G.OPERATEUR) 
WHEN MATCHED THEN UPDATE SET t.CA=g.CA, T.LOTS = G.LOT, t.MONTANT_ANNULE = 0 
WHEN NOT MATCHED THEN
    INSERT (IDTEMPS,ANNEE,MOIS,JOUR,CA,LOTS,CATEGORIE,MONTANT_ANNULE) 
    VALUES (G.TEMPS, G.ANNEE,G.MOIS,G.JOUR,G.CA,G.LOT,G.OPERATEUR,0)
            



""")
    
    conn.commit()
    
    
    
    
    
    print("La procedure d'insertion s'est bien deroulee")






directory = generalDirectory+r"BWINNERS\\"

file = glob.glob(directory+f"**\Bwinner_{str(start_date)}_{str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Bwinner du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    #print(data.head())
    print("\n BWINNER \n")
    
    chargeBwinner(data,debut,fin)

    #bwinnerManipulation(data,debut,fin)


# In[5]:


def chargeZeturf(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)

    
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

        
    #vider la table temporaire optiwaretemp.src_prd_zeturf
    
    cur.execute("""delete from optiwaretemp.src_prd_zeturf""")
    conn.commit()
    
    #print(11)

    
    #remplir la table temporaire optiwaretemp.src_prd_zeturf de donnees
    
    cur.executemany("""INSERT INTO optiwaretemp.src_prd_zeturf("HIPPODROME","COURSE", "DEPART", "PARIS", "ENJEUX", "ANNULATIONS", "MARGE","DATE_DU_DEPART") VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""", data)
    conn.commit()
    
    #print(22)
    
    #return

    #a = 1
    #b = 1+"f"
    
    #suppression de la periode sur le fait vente
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 311
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE idjeux = 311
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #insertion de la periode sur le fait vente
    
    cur.execute("""insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            311 IDJEUX, 
            case when to_number(trim(replace(replace(w.enjeux,'FCFA'),' '))) is null then 0
                else to_number(trim(replace(replace(w.enjeux,'FCFA'),' ')))
            end as MONTANT,
            case when to_number(trim(replace(replace(w.annulations,'FCFA'),' '))) is null then 0 
                else to_number(trim(replace(replace(w.annulations,'FCFA'),' '))) 
            end as MONTANT_ANNULE,
            null TICKET_EMIS,
            null TICKET_ANNULE,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    
    from optiwaretemp.src_prd_zeturf w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    
    where upper(trim(te.operateur)) like 'ZETURF TERMINAL' and 
        te.idsysteme=169 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATE_DU_DEPART,'DD/MM/RR') 
        
)

""")
    conn.commit()

    
    #insertion de la periode sur le fait lots
    
    cur.execute("""insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            311 IDJEUX, 
            case when to_number(trim(replace(replace(w.enjeux,'FCFA'),' '))) is null then 0
                else to_number(trim(replace(replace(w.enjeux,'FCFA'),' ')))
            end as MONTANT,
            case when to_number(trim(replace(replace(w.annulations,'FCFA'),' '))) is null then 0 
                else to_number(trim(replace(replace(w.annulations,'FCFA'),' '))) 
            end as MONTANT_ANNULE,
            ABS(NVL(to_number(trim(replace(replace(w.enjeux,'FCFA'),' '))),0) - NVL(to_number(trim(replace(replace(w.marge,'FCFA'),' '))),0)) PAIEMENTS,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    
    from optiwaretemp.src_prd_zeturf w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    
    where upper(trim(te.operateur)) like 'ZETURF TERMINAL' and 
        te.idsysteme=169 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATE_DU_DEPART,'DD/MM/RR') 
        
)

""")
    conn.commit()
    
    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca_daily t  
USING ( 
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_ZETURF
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR  between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 311
            AND F.idterminal=T.idterminal 
            AND T.idsysteme  = 169 
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR  
    ) g 
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour) 
WHEN MATCHED THEN UPDATE SET t.CA_ZETURF=g.CA_ZETURF 

""")
    conn.commit()
    

    
    #vider la table temporaire optiwaretemp.src_prd_zeturf
    
    cur.execute("""delete from optiwaretemp.src_prd_zeturf""")
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")








directory = generalDirectory+r"ZETURF\\"

file = glob.glob(directory+f"**\ZEturf {str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier ZEturf du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    #print(data.columns)
    
    #data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du départ'])
    
    data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du dÃ©part'])
    
    print("\n ZEturf \n")
    
    #print(data.columns)

    chargeZeturf(data,debut,fin)


# In[6]:


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


directory = generalDirectory+r"VIRTUEL_EDITEC\FINANCIAL\\"

file = glob.glob(directory+f"**\Financial {str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Financial du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=['Name', 'Total In', 'Total Out','date','Reversal','Currency'])
    
    
    
    cur.execute("""truncate table optiwaretemp.GLOB_FINANCIAL""")
    conn.commit()
    
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    
    cur.executemany("""INSERT INTO optiwaretemp.GLOB_FINANCIAL("Name","Total_In", "Total_Out", "DATE", "Reversal","Currency") VALUES(:1,:2,:3,:4,:5,:6)""", data)
    conn.commit()
    
    
    #print(data)

    #bwinnerManipulation(data,debut,fin)


# In[7]:


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


directory = generalDirectory+r"VIRTUEL_EDITEC\ZONE BETTING\\"

file = glob.glob(directory+f"**\zone betting {str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier zone betting du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=['Shop name', 'date', 'Cancelled','Stake', 'Won'])
    
    
    cur.execute("""truncate table optiwaretemp.GLOB_ZONE_BETTING""")
    conn.commit()
    
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)
    
    cur.executemany("""INSERT INTO optiwaretemp.GLOB_ZONE_BETTING("Shop name","Date", "CANCELLED", "STAKE", "WON") VALUES(:1,:2,:3,:4,:5)""", data)
    conn.commit()



    
    #data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du départ'])
    
    #print(data)

    #bwinnerManipulation(data,debut,fin)


# In[8]:


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


directory = generalDirectory+r"VIRTUEL_EDITEC\PREMIERSN\\"

file = glob.glob(directory+f"**\\{str(start_date)}-Premier SN.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Premier SN du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=['Outlet', 'Reported', 'Sales','Redeems', 'Voided'])

    
    cur.execute("""truncate table optiwaretemp.GLOB_SB_VDR""")
    conn.commit()
    
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    
    cur.executemany("""INSERT INTO optiwaretemp.GLOB_SB_VDR("Outlet","Reported", "Sales", "Redeems", "Voided") VALUES(:1,:2,:3,:4,:5)""", data)
    conn.commit()

    
    #data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du départ'])
    
    #print(data)

    #bwinnerManipulation(data,debut,fin)


# In[9]:


def chargeVirtuelEditec():#data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    #data = data.replace(np.nan, '')
    #data=data.astype(str)
    #data = list(data.to_records(index=False))
    
    #print(data)

    
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
    #print(str(debut.strftime('%d/%m/%Y')))
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 124
and  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 2)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE idjeux = 124
and  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 2)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    

    
    cur.execute("""
    insert into dim_terminal
select distinct '',241,MAGASIN,'',2 from 
(
select "Name" as Magasin,"DATE" as DATE_VENTE,
(case when ("Total_In") like '%,%' 
then  (replace (("Total_In") ,'.')) else ("Total_In") end)  as VENTE,
(case when ("Reversal") like '%,%' 
then  (replace (("Reversal") ,'.')) else ("Reversal") end)  as annulation
from optiwaretemp.GLOB_FINANCIAL where "Currency" like 'XOF' 
UNION ALL
select "Outlet","Reported","Sales","Voided" from  optiwaretemp.GLOB_SB_VDR UNION ALL
select "Shop_name",DATE_VENTE, "Placed_bets_amount","Cancelled_paid_amount"
from  optiwaretemp.GLOB_OVERALL
UNION ALL
SELECT "Shop name" MAGASIN, "Date" DATE_VENTE, STAKE, replace(CANCELLED,'.',',') ANNULATION
FROM OPTIWARETEMP.GLOB_ZONE_BETTING 
) L
where L.MAGASIN NOT IN (select distinct operateur from dim_terminal where idsysteme=2 or idsysteme is null)
            """)
    conn.commit()

    
    cur.execute("""
    
    insert into USER_DWHPR.fait_vente
(select '',7781,t.idterminal idterminal,te.idtemps idtemps,124 idjeux,
to_number(trim(replace(replace(L.VENTE,' '),'.00'))) as vente ,
to_number(trim(replace(replace( L.ANNULATION,' '),'.00'))) as annulation,
0,0,to_char(te.jour,'yyyy') as annee,to_char(te.jour,'mm') as mois, te.jour 
from (
        select "Name" as MAGASIN ,"DATE" as DATE_VENTE,
            (case when ("Total_In") like '%,%' then  to_number(replace (("Total_In") ,'.')) else  to_number(replace(("Total_In"),'.',',')) end)  as VENTE,
            (case when ("Reversal") like '%,%' then  to_number(replace (("Reversal") ,'.')) else  to_number(replace(("Reversal"),'.',',')) end)  as annulation
        from optiwaretemp.GLOB_FINANCIAL where "Currency" like 'XOF'
    UNION ALL
    /*select "Outlet" MAGASIN,"Reported" DATE_VENTE,"Sales" VENTE,"Voided" ANNULATION from  optiwaretemp.GLOB_SB_VDR*/
    select "Outlet" as Magasin
            ,"Reported" as DATE_VENTE
            ,to_number(replace("Sales",'.',',')) as VENTE
            ,to_number(replace("Voided",'.',',')) as annulation
    from  optiwaretemp.GLOB_SB_VDR 
    UNION ALL
    SELECT "Shop name" MAGASIN, "Date" DATE_VENTE, to_number(replace(STAKE,'.',',')) VENTE, to_number(replace(CANCELLED,'.',',')) ANNULATION
    FROM OPTIWARETEMP.GLOB_ZONE_BETTING
) L, dim_terminal t, dim_temps te
where (trim(L.magasin)) = (trim(t.operateur)) and to_date(L.DATE_VENTE,'dd/mm/yy')=to_date(te.jour,'dd/mm/yy') 
        and t.idsysteme=2 and (L.magasin) not like ('%Senegal%' ) and Magasin not like '%test%'
)
    
    """)
    conn.commit()

    
    cur.execute("""
    
    insert into USER_DWHPR.fait_lots
(
    select '' IDLOTS
        ,7781 as idvendeur
        ,t.idterminal
        ,te.idtemps
        ,124 as idjeux
        ,/*to_number(trim(replace(replace(L.VENTE,' '),'.00')))*/ L.VENTE as montant 
        ,/*to_number(trim(replace(replace( L.ANNULATION,' '),'.00')))*/ L.ANNULATION as montant_annule
        ,/*NVL(to_number(replace(paiements,'.',',')),0)- NVL(to_number(trim(replace(replace( L.ANNULATION,' '),'.00'))),0)*/ paiements
        ,to_char(te.jour,'yyyy') as annee
        ,to_char(te.jour,'mm') as mois
        ,to_char(te.jour) as jour
from (  
        select "Name" as MAGASIN ,
            "DATE" as DATE_VENTE,
            (case when ("Total_In") like '%,%' then  to_number(replace (("Total_In") ,'.')) else to_number(replace(("Total_In"),'.',',')) end)  as VENTE,
            (case when ("Reversal") like '%,%' then  to_number(replace (("Reversal") ,'.')) else to_number(replace(("Reversal"),'.',',')) end)  as annulation,
            to_number(replace("Total_Out",'.',',')) as paiements
        from optiwaretemp.GLOB_FINANCIAL where "Currency" like 'XOF'  
        
        UNION ALL
        
        select "Outlet" as Magasin
                ,"Reported" as DATE_VENTE
                ,to_number(replace("Sales",'.',',')) as VENTE
                ,to_number(replace("Voided",'.',',')) as annulation
                ,to_number(replace("Redeems",'.',','))-to_number(replace("Voided",'.',',')) as paiements
        from  optiwaretemp.GLOB_SB_VDR 
        
        UNION ALL
        
        SELECT "Shop name" MAGASIN, 
                "Date" DATE_VENTE, 
                to_number(replace(STAKE,'.',',')) VENTE, 
                to_number(replace(CANCELLED,'.',',')) ANNULATION,  
                to_number(replace(WON,'.',',')) PAIEMENTS
                    
        FROM OPTIWARETEMP.GLOB_ZONE_BETTING
        
            
        ) L, dim_terminal t, dim_temps te
where (trim(L.magasin)) = (trim(t.operateur)) and to_date(L.DATE_VENTE,'dd/mm/yy')=to_date(te.jour,'dd/mm/yy') 
    and t.idsysteme=2 and L.magasin not like ('%Senegal%') and L.magasin not like '%test%'
)

""")
    conn.commit()
    
    
    
    
    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR
        , CASE WHEN Te.IDTEMPS>=7945 THEN (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE))*3/100
            ELSE (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE)) END as CA_VIRTUELS_EDITEC
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE  F.IDJEUX=J.IDJEUX 
AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
    AND F.IDTEMPS=Te.IDTEMPS 
    AND F.IDJEUX=124
group by Te.ANNEEC,Te.MOISC,Te.JOUR,Te.IDTEMPS
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_VIRTUELS_EDITEC=R1.CA_VIRTUELS_EDITEC

""")
    
    
    
    cur.execute(""" truncate table OPTIWARETEMP.GLOB_ZONE_BETTING """)
    conn.commit()
    
    cur.execute(""" truncate table optiwaretemp.GLOB_FINANCIAL """)
    conn.commit()
    
    cur.execute(""" truncate table optiwaretemp.GLOB_SB_VDR """)
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")
    
    
    
chargeVirtuelEditec()


# In[10]:


def chargeVirtuelAmabel(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)
    
    
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

        
    #vider la table temporaire optiwaretemp.SRC_PRD_SUNUBET
    
    cur.execute("""delete from optiwaretemp.SRC_PRD_SUNUBET""")
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.SRC_PRD_SUNUBET de donnees
    
    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_SUNUBET("NOM", "Total enjeu", "Total Ticket Virtuel", "Total Paiement","Date Vente") VALUES(:1,:2,:3,:4,:5)""", data)
    conn.commit()

    #MAJ des terminaux
    
    cur.execute("""INSERT INTO "USER_DWHPR"."DIM_TERMINAL"
SELECT DISTINCT '' IDTERMINAL, 241 IDCCS, NOM AS OPERATEURS, '' STATUT, 141 IDSYSTEME
    FROM OPTIWARETEMP.SRC_PRD_SUNUBET
    WHERE TRIM(NOM) NOT IN (SELECT OPERATEUR FROM DIM_TERMINAL WHERE IDSYSTEME=141)
    ORDER BY SUBSTR(REPLACE(NOM,' ',''),INSTR(REPLACE(NOM,' ',''),'(')+1,7)
    """)
    conn.commit()
    
    # mettre a jour le montant annule
    
    cur.execute("""update optiwaretemp.SRC_PRD_SUNUBET set "Total annulation" = '0' """)
    conn.commit()

    #a = 1
    #b = 1+"f"
    
    #suppression de la periode sur le fait vente
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 261
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE idjeux = 261
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    
    #a = 1
    #b = 1+"f"

    
    #insertion de la periode sur le fait vente
    
    cur.execute("""INSERT INTO "USER_DWHPR"."FAIT_VENTE" 
SELECT   '' as IDVENTE, 
        (SELECT IDVENDEUR FROM "USER_DWHPR"."DIM_VENDEUR") as IDVENDEUR,
        SRC.IDTERMINAL,
        SRC.IDTEMPS,
        J.IDJEUX, 
        SRC.MONTANT,
        SRC.MONTANT_ANNULE,
        SRC.TICKET_EMIS,
        SRC.TICKET_ANNULE,
        TRIM(TO_CHAR(SRC.JOUR,'yyyy')) AS ANNEE,
        TRIM(TO_CHAR(SRC.JOUR,'mm')) AS MOIS,
        TRIM(TO_CHAR(SRC.JOUR,'ddmmyyyy')) AS JOUR 
    FROM (
            SELECT 
                Te.IDTEMPS,
                S."Total enjeu" as MONTANT,
                T.IDTERMINAL,Te.JOUR,
                S."Total annulation" as MONTANT_ANNULE,
                S."Total Ticket Virtuel" as TICKET_EMIS,  
                '' as TICKET_ANNULE,
                'VIRTUEL AMABEL' PRODUIT
            FROM "OPTIWARETEMP"."SRC_PRD_SUNUBET" S,  "USER_DWHPR"."DIM_TEMPS" Te ,USER_DWHPR.DIM_TERMINAL T
            WHERE  T.OPERATEUR=S.NOM
            AND IDSYSTEME= 141
            AND Te.JOUR=TO_DATE(S."Date Vente",'DD/MM/RR')
        ) SRC , "USER_DWHPR"."DIM_JEUX" J
    WHERE J.IDJEUX=261 
    and UPPER(J.LIBELLEJEUX)=UPPER(SRC.PRODUIT) 
    AND UPPER(SRC.PRODUIT)='VIRTUEL AMABEL'
""")
    conn.commit()

    
    #insertion de la periode sur le fait lots
    
    cur.execute("""INSERT INTO FAIT_LOTS
SELECT   '' as IDLOTS, 
        (SELECT IDVENDEUR FROM "USER_DWHPR"."DIM_VENDEUR") as IDVENDEUR,
        SRC.IDTERMINAL,
        SRC.IDTEMPS,
        J.IDJEUX, 
        SRC.MONTANT,
        SRC.MONTANT_ANNULE,
        SRC.PAIEMENTS,
        TRIM(TO_CHAR(SRC.JOUR,'yyyy')) AS ANNEE,
        TRIM(TO_CHAR(SRC.JOUR,'mm')) AS MOIS,
        TRIM(TO_CHAR(SRC.JOUR,'ddmmyyyy')) AS JOUR 
    FROM (
            SELECT 
                Te.IDTEMPS,
                S."Total enjeu" as MONTANT,
                T.IDTERMINAL,Te.JOUR,
                S."Total annulation" as MONTANT_ANNULE,
                S."Total Paiement" as PAIEMENTS,
                'VIRTUEL AMABEL' PRODUIT
            FROM "OPTIWARETEMP"."SRC_PRD_SUNUBET" S,  "USER_DWHPR"."DIM_TEMPS" Te ,USER_DWHPR.DIM_TERMINAL T
            WHERE  T.OPERATEUR=S.NOM
            AND IDSYSTEME= 141
            AND Te.JOUR=TO_DATE(S."Date Vente",'DD/MM/RR')
        ) SRC , "USER_DWHPR"."DIM_JEUX" J
    WHERE J.IDJEUX=261 
    and UPPER(J.LIBELLEJEUX)=UPPER(SRC.PRODUIT) 
    AND UPPER(SRC.PRODUIT)='VIRTUEL AMABEL'

""")
    conn.commit()
    
    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_VIRTUEL_AMABEL
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te

WHERE F.IDJEUX=J.IDJEUX 
    AND F.IDTEMPS=Te.IDTEMPS 
    AND F.IDJEUX=261
    AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_VIRTUEL_AMABEL=R1.CA_VIRTUEL_AMABEL

""")
    conn.commit()
    

    
    #doublon AR_sunubet_PRD
    
    cur.execute("""DELETE
    FROM OPTIWARETEMP.AR_SUNUBET_PRD
    WHERE  "Date Vente" IN (
                                SELECT DISTINCT "Date Vente"
                                FROM OPTIWARETEMP.SRC_PRD_SUNUBET                        
                            )""")
    conn.commit()
    
    #insertion AR_sunubet_PRD
    
    cur.execute("""INSERT INTO OPTIWARETEMP.AR_SUNUBET_PRD
SELECT *
    FROM OPTIWARETEMP.SRC_PRD_SUNUBET""")
    conn.commit()
    
    #vider la table temporaire optiwaretemp.SRC_PRD_SUNUBET
    
    cur.execute("""delete from optiwaretemp.SRC_PRD_SUNUBET""")
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")





directory = generalDirectory+r"VIRTUEL_AMABEL\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\virtuelAmabel{str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier virtuelAmabel du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    #data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du départ'])
    
    #print(data)

    chargeVirtuelAmabel(data,debut,fin)


# In[11]:


def chargeAcajouDigitain(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data=data.astype(str)
    data = list(data.to_records(index=False))

    
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

        
    #vider la table temporaire optiwaretemp.src_prd_acacia
    
    cur.execute("""delete from optiwaretemp.src_prd_acacia where PRODUIT not in ('Pick3','Grattage')""")
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.src_prd_acacia de donnees
    
    cur.executemany("""INSERT INTO optiwaretemp.src_prd_acacia("DATE_HEURE", "REFERENCE_TICKET", "TELEPHONE", "PURCHASE_METHOD", "MONTANT", "LOTS_A_PAYES","STATUS") VALUES(:1,:2,:3,:4,:5,:6,:7)""", data)
    conn.commit()

    
    # mettre a jour le produit
    
    cur.execute("""update optiwaretemp.src_prd_acacia set PRODUIT = 'Pari Sportif' """)
    conn.commit()

    #a = 1
    #b = 1+"f"
    
    #suppression de la periode sur le fait vente
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX = 305
AND IDTERMINAL = 50073
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE IDJEUX = 305
AND IDTERMINAL = 50073
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #insertion de la periode sur le fait vente
    
    cur.execute("""INSERT INTO FAIT_VENTE


SELECT '' IDVENTE, 7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, MISE_TOTAL MONTANT, 0 MONTANT_ANNULE,
        MISE_TICKET TICKET_EMIS, 0 TICKET_ANNULE, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
FROM (

        SELECT DATE_HEURE, PRODUIT, SUM(MISE_TOTAL) MISE_TOTAL, SUM(MISE_TICKET) MISE_TICKET, SUM(LOTS_TOTAL) LOTS_TOTAL   
        FROM ( 
                SELECT DATE_HEURE,TELEPHONE,OPERATEUR,NUMERO_JOUER,REFERENCE_TICKET,PRODUIT,PURCHASE_METHOD,STATUT,
                        CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(MONTANT,'.',','))
                            ELSE 0
                        END AS MISE_TOTAL,
                        NULL MISE_PAYES,
                        CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN 1
                            ELSE 0
                        END AS MISE_TICKET,
                        CASE WHEN UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(LOTS_A_PAYES,'.',','))
                            ELSE 0
                        END AS LOTS_TOTAL,
                        NULL LOTS_PAYES,
                        NULL LOTS_TICKET
                        
                FROM OPTIWARETEMP.SRC_PRD_ACACIA
                
                WHERE PRODUIT IN ('Pari Sportif')
        )
        
        GROUP BY DATE_HEURE, PRODUIT
        
) F, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
WHERE T.OPERATEUR= F.PRODUIT

AND Te.JOUR= REPLACE(TO_CHAR(F.DATE_HEURE),'/','')
    
    AND J.LIBELLEJEUX='ACAJOU'
    
    

""")
    conn.commit()

    
    #insertion de la periode sur le fait lots
    
    cur.execute("""INSERT INTO FAIT_LOTS
SELECT '' IDVENTE, 7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, MISE_TOTAL MONTANT, 0 MONTANT_ANNULE,
        LOTS_PAYES PAIEMENTS, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
    FROM (
            SELECT DATE_HEURE, PRODUIT, SUM(MISE_TOTAL) MISE_TOTAL, SUM(MISE_TICKET) MISE_TICKET, SUM(LOTS_TOTAL) LOTS_PAYES   
            FROM ( 
                    
                    SELECT DATE_HEURE,TELEPHONE,OPERATEUR,NUMERO_JOUER,REFERENCE_TICKET,PRODUIT,PURCHASE_METHOD,STATUT,
                            CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(MONTANT,'.',','))
                                ELSE 0
                            END AS MISE_TOTAL,
                            NULL MISE_PAYES,
                            CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN 1
                                ELSE 0
                            END AS MISE_TICKET,
                            CASE WHEN UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(LOTS_A_PAYES,'.',','))
                                ELSE 0
                            END AS LOTS_TOTAL,
                            NULL LOTS_PAYES,
                            NULL LOTS_TICKET
                            
                    FROM OPTIWARETEMP.SRC_PRD_ACACIA
                    
                    WHERE PRODUIT IN ('Pari Sportif')
                )
        
                GROUP BY DATE_HEURE, PRODUIT      
                
            ) F, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
WHERE T.OPERATEUR= F.PRODUIT
    AND Te.JOUR= REPLACE(TO_CHAR(F.DATE_HEURE),'/','')
    AND J.LIBELLEJEUX='ACAJOU'
""")
    conn.commit()
    
    
    
    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_ACAJOU_PARIFOOT
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE IDTERMINAL=50073 and F.IDJEUX=J.IDJEUX 
    AND F.IDTEMPS=Te.IDTEMPS AND F.IDJEUX=305 
    AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ACAJOU_PARIFOOT=R1.CA_ACAJOU_PARIFOOT

""")
    

    
    #vider la table temporaire optiwaretemp.src_prd_acacia
    
    cur.execute("""delete from optiwaretemp.src_prd_acacia where PRODUIT not in ('Pick3','Grattage')""")
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")





    
directory = generalDirectory+r"ACAJOU\DIGITAIN\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\Listing_Tickets_Sports_betting {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Acajou DIGITAIN du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=['Date Created', 'Ticket ID', 'Msisdn', 'Purchase Method', 'Collection','Gross Payout', 'Status'])

    #print(data)

    chargeAcajouDigitain(data,debut,fin)



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

directory = generalDirectory+r"ACAJOU\PICK3\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\Listing_Tickets_Pick3 {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv",recursive=True)

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Acajou Pick3 du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=['Date Created', 'Msisdn', 'Ticket ID', 'Purchase Method','Collection', 'Status', 'Gross Payout', 'Produit'])

    
    cur.execute("""
delete from OPTIWARETEMP.SRC_PRD_ACACIA
where UPPER(TRIM(PRODUIT)) in (UPPER('Pick3'))
""")
    conn.commit()
    
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)
    
    #Purchase_Method
    cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_ACACIA( "DATE_HEURE","TELEPHONE","REFERENCE_TICKET","PURCHASE_METHOD","MONTANT","STATUS","LOTS_A_PAYES","PRODUIT") VALUES(:1, :2, :3, :4, :5, :6, :7, :8)""", data)
    conn.commit()
    

    
    #data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du départ'])
    
    #print(data)

    #bwinnerManipulation(data,debut,fin)


# In[12]:


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

directory = generalDirectory+r"ACAJOU\GRATTAGE\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\Listing_Tickets_Grattage {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Acajou Grattage du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=['Date Created', 'Msisdn', 'Ticket ID', 'Purchase Method','Collection', 'Status', 'Gross Payout', 'Produit'])
    
    
    cur.execute("""
delete from OPTIWARETEMP.SRC_PRD_ACACIA
where UPPER(TRIM(PRODUIT)) in (UPPER('grattage'))
""")
    conn.commit()

    
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    
    cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_ACACIA( "DATE_HEURE","TELEPHONE","REFERENCE_TICKET","PURCHASE_METHOD","MONTANT","STATUS","LOTS_A_PAYES","PRODUIT") VALUES(:1, :2, :3, :4, :5, :6, :7, :8)""", data)
    conn.commit()
    
    
    #data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du départ'])
    
    #print(data)

    #bwinnerManipulation(data,debut,fin)


# In[13]:


#def chargeAcajouPick3Grattage():#data,debut,fin):
def chargeAcajouPick3Grattage(data,debut,fin):#data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    #data = data.replace(np.nan, '')
    #data=data.astype(str)
    #data = list(data.to_records(index=False))
    
    #print(data)
    
    
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
WHERE IDJEUX = 305
AND IDTERMINAL not in (50073)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE IDJEUX = 305
AND IDTERMINAL not in (50073)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

        
    #vider la table temporaire optiwaretemp.SRC_PRD_SUNUBET
    
    
    cur.execute("""
    
    INSERT INTO USER_DWHPR.FAIT_VENTE(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
SELECT  7181 IDVENDEUR, 
        T.IDTERMINAL, 
        Te.IDTEMPS, 
        J.IDJEUX, 
        MISE_TOTAL MONTANT, 
        0 MONTANT_ANNULE,
        MISE_TICKET TICKET_EMIS, 
        0 TICKET_ANNULE, 
        Te.ANNEEC AS ANNEE,
        Te.MOISC AS MOIS,
        REPLACE(TO_CHAR(Te.JOUR),'/','') AS JOUR 
FROM (
        
        SELECT DATE_HEURE, PRODUIT, SUM(MISE_TOTAL) MISE_TOTAL, SUM(MISE_TICKET) MISE_TICKET, SUM(LOTS_TOTAL) LOTS_TOTAL   
        FROM (		
                SELECT DATE_HEURE,TELEPHONE,OPERATEUR,NUMERO_JOUER,REFERENCE_TICKET,PRODUIT,PURCHASE_METHOD,STATUT,
                        CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(MONTANT,'.',','))
                            ELSE 0
                        END AS MISE_TOTAL,
                        NULL MISE_PAYES,
                        CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN 1
                            ELSE 0
                        END AS MISE_TICKET,
                        CASE WHEN UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(LOTS_A_PAYES,'.',','))
                            ELSE 0
                        END AS LOTS_TOTAL,
                        NULL LOTS_PAYES,
                        NULL LOTS_TICKET
                        
                FROM OPTIWARETEMP.SRC_PRD_ACACIA
                
                WHERE PRODUIT IN ('Grattage','Pick3')
        )
        
        GROUP BY DATE_HEURE, PRODUIT
        
) F, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
WHERE T.OPERATEUR= F.PRODUIT
    AND Te.JOUR= F.DATE_HEURE
    AND J.LIBELLEJEUX='ACAJOU'

    
    """)
    conn.commit()

    '''
    cur.execute("""
    
    INSERT INTO USER_DWHPR.FAIT_LOTS(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
SELECT 7181 IDVENDEUR, 
        T.IDTERMINAL, 
        Te.IDTEMPS, 
        J.IDJEUX, 
        MISE_TOTAL MONTANT, 
        0 MONTANT_ANNULE,
        LOTS_TOTAL PAIEMENTS, 
        Te.ANNEEC AS ANNEE,
        Te.MOISC AS MOIS,
        REPLACE(TO_CHAR(Te.JOUR),'/','') AS JOUR 

    FROM (
            SELECT DATE_HEURE, PRODUIT, SUM(MISE_TOTAL) MISE_TOTAL, SUM(MISE_TICKET) MISE_TICKET, SUM(LOTS_TOTAL) LOTS_TOTAL   
            FROM (	
                    SELECT DATE_HEURE,TELEPHONE,OPERATEUR,NUMERO_JOUER,REFERENCE_TICKET,PRODUIT,PURCHASE_METHOD,STATUT,
                        CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(MONTANT,'.',','))
                            ELSE 0
                        END AS MISE_TOTAL,
                        NULL MISE_PAYES,
                        CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN 1
                            ELSE 0
                        END AS MISE_TICKET,
                        CASE WHEN UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(LOTS_A_PAYES,'.',','))
                            ELSE 0
                        END AS LOTS_TOTAL,
                        NULL LOTS_PAYES,
                        NULL LOTS_TICKET
                        
                FROM OPTIWARETEMP.SRC_PRD_ACACIA
                
                WHERE PRODUIT IN ('Grattage','Pick3')
        )
        
        GROUP BY DATE_HEURE, PRODUIT

) F, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
WHERE T.OPERATEUR= F.PRODUIT
    AND Te.JOUR= F.DATE_HEURE
    AND J.LIBELLEJEUX='ACAJOU' 
    
    
    """)
    '''
    cur.execute("""INSERT INTO FAIT_LOTS
SELECT '' IDVENTE, 7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, MISE_TOTAL MONTANT, 0 MONTANT_ANNULE,
        LOTS_PAYES PAIEMENTS, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
    FROM (
            SELECT DATE_HEURE, PRODUIT, SUM(MISE_TOTAL) MISE_TOTAL, SUM(MISE_TICKET) MISE_TICKET, SUM(LOTS_TOTAL) LOTS_PAYES   
            FROM ( 
                    
                    SELECT DATE_HEURE,TELEPHONE,OPERATEUR,NUMERO_JOUER,REFERENCE_TICKET,PRODUIT,PURCHASE_METHOD,STATUT,
                            CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(MONTANT,'.',','))
                                ELSE 0
                            END AS MISE_TOTAL,
                            NULL MISE_PAYES,
                            CASE WHEN UPPER(TRIM(PURCHASE_METHOD)) NOT LIKE 'PROMO%' AND UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN 1
                                ELSE 0
                            END AS MISE_TICKET,
                            CASE WHEN UPPER(TRIM(STATUS)) NOT IN ('UNRESULTED','REFUNDED') THEN TO_NUMBER(REPLACE(LOTS_A_PAYES,'.',','))
                                ELSE 0
                            END AS LOTS_TOTAL,
                            NULL LOTS_PAYES,
                            NULL LOTS_TICKET
                            
                    FROM OPTIWARETEMP.SRC_PRD_ACACIA
                    
                    WHERE PRODUIT IN ('Grattage','Pick3')
                )
        
                GROUP BY DATE_HEURE, PRODUIT      
                
            ) F, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
WHERE T.OPERATEUR= F.PRODUIT
    AND Te.JOUR= REPLACE(TO_CHAR(F.DATE_HEURE),'/','')
    AND J.LIBELLEJEUX='ACAJOU'
""")
    conn.commit()
    

    
    cur.execute("""
    
        INSERT INTO OPTIWARETEMP.AR_ACACIA_PRD
    SELECT '' ID_ACACIA, DATE_HEURE, TELEPHONE, OPERATEUR,NUMERO_JOUER, REFERENCE_TICKET, MONTANT, STATUT, LOTS_A_PAYES, PRODUIT
        FROM (  SELECT *
                FROM OPTIWARETEMP.SRC_PRD_ACACIA
            ORDER BY DATE_HEURE
            )
    
    
    """)
    conn.commit()

    
    
    cur.execute("""
    
    INSERT INTO OPTIWARETEMP.AR_ACACIA_PRD_2
    SELECT DATE_HEURE "X axis legend", '' "stakes free", '' "prizes free", '' "Nb Players free", '' "Nb Tickets free", TO_CHAR(MISE_TOTAL) STAKES, TO_CHAR(to_number(replace(LOTS_PAYES,'.',','))) PRIZES
            , '' "Nb Tickets pending", 
            TO_CHAR(MISE_TICKET) "Nb Tickets played",
            '' "Nb Tickets losing",
            TO_CHAR(LOTS_TICKET) "Nb Tickets paid", 
            '' "Nb Tickets to_pay", 
            '' "Nb Tickets available",  
            '' "Nb Tickets payment_unknown",
            PRODUIT PRODUITS
        
    FROM OPTIWARETEMP.AR_ACACIA_PRD
    PIVOT(
            SUM(MONTANT) TOTAL, SUM(replace(LOTS_A_PAYES,'.',',')) PAYES, COUNT (*) TICKET FOR STATUT IN ('PLAYED' MISE, 'PAID' LOTS) 
            )  
WHERE SUBSTR(DATE_HEURE,7,2)=TO_CHAR(SYSDATE,'YY')
    AND SUBSTR(DATE_HEURE,4,2)=TO_CHAR(SYSDATE,'MM')
    
    """)
    conn.commit()
    
    
    cur.execute("""
    
    delete FROM OPTIWARETEMP.SRC_PRD_ACACIA WHERE PRODUIT IN ('Grattage','Pick3')
    
    """)
    conn.commit()
    
    
    cur.execute(f"""
    
        MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_ACAJOU_PICK3
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE IDTERMINAL=50074 and F.IDJEUX=J.IDJEUX 
    AND F.IDTEMPS=Te.IDTEMPS AND F.IDJEUX=305 
    AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ACAJOU_PICK3=R1.CA_ACAJOU_PICK3

    
    """)
    conn.commit()

    
    cur.execute(f"""
    
        
MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_ACAJOU_GRATTAGE
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE IDTERMINAL=50075 and F.IDJEUX=J.IDJEUX 
    AND F.IDTEMPS=Te.IDTEMPS AND F.IDJEUX=305 
    AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ACAJOU_GRATTAGE=R1.CA_ACAJOU_GRATTAGE

    
    """)
    conn.commit()

    
    print("La procedure d'insertion s'est bien deroulee")
    
#chargeAcajouPick3Grattage(data,debut,fin)


# In[14]:


# In[15]:


def chargeGitechAlr(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)

    
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
    
    #vider la table temporaire optiwaretemp.src_prd_acacia
    
    cur.execute("""TRUNCATE TABLE OPTIWARETEMP.GITECH """)
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.src_prd_acacia de donnees
    
    cur.executemany("""INSERT INTO OPTIWARETEMP.GITECH( "Agences","Operateurs","date_de_vente","Recette_CFA","Annulation_CFA","Paiements_CFA") VALUES(:1, :2, :3, :4, :5, :6)""", data)
    conn.commit()
    
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX = 25
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 81)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE IDJEUX = 25
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 81)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX = 223
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 123)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE IDJEUX = 223
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 123)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    
    
    
    
    cur.execute(f""" 
    insert into dim_terminal 
select distinct '' idterminal, c.idccs,operateurs,'' statut,81 idsysteme from
( select case when "Agences" like 'KOLDA' then 'ZIGUINCHOR' when
    "Agences" like 'TAMBACOUNDA' then 'TAMBA' when "Agences" like 'MATAM' then 'TAMBA' 
    when "Agences" like 'MBACKE' then 'DIOURBEL' 
    when "Agences" like 'SAINT LOUIS' then 'SAINT-LOUIS'
    when "Agences" like 'RICHARD TOLL' then 'SAINT-LOUIS'
    when "Agences" like 'FATICK' then 'KAOLACK'
    when "Agences" like 'BAMBEY' then 'DIOURBEL'
    when "Agences" like 'KAFFRINE' then 'KAOLACK'
    when "Agences" like 'KEDOUGOU' then 'TAMBA'
    when "Agences" like 'Lonase Head Office' then 'INCONNU'
    else "Agences" end as agences,"Operateurs" as operateurs
    from optiwaretemp.gitech) s ,dim_ccs c
    where UPPER(trim(s.agences))= UPPER(trim(nomccs)) and s.operateurs not in (select distinct operateur from dim_terminal
    where idsysteme=81)
    
""")
    conn.commit()

    
    
    cur.execute(f"""
    insert into fait_vente
select '',7181 as idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" as montant_annule,
0 as ticket_emis,0 as ticket_annule,to_char(te.jour,'yyyy') as annee,
to_char(jour,'mm') as mois,te.jour
from optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
where s."Operateurs"=t.operateur and t.idsysteme=81
and j.libellejeux='ALR' and to_date(s."date_de_vente",'dd/mm/yy')=to_date(te.jour,'dd/mm/yy') 

""")
    conn.commit()

    
    
    cur.execute(f"""
    insert into fait_vente
select '',7181 as idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" as montant_annule,
0 as ticket_emis,0 as ticket_annule,to_char(te.jour,'yyyy') as annee,
to_char(jour,'mm') as mois,te.jour
from optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
where s."Operateurs"=t.operateur and t.idsysteme=123
and j.libellejeux='PMU ONLINE' and to_date(s."date_de_vente",'dd/mm/yy')=to_date(te.jour,'dd/mm/yy') 

""")
    conn.commit()

    
    
    
    cur.execute(f"""
    insert into fait_lots
select '',7181 as idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" as montant_annule,
s."Paiements_CFA" paiements,to_char(te.jour,'yyyy') as annee,
to_char(jour,'mm') as mois,te.jour
from optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
where s."Operateurs"=t.operateur and t.idsysteme=81
and j.libellejeux='ALR' and to_date(s."date_de_vente",'dd/mm/yy')=to_date(te.jour,'dd/mm/yy') 
""")
    conn.commit()

    
    
    cur.execute(f"""
    insert into fait_lots
select '',7181 as idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" as montant_annule,
0 as paiements,to_char(te.jour,'yyyy') as annee,
to_char(jour,'mm') as mois,te.jour
from optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
where s."Operateurs"=t.operateur and t.idsysteme=123
and j.libellejeux='PMU ONLINE' and to_date(s."date_de_vente",'dd/mm/yy')=to_date(te.jour,'dd/mm/yy') 
""")
    conn.commit()

    
    
    cur.execute(f"""
    DELETE
    FROM OPTIWARETEMP.AR_GITECH_PRD
    WHERE  DATE_OP IN (
                            SELECT DISTINCT "date_de_vente"
                            FROM OPTIWARETEMP.GITECH                         
                        )
""")
    conn.commit()

    
    
    cur.execute(f"""
    INSERT INTO OPTIWARETEMP.AR_GITECH_PRD 

SELECT "Agences" AGENCES, "Operateurs" OPERATEURS, "date_de_vente" DATE_OP, "Recette_CFA" RECETTE, "Annulation_CFA" ANNULATION, "Recette_CFA"-"Annulation_CFA" VENTES_RESULTANT, "Paiements_CFA" PAIEMENT
            , "Recette_CFA"-"Annulation_CFA"-"Paiements_CFA" RESULTATS

FROM OPTIWARETEMP.GITECH
    

""")
    conn.commit()

    
    
    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_ALR_GITECH
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE  F.IDJEUX=J.IDJEUX 
    AND F.IDTEMPS=Te.IDTEMPS 
    AND F.IDTERMINAL IN (SELECT IDTERMINAL FROM DIM_TERMINAL WHERE IDSYSTEME=81)
    AND F.IDJEUX=25 
    AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ALR_GITECH=R1.CA_ALR_GITECH


""")
    conn.commit()

    
    
    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_PMU_ONLINE
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE F.IDJEUX=J.IDJEUX AND F.IDTEMPS=Te.IDTEMPS AND F.IDJEUX=223
AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_PMU_ONLINE=R1.CA_PMU_ONLINE


""")
    conn.commit()
    
    cur.execute("""TRUNCATE TABLE OPTIWARETEMP.GITECH """)
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")




    

directory = generalDirectory+r"GITECH\ALR\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\GITECH {str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier ALR GITECH du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=['Agences', 'Operateur', 'Date vente', 'Vente', 'Annulation', 'Paiement'])

    
    #print(data)

    chargeGitechAlr(data,debut,fin)


# In[16]:


def chargeGitechCasino(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)

    
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
    
    #vider la table temporaire optiwaretemp.src_prd_acacia
    
    cur.execute("""TRUNCATE TABLE OPTIWARETEMP.GITECH """)
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.src_prd_casino_gitech de donnees

    
    cur.executemany("""INSERT INTO OPTIWARETEMP.src_prd_casino_gitech( "IDJEU","NOMJEU","DATEVENTE","VENTE","PAIEMENT","POURCENTAGEPAIEMENT") VALUES(:1, :2, :3, :4, :5, :6)""", data)
    conn.commit()
    
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX = 316
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 81)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE IDJEUX = 316
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 81)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    cur.execute(f"""
    
    insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            316 IDJEUX, 
            case when to_number(trim(w.vente)) is null then 0
                else to_number(trim(w.vente))
            end as MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS,
            0 TICKET_ANNULE,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    
    from optiwaretemp.src_prd_casino_gitech w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    
    where upper(trim(te.operateur)) like 'CASINO GITECH' and 
        te.idsysteme=81 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATEVENTE,'DD/MM/RR') 
)


""")
    conn.commit()

    
    
    cur.execute(f"""
    insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            316 IDJEUX, 
            case when to_number(trim(w.vente)) is null then 0
                else to_number(trim(w.vente))
            end as MONTANT,
            0 MONTANT_ANNULE,
            case when to_number(trim(w.PAIEMENT)) is null then 0
                else to_number(trim(w.PAIEMENT))
            end as PAIEMENTS,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    
    from optiwaretemp.src_prd_casino_gitech w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    
    where upper(trim(te.operateur)) like 'CASINO GITECH' and 
        te.idsysteme=81 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATEVENTE,'DD/MM/RR') 
)


""")
    conn.commit()
    
    
    cur.execute(f"""
    delete from optiwaretemp.src_prd_casino_gitech

""")
    conn.commit()

    
    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca_daily t  
USING ( 
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_CASINO_GITECH
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 316
            AND F.idterminal=T.idterminal 
            AND T.idsysteme  = 81 
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR  
    ) g 
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour) 
WHEN MATCHED THEN UPDATE SET t.CA_CASINO_GITECH=g.CA_CASINO_GITECH 


""")
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")

    
    


directory = generalDirectory+r"GITECH\CASINO\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\GITECH CASINO {str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier CASINO GITECH du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    #data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du départ'])
    
    #print(data)

    chargeGitechCasino(data,debut,fin)


# In[18]:


def chargeLonasebetCasino(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)

    
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

        
    #vider la table temporaire optiwaretemp.SRC_PRD_CASINO_LONASEBET
    
    cur.execute("""delete  from optiwaretemp.SRC_PRD_CASINO_LONASEBET""")
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.SRC_PRD_SUNUBET de donnees
    
    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_CASINO_LONASEBET(DATE_VENTE,MISE_TOTALE, SOMME_PAYEE) VALUES(:1,:2,:3)""", data)
    conn.commit()

    
    #a = 1
    #b = 1+"f"
    
    #suppression de la periode sur le fait vente
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 316
AND  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 167)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE idjeux = 316
AND  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 167)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    
    #a = 1
    #b = 1+"f"

    
    #insertion de la periode sur le fait vente
    
    cur.execute("""insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            316 IDJEUX, 
            case when to_number(trim(replace(replace(w.MISE_TOTALE,'XOF'),' '))) is null then 0
                else to_number(trim(replace(replace(w.MISE_TOTALE,'XOF'),' ')))
            end as MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS,
            0 TICKET_ANNULE,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    
    from optiwaretemp.src_prd_casino_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    
    where upper(trim(te.operateur)) like 'CASINO LONASEBET' and 
        te.idsysteme=167 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATE_VENTE,'DD/MM/RR') 
)

""")
    conn.commit()

    
    #insertion de la periode sur le fait lots
    
    cur.execute("""insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            316 IDJEUX, 
            case when to_number(trim(replace(replace(w.MISE_TOTALE,'XOF'),' '))) is null then 0
                else to_number(trim(replace(replace(w.MISE_TOTALE,'XOF'),' ')))
            end as MONTANT,
            0 MONTANT_ANNULE,
            case when to_number(trim(replace(replace(w.SOMME_PAYEE,'XOF'),' '))) is null then 0
                else to_number(trim(replace(replace(w.SOMME_PAYEE,'XOF'),' ')))
            end as PAIEMENTS,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    
    from optiwaretemp.src_prd_casino_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    
    where upper(trim(te.operateur)) like 'CASINO LONASEBET' and 
        te.idsysteme=167 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATE_VENTE,'DD/MM/YYYY') 
)
""")
    conn.commit()
    
    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca_daily t  
USING ( 
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_CASINO_LONASEBET
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 316
            AND F.idterminal=T.idterminal 
            AND T.idsysteme  = 167 
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR  
    ) g 
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour) 
WHEN MATCHED THEN UPDATE SET t.CA_CASINO_LONASEBET=g.CA_CASINO_LONASEBET 

    """)
    conn.commit()


    
    #vider la table temporaire optiwaretemp.SRC_PRD_CASINO_LONASEBET
    cur.execute("""delete from optiwaretemp.SRC_PRD_CASINO_LONASEBET""")
    conn.commit()

    print("La procedure d'insertion s'est bien deroulee")



directory = generalDirectory+r"LONASEBET\CASINO\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\casinoLonasebet {str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier CASINO Lonasebet  du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=["JOUR","Stake","PaidAmount"])

    #print(data)

    chargeLonasebetCasino(data,debut,fin)


# In[ ]:


def chargeHonoregaming(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)

    
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

        
    #vider la table temporaire optiwaretemp.SRC_PRD_ALR_HONORE_GAMING
    
    cur.execute("""delete  from optiwaretemp.SRC_PRD_ALR_HONORE_GAMING""")
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.SRC_PRD_SUNUBET de donnees
    
    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_ALR_HONORE_GAMING ("REPORTDATETIME"
        ,"TICKETNUMBER"
        ,"STATE"
        ,"ISSUEDATETIME"
        ,"TERMINALID"
        ,"TERMINALDESCRIPTION"
        ,"RETAILCATEGORYNAME"
        ,"RETAILCATEGORYDESCRIPTION"
        ,"AGENTID"
        ,"AGENTNAME"
        ,"PAYMENTDATETIME"
        ,"PAYMENTTERMINALID"
        ,"PAYMENTTERMINALDESCRIPTION"
        ,"PAYMENTRETAILCATEGORYNAME"
        ,"PAYMTRETAILCATEGORYDESCRIPTION"
        ,"PAYMENTAGENTID"
        ,"PAYMENTAGENTNAME"
        ,"CANCELDATETIME"
        ,"CANCELTERMINALID"
        ,"CANCELTERMINALDESCRIPTION"
        ,"CANCELRETAILCATEGORYNAME"
        ,"CANCELRTAILCATEGORYDESCRIPTION"
        ,"CANCELAGENTID"
        ,"CANCELAGENTNAME"
        ,"CANCELADMINISTRATORLOGIN"
        ,"MEETINGDATE"
        ,"MEETINGNUMBER"
        ,"RACENUMBER"
        ,"BETCATEGORYNAME"
        ,"BETTYPE"
        ,"SELECTION"
        ,"MULTIVALUE"
        ,"TOTALSTAKE"
        ,"PAYABLEAMOUNT"
        ,"PAIDAMOUNT"
        ,"GAMENAME") VALUES(:1, :2, :3, :4, :5,:6, :7, :8, :9, :10,:11, :12, :13, :14, :15,:16, :17, :18, :19, :20,:21, :22, :23, :24, :25,:26, :27, :28, :29, :30,:31, :32, :33, :34, :35,:36)""", data)
    
    conn.commit()

    
    #a = 1
    #b = 1+"f"
    
    #suppression de la periode sur le fait vente
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux in (25,26)
AND  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 166)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE idjeux in (25,26)
AND  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 166)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    cur.execute(f"""
    INSERT INTO DIM_TERMINAL
SELECT DISTINCT '' IDTERMINAL, C.IDCCS, OPERATEUR, '' STATUT, 166 IDSYSTEME 
    FROM (
                SELECT DISTINCT TERMINALDESCRIPTION OPERATEUR, RETAILCATEGORYNAME,
                        CASE 
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE '%Backe' THEN 'Diourbel'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Grand-Dakar' THEN 'Grand Dakar'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Bambey' THEN 'Diourbel'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Tambacounda' THEN 'Tamba'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Kedougou' THEN 'Tamba'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Grand-Dakar' THEN 'Grand Dakar'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'TAMBACOUNDA' THEN 'Tamba'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Richard Toll' THEN 'Tamba'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Kaffrine' THEN 'Kaolack'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Kolda' THEN 'Ziguinchor'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Dahra' THEN 'Louga'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Matam' THEN 'Tamba'
                            WHEN TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))LIKE 'Tambacounda Paiement' THEN 'Tamba'
                            ELSE 'Inconnu' /*TRIM(REPLACE(RETAILCATEGORYNAME,'PLR',''))*/
                        END NOMCCS  
                FROM OPTIWARETEMP.SRC_PRD_ALR_HONORE_GAMING     
                WHERE TERMINALDESCRIPTION NOT IN (SELECT OPERATEUR FROM DIM_TERMINAL WHERE IDSYSTEME=166)
            ) S, DIM_CCS C
    WHERE C.NOMCCS=S.NOMCCS
    
""")
    conn.commit()

    
    
    cur.execute(f"""
    INSERT INTO FAIT_VENTE
SELECT '' IDVENTE, 7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, MONTANT, MONTANT_ANNULE,
        TICKET_EMIS, TICKET_ANNULE, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
    FROM (
                SELECT TO_DATE(SUBSTR(REPORTDATETIME,1,10))-1 DATEOP, TERMINALDESCRIPTION OPERATEUR, TO_NUMBER(TRIM(REPLACE(REPLACE(TOTALSTAKE,'.',','),' ',''))) MONTANT
                        , CASE WHEN STATE LIKE 'Cancelled' THEN TO_NUMBER(TRIM(REPLACE(REPLACE(TOTALSTAKE,'.',','),' ',''))) ELSE 0 END MONTANT_ANNULE
                        , 1 TICKET_EMIS, CASE WHEN STATE LIKE 'Cancelled' THEN 1 ELSE 0 END TICKET_ANNULE, TO_NUMBER(TRIM(REPLACE(REPLACE(PAIDAMOUNT,'.',','),' ',''))) PAIEMENTS
                        ,
                        CASE WHEN upper(trim(GAMENAME)) in ('ALR','PLR') THEN upper(GAMENAME)
                            WHEN upper(trim(GAMENAME))like '%MCI%' AND (upper(trim(BETTYPE)) like '%SIMPLE%' OR upper(trim(BETTYPE)) like '%COUPLE%' OR upper(trim(BETTYPE)) like '%TRIO%') THEN 'PLR' 
                            WHEN upper(trim(GAMENAME))like '%MCI%' AND (upper(trim(BETTYPE)) like '%MULTI%' OR upper(trim(BETTYPE)) like '%QUINTE%' OR upper(trim(BETTYPE)) like '%QUARTE%' OR upper(trim(BETTYPE)) like '%QUARTE%' OR upper(trim(BETTYPE)) like '%TIERCE%' ) THEN 'ALR'
                            ELSE 'ALR'
                        END GAMENAME
                        
                FROM OPTIWARETEMP.SRC_PRD_ALR_HONORE_GAMING
                WHERE TO_DATE(SUBSTR(MEETINGDATE,1,10))=TO_DATE(SUBSTR(REPORTDATETIME,1,10))-1
                        
            ) F, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
WHERE T.OPERATEUR= F.OPERATEUR
    AND T.IDSYSTEME=166
    AND Te.JOUR= F.DATEOP
    AND J.LIBELLEJEUX=UPPER(GAMENAME)
    AND J.LIBELLEJEUX IN ('ALR','PLR')
    
""")
    conn.commit()


    cur.execute(f"""
    INSERT INTO FAIT_LOTS
SELECT '' IDVENTE, 7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, MONTANT, MONTANT_ANNULE,
        NVL(PAIEMENTS,0) PAIEMENTS, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
    FROM (
                SELECT TO_DATE(SUBSTR(REPORTDATETIME,1,10))-1 DATEOP, TERMINALDESCRIPTION OPERATEUR, TO_NUMBER(TRIM(REPLACE(REPLACE(TOTALSTAKE,'.',','),' ',''))) MONTANT
                        , CASE WHEN STATE LIKE 'Cancelled' THEN TO_NUMBER(TRIM(REPLACE(REPLACE(TOTALSTAKE,'.',','),' ',''))) ELSE 0 END MONTANT_ANNULE
                        , 1 TICKET_EMIS, CASE WHEN STATE LIKE 'Cancelled' THEN 1 ELSE 0 END TICKET_ANNULE, 
                        /*TO_NUMBER(TRIM(REPLACE(REPLACE(PAIDAMOUNT,'.',','),' ',''))) PAIEMENTS,*/
                        CASE WHEN upper(trim(GAMENAME)) like 'MCI' THEN 0 
                            ELSE TO_NUMBER(TRIM(REPLACE(REPLACE(PAIDAMOUNT,'.',','),' ',''))) 
                        END PAIEMENTS,
                        CASE WHEN upper(trim(GAMENAME)) in ('ALR','PLR') THEN upper(GAMENAME)
                            WHEN upper(trim(GAMENAME))like '%MCI%' AND (upper(trim(BETTYPE)) like '%SIMPLE%' OR upper(trim(BETTYPE)) like '%COUPLE%' OR upper(trim(BETTYPE)) like '%TRIO%') THEN 'PLR' 
                            WHEN upper(trim(GAMENAME))like '%MCI%' AND (upper(trim(BETTYPE)) like '%MULTI%' OR upper(trim(BETTYPE)) like '%QUINTE%' OR upper(trim(BETTYPE)) like '%QUARTE%' OR upper(trim(BETTYPE)) like '%QUARTE%' OR upper(trim(BETTYPE)) like '%TIERCE%' ) THEN 'ALR'
                            ELSE 'ALR'
                        END GAMENAME
                        
                FROM OPTIWARETEMP.SRC_PRD_ALR_HONORE_GAMING R
                WHERE TO_DATE(SUBSTR(MEETINGDATE,1,10))=TO_DATE(SUBSTR(REPORTDATETIME,1,10))-1
                        
            ) F, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
WHERE T.OPERATEUR= F.OPERATEUR
    AND T.IDSYSTEME=166
    AND Te.JOUR= F.DATEOP
    AND J.LIBELLEJEUX=UPPER(GAMENAME)
    AND J.LIBELLEJEUX IN ('ALR','PLR')
    
""")
    conn.commit()


    cur.execute(f"""
    INSERT INTO FAIT_LOTS
SELECT '' IDVENTE, 7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, MONTANT, MONTANT_ANNULE,
        NVL(PAIEMENTS,0) PAIEMENTS, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
    FROM (
                SELECT TO_DATE(SUBSTR(DATE_REUN,1,10)) DATE_REUN, 
                        'IPMU TERMINAL' OPERATEUR, 
                        0 MONTANT,
                        0 MONTANT_ANNULE,
                        0 TICKET_EMIS, 
                        0 TICKET_ANNULE, 
                        TO_NUMBER(TRIM(REPLACE(REPLACE(COL_GA,'.',','),' ','')))*655.95 PAIEMENTS,
                        
                        CASE WHEN trim(PARI) IN ('1','2','3','4','5','9','26')  THEN 'PLR' 
                            WHEN trim(PARI) IN ('11','16','13','15')  THEN 'ALR'
                            ELSE 'ALR'
                        END GAMENAME
                        
                FROM OPTIWARETEMP.SRC_PRD_IPMU_DAILY R 
                WHERE TO_CHAR(TO_DATE(SUBSTR(DATE_REUN,1,10)),'YYYY') = TO_CHAR(SYSDATE,'YYYY')
                
        ) F, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
WHERE T.OPERATEUR= F.OPERATEUR
    AND T.IDSYSTEME=166
    AND Te.JOUR= F.DATE_REUN
    AND J.LIBELLEJEUX=UPPER(GAMENAME)
    AND J.LIBELLEJEUX IN ('ALR','PLR')


""")
    conn.commit()


    cur.execute(f"""
    MERGE INTO DTM_MASSE_COMMUNE R1 USING(

    SELECT TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, Te.JOUR JOUR,
            F.OPERATEUR TERMINAL, F.BETTYPE TYPE_PARI, J.LIBELLEJEUX TYPE_JEU,
            SUM(F.MONTANT) MONTANT, SUM(F.MONTANT_ANNULE) MONTANT_ANNULE, SUM(F.PAIEMENTS) PAIEMENTS,
            SUM(F.TICKET_EMIS) TICKET_EMIS, SUM(F.TICKET_ANNULE) TICKET_ANNULE, 'HONORE GAMING' SOURCE
        FROM (
                    SELECT TO_DATE(SUBSTR(REPORTDATETIME,1,10))-1 DATEOP, 
                            TRIM(TERMINALDESCRIPTION) OPERATEUR, 
                            TO_NUMBER(TRIM(REPLACE(REPLACE(TOTALSTAKE,'.',','),' ',''))) MONTANT, 
                            CASE WHEN STATE LIKE 'Cancelled' THEN TO_NUMBER(TRIM(REPLACE(REPLACE(TOTALSTAKE,'.',','),' ',''))) ELSE 0 END MONTANT_ANNULE,
                            TO_NUMBER(TRIM(REPLACE(REPLACE(PAIDAMOUNT,'.',','),' ',''))) PAIEMENTS, 
                            1 TICKET_EMIS, CASE WHEN STATE LIKE 'Cancelled' THEN 1 ELSE 0 END TICKET_ANNULE,
                            upper(trim(BETTYPE)) BETTYPE,
                            CASE WHEN upper(trim(GAMENAME)) in ('ALR','PLR') THEN upper(GAMENAME)
                                WHEN upper(trim(GAMENAME)) like '%MCI%' AND (upper(trim(BETTYPE)) like '%SIMPLE%' OR upper(trim(BETTYPE)) like '%COUPLE%' OR upper(trim(BETTYPE)) like '%TRIO%') THEN 'PLR' 
                                WHEN upper(trim(GAMENAME)) like '%MCI%' AND (upper(trim(BETTYPE)) like '%MULTI%' OR upper(trim(BETTYPE)) like '%QUINTE%' OR upper(trim(BETTYPE)) like '%QUARTE%' OR upper(trim(BETTYPE)) like '%QUARTE%' OR upper(trim(BETTYPE)) like '%TIERCE%' ) THEN 'ALR'
                                ELSE 'ALR'
                            END GAME_NAME
                            
                    FROM OPTIWARETEMP.SRC_PRD_ALR_HONORE_GAMING
                    WHERE upper(trim(GAMENAME)) like '%MCI%' AND TO_DATE(SUBSTR(MEETINGDATE,1,10))=TO_DATE(SUBSTR(REPORTDATETIME,1,10))-1
                            
                ) F, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
                
    WHERE T.OPERATEUR = F.OPERATEUR
        AND T.IDSYSTEME=166
        AND Te.JOUR = F.DATEOP
        AND J.LIBELLEJEUX=UPPER(F.GAME_NAME)
        AND J.LIBELLEJEUX IN ('ALR','PLR')
        
    GROUP BY TO_CHAR(Te.JOUR,'YYYY'), TO_CHAR(Te.JOUR,'MM'), Te.JOUR,F.OPERATEUR,F.BETTYPE, J.LIBELLEJEUX
    
    UNION ALL 
    
    SELECT TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, Te.JOUR JOUR,
            F.OPERATEUR TERMINAL, F.BETTYPE TYPE_PARI, J.LIBELLEJEUX TYPE_JEU,
            SUM(F.MONTANT) MONTANT, SUM(F.MONTANT_ANNULE) MONTANT_ANNULE, SUM(F.PAIEMENTS) PAIEMENTS,
            SUM(F.TICKET_EMIS) TICKET_EMIS, SUM(F.TICKET_ANNULE) TICKET_ANNULE, 'IPMU' SOURCE
        FROM (
                    SELECT DATE_REUN DATEOP, 
                            'IPMU TERMINAL' OPERATEUR, 
                            TO_NUMBER(TRIM(REPLACE(REPLACE(COL_EB,'.',','),' ','')))*655.95 MONTANT, 
                            0  MONTANT_ANNULE,
                            TO_NUMBER(TRIM(REPLACE(REPLACE(COL_GA,'.',','),' ','')))*655.95 PAIEMENTS, 
                            1 TICKET_EMIS, 0 TICKET_ANNULE,
                            CASE WHEN trim(PARI)='1' THEN UPPER('SimpleGagant') 
                                WHEN trim(PARI)='2' THEN UPPER('SimplePlace') 
                                WHEN trim(PARI)='3' THEN UPPER('CoupleGagant') 
                                WHEN trim(PARI)='4' THEN UPPER('CouplePlace') 
                                WHEN trim(PARI)='5' THEN UPPER('CoupleOrdre') 
                                WHEN trim(PARI)='9' THEN UPPER('Trio') 
                                WHEN trim(PARI)='11' THEN UPPER('Tierce') 
                                WHEN trim(PARI)='13' THEN UPPER('QuartePlus') 
                                WHEN trim(PARI)='15' THEN UPPER('QuintePlus') 
                                WHEN trim(PARI)='16' THEN UPPER('Multi') 
                                WHEN trim(PARI)='26' THEN UPPER('TrioOrdre')
                                
                            END BETTYPE,
                            CASE WHEN trim(PARI) IN ('1','2','3','4','5','9','26')  THEN 'PLR' 
                                WHEN trim(PARI) IN ('11','16','13','15')  THEN 'ALR'
                                ELSE 'ALR'
                            END GAME_NAME
                            
                    FROM OPTIWARETEMP.SRC_PRD_IPMU_DAILY
                    WHERE  TO_CHAR(TO_DATE(SUBSTR(DATE_REUN,1,10)),'YYYY') = TO_CHAR(SYSDATE,'YYYY')
                            
                ) F, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
                
    WHERE T.OPERATEUR = F.OPERATEUR
        AND T.IDSYSTEME=166
        AND Te.JOUR = F.DATEOP
        AND J.LIBELLEJEUX=UPPER(F.GAME_NAME)
        AND J.LIBELLEJEUX IN ('ALR','PLR')
        
    GROUP BY TO_CHAR(Te.JOUR,'YYYY'), TO_CHAR(Te.JOUR,'MM'), Te.JOUR,F.OPERATEUR,F.BETTYPE, J.LIBELLEJEUX
    
    
) R2
ON ( R1.ANNEE = R2.ANNEE and R1.MOIS=R2.MOIS AND R1.JOUR=R2.JOUR AND R1.TERMINAL=R2.TERMINAL AND R1.TYPE_PARI=R2.TYPE_PARI AND R1.TYPE_JEU=R2.TYPE_JEU) 
WHEN MATCHED THEN UPDATE SET R1.MONTANT=R2.MONTANT,R1.MONTANT_ANNULE=R2.MONTANT_ANNULE,R1.PAIEMENTS=R2.PAIEMENTS,
                                R1.TICKET_EMIS=R2.TICKET_EMIS,R1.TICKET_ANNULE=R2.TICKET_ANNULE, R1.SOURCE=R2.SOURCE 
WHEN NOT MATCHED THEN INSERT(R1.ANNEE,R1.MOIS,R1.JOUR,R1.TERMINAL,R1.TYPE_PARI,R1.TYPE_JEU,R1.MONTANT,R1.MONTANT_ANNULE,R1.PAIEMENTS,R1.TICKET_EMIS,R1.TICKET_ANNULE,R1.SOURCE)
VALUES(R2.ANNEE,R2.MOIS,R2.JOUR,R2.TERMINAL,R2.TYPE_PARI,R2.TYPE_JEU,R2.MONTANT,R2.MONTANT_ANNULE,R2.PAIEMENTS,R2.TICKET_EMIS,R2.TICKET_ANNULE,R2.SOURCE)


""")
    conn.commit()


    cur.execute(f"""INSERT INTO DTM_MASSE_COMMUNE_IPMU 
SELECT IDTEMPS, ANNEE, MOIS, JOUR, SUM(MCI_SPORTYTOTE) MCI_SPORTYTOTE, SUM(MCI_SIMPLE) MCI_SIMPLE, SUM(MCI_AUTRES_PARIS) MCI_AUTRES_PARIS
FROM
(
        SELECT Te.IDTEMPS, Te.ANNEEC ANNEE, Te.MOISC MOIS, S.JOUR, 
                CASE WHEN UPPER(TRIM("Pari")) NOT LIKE '%SIMPLE%' THEN TO_NUMBER(REPLACE("Somme encaissées",'.')) 
                    ELSE 0 
                END MCI_SPORTYTOTE, 
                CASE WHEN UPPER(TRIM("Pari")) LIKE '%SIMPLE%' THEN TO_NUMBER(REPLACE("Somme encaissées",'.')) 
                    ELSE 0 
                END MCI_SIMPLE, 
                CASE WHEN UPPER(TRIM("Pari")) NOT LIKE '%SIMPLE%' THEN 
                            TO_NUMBER(REPLACE("Déduction Prop sur Enjeux",'.')) + 
                            TO_NUMBER(REPLACE("Arrondis sur Rapports",'.')) + 
                            TO_NUMBER(REPLACE("CAM",'.'))
                    ELSE 0 
                END MCI_AUTRES_PARIS
        FROM OPTIWARETEMP.SRC_PRD_MCI_IPMU_AGREGE S, USER_DWHPR.DIM_TEMPS Te
        WHERE TO_DATE(TRIM(S.JOUR)) = Te.JOUR
        
)    
GROUP BY IDTEMPS,ANNEE,MOIS,JOUR


""")
    conn.commit()


    cur.execute(f"""DELETE FROM OPTIWARETEMP.SRC_PRD_MCI_IPMU_AGREGE
    
""")
    conn.commit()


    cur.execute(f"""
    DELETE
    FROM OPTIWARETEMP.AR_HONORE_GAMING_PRD
    WHERE TO_DATE(SUBSTR(REPORTDATETIME,1,10)) IN (
    
                                                    SELECT DISTINCT TO_DATE(SUBSTR(REPORTDATETIME,1,10))
                                                        FROM OPTIWARETEMP.SRC_PRD_ALR_HONORE_GAMING
    
                                                )
                                                
""")
    conn.commit()


    cur.execute(f"""
    INSERT INTO OPTIWARETEMP.AR_HONORE_GAMING_PRD
    SELECT REPORTDATETIME,TICKETNUMBER,STATE,ISSUEDATETIME,TERMINALID,TERMINALDESCRIPTION,RETAILCATEGORYNAME
        ,RETAILCATEGORYDESCRIPTION,AGENTID,AGENTNAME,PAYMENTDATETIME,PAYMENTTERMINALID,PAYMENTTERMINALDESCRIPTION
        ,PAYMENTRETAILCATEGORYNAME,PAYMTRETAILCATEGORYDESCRIPTION,PAYMENTAGENTID,PAYMENTAGENTNAME,CANCELDATETIME
        ,CANCELTERMINALID,CANCELTERMINALDESCRIPTION,CANCELRETAILCATEGORYNAME,CANCELRTAILCATEGORYDESCRIPTION
        ,CANCELAGENTID,CANCELAGENTNAME,CANCELADMINISTRATORLOGIN,SUBSTR(MEETINGDATE,1,10),MEETINGNUMBER,RACENUMBER,BETCATEGORYNAME
        ,BETTYPE,SELECTION,MULTIVALUE,TOTALSTAKE,PAYABLEAMOUNT,PAIDAMOUNT,GAMENAME
    FROM OPTIWARETEMP.SRC_PRD_ALR_HONORE_GAMING
    
""")
    conn.commit()


    cur.execute(f"""
    DELETE
FROM OPTIWARETEMP.AR_IPMU_PRD
WHERE TO_DATE(SUBSTR(DATE_REUN,1,10)) IN ( SELECT DISTINCT TO_DATE(SUBSTR(DATE_REUN,1,10))
                                    FROM OPTIWARETEMP.SRC_PRD_IPMU_DAILY
                                    )
                                    
""")
    conn.commit()


    cur.execute(f"""
    INSERT INTO OPTIWARETEMP.AR_IPMU_PRD
    SELECT *
    FROM OPTIWARETEMP.SRC_PRD_IPMU_DAILY
    
""")
    conn.commit()

    cur.execute(f"""DELETE FROM OPTIWARETEMP.SRC_PRD_IPMU_DAILY
    
""")
    conn.commit()

    
    cur.execute(f"""
    
    delete from OPTIWARETEMP.SRC_PRD_ALR_HONORE_GAMING
""")
    conn.commit()

    cur.execute(f"""
    
MERGE INTO DTM_CA_DAILY R0 USING 
( 
    select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_PLR_HONORE_GAMING
    FROM FAIT_VENTE F, DIM_JEUX J ,DIM_TERMINAL Ter, DIM_TEMPS Te
    WHERE F.IDJEUX=J.IDJEUX 
        and F.IDTERMINAL=Ter.IDTERMINAL
        and F.IDTEMPS=Te.IDTEMPS and F.IDJEUX=26 and Ter.IDSYSTEME=166
        AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
    group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_PLR_HONORE_GAMING=R1.CA_PLR_HONORE_GAMING


""")
    conn.commit()

    cur.execute(f"""
    
MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_ALR_HONORE_GAMING
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE F.IDJEUX=J.IDJEUX 
    AND F.IDTEMPS=Te.IDTEMPS 
    AND F.IDTERMINAL IN (SELECT IDTERMINAL FROM DIM_TERMINAL WHERE IDSYSTEME=166)
    AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
    AND F.IDJEUX=25 
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ALR_HONORE_GAMING=R1.CA_ALR_HONORE_GAMING


""")
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")



directory = generalDirectory+r"HONORE_GAMING\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\daily-modified-horse-racing-tickets-detailed_{str(end_date).replace('-','')}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier HONORE_GAMING du {start_date} n'a pas ete extrait ")
else:
    pass
    '''
    from dateutil.parser import parse
    
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=['ReportDateTime', 'TicketNumber', 'State', 'IssueDateTime',
        'TerminalId', 'TerminalDescription', 'RetailCategoryName',
        'RetailCategoryDescription', 'AgentId', 'AgentName', 'PaymentDateTime',
        'PaymentTerminalId', 'PaymentTerminalDescription',
        'PaymentRetailCategoryName', 'PaymentRetailCategoryDescription',
        'PaymentAgentId', 'PaymentAgentName', 'CancelDateTime',
        'CancelTerminalId', 'CancelTerminalDescription',
        'CancelRetailCategoryName', 'CancelRetailCategoryDescription',
        'CancelAgentId', 'CancelAgentName', 'CancelAdministratorLogin',
        'MeetingDate', 'MeetingNumber', 'RaceNumber', 'BetCategoryName',
        'BetType', 'Selection', 'MultiValue', 'TotalStake', 'PayableAmount',
        'PaidAmount', 'GameName'])
    
    data['ReportDateTime'] = [parse(str(datee)).strftime("%d/%m/%Y") for datee in data['ReportDateTime']]
    data['MeetingDate'] = [parse(str(datee)).strftime("%d/%m/%Y") for datee in data['MeetingDate']]
    
    #print(file.split("\\")[-1])
    
    #filename = r"Z:\Lonase\File_Production\ALR_HONORE_GAMING\\"+file.split("\\")[-1]
    filename = r"Z:\Lonase\File_Production\ALR_HONORE_GAMING\\"+file.split("\\")[-1]
    
    filename = r"\\192.168.1.237\c$\Lonase\File_Production\ALR_HONORE_GAMING\\"+file.split("\\")[-1]
    
    data.to_csv(filename,sep=';',index=False)

    
    #print(data)

    #chargeHonoregaming(data,debut,fin)
    '''

    


# In[ ]:


def chargeAFITECHCommissionHistory(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    
    #print(data.head())
    #print(data.columns)
    data = data.replace(np.nan, '')
    data = data.applymap(lambda x: str(x).replace('.',','))
    #print(data['Partner'])
    #print(data.columns)
    data['Partner'] = data['Partner'].str.replace(',', '.',regex=False)
    data['Début de la période'] = data['Début de la période'].str.replace('-', '/',regex=False) # Fin de la période
    data['Fin de la période'] = data['Fin de la période'].str.replace('-', '/',regex=False)
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)
    
    


    
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

        
    #vider la table temporaire optiwaretemp.SRC_PRD_AFITECH_COMMISSION
    
    cur.execute("""delete  from optiwaretemp.SRC_PRD_AFITECH_COMMISSION""")
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.SRC_PRD_AFITECH_COMMISSION de donnees
    
    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_AFITECH_COMMISSION("DEBUT_PERIODE"
,"FIN_PERIODE"
,"PARTNER"
,"PAYEMENT_PROVIDER"
,"TOTAL_COMMISSON"
,"DEPOSIT_TOTAL_AMOUNT"
,"DEPOSIT_COUNT"
,"WITHDRAWAL_TOTAL_AMOUNT"
,"WITHDRAWAL_COUNT") VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9)""", data)
    conn.commit()

    
    #a = 1
    #b = 1+"f"
    #return 0
    
    #suppression de la periode sur le DTM_MISE_AFITECH_COMMISSION
    
    cur.execute(f"""delete  from  user_dwhpr.DTM_MISE_AFITECH_COMMISSION
WHERE idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(firstDay.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    
    #insertion de la periode sur le DTM_MISE_AFITECH_COMMISSION
    
    cur.execute("""insert into user_dwhpr.DTM_MISE_AFITECH_COMMISSION(
DEBUT_PERIODE
,FIN_PERIODE
,PARTNER
,PAYEMENT_PROVIDER
,TOTAL_COMMISSON
,DEPOSIT_TOTAL_AMOUNT
,DEPOSIT_COUNT
,WITHDRAWAL_TOTAL_AMOUNT
,WITHDRAWAL_COUNT
,IDTEMPS,MOIS, ANNEE
)
(

SELECT to_char(to_date(trim(substr(DEBUT_PERIODE,1,10)),'YYYY/mm/dd'),'DD/MM/YYYY'),
        to_char(to_date(trim(substr(FIN_PERIODE,1,10)),'YYYY/mm/dd'),'DD/MM/YYYY') as JOUR,
            PARTNER,
            PAYEMENT_PROVIDER,
            NVL(TOTAL_COMMISSON,0),
            NVL(DEPOSIT_TOTAL_AMOUNT,0),
            NVL(DEPOSIT_COUNT,0),
            NVL(WITHDRAWAL_TOTAL_AMOUNT,0),
            NVL(WITHDRAWAL_COUNT,0),Te.idtemps as IDTEMPS,Te.MOISC as MOIS,Te.ANNEEC as ANNEE
        FROM optiwaretemp.SRC_PRD_AFITECH_COMMISSION F, user_dwhpr.DIM_TEMPS Te
    where to_date(trim(substr(f.FIN_PERIODE,1,10)),'YYYY/mm/dd') = to_date(trim(substr(Te.jour,1,10)),'DD/MM/rr')

)


""")
    conn.commit()

    #return
    #vider la table temporaire optiwaretemp.DTM_MISE_AFITECH_COMMISSION
    
    cur.execute("""delete  from optiwaretemp.SRC_PRD_AFITECH_COMMISSION""")
    conn.commit()

    print("La procedure d'insertion s'est bien deroulee")




directory = generalDirectory+r"AFITECH\CommissionHistory\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
#firstDay = datetime.date((end_date -  delta).year, (end_date -  delta).month, 1)
firstDay = date((end_date -  delta).year, (end_date -  delta).month, 1)

file = glob.glob(directory+f"**\\AFITECH_CommissionHistory {str(firstDay)}_{str(start_date)}.csv",recursive=True)

#file = glob.glob(r"C:\Users\CFAC\Documents\jules\Stage\ExtractedFiles\afitech\AFITECH_DailyPaymentActivity 2024-05-27_2024_06_04.csv")

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier AFITECH_CommissionHistory  du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    #data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du départ'])
    
    #print(data)

    chargeAFITECHCommissionHistory(data,debut,fin)


# In[ ]:


def chargeAFITECHDailyPaymentActivity(data,debut,fin):
    
    import cx_Oracle
    
    #print(data)
    
    #global start_date
    data = data.replace(np.nan, '')
    data = data.applymap(lambda x: str(x).replace('.',','))
    data['Partner'] = data['Partner'].str.replace(',', '.',regex=False)
    data['Date'] = data['Date'].str.replace('-', '/',regex=False)
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)

    
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

        
    #vider la table temporaire optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT
    
    cur.execute("""delete  from optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT""")
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT de donnees
    
    #print("return")
    
    #,"T_AMOUNT_OF_PARTNER_DEPOSITS","T_AM_OF_PARTNER_WITHDRAWALS"
    
    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT("JOUR"
,"PARTNER"
,"PAYMENT_PROVIDER"
,"TOTAL_AMOUNT_OF_DEPOSIT"
,"TOTAL_NUMBER_OF_DEPOSIT"
,"TOTAL_AMOUNT_OF_WITHDRAWALS"
,"TOTAL_NUMBER_OF_WITHDRAWALS"
,"TOTAL_COMMISSIONS"
) VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""", data) #,:9,:10
    conn.commit()
    
    #return

    
    #a = 1
    #b = 1+"f"
    
    #suppression de la periode sur le DTM_MISE_AFITECH_DAILYPAYMENT
    
    cur.execute(f"""delete  from  user_dwhpr.DTM_MISE_AFITECH_DAILYPAYMENT
WHERE idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    
    #insertion de la periode sur le DTM_MISE_AFITECH_DAILYPAYMENT
    
    #,T_AMOUNT_OF_PARTNER_DEPOSITS,T_AM_OF_PARTNER_WITHDRAWALS
    
    #,NVL(T_AMOUNT_OF_PARTNER_DEPOSITS,0),NVL(T_AM_OF_PARTNER_WITHDRAWALS,0)
    
    cur.execute("""insert into user_dwhpr.DTM_MISE_AFITECH_DAILYPAYMENT(
JOUR
,PARTNER
,PAYMENT_PROVIDER
,TOTAL_AMOUNT_OF_DEPOSIT
,TOTAL_NUMBER_OF_DEPOSIT
,TOTAL_AMOUNT_OF_WITHDRAWALS
,TOTAL_NUMBER_OF_WITHDRAWALS
,TOTAL_COMMISSIONS
,IDTEMPS,MOIS, ANNEE
)
(

SELECT to_char(to_date(trim(substr(f.jour,1,10)),'YYYY/mm/dd'),'DD/MM/YYYY') JOUR
        ,PARTNER
        ,PAYMENT_PROVIDER
        ,NVL(TOTAL_AMOUNT_OF_DEPOSIT,0)
        ,NVL(TOTAL_NUMBER_OF_DEPOSIT,0)
        ,NVL(TOTAL_AMOUNT_OF_WITHDRAWALS,0)
        ,NVL(TOTAL_NUMBER_OF_WITHDRAWALS,0)
        ,NVL(TOTAL_COMMISSIONS,0)
        ,Te.idtemps as IDTEMPS,Te.MOISC as MOIS,Te.ANNEEC as ANNEE
        FROM optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT F, user_dwhpr.DIM_TEMPS Te
        where to_date(trim(substr(f.jour,1,10)),'YYYY/mm/dd') = to_date(trim(substr(Te.jour,1,10)),'DD/MM/rr')

)


""")
    conn.commit()

    #return
    #vider la table temporaire optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT
    
    cur.execute("""delete  from optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT""")
    conn.commit()

    print("La procedure d'insertion s'est bien deroulee")
    



directory = generalDirectory+r"AFITECH\DailyPaymentActivity\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
#firstDay = datetime.date((end_date -  delta).year, (end_date -  delta).month, 1)
firstDay = date((end_date -  delta).year, (end_date -  delta).month, 1)

file = glob.glob(directory+f"**\\AFITECH_DailyPaymentActivity {str(start_date)}_{str(start_date)}.csv",recursive=True)

#file = glob.glob(r"C:\Users\CFAC\Documents\jules\Stage\ExtractedFiles\afitech\AFITECH_DailyPaymentActivity 2024-05-27_2024_06_04.csv")

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier AFITECH_DailyPaymentActivity du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    #data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du départ'])
    
    #print(data)

    chargeAFITECHDailyPaymentActivity(data,debut,fin)


# In[19]:


# In[ ]:


def chargeLonasebetAlrParifoot(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data[:5])

    
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
    
    #vider la table temporaire optiwaretemp.src_prd_lonasebet
    
    cur.execute("""delete from optiwaretemp.src_prd_lonasebet """)
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.src_prd_lonasebet de donnees

    
    cur.executemany("""INSERT INTO OPTIWARETEMP.src_prd_lonasebet( "ID","ISSUEDATETIME","STAKE","BETCATEGORYTYPE","STATE","PAIDAMOUNT","CUSTOMERLOGIN","FREEBET") VALUES(:1, :2, :3, :4, :5, :6,:7,:8)""", data)
    conn.commit()
    
    #return
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX in (25,27,467)
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 167)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE IDJEUX in (25,27,467)
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 167)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    cur.execute(f"""
    
    insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            case when upper(w.betcategorytype) like '%SPORTS%' then to_number(27)
                when upper(w.betcategorytype) like '%HORSERACING%' then to_number(25)
                when upper(w.betcategorytype) like '%VIRTUAL%' then to_number(467)
            end as IDJEUX, 
            case when upper(trim(w.freebet)) in ('FALSE') then to_number(trim(replace(w.stake,'.',','))) 
            else to_number(0) 
        end as MONTANT,
        to_number(0) as MONTANT_ANNULE,
    null TICKET_EMIS,
            null TICKET_ANNULE,
            to_char(to_date(trim(substr(w.issuedatetime,1,10)),'DD/MM/YYYY'),'YYYY') ANNEE,
            to_char(to_date(trim(substr(w.issuedatetime,1,10)),'DD/MM/YYYY'),'MM')MOIS,
            replace(trim(substr(w.issuedatetime,1,10)),'/','') JOUR
    from optiwaretemp.src_prd_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    where upper(trim(te.operateur)) like upper(trim(w.betcategorytype)) and te.idsysteme=167
        and m.jour = to_char( to_date(trim(substr(w.issuedatetime,1,10))),'DD/MM/YYYY') 
        /*and to_char( to_date(trim(substr(w.issuedatetime,1,10))),'DD/MM/YYYY') like 
        to_char( to_date(trim(substr(sysdate-1,1,10))),'DD/MM/YYYY') */
)
""")
    conn.commit()

    
    
    cur.execute(f"""
    insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
(
    select  
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
        case when upper(w.betcategorytype) like '%SPORTS%' then to_number(27)
                when upper(w.betcategorytype) like '%HORSERACING%' then to_number(25)
                when upper(w.betcategorytype) like '%VIRTUAL%' then to_number(467)
        end as IDJEUX, 
        case when upper(trim(w.freebet)) in ('FALSE') then to_number(trim(replace(w.stake,'.',','))) 
            else to_number(0) 
        end as MONTANT,
        to_number(0) as MONTANT_ANNULE,
    case when w.paidamount is null then to_number(0) else to_number(trim(replace(w.paidamount,'.',','))) end as PAIEMENTS,
        to_char(to_date(trim(substr(w.issuedatetime,1,10)),'DD/MM/YYYY'),'YYYY') ANNEE,
        to_char(to_date(trim(substr(w.issuedatetime,1,10)),'DD/MM/YYYY'),'MM')MOIS,
        replace(trim(substr(w.issuedatetime,1,10)),'/','') JOUR
        
    from optiwaretemp.src_prd_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    where upper(trim(te.operateur)) like upper(trim(w.betcategorytype)) and te.idsysteme=167
        and m.jour = to_char( to_date(trim(substr(w.issuedatetime,1,10))),'DD/MM/YYYY') 
        /*and to_char( to_date(trim(substr(w.issuedatetime,1,10))),'DD/MM/YYYY') like 
        to_char( to_date(trim(substr(sysdate-1,1,10))),'DD/MM/YYYY') */
)
""")
    conn.commit()
    
    
    cur.execute(f"""
    delete from optiwaretemp.src_prd_lonasebet

""")
    conn.commit()
    
    

    
    cur.execute(f"""
    
MERGE INTO user_dwhpr.dtm_ca_daily t  
USING ( 
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(MONTANT)-SUM(MONTANT_ANNULE) CA_ALR_LONASEBET
        FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=25
            AND F.idterminal in (select idterminal from user_dwhpr.dim_terminal where idsysteme  = 167) 
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR  
    ) g 
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour) 
WHEN MATCHED THEN UPDATE SET t.CA_ALR_LONASEBET=g.CA_ALR_LONASEBET 

""")
    conn.commit()
    
    cur.execute(f"""
    
MERGE INTO user_dwhpr.dtm_ca_daily t  
USING ( 
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(MONTANT)-SUM(MONTANT_ANNULE) CA_PARIFOOT_LONASEBET
        FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=27
            AND F.idterminal in (select idterminal from user_dwhpr.dim_terminal where idsysteme  = 167) 
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR  
    ) g 
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour) 
WHEN MATCHED THEN UPDATE SET t.CA_PARIFOOT_LONASEBET=g.CA_PARIFOOT_LONASEBET

""")
    conn.commit()
    
    
    cur.execute(f"""
    
MERGE INTO user_dwhpr.dtm_ca_daily t  
USING ( 
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(MONTANT)-SUM(MONTANT_ANNULE) CA_LONASEBET_VIRTUEL
        FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=467
            AND F.idterminal in (select idterminal from user_dwhpr.dim_terminal where idsysteme  = 167) 
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR  
    ) g 
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour) 
WHEN MATCHED THEN UPDATE SET t.CA_LONASEBET_VIRTUEL=g.CA_LONASEBET_VIRTUEL

""")
    conn.commit()
    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca t
    USING (
              SELECT F.ANNEE ANNEE, F.MOIS MOIS, SUM(COALESCE(MONTANT,0))-SUM(COALESCE(MONTANT_ANNULE,0)) CA_LONASEBET_VIRTUEL
              FROM USER_DWHPR.FAIT_VENTE F, USER_DWHPR.DIM_TERMINAL T,USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
                      AND Te.ANNEEC in ('{str(debut.strftime('%Y'))}','{str(fin.strftime('/%Y'))}')
                      AND F.IDJEUX=J.IDJEUX
                      AND F.IDJEUX = 467
                      AND F.idterminal=T.idterminal
                      AND T.idsysteme  = 167
              GROUP BY F.ANNEE , F.MOIS
           ) g

    ON (t.annee = g.annee and t.mois=g.mois)
        WHEN MATCHED THEN UPDATE SET t.CA_LONASEBET_VIRTUEL= g.CA_LONASEBET_VIRTUEL
    """)
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")

    
    


directory = generalDirectory+r"LONASEBET\ALR_PARIFOOT\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\OnlineLonasebet {str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier ALR LONASEBET du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    #print(data.index[3])
    
    #print(len(data.columns))
    
    #print(data[:3])
    
    data = pd.DataFrame(data,columns=["BetId","JOUR","Stake","BetCategory","State","PaidAmount","CustomerLogin","Freebet"])
    
    #data = pd.DataFrame(data,columns=["ID","JOUR","STAKE","BETCATEGORYTYPE","STATE","PAIDAMOUNT","CUSTOMERLOGIN","FREEBET"])
    
    #data = list(data.to_records(index=False))
    
    #print(data[:3])

    chargeLonasebetAlrParifoot(data,debut,fin)


# In[20]:
    
#Hour11 =  datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=8, minute=10, second=0, microsecond=0)
#pause.until(Hour11)

    

def chargeParifootonline(data,debut,fin):
    
    import cx_Oracle
    
    #global start_date
    data = data.replace(np.nan, '')
    data=data.astype(str)
    data = list(data.to_records(index=False))
    
    #print(data)

    
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

        
    #vider la table temporaire optiwaretemp.SRC_PRD_CASINO_LONASEBET
    
    cur.execute("""delete  from OPTIWARETEMP.SRC_PRD_PREMIERBET""")
    conn.commit()

    
    #remplir la table temporaire optiwaretemp.SRC_PRD_SUNUBET de donnees
    
    cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_PREMIERBET( "ID","Username", "Balance", "Total Players","Total Players Date Range", "SB Bets No.", "SB Stake","SB Closed Stake", "SB Wins No.", "SB Wins", "SB Ref No.", "SB Refunds","SB GGR", "Cas.Bets No.", "Cas.Stake", "Cas.Wins No.", "Cas.Wins","Cas.Ref No.", "Cas.Refunds", "Cas.GGR", "Total GGR", "Adjustments","Deposits", "Financial Deposits", "Financial Withdrawals","Transaction Fee", "Date") VALUES(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27)""", data)
    conn.commit()

    
    #a = 1
    #b = 1+"f"
    
    #suppression de la periode sur le fait vente
    
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 281
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
WHERE idjeux = 281
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    
    
    cur.execute(f"""
    DELETE FROM OPTIWARETEMP.SRC_PRD_PREMIERBET WHERE ID IN ('Total:','Total: ')

""")
    conn.commit()
    
    #return
    
    
    cur.execute(f"""
    INSERT INTO FAIT_VENTE
    SELECT '' AS IDVENTE,
        7181 AS IDVENDEUR,  
        IDTERMINAL,
        Te.IDTEMPS,
        281 AS IDJEUX,
        SUM(VENTES)AS MONTANT,
        SUM(ANNULATIONS) AS MONTANT_ANNULE,
        SUM(NB_TKS_BRUT) TICKET_EMIS,
        SUM(NB_TKS_ANNULE) TICKET_ANNULE,
        TRIM(TO_CHAR(Te.JOUR,'yyyy')) AS ANNEE,
        TRIM(TO_CHAR(Te.JOUR,'mm')) AS MOIS,
        TRIM(TO_CHAR(Te.JOUR,'ddmmyyyy')) AS JOUR 
    FROM
(
        SELECT '52222' TERMINAL,
            "Date",
            TO_NUMBER(REPLACE("SB Stake",'.',',')) VENTES,
            TO_NUMBER(REPLACE("SB Refunds",'.',',')) ANNULATIONS,     
            TO_NUMBER(REPLACE("SB Bets No.",'.',',')) NB_TKS_BRUT,
            TO_NUMBER(REPLACE("SB Ref No.",'.',',')) NB_TKS_ANNULE,
            TO_NUMBER(REPLACE("SB Wins",'.',',')) PAIEMENTS,
            TO_NUMBER(REPLACE("SB Wins No.",'.',',')) NB_TKS_GAGNE,
            TO_NUMBER(REPLACE("SB GGR",'.',',')) GGR         
        FROM OPTIWARETEMP.SRC_PRD_PREMIERBET
        
        UNION ALL
        
        SELECT '52223' TERMINAL,
            "Date",
            TO_NUMBER(REPLACE("Cas.Stake",'.',',')) VENTES,
            TO_NUMBER(REPLACE("Cas.Refunds",'.',',')) ANNULATIONS, 
            TO_NUMBER(REPLACE("Cas.Bets No.",'.',',')) NB_TKS_BRUT,
            TO_NUMBER(REPLACE("Cas.Ref No.",'.',',')) NB_TKS_ANNULE,
            TO_NUMBER(REPLACE("Cas.Wins",'.',',')) PAIEMENTS, 
            TO_NUMBER(REPLACE("Cas.Wins No.",'.',',')) NB_TKS_GAGNE,
            TO_NUMBER(REPLACE("Cas.GGR",'.',',')) GGR           
        FROM OPTIWARETEMP.SRC_PRD_PREMIERBET

) F, DIM_TEMPS Te, DIM_TERMINAL T
    WHERE Te.JOUR= F."Date"
    AND T.IDTERMINAL=F.TERMINAL
GROUP BY Te.IDTEMPS, IDTERMINAL,
            TRIM(TO_CHAR(Te.JOUR,'yyyy')),
            TRIM(TO_CHAR(Te.JOUR,'mm')),
            TRIM(TO_CHAR(Te.JOUR,'ddmmyyyy'))
            
""")
    conn.commit()
    
    
    cur.execute(f"""
    INSERT INTO FAIT_LOTS
    SELECT '' AS IDLOTS,
        7181 AS IDVENDEUR,  
        IDTERMINAL,
        Te.IDTEMPS,
        281 AS IDJEUX,
        SUM(VENTES)AS MONTANT,
        SUM(ANNULATIONS) AS MONTANT_ANNULE,
        SUM(PAIEMENTS) PAIEMENTS,
        TRIM(TO_CHAR(Te.JOUR,'yyyy')) AS ANNEE,
        TRIM(TO_CHAR(Te.JOUR,'mm')) AS MOIS,
        TRIM(TO_CHAR(Te.JOUR,'ddmmyyyy')) AS JOUR 
    FROM
(
        SELECT '52222' TERMINAL,
            "Date",
            TO_NUMBER(REPLACE("SB Stake",'.',',')) VENTES,
            TO_NUMBER(REPLACE("SB Refunds",'.',',')) ANNULATIONS,     
            TO_NUMBER(REPLACE("SB Bets No.",'.',',')) NB_TKS_BRUT,
            TO_NUMBER(REPLACE("SB Ref No.",'.',',')) NB_TKS_ANNULE,
            TO_NUMBER(REPLACE("SB Wins",'.',',')) PAIEMENTS,
            TO_NUMBER(REPLACE("SB Wins No.",'.',',')) NB_TKS_GAGNE,
            TO_NUMBER(REPLACE("SB GGR",'.',',')) GGR         
        FROM OPTIWARETEMP.SRC_PRD_PREMIERBET
        
        UNION ALL
        
        SELECT '52223' TERMINAL,
            "Date",
            TO_NUMBER(REPLACE("Cas.Stake",'.',',')) VENTES,
            TO_NUMBER(REPLACE("Cas.Refunds",'.',',')) ANNULATIONS, 
            TO_NUMBER(REPLACE("Cas.Bets No.",'.',',')) NB_TKS_BRUT,
            TO_NUMBER(REPLACE("Cas.Ref No.",'.',',')) NB_TKS_ANNULE,
            TO_NUMBER(REPLACE("Cas.Wins",'.',',')) PAIEMENTS, 
            TO_NUMBER(REPLACE("Cas.Wins No.",'.',',')) NB_TKS_GAGNE,
            TO_NUMBER(REPLACE("Cas.GGR",'.',',')) GGR           
        FROM OPTIWARETEMP.SRC_PRD_PREMIERBET

) F, DIM_TEMPS Te, DIM_TERMINAL T
    WHERE Te.JOUR= F."Date"
    AND T.IDTERMINAL=F.TERMINAL
GROUP BY Te.IDTEMPS, IDTERMINAL,
            TRIM(TO_CHAR(Te.JOUR,'yyyy')),
            TRIM(TO_CHAR(Te.JOUR,'mm')),
            TRIM(TO_CHAR(Te.JOUR,'ddmmyyyy'))
            
""")
    conn.commit()
    
    
    cur.execute(f"""
    INSERT INTO FACT_PARIFOOT_ONLINE
    SELECT "ID" SB_USER_ID,
        "Username" TELEPHONE,
        SUM("SB Stake")+SUM("Cas Stake") AS MONTANT,
        SUM("SB Refunds")+SUM("Cas Refunds") AS MONTANT_ANNULE,
        SUM("SB Bets No")+SUM("Cas Bets No") TICKET_EMIS,
        SUM("SB Ref No")+SUM("Cas Ref No") TICKET_ANNULE, 
        SUM("SB Wins")+SUM("Cas Wins") AS LOTS_PAYÉS,
        SUM("SB Wins No.")+SUM("Cas.Wins No.") AS TICKET_PAYÉS,  
        SUM("Cas.GGR") AS SB_BENEFICE, 
        SUM("Cas.GGR") AS CAS_BENEFICE, 
        SUM("Total GGR") AS BENEFICE,
        SUM("Balance") AS SOLDE_CLIENT,
        SUM("Deposits") AS DEPOTS,
        SUM("Financial Withdrawals") AS RETRAIT_CLIENT,
        TRIM(TO_CHAR(Te.JOUR,'yyyy')) AS ANNEE,
        TRIM(TO_CHAR(Te.JOUR,'mm')) AS MOIS,
        TRIM(TO_CHAR(Te.JOUR,'dd/mm/yyyy')) AS JOUR 
    FROM
(
    SELECT "ID" ,
        "Username",
        "Date",
        TO_NUMBER(REPLACE("Balance",'.',',')) "Balance",
        TO_NUMBER(REPLACE("SB Stake",'.',',')) "SB Stake",
        TO_NUMBER(REPLACE("Cas.Stake",'.',',')) "Cas Stake",
        TO_NUMBER(REPLACE("SB Refunds",'.',',')) "SB Refunds",
        TO_NUMBER(REPLACE("Cas.Refunds",'.',',')) "Cas Refunds",      
        TO_NUMBER(REPLACE("SB Bets No.",'.',',')) "SB Bets No",
        TO_NUMBER(REPLACE("Cas.Bets No.",'.',',')) "Cas Bets No",
        TO_NUMBER(REPLACE("SB Ref No.",'.',',')) "SB Ref No",
        TO_NUMBER(REPLACE("Cas.Ref No.",'.',',')) "Cas Ref No",
        TO_NUMBER(REPLACE("SB Wins",'.',',')) "SB Wins",
        TO_NUMBER(REPLACE("Cas.Wins",'.',',')) "Cas Wins", 
        TO_NUMBER(REPLACE("SB Wins No.",'.',',')) "SB Wins No.",
        TO_NUMBER(REPLACE("Cas.Wins No.",'.',',')) "Cas.Wins No.",
        TO_NUMBER(REPLACE("SB GGR",'.',',')) "SB GGR",
        TO_NUMBER(REPLACE("Cas.GGR",'.',',')) "Cas.GGR",
        TO_NUMBER(REPLACE("Total GGR",'.',',')) "Total GGR",  
        TO_NUMBER(REPLACE("Deposits",'.',',')) "Deposits",
        TO_NUMBER(REPLACE("Financial Withdrawals",'.',',')) "Financial Withdrawals"
        
    FROM OPTIWARETEMP.SRC_PRD_PREMIERBET 
) F, DIM_TEMPS Te
    WHERE Te.JOUR= F."Date"
GROUP BY "ID" ,
        "Username",
            TRIM(TO_CHAR(Te.JOUR,'yyyy')),
            TRIM(TO_CHAR(Te.JOUR,'mm')),
            TRIM(TO_CHAR(Te.JOUR,'dd/mm/yyyy'))
            
""")
    conn.commit()
    
    cur.execute(f"""
    INSERT INTO OPTIWARETEMP.FACT_VOUCHER
    SELECT SB_USER_ID,
        TELEPHONE,
        SOLDE_CLIENT,
        TICKET_EMIS NOMBRE_PARIS,
        MONTANT MISE,
        "TICKET_PAYÉS" NOMBRE_PARIS_GAGNES,
        LOTS_PAYÉS MONTANT_GAGNES,
        MONTANT_ANNULE,
        BENEFICE,
        DEPOTS,
        MOIS,
        RETRAIT_CLIENT,
        JOUR,
        ANNEE
    FROM USER_DWHPR.FACT_PARIFOOT_ONLINE
    WHERE JOUR NOT IN (
                        SELECT DISTINCT JOUR
                            FROM OPTIWARETEMP.FACT_VOUCHER
                    )
                    
""")
    conn.commit()
    
    cur.execute(f"""
    DELETE
    FROM OPTIWARETEMP.AR_PREMIERBET
    WHERE  "Date" IN (
                                SELECT DISTINCT "Date"
                                FROM OPTIWARETEMP.SRC_PRD_PREMIERBET                        
                            )
                            
""")
    conn.commit()
    
    
    cur.execute(f"""
    INSERT INTO OPTIWARETEMP.AR_PREMIERBET
SELECT *
    FROM OPTIWARETEMP.SRC_PRD_PREMIERBET
""")
    conn.commit()
    
    
    cur.execute(f"""
    truncate table OPTIWARETEMP.SRC_PRD_PREMIERBET  
    
""")
    conn.commit()
    
    
    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING 
( 
    SELECT ANNEEC, MOISC, JOUR, SUM(CA_PARIFOOT_ONLINE) CA_PARIFOOT_ONLINE
        FROM (
                select Te.ANNEEC,Te.MOISC,Te.JOUR
                        , CASE 
                                WHEN Te.IDTEMPS>=7945 AND T.OPERATEUR LIKE 'SPORT BETTING ONLINE' THEN (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE))*4/100
                                WHEN Te.IDTEMPS>=7945 AND T.OPERATEUR LIKE 'CASINO ONLINE' THEN (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE))*1.5/100
                            ELSE SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) END as CA_PARIFOOT_ONLINE
                    FROM FAIT_VENTE F, DIM_TERMINAL T, DIM_JEUX J , DIM_TEMPS Te
                    WHERE T.IDTERMINAL=F.IDTERMINAL
                    AND F.IDJEUX=J.IDJEUX 
                    AND F.IDTEMPS=Te.IDTEMPS 
                    AND F.IDJEUX IN (27,281) 
                    and F.IDTERMINAL IN (46864,52222,52223)
                    AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
                group by Te.ANNEEC,Te.MOISC,Te.JOUR,T.OPERATEUR,Te.IDTEMPS
            )
GROUP BY ANNEEC, MOISC, JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0. CA_PARIFOOT_ONLINE=R1. CA_PARIFOOT_ONLINE

""")
    conn.commit()
    
    
    print("La procedure d'insertion s'est bien deroulee")

    
    
    



directory = generalDirectory+r"PARIFOOT_ONLINE\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
#firstDay = datetime.date((end_date -  delta).year, (end_date -  delta).month, 1)
firstDay = date((end_date -  delta).year, (end_date -  delta).month, 1)

file = glob.glob(directory+f"**\\ParifootOnline {str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Parifoot Online du {start_date} n'a pas ete extrait ")
else:
    file = file[0]
    
    data = pd.read_csv(file,sep=';',index_col=False)
    
    data = pd.DataFrame(data,columns=['Unnamed: 0','Username', 'Balance', 'Total Players','Total Players Date Range', 'SB Bets No.', 'SB Stake','SB Closed Stake', 'SB Wins No.', 'SB Wins', 'SB Ref No.', 'SB Refunds','SB GGR', 'Cas.Bets No.', 'Cas.Stake', 'Cas.Wins No.', 'Cas.Wins','Cas.Ref No.', 'Cas.Refunds', 'Cas.GGR', 'Total GGR', 'Adjustments','Deposits', 'Financial Deposits', 'Financial Withdrawals','Transaction Fee', 'date'])
    
    #print(data)

    #chargeParifootonline(data,debut,fin)





    
    




cur.execute("""
truncate table OPTIWARETEMP.src_prd_sunubet_online
""")
conn.commit()

cur.execute("""
    truncate table OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO
    """)
conn.commit()

    
        
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

    





cur.execute("""
truncate table OPTIWARETEMP.src_prd_sunubet_online
""")
conn.commit()

cur.execute("""
    truncate table OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO
    """)
conn.commit()

print("################# DEBUT INSERT USSD ############")


def ChargeUSSD(debut, fin):


    # terminaux
    cur.execute(f"""
    INSERT INTO USER_DWHPR.DIM_TERMINAL(IDCCS,OPERATEUR,STATUT,IDSYSTEME)
    SELECT  389 IDCCS, OPERATEUR, '' STATUT, 175 IDSYSTEME 
        FROM (
                   SELECT DISTINCT NumeroServeur OPERATEUR

                    FROM OPTIWARETEMP.TEMP_USSD_IVR     
                   WHERE NumeroServeur NOT IN (SELECT OPERATEUR FROM USER_DWHPR.DIM_TERMINAL WHERE IDSYSTEME=175)
             ) S, USER_DWHPR.DIM_CCS

    GROUP BY OPERATEUR
    """)
    conn.commit()
    # suppression de la periode sur le fait vente

    cur.execute(f""" delete from user_dwhpr.fait_vente
    WHERE IDJEUX = 471
    AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 175)
    AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
    """)
    conn.commit()

    cur.execute(f"""delete from user_dwhpr.fait_lots
    WHERE IDJEUX = 471
    AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 175)
    AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
    """)
    conn.commit()

    cur.execute(f"""  
    INSERT INTO USER_DWHPR.FAIT_VENTE(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)            
    SELECT  7181 IDVENDEUR, 
        T.IDTERMINAL, 
		Te.IDTEMPS, 
	    471 IDJEUX, 
		MONTANT, 
		0 MONTANT_ANNULE,
       '' TICKET_EMIS, 
		'' TICKET_ANNULE, 
		TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
         TO_CHAR(Te.JOUR,'MM') MOIS,
         Te.JOUR   
        FROM (
	         select NumeroServeur as Operateur , TO_DATE(JOUR,'dd/mm/yyyy') JOUR, TO_NUMBER(trim(REPLACE(REPLACE(TOTALCA,'.',','),' ',''))) Montant
		    FROM OPTIWARETEMP.TEMP_USSD_IVR       

         ) F, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te
    WHERE T.OPERATEUR = F.OPERATEUR 
    AND T.IDSYSTEME=175
    AND TO_DATE(Te.JOUR,'dd/mm/yy')=TO_DATE(F.JOUR,'dd/mm/yy') 

    """)
    conn.commit()

    cur.execute(f"""
    INSERT INTO USER_DWHPR.FAIT_LOTS(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
    SELECT  7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS,
        471 IDJEUX, MONTANT, 0 MONTANT_ANNULE,
        0  PAIEMENTS, 
		TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
         TO_CHAR(Te.JOUR,'MM') MOIS,
         Te.JOUR 
    FROM (   
	     select NumeroServeur as Operateur , TO_DATE(JOUR,'dd/mm/yyyy') JOUR, TO_NUMBER(trim(REPLACE(REPLACE(TOTALCA,'.',','),' ',''))) Montant
		 FROM OPTIWARETEMP.TEMP_USSD_IVR      

         ) F, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te
    WHERE  upper(trim(T.OPERATEUR ))= upper(trim(F.OPERATEUR))
    AND T.IDSYSTEME=175                     
    AND TO_DATE(Te.JOUR,'dd/mm/yy')=TO_DATE(F.JOUR,'dd/mm/yy')


    """)
    conn.commit()

    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca_daily t  
    USING (
       SELECT Te.ANNEEC AS ANNEE,
              Te.MOISC AS MOIS,
              Te.JOUR,
              SUM(NVL(F.MONTANT, 0)) - SUM(NVL(F.MONTANT_ANNULE, 0)) AS CA_USSD
         FROM user_dwhpr.FAIT_VENTE F
         JOIN user_dwhpr.DIM_TERMINAL T ON F.idterminal = T.idterminal
         JOIN user_dwhpr.DIM_TEMPS Te ON Te.IDTEMPS = F.IDTEMPS
         JOIN user_dwhpr.DIM_JEUX J ON F.IDJEUX = J.IDJEUX
         WHERE Te.ANNEEC = TO_CHAR(SYSDATE, 'YYYY')
          AND F.IDJEUX = 471
          AND T.IDSYSTEME = 175
        GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
    ON (t.annee = g.annee AND t.mois = g.mois AND t.jour = g.jour)
    WHEN MATCHED THEN UPDATE SET t.CA_USSD = g.CA_USSD

    """)
    conn.commit()

    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca t 
    USING (
       SELECT F.ANNEE AS ANNEE,
              F.MOIS AS MOIS,
              SUM(NVL(F.MONTANT, 0)) - SUM(NVL(F.MONTANT_ANNULE, 0)) AS CA_USSD
         FROM user_dwhpr.FAIT_VENTE F
         JOIN user_dwhpr.DIM_TERMINAL T ON F.idterminal = T.idterminal
         JOIN user_dwhpr.DIM_TEMPS Te ON Te.IDTEMPS = F.IDTEMPS
         JOIN user_dwhpr.DIM_JEUX J ON F.IDJEUX = J.IDJEUX
        WHERE Te.ANNEEC = TO_CHAR(SYSDATE, 'YYYY')
          AND F.IDJEUX = 471
          AND T.IDSYSTEME = 175
        GROUP BY F.ANNEE, F.MOIS
     ) g
     ON (t.annee = g.annee AND t.mois = g.mois)
     WHEN MATCHED THEN UPDATE SET t.CA_USSD = g.CA_USSD

    """)
    conn.commit()

    cur.execute(f"""
        delete from OPTIWARETEMP.AR_USSD_IVR
      where jour in (select distinct jour from OPTIWARETEMP.TEMP_USSD_IVR)
    """)
    conn.commit()

    cur.execute(f"""
        insert into OPTIWARETEMP.AR_USSD_IVR
        select *  from OPTIWARETEMP.TEMP_USSD_IVR
    """)
    conn.commit()

    print("La procedure d'insertion s'est bien deroulee")

    cur.execute("""
        truncate table optiwaretemp.TEMP_USSD_IVR
    """)
    conn.commit()

    cur.close()
    conn.close()


directory = generalDirectory + r"USSD\\"


file = glob.glob(directory + f"**\\GFM_CDR_DETAILS_{str(start_date)}.csv", recursive=True)

print(len(file))

if len(file) == 0:
    print(f"Le fichier USSD du {start_date} n'a pas ete extrait ")
else:
    file = file[0]

    data = pd.read_csv(file, sep=';', index_col=False, dtype=str)
    data['Jour'] = pd.to_datetime(data['Jour'], errors='coerce').dt.strftime('%d/%m/%Y')
    data['Date Appel'] = pd.to_datetime(data['Date Appel'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')
    # print(data)
    data = pd.DataFrame(data, columns=['Date Appel', 'Jour', 'Numéro Serveur', 'Numéro Appelant', 'Durée Appel',
                                       'Total Appels', 'Total CA'])

    # print(data.columns)

    data = data.replace(np.nan, '')
    # data = data.applymap(lambda x: str(x).replace('.',','))
    # data=data.astype(str)
    data = list(data.to_records(index=False))
    # print(data)
    cur.executemany(
        """INSERT INTO optiwaretemp.TEMP_USSD_IVR("DATEAPPEL","JOUR","NUMEROSERVEUR","NUMEROAPPELANT","DUREEAPPEL","TOTALAPPELS","TOTALCA") VALUES(:1, :2, :3, :4, :5, :6, :7)""",
        data)
    conn.commit()

# file = glob.glob(directory+f"**\\GFM_CDR_DETAILS_{str(start_date)}.csv",recursive=True)

    ChargeUSSD(debut, fin)

print("################# FIN INSERT USSD ############")






print("\n insertPmuSenegal \n")
exec(open("C:\Batchs\scripts_python\extractions\journalier\insertPmuSenegal.py").read())

print("\n insert_Mini_Shop \n")
exec(open("C:\Batchs\scripts_python\extractions\journalier\insertMiniShopOracle_bis.py").read())


print("fin des insertions sur oracle")

#subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\insertMiniShopOracle_bis.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)



#print("\n all_product_daily_oracle \n")
#exec(open("C:\\Batchs\\scripts_python\\extractions\\journalier\\all_product_daily_oracle.py").read())






import gc
gc.collect()


    
    
    
    
    
    
    
    

#nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=0, minute=10, second=0, microsecond=0)

#pause.until(nextday)

    
#print(f"----------FIN:{str(datetime.now())}--------------------------")



"""

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
#checking for built-in variables/functions
if not obj.startswith('__'):
    #deleting the said obj, since a user-defined function
    del globals()[obj]

"""
