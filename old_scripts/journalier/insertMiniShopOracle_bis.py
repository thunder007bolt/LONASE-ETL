#!/usr/bin/env python
# coding: utf-8

# In[16]:


from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

import cx_Oracle


# In[17]:


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()- delta
start_date = end_date - delta

#print(start_date)
#start_date = datetime.date(2025, 3, 13)
#end_date = start_date+delta
#end_date = datetime.date(2023, 8, 1)


debut = start_date
fin = end_date-delta

generalDirectory = r"K:\\DATA_FICHIERS\\"

print(start_date)
#print(directory+f"**\\daily-modified-horse-racing-tickets-detailed_{str(start_date+delta).replace('-','')}.csv")


# In[18]:


def chargeMinishop(debut,fin):
    #pass
    import cx_Oracle

    #global start_date
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

    #vider la table temporaire optiwaretemp.src_prd_acacia

    #cur.execute("""TRUNCATE TABLE OPTIWARETEMP.GITECH """)
    #conn.commit()


    #remplir la table temporaire optiwaretemp.src_prd_acacia de donnees

    #cur.executemany("""INSERT INTO OPTIWARETEMP.GITECH( "Agences","Operateurs","date_de_vente","Recette_CFA","Annulation_CFA","Paiements_CFA") VALUES(:1, :2, :3, :4, :5, :6)""", data)
    #conn.commit()


    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX in (469,470)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    
    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""delete  from user_dwhpr.fait_lots 
    WHERE IDJEUX in (469,470)
    AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
    """)
    conn.commit()
    
    
    
    
    cur.execute(f"""
                INSERT INTO USER_DWHPR.DIM_TERMINAL(IDCCS,OPERATEUR,STATUT,IDSYSTEME)
    SELECT   IDCCS, OPERATEUR, '' STATUT, 174 IDSYSTEME 
    FROM (   SELECT DISTINCT F.OPERATEUR, IDCCS,174 IDSYSTEME
       from(
               SELECT DISTINCT t.TERMINAL OPERATEUR, IDCCS
               FROM OPTIWARETEMP.SRC_PRD_MINI_SHOP t ,USER_DWHPR.DIM_TERMINAL L
               WHERE t.TERMINAL= L.OPERATEUR
               AND IDSYSTEME IN(166,2)
          )F
          WHERE F.OPERATEUR NOT IN (SELECT OPERATEUR FROM USER_DWHPR.DIM_TERMINAL WHERE IDSYSTEME = 174)
     ) S
    
                """)
    conn.commit()
    
    
    cur.execute(f"""
                INSERT INTO USER_DWHPR.DIM_TERMINAL(IDCCS,OPERATEUR,STATUT,IDSYSTEME)
SELECT  388 IDCCS, OPERATEUR, '' STATUT, 174 IDSYSTEME 
    FROM (
               SELECT DISTINCT TERMINAL OPERATEUR
                      
                FROM OPTIWARETEMP.SRC_PRD_MINI_SHOP     
               WHERE TERMINAL NOT IN (SELECT OPERATEUR FROM USER_DWHPR.DIM_TERMINAL WHERE IDSYSTEME=174)
			   and JEU = 'SOLIDICON'
         ) S, USER_DWHPR.DIM_CCS
 
GROUP BY OPERATEUR

    
                """)
    conn.commit()
    
    
    
    
    cur.execute(f"""
                INSERT INTO USER_DWHPR.FAIT_VENTE(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
SELECT  7181 IDVENDEUR, 
        T.IDTERMINAL, 
		--T.OPERATEUR,
		Te.IDTEMPS, 
		F.IDJEUX, 
		MONTANT, 
		0 MONTANT_ANNULE,
       '' TICKET_EMIS, 
		'' TICKET_ANNULE, 
TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
TO_CHAR(Te.JOUR,'MM') MOIS,
REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
    FROM (
               SELECT TO_DATE(SUBSTR("DATE",1,10),'yyyy-mm-dd') DATEOP,
			    TERMINAL OPERATEUR,
			           
              TO_NUMBER(TRIM(REPLACE(REPLACE("MONTANT A VERSER",'.',','),' ',''))) MONTANT,
             case when UPPER(trim(JEU)) like 'SOLIDICON' THEN '470' ELSE '469' end IDJEUX     
                FROM OPTIWARETEMP.SRC_PRD_MINI_SHOP	
				where NOT (JEU = 'ALR HONORE GAMING' AND TERMINAL = '10961')
                --group by DATE, TERMINAL
			          
         ) F, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te
WHERE upper(trim(T.OPERATEUR)) = upper(trim(F.OPERATEUR ))
AND T.IDSYSTEME=174
AND Te.JOUR = F.DATEOP

                """)
    conn.commit()
    
    
    
    
    
    
    cur.execute(f"""
                INSERT INTO USER_DWHPR.FAIT_LOTS(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
SELECT  7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, 
   F.IDJEUX, MONTANT, 0 MONTANT_ANNULE,
        NVL(PAIEMENTS,0) PAIEMENTS, 
		TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
      TO_CHAR(Te.JOUR,'MM') MOIS,
       REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
    FROM (  
             SELECT TO_DATE(SUBSTR("DATE",1,10),'yyyy-mm-dd') DATEOP,
			    TERMINAL OPERATEUR,
			           
				 TO_NUMBER(TRIM(REPLACE(REPLACE("MONTANT A VERSER",'.',','),' ',''))) MONTANT,
                   TO_NUMBER(TRIM(REPLACE(REPLACE("MONTANT A PAYER",'.',','),' ',''))) PAIEMENTS,
                case when UPPER(trim(JEU)) like 'SOLIDICON' THEN '470' ELSE '469' end IDJEUX
                FROM OPTIWARETEMP.SRC_PRD_MINI_SHOP
				where NOT (JEU = 'ALR HONORE GAMING' AND TERMINAL = '10961')
               -- group by DATE, TERMINAL
                              
         ) F, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te
WHERE  upper(trim(T.OPERATEUR)) = upper(trim(F.OPERATEUR ))
  AND T.IDSYSTEME=174
  AND Te.JOUR= F.DATEOP

                """)
    conn.commit()
    
    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""
                MERGE INTO USER_DWHPR.DTM_MINI_SHOP R0 USING (
    
      SELECT  Te.IDTEMPS, Te.ANNEEC ANNEE, Te.MOISC MOIS,
                TO_DATE(SUBSTR("DATE",1,10),'yyyy-mm-dd') DATEOP, 
                  TERMINAL OPERATEUR, JEU as PRODUIT,
    
             SUM(TO_NUMBER(TRIM(REPLACE(REPLACE("MONTANT A VERSER",'.',','),' ','')))) MONTANT,
              SUM( TO_NUMBER(TRIM(REPLACE(REPLACE("MONTANT A PAYER",'.',','),' ','')))) PAIEMENTS
    
    
            FROM OPTIWARETEMP.SRC_PRD_MINI_SHOP , USER_DWHPR.DIM_TEMPS Te
    
            where te.JOUR = TO_DATE(SUBSTR("DATE",1,10),'yyyy-mm-dd')
            AND  NOT (JEU = 'ALR HONORE GAMING' AND TERMINAL = '10961')
           group by Te.IDTEMPS,Te.ANNEEC, Te.MOISC,TO_DATE(SUBSTR("DATE",1,10),'yyyy-mm-dd'),TERMINAL,JEU
    ) R1
    ON (R0.IDTEMPS=R1.IDTEMPS and R0.ANNEE= R1.ANNEE and R0.MOIS=R1.MOIS and R0.JOUR=R1.DATEOP and R0.OPERATEUR=R1.OPERATEUR  and R0.PRODUIT=R1.PRODUIT) 
    WHEN MATCHED THEN UPDATE SET R0.CA=R1.MONTANT, R0.LOTS=R1.PAIEMENTS
    WHEN NOT MATCHED THEN INSERT (IDTEMPS, ANNEE, MOIS, JOUR,CA,LOTS,PRODUIT,OPERATEUR)
                  VALUES (R1.IDTEMPS, R1.ANNEE, R1.MOIS, R1.DATEOP, R1.MONTANT, R1.PAIEMENTS,R1.PRODUIT,R1.OPERATEUR)	
                """)
    conn.commit()
    
    
    cur.execute(f"""
        MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(COALESCE(F.MONTANT,0)) - SUM(COALESCE(F.MONTANT_ANNULE,0)) as CA_MINI_SHOP
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te

WHERE F.IDJEUX=J.IDJEUX 
  AND F.IDTEMPS=Te.IDTEMPS 
  AND F.IDJEUX=469
  AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_MINI_SHOP=R1.CA_MINI_SHOP

""")
    conn.commit()
    
    
    cur.execute(f"""
        MERGE INTO DTM_CA_DAILY R0 USING 
( 
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(COALESCE(F.MONTANT,0)) - SUM(COALESCE(F.MONTANT_ANNULE,0)) as CA_VIRTUEL_SHOP
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te

WHERE F.IDJEUX=J.IDJEUX 
  AND F.IDTEMPS=Te.IDTEMPS 
  AND F.IDJEUX=470
  AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_VIRTUEL_SHOP=R1.CA_VIRTUEL_SHOP

""")
    conn.commit()
    
    '''

    cur.execute(f"""
        MERGE INTO user_dwhpr.dtm_ca t
USING (
          SELECT F.ANNEE ANNEE, F.MOIS MOIS, SUM(COALESCE(MONTANT,0))-SUM(COALESCE(MONTANT_ANNULE,0)) CA_MINI_SHOP
          FROM USER_DWHPR.FAIT_VENTE F, USER_DWHPR.DIM_TERMINAL T,USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
WHERE Te.IDTEMPS=F.IDTEMPS
                  AND Te.ANNEEC in ('{str(debut.strftime('%Y'))}','{str(fin.strftime('/%Y'))}')
                  AND F.IDJEUX=J.IDJEUX
                  AND F.IDJEUX = 469
                  AND F.idterminal=T.idterminal
                  AND T.idsysteme  = 174
          GROUP BY F.ANNEE , F.MOIS
       ) g

ON (t.annee = g.annee and t.mois=g.mois)
    WHEN MATCHED THEN UPDATE SET t.CA_MINI_SHOP= g.CA_MINI_SHOP
""")
    conn.commit()
    
    
    cur.execute(f"""
        MERGE INTO user_dwhpr.dtm_ca t
USING (
          SELECT F.ANNEE ANNEE, F.MOIS MOIS, SUM(COALESCE(MONTANT,0))-SUM(COALESCE(MONTANT_ANNULE,0)) CA_VIRTUEL_SHOP
          FROM USER_DWHPR.FAIT_VENTE F, USER_DWHPR.DIM_TERMINAL T,USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
WHERE Te.IDTEMPS=F.IDTEMPS
                  AND Te.ANNEEC in ('{str(debut.strftime('%Y'))}','{str(fin.strftime('/%Y'))}')
                  AND F.IDJEUX=J.IDJEUX
                  AND F.IDJEUX = 470
                  AND F.idterminal=T.idterminal
                  AND T.idsysteme  = 174
          GROUP BY F.ANNEE , F.MOIS
       ) g

ON (t.annee = g.annee and t.mois=g.mois)
    WHEN MATCHED THEN UPDATE SET t.CA_VIRTUEL_SHOP= g.CA_VIRTUEL_SHOP
""")
    conn.commit()
    
    '''
    
    
    
    
    
    
    cur.execute(f"""
                DELETE FROM OPTIWARETEMP.AR_MINI_SHOP
    WHERE "DATE" in (SELECT DISTINCT "DATE" FROM OPTIWARETEMP.SRC_PRD_MINI_SHOP  )
    
                """)
    conn.commit()
    
    
    #suppression de la periode sur le fait lots
    
    cur.execute(f"""INSERT INTO OPTIWARETEMP.AR_MINI_SHOP
    SELECT * FROM OPTIWARETEMP.SRC_PRD_MINI_SHOP
    
                """)
    conn.commit()
    
    
    cur.execute(f"""
                TRUNCATE TABLE OPTIWARETEMP.SRC_PRD_MINI_SHOP
                """)
    conn.commit()
    
    print("La procedure d'insertion s'est bien deroulee")


# In[19]:


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
    truncate table OPTIWARETEMP.SRC_PRD_MINI_SHOP
    """)
conn.commit()


# In[ ]:


while start_date<end_date:

    directory = generalDirectory+r"MINI_SHOP\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    file = glob.glob(directory+f"**\\minishop_{str(start_date)}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier Minishop du {start_date} n'a pas ete extrait ")
    else:
        file = file[0]

        data = pd.read_csv(file,sep=';',index_col=False)
        
        # 						


        data = pd.DataFrame(data,columns=['DATE', 'ETABLISSEMENT', 'JEU', 'TERMINAL', 'VENDEUR', 'MONTANT A VERSER','MONTANT A PAYER'])
        
        data=data.astype(str)
        data = list(data.to_records(index=False))
    
        cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_MINI_SHOP( "DATE"
      ,"ETABLISSEMENT"
      ,"JEU"
      ,"TERMINAL"
      ,"VENDEUR"
      ,"MONTANT A VERSER"
      ,"MONTANT A PAYER") VALUES(:1, :2, :3, :4, :5, :6, :7)""", data)
        conn.commit()

        #print(data)
        
    print(start_date)
        
    #chargeAcajouPick3Grattage()
        
    start_date+=delta

chargeMinishop(debut,fin)


# In[ ]:


#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]

