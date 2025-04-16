# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 14:17:45 2025

@author: optiware3
"""
from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

import cx_Oracle

 delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
start_date = end_date - delta

#print(start_date)
start_date = datetime.date(2025, 3, 27)
end_date = start_date+delta
#end_date = datetime.date(2024, 6, 20)


debut = start_date
fin = end_date-delta

generalDirectory = r"K:\\DATA_FICHIERS\\"
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