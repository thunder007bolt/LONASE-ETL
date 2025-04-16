# -*- coding: utf-8 -*-


from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

import cx_Oracle


# In[37]:


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()#- delta
start_date = end_date - delta

#print(start_date)
#start_date = datetime.date(2025, 1, 23)
#end_date = start_date+delta
#end_date = datetime.date(2025, 2, 7)


debut = start_date
fin = end_date-delta

generalDirectory = r"K:\\DATA_FICHIERS\\"

print(start_date)
#print(directory+f"**\\daily-modified-horse-racing-tickets-detailed_{str(start_date+delta).replace('-','')}.csv")


# In[38]:


def chargeHonoregaming(data,debut,fin):
    
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
                     , 1 TICKET_EMIS, CASE WHEN STATE LIKE 'Cancelled' THEN 1 ELSE 0 END TICKET_ANNULE, TO_NUMBER(TRIM(REPLACE(REPLACE(PAYABLEAMOUNT,'.',','),' ',''))) PAIEMENTS
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
    
    print("fait_vente")


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
                          ELSE TO_NUMBER(TRIM(REPLACE(REPLACE(PAYABLEAMOUNT,'.',','),' ',''))) 
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
    
    print("fait_lots")


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



# In[39]:


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
    truncate table optiwaretemp.SRC_PRD_ALR_HONORE_GAMING
    """)
conn.commit()


# In[40]:


from dateutil.parser import parse

directory = generalDirectory+r"HONORE_GAMING\\"
#print(f"virtuelAmabel{str(start_date)}.csv")

data = []

value = False

while start_date<end_date:
    
    file = glob.glob(directory+f"**\\daily-modified-horse-racing-tickets-detailed_{str(start_date+delta).replace('-','')}.csv",recursive=True)

    print(file)
    
    if len( file )>0:
        value = True
        #print(file[0])
        data = pd.read_csv(file[0],sep=';',index_col=False)
        
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
        data['MeetingDate'] = [parse(str(datee)).strftime("%d/%m/%Y") if pd.notna(datee) else datee for datee in data['MeetingDate']]

        
                     
        data = data.replace(np.nan, '')
    
        #print(len(data))
        data=data.astype(str)
        data = list(data.to_records(index=False))
        #print(len(data))

        first = 0
        second = 30000
        status = False
        while True:
                     
            if second >= len(data):
                second = len(data)
                status = True
        
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
          ,"GAMENAME") VALUES(:1, :2, :3, :4, :5,:6, :7, :8, :9, :10,:11, :12, :13, :14, :15,:16, :17, :18, :19, :20,:21, :22, :23, :24, :25,:26, :27, :28, :29, :30,:31, :32, :33, :34, :35,:36)""", data[first:second])
            first = second
            second += 30000
                     
            if status:
                break



                     
        conn.commit()

        
        print(start_date)
        #chargeHonoregaming(data,debut,fin)
        
        
        
    else:
        print(f"le fichier de la date du {start_date} est manquant")
    
    start_date+=delta
    


# In[41]:


#break


# In[42]:


if value:
    chargeHonoregaming(data,debut,fin)


# In[43]:


#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]
