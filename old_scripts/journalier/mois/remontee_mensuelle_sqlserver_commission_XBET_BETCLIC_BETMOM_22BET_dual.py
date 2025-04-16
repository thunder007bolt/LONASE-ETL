#!/usr/bin/env python
# coding: utf-8

# In[11]:


from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

import pyodbc


# In[12]:


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
start_date = end_date - delta

#print(start_date)
#start_date = datetime.date(2024, 2, 1)
#end_date = start_date+delta
#end_date = datetime.date(2024, 3, 1)


debut = start_date
fin = end_date-delta

#generalDirectory = r"K:\\DATA_FICHIERS\\"

start_date = datetime.date((end_date -  delta).year, (end_date -  delta).month, 1) -  delta

#print(start_date)

annee = start_date.strftime("%Y")
mois = start_date.strftime("%m")
month = start_date.strftime("%B")

print(annee,start_date.strftime("%B"))

print(datetime.datetime.now())


# In[13]:


SERVER = 'SRVSQLDWHPRD'
DATABASE = 'DWHPR'
USERNAME = 'USER_DWHPR'
PASSWORD = 'optiware2016'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
conn = pyodbc.connect(connectionString)
cursor2 = conn2.cursor()


# In[ ]:


print("Suppression au niveau de DTM_AFITECH_REDEVANCE")

cursor2.execute(f"""
delete
from "USER_DWHPR"."DTM_AFITECH_REDEVANCE"
where annee = '{annee}'
and mois = '{mois}'
""")


# In[ ]:


print("Suppression au niveau de DTM_CHARGES_CONVENTIONNELLES")

cursor2.execute(f"""
delete
from "USER_DWHPR"."DTM_CHARGES_CONVENTIONNELLES"
where annee = '{annee}'
and mois = '{mois}'
""")
conn.commit()


# In[ ]:


print("Merge calcul commission")

cursor2.execute(f"""
MERGE INTO [USER_DWHPR].[DTM_AFITECH_REDEVANCE] R1 USING (  
  
  SELECT IDTEMPS, ANNEE, MOIS, JOUR, PARTENAIRE, BENEFICIAIRE, 
         SUM(ISNULL(DEPOT,0)) DEPOT, SUM(ABS(ISNULL(RETRAIT,0))) RETRAIT, 
         SUM(ISNULL(COMMISSION_DEPOT,0)) COMMISSION_DEPOT, SUM(ISNULL(COMMISSION_RETRAIT,0)) COMMISSION_RETRAIT, 
         SUM(ISNULL(COMMISSION,0)) COMMISSION, SUM(ISNULL(REDEVANCE,0)) REDEVANCE
  FROM
  (
     
      
      SELECT Te.IDTEMPS IDTEMPS, Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, 
              CASE WHEN upper(trim(PARTNER)) LIKE 'SERVICE ONLINE INTERNATIONAL' THEN 'SOI' ELSE PARTNER END PARTENAIRE, 
              PAYMENT_PROVIDER BENEFICIAIRE, SUM(ISNULL(DEPOT,0)) DEPOT, SUM(ABS(ISNULL(RETRAIT,0))) RETRAIT, 
              0.035*SUM(ISNULL(DEPOT,0)) COMMISSION_DEPOT, 
              0.035*SUM(ABS(ISNULL(RETRAIT,0))) COMMISSION_RETRAIT, 
              0.035*SUM(ISNULL(DEPOT,0)) + 0.035*SUM(ABS(ISNULL(RETRAIT,0))) COMMISSION,
            case when upper(trim(PARTNER)) in ('1XBET','SERVICE ONLINE INTERNATIONAL') and Te.JOUR >= '01/06/2022' and Te.JOUR < '01/07/2023' then 0.18*( SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) - (SUM(FC_ORANGE)+SUM(FC_WAVE)+SUM(FC_WIZALL)+SUM(FC_FREE)) )
                 when upper(trim(PARTNER)) in ('1XBET','SERVICE ONLINE INTERNATIONAL') and Te.JOUR < '01/06/2022' then 0.15*( SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) - (SUM(FC_ORANGE)+SUM(FC_WAVE)+SUM(FC_WIZALL)+SUM(FC_FREE)) )
                 when upper(trim(PARTNER)) like 'SUNUBET' and Te.JOUR >= '01/07/2022' and Te.JOUR < '01/07/2023' then 0.17*(SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) - (SUM(FC_ORANGE)+SUM(FC_WAVE)+SUM(FC_WIZALL)+SUM(FC_FREE)) )
                 when upper(trim(PARTNER)) like 'BETMOMO' and Te.JOUR < '01/07/2023' then 0.15*(SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) - (SUM(FC_ORANGE)+SUM(FC_WAVE)+SUM(FC_WIZALL)+SUM(FC_FREE)) ) 
                 when upper(trim(PARTNER)) like 'BETCLIC' and Te.JOUR < '01/07/2023' then 0.15*(SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) - (SUM(FC_ORANGE)+SUM(FC_WAVE)+SUM(FC_WIZALL)+SUM(FC_FREE)) )
            
                 when upper(trim(PARTNER)) in ('1XBET','SERVICE ONLINE INTERNATIONAL') and Te.JOUR >= '01/07/2023' then 0.15*( SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) - (SUM(FC_ORANGE)+SUM(FC_WAVE)+SUM(FC_WIZALL)+SUM(FC_FREE)) )
                 when upper(trim(PARTNER)) like 'BETMOMO' and Te.JOUR >='01/07/2023' then 0.15*( SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) - (SUM(FC_ORANGE)+SUM(FC_WAVE)+SUM(FC_WIZALL)+SUM(FC_FREE)) )
                 when upper(trim(PARTNER)) like 'SUNUBET' and Te.JOUR >='01/07/2023' then 0.17*(SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) - (SUM(FC_ORANGE)+SUM(FC_WAVE)+SUM(FC_WIZALL)+SUM(FC_FREE)) )
                 when upper(trim(PARTNER)) like 'BETCLIC' and Te.JOUR >='01/07/2023' then 0.15*(SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) - (SUM(FC_ORANGE)+SUM(FC_WAVE)+SUM(FC_WIZALL)+SUM(FC_FREE)) )
                 when upper(trim(PARTNER)) like 'ACAJOU' and Te.JOUR >='11/08/2023' then 0.15*(SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) )
                 when upper(trim(PARTNER)) like '22BET' and Te.JOUR >='01/10/2023' then 0.17*(SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) )
                 when upper(trim(PARTNER)) like 'MELBET' and Te.JOUR >='02/05/2023' then 0.18*(SUM(ISNULL(DEPOT,0)) - SUM(ABS(ISNULL(RETRAIT,0))) )
				 else 0 
                 
            end as REDEVANCE
             
      FROM user_dwhpr.DTM_FRAIS_CONNEXION_AFITECH F, user_dwhpr.DIM_TEMPS Te
      WHERE CONVERT(DATETIME, F.JOUR,103)=CONVERT(DATETIME, Te.JOUR,103)
        AND Te.ANNEEC = '{annee}' 
        AND Te.MOISC = '{mois}'  
      GROUP BY Te.IDTEMPS, Te.ANNEEC, Te.MOISC, Te.JOUR, PARTNER, PAYMENT_PROVIDER
  ) s
  GROUP BY IDTEMPS, ANNEE, MOIS, JOUR, PARTENAIRE, BENEFICIAIRE
       
        
) R2 
ON (R1.IDTEMPS=R2.IDTEMPS AND R1.ANNEE=R2.ANNEE AND R1.MOIS=R2.MOIS AND R1.JOUR=R2.JOUR AND upper(trim(R1.PARTENAIRE))=upper(trim(R2.PARTENAIRE)) AND upper(trim(R1.BENEFICIAIRE))=upper(trim(R2.BENEFICIAIRE)) )
WHEN MATCHED THEN UPDATE SET R1.DEPOT=R2.DEPOT, R1.RETRAIT=R2.RETRAIT, R1.COMMISSION_DEPOT=R2.COMMISSION_DEPOT, 
                             R1.COMMISSION_RETRAIT=R2.COMMISSION_RETRAIT, R1.COMMISSION=R2.COMMISSION, R1.REDEVANCE=R2.REDEVANCE
WHEN NOT MATCHED THEN INSERT (IDTEMPS,ANNEE,MOIS,JOUR,DEPOT,RETRAIT,COMMISSION_DEPOT,COMMISSION_RETRAIT,COMMISSION,PARTENAIRE,REDEVANCE,BENEFICIAIRE)
                      VALUES (R2.IDTEMPS,R2.ANNEE,R2.MOIS,R2.JOUR,R2.DEPOT,R2.RETRAIT,R2.COMMISSION_DEPOT,R2.COMMISSION_RETRAIT,R2.COMMISSION,R2.PARTENAIRE,R2.REDEVANCE,R2.BENEFICIAIRE)

;
""")
conn.commit()


# In[ ]:


print("Merge calcul redevance")

cursor2.execute(f"""
MERGE INTO [USER_DWHPR].[DTM_AFITECH_REDEVANCE] R1 USING ( 
    SELECT IDTEMPS,ANNEE,MOIS,JOUR,SUM(isnull(REDEVANC,0)) REDEVANCE,PARTENAIRE
    FROM (
            SELECT G.IDTEMPS IDTEMPS, G.ANNEE ANNEE, G.MOIS MOIS, G.JOUR JOUR, 
                  CASE WHEN upper(trim(G.AGENCE)) like 'LONASEBET' then 'Lonase.bet'
                       ELSE upper(trim(G.PRODUIT))
                  END as PARTENAIRE,
                  CASE /* SQLINES DEMO *** PRODUIT)) like '22BET' then 10*(NVL(G.CA_LONASE,0))/100*/
                       WHEN upper(trim(G.PRODUIT)) like 'BWINNERS' then 0.18*(ISNULL(G.CA_LONASE,0) - ISNULL(G.LOTS_PAYE,0))
                       WHEN upper(trim(G.PRODUIT)) in ('PARIFOOT','LOTO','LOTO 5_90','PARIFOOT ONLINE','VIRTUEL EDITEC') and upper(trim(G.AGENCE)) not in ('LONASEBET','SUNUBET') 
                            then ISNULL(G.CA_LONASE,0)      
                       ELSE null 
                  END as REDEVANC 
            FROM
            (    SELECT IDTEMPS,ANNEE, MOIS, JOUR,LIBELLEJEUX PRODUIT,AGENCE,SUM(isnull(CA_LONASE,0)) CA_LONASE, SUM(isnull(LOTS_PAYE,0)) LOTS_PAYE
                 FROM (
                         SELECT Te.IDTEMPS,te.anneec AS ANNEE, te.moisc AS MOIS, te.jour JOUR,C.NOMCCS AGENCE, J.LIBELLEJEUX,
                                CASE 
                                     WHEN F.IDJEUX IN (27,123,310) AND T.IDCCS=181 THEN (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))*3/100
                                     WHEN F.IDJEUX IN (27,123,310) AND T.IDCCS<>181 THEN 0
                                     WHEN F.IDJEUX IN (124) THEN (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))*3/100
                                     WHEN T.OPERATEUR='SPORT BETTING ONLINE' THEN (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))*4/100
                                     WHEN T.OPERATEUR='CASINO ONLINE' THEN (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))*1.5/100
                                     ELSE (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))
                                END CA_LONASE,
                                SUM(isnull(F.PAIEMENTS,0)) LOTS_PAYE
                         FROM user_dwhpr.FAIT_LOTS F, user_dwhpr.DIM_TEMPS Te, user_dwhpr.DIM_TERMINAL T, user_dwhpr.DIM_CCS C, user_dwhpr.DIM_JEUX J
                         WHERE f.annee = '{annee}'
                           and f.mois = '{mois}'
                           AND T.IDTERMINAL=F.IDTERMINAL AND C.IDCCS=T.IDCCS AND J.IDJEUX=F.IDJEUX
                         GROUP BY Te.IDTEMPS,te.anneec, Te.moisc,te.jour,
						 T.IDCCS,C.NOMCCS,T.OPERATEUR,F.IDJEUX,J.LIBELLEJEUX
                      ) s
                GROUP BY IDTEMPS,ANNEE, MOIS,JOUR,LIBELLEJEUX,AGENCE
            ) G 
            WHERE G.annee = '{annee}'
            and G.mois = '{mois}'
    ) s
    WHERE PARTENAIRE IN ('Lonase.bet','PARIFOOT','LOTO','LOTO 5_90','PARIFOOT ONLINE','VIRTUEL EDITEC','BWINNERS') 
    GROUP BY IDTEMPS,ANNEE,MOIS,JOUR,PARTENAIRE 
    
) R2 
ON (R1.IDTEMPS=R2.IDTEMPS AND R1.ANNEE=R2.ANNEE AND R1.MOIS=R2.MOIS AND R1.JOUR=R2.JOUR AND upper(trim(R1.PARTENAIRE))=upper(trim(R2.PARTENAIRE)))
WHEN MATCHED THEN UPDATE SET R1.REDEVANCE = R2.REDEVANCE
WHEN NOT MATCHED THEN INSERT (IDTEMPS,ANNEE,MOIS,JOUR,REDEVANCE,PARTENAIRE)
                      VALUES (R2.IDTEMPS,R2.ANNEE,R2.MOIS,R2.JOUR,R2.REDEVANCE,R2.PARTENAIRE)
;
""")


# In[ ]:


print("Suppression XBET au niveau de fait_vente")

cursor2.execute(f"""
delete from "USER_DWHPR".fait_vente
where annee = '{annee}'
and mois = '{mois}'
and idjeux = 221
""")


# In[ ]:


print("Suppression XBET au niveau de fait_lots")

cursor2.execute(f"""
delete from "USER_DWHPR".fait_lots
where annee = '{annee}'
and mois = '{mois}'
and idjeux = 221
""")


# In[ ]:


print("START REMONTEE XBET")


# In[ ]:





# In[ ]:





# In[ ]:


print("REMONTEE XBET FAIT_VENTE")

cursor2.execute(f"""
INSERT INTO USER_DWHPR.FAIT_VENTE(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
 SELECT     7181 IDVENDEUR, 
            47781 IDTERMINAL, 
            Te.IDTEMPS, 
            221 IDJEUX,  
            ISNULL(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS, 
            0 TICKET_ANNULE, 
            FORMAT(CAST(Te.JOUR as datetime2), 'yyyy') ANNEE, 
            FORMAT(CAST(Te.JOUR as datetime2), 'MM') MOIS, 
            replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','') JOUR
            
            FROM DWHPR.USER_DWHPR.DTM_AFITECH_REDEVANCE E, /*DIM_JEUX J ,DIM_TERMINAL T,*/ DWHPR.USER_DWHPR.DIM_TEMPS Te
            
 WHERE FORMAT(CAST(Te.JOUR as datetime2),'dd/MM/yyyy') = FORMAT(CAST(E.JOUR as datetime2),'dd/MM/yyyy')
  AND Te.ANNEEC = '{annee}' 
  AND Te.MOISC = '{mois}'
  AND UPPER(E.PARTENAIRE) LIKE 'SOI'
   
GROUP BY /*T.IDTERMINAL, J.IDJEUX,*/ Te.IDTEMPS, FORMAT(CAST(Te.JOUR as datetime2), 'yyyy'), FORMAT(CAST(Te.JOUR as datetime2), 'MM'), replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','');

""")


# In[ ]:


print("REMONTEE XBET FAIT_LOTS")

cursor2.execute(f"""
INSERT INTO USER_DWHPR.FAIT_LOTS(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
SELECT  7181 IDVENDEUR, 
            47781 IDTERMINAL, 
            Te.IDTEMPS, 
            221 IDJEUX, 
            ISNULL(SUM(E.REDEVANCE),0) MONTANT, 
            0 MONTANT_ANNULE,
            0 PAIEMENTS, 
            FORMAT(CAST(Te.JOUR as datetime2), 'yyyy') ANNEE, 
            FORMAT(CAST(Te.JOUR as datetime2), 'MM') MOIS, 
            replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','') JOUR
            
FROM DWHPR.USER_DWHPR.DTM_AFITECH_REDEVANCE E, /*DIM_TERMINAL T , DIM_JEUX J, */ DWHPR.USER_DWHPR.DIM_TEMPS Te
            
 WHERE FORMAT(CAST(Te.JOUR as datetime2),'dd/MM/yyyy') = FORMAT(CAST(E.JOUR as datetime2),'dd/MM/yyyy')
   AND Te.ANNEEC = '{annee}' 
   AND Te.MOISC = '{mois}'
   AND UPPER(E.PARTENAIRE) LIKE 'SOI'
   
GROUP BY  Te.IDTEMPS, FORMAT(CAST(Te.JOUR as datetime2), 'yyyy'), FORMAT(CAST(Te.JOUR as datetime2), 'MM'), replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','') ;

;
""")


# In[ ]:


print("END REMONTEE XBET")


# In[ ]:


print("Suppression BETMOMO ET BETCLIC au niveau de fait_vente")

cursor2.execute(f"""
delete from "USER_DWHPR".fait_vente
where annee = '{annee}'
and mois = '{mois}'
and idjeux in (314,315)
""")


# In[ ]:


print("Suppression BETMOMO ET BETCLIC au niveau de fait_lots")

cursor2.execute(f"""
delete from "USER_DWHPR".fait_lots
where annee = '{annee}'
and mois = '{mois}'
and idjeux in (314,315)
""")


# In[ ]:


print("START REMONTEE BETMOMO ET BETCLIC")


# In[ ]:


print("REMONTEE BETMOMO ET BETCLIC au niveau de fait_vente")

cursor2.execute(f"""
INSERT INTO USER_DWHPR.FAIT_VENTE(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
 SELECT  7181 IDVENDEUR, 
            T.IDTERMINAL, 
            Te.IDTEMPS, 
            J.IDJEUX,
            ISNULL(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS, 
            0 TICKET_ANNULE, 
            FORMAT(CAST(Te.JOUR as datetime2), 'yyyy') ANNEE, 
            FORMAT(CAST(Te.JOUR as datetime2), 'MM') MOIS, 
            replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','') JOUR
            
            FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
            
 WHERE FORMAT(CAST(Te.JOUR as datetime2),'dd/MM/yyyy') = FORMAT(CAST(E.JOUR as datetime2),'dd/MM/yyyy')
   AND Te.ANNEEC = '{annee}' 
   AND Te.MOISC = '{mois}'
   AND UPPER(T.OPERATEUR) = UPPER(E.PARTENAIRE)
   AND UPPER(J.LIBELLEJEUX) = UPPER(E.PARTENAIRE) 
   AND UPPER(E.PARTENAIRE) IN ('BETMOMO','BETCLIC')
   
GROUP BY T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, FORMAT(CAST(Te.JOUR as datetime2), 'yyyy'), FORMAT(CAST(Te.JOUR as datetime2), 'MM'), replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','')
;
""")


# In[ ]:


print("REMONTEE BETMOMO ET BETCLIC au niveau de fait_lots")

cursor2.execute(f"""
INSERT INTO USER_DWHPR.FAIT_LOTS(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
 SELECT 7181 IDVENDEUR, 
            T.IDTERMINAL, 
            Te.IDTEMPS, 
            J.IDJEUX,
            ISNULL(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 PAIEMENTS, 
            FORMAT(CAST(Te.JOUR as datetime2), 'yyyy') ANNEE, 
            FORMAT(CAST(Te.JOUR as datetime2), 'MM') MOIS, 
            replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','') JOUR
            
            FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
            
 WHERE FORMAT(CAST(Te.JOUR as datetime2),'dd/MM/yyyy') = FORMAT(CAST(E.JOUR as datetime2),'dd/MM/yyyy')
   AND Te.ANNEEC = '{annee}' 
   AND Te.MOISC = '{mois}'
   AND UPPER(T.OPERATEUR) = UPPER(E.PARTENAIRE)
   AND UPPER(J.LIBELLEJEUX) = UPPER(E.PARTENAIRE) 
   AND UPPER(E.PARTENAIRE) IN ('BETMOMO','BETCLIC')
   
GROUP BY T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, FORMAT(CAST(Te.JOUR as datetime2), 'yyyy'), FORMAT(CAST(Te.JOUR as datetime2), 'MM'), replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','')
;
""")


# In[ ]:


print("END REMONTEE BETMOMO ET BETCLIC")


# In[ ]:


print("Suppression SUNUBET ET 22BET au niveau de fait_vente")

cursor2.execute(f"""
delete from USER_DWHPR.fait_vente
where annee = '{annee}'
and mois = '{mois}'
and idjeux in (464,313)
""")
conn.commit()


# In[ ]:


print("Suppression SUNUBET ET 22BET au niveau de fait_lots")

cursor2.execute(f"""
delete from USER_DWHPR.fait_lots
where annee = '{annee}'
and mois = '{mois}'
and idjeux in (464,313)
""")


# In[ ]:


print("START REMONTEE SUNUBET ET 22BET")


# In[ ]:


print("REMONTEE SUNUBET ET 22BET au niveau de fait_vente")

cursor2.execute(f"""

INSERT INTO USER_DWHPR.FAIT_VENTE(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
 SELECT  7181 IDVENDEUR, 
            T.IDTERMINAL, 
            Te.IDTEMPS, 
            J.IDJEUX,
            ISNULL(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS, 
            0 TICKET_ANNULE, 
            FORMAT(CAST(Te.JOUR as datetime2), 'yyyy') ANNEE, 
            FORMAT(CAST(Te.JOUR as datetime2), 'MM') MOIS, 
            replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','') JOUR 
            
            FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
            
 WHERE FORMAT(CAST(Te.JOUR as datetime2),'dd/MM/yyyy')  = FORMAT(CAST(E.JOUR as datetime2),'dd/MM/yyyy')
   AND Te.ANNEEC = '{annee}' 
   AND Te.MOISC = '{mois}'
   AND T.OPERATEUR LIKE (CASE WHEN J.IDJEUX=313 THEN 'SUNUBET ONLINE REDEVANCE' ELSE '22BET SPORT' END) 
   --AND T.IDSYSTEME = 168
   AND UPPER(J.LIBELLEJEUX) = UPPER(E.PARTENAIRE) 
   AND UPPER(E.PARTENAIRE) IN ('SUNUBET','22BET')
   
GROUP BY T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, FORMAT(CAST(Te.JOUR as datetime2), 'yyyy'), FORMAT(CAST(Te.JOUR as datetime2), 'MM'), replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','')
;
""")


# In[ ]:


print("REMONTEE SUNUBET ET 22BET au niveau de fait_lots")

cursor2.execute(f"""
INSERT INTO USER_DWHPR.FAIT_LOTS(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
 SELECT  7181 IDVENDEUR, 
            T.IDTERMINAL, 
            Te.IDTEMPS, 
            J.IDJEUX,
            ISNULL(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 PAIEMENTS, 
            FORMAT(CAST(Te.JOUR as datetime2), 'yyyy') ANNEE, 
            FORMAT(CAST(Te.JOUR as datetime2), 'MM') MOIS, 
            replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','') JOUR
            
            FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
            
 WHERE FORMAT(CAST(Te.JOUR as datetime2),'dd/MM/yyyy') = FORMAT(CAST(E.JOUR as datetime2),'dd/MM/yyyy')
   AND Te.ANNEEC = '{annee}' 
   AND Te.MOISC = '{mois}'
   AND T.OPERATEUR LIKE (CASE WHEN J.IDJEUX=313 THEN 'SUNUBET ONLINE REDEVANCE' ELSE '22BET SPORT' END)
   --AND T.IDSYSTEME = 168
   AND UPPER(J.LIBELLEJEUX) = UPPER(E.PARTENAIRE) 
   AND UPPER(E.PARTENAIRE) IN ('SUNUBET','22BET') --= 'SUNUBET'
   
GROUP BY T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, FORMAT(CAST(Te.JOUR as datetime2), 'yyyy'), FORMAT(CAST(Te.JOUR as datetime2), 'MM'),replace(replace(CONVERT( varchar(10),Te.JOUR,34),'-',''),'/','')
;

""")


# In[ ]:


print("END REMONTEE SUNUBET ET 22BET")


# In[ ]:


print(f"La remontee mensuelle des produit XBET, BETCLIC, BETMOMO, SUNUBET et 22BET de {month} '{annee}' est un succes")


# In[ ]:


print("MONTANT ENCAISSE DTM_CHARGES_CONVENTIONNELLES")

cursor2.execute(f"""
MERGE INTO  USER_DWHPR.DTM_CHARGES_CONVENTIONNELLES R0 USING (

      SELECT Te.IDTEMPS,Te.ANNEEC,Te.MOISC,
            CASE WHEN UPPER(TRIM(C.NOMCCS)) like UPPER('Acacia') THEN 'ACAJOU' ELSE TRIM(C.NOMCCS) END AS NOMCCS, 
            J.LIBELLEJEUX,
           CASE WHEN UPPER(J.LIBELLEJEUX)IN ('XBET','SUNUBET','BETMOMO','BETCLIC','22BET','ACAJOU') THEN 0 ELSE SUM(ISNULL(F.MONTANT,0))-SUM(ISNULL(F.MONTANT_ANNULE,0)) END  AS MONTANT_ENCAISSE
      FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_CCS C, user_dwhpr.DIM_TERMINAL T, user_dwhpr.DIM_JEUX J, user_dwhpr.DIM_TEMPS Te 
      WHERE  F.IDTERMINAL=T.IDTERMINAL 
          AND Te.ANNEEC = '{annee}' 
          AND Te.MOISC = '{mois}'
          AND Te.IDTEMPS=F.IDTEMPS 
          AND F.IDJEUX= J.IDJEUX
          AND C.IDCCS=T.IDCCS
          
      GROUP BY Te.IDTEMPS,Te.ANNEEC,Te.MOISC,C.NOMCCS, J.LIBELLEJEUX
      
    
)R1 ON (R0.IDTEMPS=R1.IDTEMPS AND R0.ANNEE=R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.AGENCE=R1.NOMCCS AND R0.PRODUIT=R1.LIBELLEJEUX)
WHEN MATCHED THEN UPDATE SET R0.MONTANT_ENCAISSE=R1.MONTANT_ENCAISSE 
WHEN NOT MATCHED THEN INSERT (IDTEMPS,ANNEE,MOIS,AGENCE,PRODUIT,MONTANT_ENCAISSE) 
VALUES(R1.IDTEMPS,R1.ANNEEC,R1.MOISC,R1.NOMCCS,R1.LIBELLEJEUX,R1.MONTANT_ENCAISSE);

""")


# In[ ]:


print("CA LONASE DTM_CHARGES_CONVENTIONNELLES")

cursor2.execute(f"""
MERGE INTO  USER_DWHPR.DTM_CHARGES_CONVENTIONNELLES R0 USING 
(
    SELECT IDTEMPS,ANNEE, MOIS, NOMCCS, LIBELLEJEUX, SUM(ISNULL(CA_LONASE,0)) CA_LONASE
      FROM (
 
                     SELECT Te.IDTEMPS,te.anneec AS ANNEE, te.moisc AS MOIS, C.NOMCCS, J.LIBELLEJEUX,
                                CASE 
                                    WHEN F.IDJEUX IN (27,123,310) AND T.IDCCS=181 THEN (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))*3/100
                                    WHEN F.IDJEUX IN (124) THEN (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))*3/100
                                    WHEN T.OPERATEUR='SPORT BETTING ONLINE' THEN (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))*4/100
                                    WHEN T.OPERATEUR='CASINO ONLINE' THEN (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))*1.5/100
                                    WHEN F.IDJEUX = 312 AND Te.IDTEMPS >= 8402  THEN 0
                                    ELSE (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)))
                                END CA_LONASE
                      FROM USER_DWHPR.FAIT_VENTE F, USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_CCS C, USER_DWHPR.DIM_JEUX J
                      WHERE F.IDTEMPS=Te.IDTEMPS
                        AND Te.ANNEEC = '{annee}' 
                        AND Te.MOISC = '{mois}'
                        AND T.IDTERMINAL=F.IDTERMINAL AND C.IDCCS=T.IDCCS AND J.IDJEUX=F.IDJEUX
                      GROUP BY Te.IDTEMPS,te.anneec, te.moisc,T.IDCCS, T.OPERATEUR,F.IDJEUX,C.NOMCCS, J.LIBELLEJEUX
                      
                      UNION ALL
                      
                      SELECT Te.IDTEMPS,te.anneec AS ANNEE, te.moisc AS MOIS, C.NOMCCS, J.LIBELLEJEUX,
                                CASE 
                                    WHEN F.IDJEUX = 312 AND Te.IDTEMPS >= 8402 THEN (SUM(ISNULL(F.MONTANT,0)) - SUM(ISNULL(F.MONTANT_ANNULE,0)) - SUM(ISNULL(F.PAIEMENTS,0)))*18/100
                                    ELSE 0 
                                END CA_LONASE
                      FROM USER_DWHPR.FAIT_LOTS F, USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_CCS C, USER_DWHPR.DIM_JEUX J
                      WHERE F.IDTEMPS=Te.IDTEMPS 
                        AND Te.ANNEEC = '{annee}' 
                        AND Te.MOISC = '{mois}'
                        
                        AND T.IDTERMINAL=F.IDTERMINAL AND C.IDCCS=T.IDCCS AND J.IDJEUX=F.IDJEUX AND J.IDJEUX = 312
                      GROUP BY Te.IDTEMPS,te.anneec, te.moisc,T.IDCCS, T.OPERATEUR,F.IDJEUX,C.NOMCCS, J.LIBELLEJEUX
                       ) s
  GROUP BY IDTEMPS,ANNEE, MOIS, NOMCCS, LIBELLEJEUX
)R1 ON (R0.IDTEMPS=R1.IDTEMPS AND R0.ANNEE=R1.ANNEE AND R0.MOIS=R1.MOIS AND R0.AGENCE=R1.NOMCCS AND R0.PRODUIT=R1.LIBELLEJEUX)
WHEN MATCHED THEN UPDATE SET R0.CA_LONASE=R1.CA_LONASE 
WHEN NOT MATCHED THEN INSERT (IDTEMPS,ANNEE,MOIS,AGENCE,PRODUIT,CA_LONASE)
VALUES(R1.IDTEMPS,R1.ANNEE,R1.MOIS,R1.NOMCCS,R1.LIBELLEJEUX,R1.CA_LONASE);
""")


# In[ ]:

conn.commit()

print(datetime.datetime.now())


# In[ ]:


cursor2.close()

conn2.close()


# In[ ]:


#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


# In[ ]:





# In[ ]:




