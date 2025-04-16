#!/usr/bin/env python
# coding: utf-8

# In[2]:


from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np

import glob

import pyodbc


# In[4]:


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

#print(annee,start_date.strftime("%B"))
print(annee,mois)


# In[3]:


SERVER = 'SRVSQLDWHPRD'
DATABASE = 'DWHPR'
USERNAME = 'USER_DWHPR'
PASSWORD = 'optiware2016'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

conn = pyodbc.connect(connectionString)
cur = conn.cursor()




# In[4]:


print("Suppression au niveau de DTM_AFITECH_REDEVANCE")

cur.execute(f"""
delete
from "USER_DWHPR"."DTM_AFITECH_REDEVANCE"
where annee = '{annee}'
and mois = '{mois}'
""")
conn.commit()


# In[5]:


print("Suppression au niveau de DTM_CHARGES_CONVENTIONNELLES")

cur.execute(f"""
delete
from "USER_DWHPR"."DTM_CHARGES_CONVENTIONNELLES"
where annee = '{annee}'
and mois = '{mois}'
""")
conn.commit()


# In[6]:


print("Merge calcul redevance")

cur.execute(f"""
MERGE INTO "USER_DWHPR"."DTM_AFITECH_REDEVANCE" R1
USING (
    SELECT 
        IDTEMPS, ANNEE, MOIS, JOUR, PARTENAIRE, BENEFICIAIRE, 
        SUM(COALESCE(DEPOT, 0)) DEPOT, 
        SUM(ABS(COALESCE(RETRAIT, 0))) RETRAIT, 
        SUM(COALESCE(COMMISSION_DEPOT, 0)) COMMISSION_DEPOT, 
        SUM(COALESCE(COMMISSION_RETRAIT, 0)) COMMISSION_RETRAIT, 
        SUM(COALESCE(COMMISSION, 0)) COMMISSION,
        SUM(COALESCE(REDEVANCE, 0)) REDEVANCE
    FROM (
        SELECT 
            Te.IDTEMPS IDTEMPS, 
            Te.ANNEEC ANNEE, 
            Te.MOISC MOIS, 
            Te.JOUR, 
            CASE 
                WHEN upper(trim(PARTNER)) LIKE 'SERVICE ONLINE INTERNATIONAL' THEN 'SOI' 
                ELSE PARTNER 
            END PARTENAIRE, 
            PAYMENT_PROVIDER BENEFICIAIRE, 
            SUM(COALESCE(DEPOT, 0)) DEPOT, 
            SUM(ABS(COALESCE(RETRAIT, 0))) RETRAIT, 
            0.035 * SUM(COALESCE(DEPOT, 0)) COMMISSION_DEPOT, 
            0.035 * SUM(ABS(COALESCE(RETRAIT, 0))) COMMISSION_RETRAIT, 
            0.035 * SUM(COALESCE(DEPOT, 0)) + 0.035 * SUM(ABS(COALESCE(RETRAIT, 0))) COMMISSION,
            CASE 
                WHEN upper(trim(PARTNER)) IN ('1XBET', 'SERVICE ONLINE INTERNATIONAL') 
                    AND Te.JOUR >= '01/06/2022' AND Te.JOUR < '01/07/2023' THEN 0.18 * (
                    SUM(COALESCE(DEPOT, 0)) - SUM(ABS(COALESCE(RETRAIT, 0))) - (
                    SUM(FC_ORANGE) + SUM(FC_WAVE) + SUM(FC_WIZALL) + SUM(FC_FREE))
                )
                -- Add other conditions here, similar to the ones you already have
                ELSE 0 
            END AS REDEVANCE
        FROM 
            "USER_DWHPR".DTM_FRAIS_CONNEXION_AFITECH F
            JOIN "USER_DWHPR".DIM_TEMPS Te ON CAST(F.JOUR AS DATE) = CAST(Te.JOUR AS DATE)
        WHERE 
            Te.ANNEEC = '{annee}' 
            AND Te.MOISC = '{mois}'
        GROUP BY 
            Te.IDTEMPS, Te.ANNEEC, Te.MOISC, Te.JOUR, PARTNER, PAYMENT_PROVIDER
    ) r3
    GROUP BY 
        IDTEMPS, ANNEE, MOIS, JOUR, PARTENAIRE, BENEFICIAIRE
) r3_data
ON (R1.IDTEMPS = r3_data.IDTEMPS 
    AND R1.ANNEE = r3_data.ANNEE 
    AND R1.MOIS = r3_data.MOIS 
    AND R1.JOUR = r3_data.JOUR 
    AND R1.PARTENAIRE = r3_data.PARTENAIRE)

WHEN MATCHED THEN 
    UPDATE 
    SET 
        R1.DEPOT = r3_data.DEPOT,
        R1.RETRAIT = r3_data.RETRAIT,
        R1.COMMISSION_DEPOT = r3_data.COMMISSION_DEPOT,
        R1.COMMISSION_RETRAIT = r3_data.COMMISSION_RETRAIT,
        R1.COMMISSION = r3_data.COMMISSION,
        R1.REDEVANCE = r3_data.REDEVANCE

WHEN NOT MATCHED THEN 
    INSERT (IDTEMPS, ANNEE, MOIS, JOUR, PARTENAIRE, BENEFICIAIRE, DEPOT, RETRAIT, 
            COMMISSION_DEPOT, COMMISSION_RETRAIT, COMMISSION, REDEVANCE)
    VALUES (r3_data.IDTEMPS, r3_data.ANNEE, r3_data.MOIS, r3_data.JOUR, r3_data.PARTENAIRE, 
            r3_data.BENEFICIAIRE, r3_data.DEPOT, r3_data.RETRAIT, 
            r3_data.COMMISSION_DEPOT, r3_data.COMMISSION_RETRAIT, r3_data.COMMISSION, 
            r3_data.REDEVANCE);
   """)
conn.commit()


# In[ ]:


print("Merge calcul commission")

cur.execute(f"""
MERGE INTO "USER_DWHPR"."DTM_AFITECH_REDEVANCE" R1 USING ( 
    SELECT IDTEMPS,ANNEE,MOIS,JOUR,SUM(COALESCE(REDEVANC,0)) REDEVANCE,PARTENAIRE
    FROM (
            SELECT G.IDTEMPS IDTEMPS, G.ANNEE ANNEE, G.MOIS MOIS, G.JOUR JOUR, 
                  CASE WHEN upper(trim(G.AGENCE)) like 'LONASEBET' then 'Lonase.bet'
                       ELSE upper(trim(G.PRODUIT))
                  END as PARTENAIRE,
                  CASE /*WHEN upper(trim(G.PRODUIT)) like '22BET' then 10*(COALESCE(G.CA_LONASE,0))/100*/
                       WHEN upper(trim(G.PRODUIT)) like 'BWINNERS' then 0.18*(COALESCE(G.CA_LONASE,0) - COALESCE(G.LOTS_PAYE,0))
                       WHEN upper(trim(G.PRODUIT)) in ('PARIFOOT','LOTO','LOTO 5_90','PARIFOOT ONLINE','VIRTUEL EDITEC') and upper(trim(G.AGENCE)) not in ('LONASEBET','SUNUBET') 
                            then COALESCE(G.CA_LONASE,0)      
                       ELSE null 
                  END as REDEVANC 
            FROM
            (    SELECT IDTEMPS,ANNEE, MOIS, JOUR,LIBELLEJEUX PRODUIT,AGENCE,SUM(CA_LONASE) CA_LONASE, SUM(LOTS_PAYE) LOTS_PAYE
                 FROM (
                         SELECT Te.IDTEMPS,to_char(te.jour, 'yyyy') AS ANNEE, to_char(te.jour, 'mm') AS MOIS,te.jour JOUR,C.NOMCCS AGENCE, J.LIBELLEJEUX,
                                CASE 
                                     WHEN F.IDJEUX IN (27,123,310) AND T.IDCCS=181 THEN (COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0))*3/100
                                     WHEN F.IDJEUX IN (27,123,310) AND T.IDCCS<>181 THEN 0
                                     WHEN F.IDJEUX IN (124) THEN (COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0))*3/100
                                     WHEN T.OPERATEUR='SPORT BETTING ONLINE' THEN (COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0))*4/100
                                     WHEN T.OPERATEUR='CASINO ONLINE' THEN (COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0))*1.5/100
                                     ELSE COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0)
                                END CA_LONASE,
                                COALESCE(SUM(F.PAIEMENTS),0) LOTS_PAYE
                         FROM FAIT_LOTS F, DIM_TEMPS Te, DIM_TERMINAL T, DIM_CCS C, DIM_JEUX J
                         WHERE f.annee = '{annee}'
                        and    f.mois = '{mois}'
                         and F.IDTEMPS=Te.IDTEMPS 
                               AND T.IDTERMINAL=F.IDTERMINAL AND C.IDCCS=T.IDCCS AND J.IDJEUX=F.IDJEUX
                         GROUP BY Te.IDTEMPS,to_char(te.jour, 'yyyy'), to_char(te.jour, 'mm'),te.jour,T.IDCCS,C.NOMCCS,T.OPERATEUR,F.IDJEUX,J.LIBELLEJEUX
                      )
                GROUP BY IDTEMPS,ANNEE, MOIS,JOUR,LIBELLEJEUX,AGENCE
            ) G 
            WHERE G.annee = '{annee}'
            and   G.mois = '{mois}'
    )
    WHERE PARTENAIRE IN ('Lonase.bet','PARIFOOT','LOTO','LOTO 5_90','PARIFOOT ONLINE','VIRTUEL EDITEC','BWINNERS') 
    GROUP BY IDTEMPS,ANNEE,MOIS,JOUR,PARTENAIRE 
    
) R2 
ON (R1.IDTEMPS=R2.IDTEMPS AND R1.ANNEE=R2.ANNEE AND R1.MOIS=R2.MOIS AND R1.JOUR=R2.JOUR AND upper(trim(R1.PARTENAIRE))=upper(trim(R2.PARTENAIRE)))
WHEN MATCHED THEN UPDATE SET R1.REDEVANCE = R2.REDEVANCE
WHEN NOT MATCHED THEN INSERT (R1.IDTEMPS,R1.ANNEE,R1.MOIS,R1.JOUR,R1.REDEVANCE,R1.PARTENAIRE)
                      VALUES (R2.IDTEMPS,R2.ANNEE,R2.MOIS,R2.JOUR,R2.REDEVANCE,R2.PARTENAIRE)
""")
conn.commit()


# In[ ]:


print("Suppression XBET au niveau de fait_vente")

cur.execute(f"""
delete from "USER_DWHPR".fait_vente
where annee = '{annee}'
and mois = '{mois}'
and idjeux = 221
""")
conn.commit()


# In[ ]:


print("Suppression XBET au niveau de fait_lots")

cur.execute(f"""
delete from "USER_DWHPR".fait_lots
where annee = '{annee}'
and mois = '{mois}'
and idjeux = 221
""")
conn.commit()


# In[ ]:


print("START REMONTEE XBET")


# In[ ]:


print("REMONTEE XBET FAIT_VENTE")

cur.execute(f"""
INSERT INTO "USER_DWHPR".FAIT_VENTE
 SELECT '' IDVENTE, 7181 IDVENDEUR, 
            47781 IDTERMINAL, 
            Te.IDTEMPS, 
            221 IDJEUX,  
            COALESCE(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS, 
            0 TICKET_ANNULE, 
            TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
            TO_CHAR(Te.JOUR,'MM') MOIS, 
            REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
            
            FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, DIM_TEMPS Te
            
 WHERE TO_DATE(Te.JOUR,'DD/MM/RR') = TO_DATE(E.JOUR,'DD/MM/RR')
         AND Te.ANNEEC = '{annee}' 
        AND Te.MOISC = '{mois}'
   AND UPPER(E.PARTENAIRE) IN ('SOI','1XBET') --AND UPPER(E.PARTENAIRE) LIKE 'SOI'
   
GROUP BY Te.IDTEMPS, TO_CHAR(Te.JOUR,'YYYY'), TO_CHAR(Te.JOUR,'MM'), REPLACE(TO_CHAR(Te.JOUR),'/','')
""")
conn.commit()


# In[ ]:


print("REMONTEE XBET FAIT_LOTS")

cur.execute(f"""
INSERT INTO "USER_DWHPR".FAIT_LOTS
SELECT '' IDVENTE, 7181 IDVENDEUR, 
            47781 IDTERMINAL, 
            Te.IDTEMPS, 
            221 IDJEUX, 
            COALESCE(SUM(E.REDEVANCE),0) MONTANT, 
            0 MONTANT_ANNULE,
            0 PAIEMENTS, 
            TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
            TO_CHAR(Te.JOUR,'MM') MOIS, 
            REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
            
FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, DIM_TEMPS Te
            
 WHERE TO_DATE(Te.JOUR,'DD/MM/RR') = TO_DATE(E.JOUR,'DD/MM/RR')
          AND Te.ANNEEC = '{annee}' 
        AND Te.MOISC = '{mois}'
   AND UPPER(E.PARTENAIRE) IN ('SOI','1XBET') --AND UPPER(E.PARTENAIRE) LIKE 'SOI'
   
GROUP BY Te.IDTEMPS, TO_CHAR(Te.JOUR,'YYYY'), TO_CHAR(Te.JOUR,'MM'), REPLACE(TO_CHAR(Te.JOUR),'/','')
""")
conn.commit()


# In[ ]:


print("END REMONTEE XBET")


# In[ ]:


print("Suppression BETMOMO ET BETCLIC au niveau de fait_vente")

cur.execute(f"""
delete from "USER_DWHPR".fait_vente
where annee = '{annee}'
and mois = '{mois}'
and idjeux in (314,315)
""")
conn.commit()


# In[ ]:


print("Suppression BETMOMO ET BETCLIC au niveau de fait_lots")

cur.execute(f"""
delete from "USER_DWHPR".fait_lots
where annee = '{annee}'
and mois = '{mois}'
and idjeux in (314,315)
""")
conn.commit()


# In[ ]:


print("START REMONTEE BETMOMO ET BETCLIC")


# In[ ]:


print("REMONTEE BETMOMO ET BETCLIC au niveau de fait_vente")

cur.execute(f"""
INSERT INTO "USER_DWHPR".FAIT_VENTE
 SELECT '' IDVENTE, 7181 IDVENDEUR, 
            T.IDTERMINAL, 
            Te.IDTEMPS, 
            J.IDJEUX,
            COALESCE(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS, 
            0 TICKET_ANNULE, 
            TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
            TO_CHAR(Te.JOUR,'MM') MOIS, 
            REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
            
            FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
            
 WHERE TO_DATE(Te.JOUR,'DD/MM/RR') = TO_DATE(E.JOUR,'DD/MM/RR')
   AND Te.ANNEEC = '{annee}' 
    AND Te.MOISC = '{mois}'
   AND UPPER(T.OPERATEUR) = UPPER(E.PARTENAIRE)
   AND UPPER(J.LIBELLEJEUX) = UPPER(E.PARTENAIRE) 
   AND UPPER(E.PARTENAIRE) IN ('BETMOMO','BETCLIC')
   
GROUP BY T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, TO_CHAR(Te.JOUR,'YYYY'), TO_CHAR(Te.JOUR,'MM'), REPLACE(TO_CHAR(Te.JOUR),'/','')
""")
conn.commit()


# In[ ]:


print("REMONTEE BETMOMO ET BETCLIC au niveau de fait_lots")

cur.execute(f"""
INSERT INTO USER_DWHPR.FAIT_LOTS
 SELECT '' IDVENTE, 7181 IDVENDEUR, 
            T.IDTERMINAL, 
            Te.IDTEMPS, 
            J.IDJEUX,
            COALESCE(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 PAIEMENTS, 
            TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
            TO_CHAR(Te.JOUR,'MM') MOIS, 
            REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
            
            FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
            
 WHERE TO_DATE(Te.JOUR,'DD/MM/RR') = TO_DATE(E.JOUR,'DD/MM/RR')
   AND Te.ANNEEC = '{annee}' 
    AND Te.MOISC = '{mois}'
   AND UPPER(T.OPERATEUR) = UPPER(E.PARTENAIRE)
   AND UPPER(J.LIBELLEJEUX) = UPPER(E.PARTENAIRE) 
   AND UPPER(E.PARTENAIRE) IN ('BETMOMO','BETCLIC')
   
GROUP BY T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, TO_CHAR(Te.JOUR,'YYYY'), TO_CHAR(Te.JOUR,'MM'), REPLACE(TO_CHAR(Te.JOUR),'/','')
""")
conn.commit()


# In[ ]:


print("END REMONTEE BETMOMO ET BETCLIC")


# In[ ]:


print("Suppression SUNUBET ET 22BET au niveau de fait_vente")

cur.execute(f"""
delete from USER_DWHPR.fait_vente
where annee = '{annee}'
and mois = '{mois}'
and idjeux in (464,313)
""")
conn.commit()


# In[ ]:


print("Suppression SUNUBET ET 22BET au niveau de fait_lots")

cur.execute(f"""
delete from USER_DWHPR.fait_lots
where annee = '{annee}'
and mois = '{mois}'
and idjeux in (464,313)
""")
conn.commit()


# In[ ]:


print("START REMONTEE SUNUBET ET 22BET")


# In[ ]:


print("REMONTEE SUNUBET ET 22BET au niveau de fait_vente")

cur.execute(f"""

INSERT INTO USER_DWHPR.FAIT_VENTE
 SELECT '' IDVENTE, 7181 IDVENDEUR, 
            T.IDTERMINAL, 
            Te.IDTEMPS, 
            J.IDJEUX,
            COALESCE(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS, 
            0 TICKET_ANNULE, 
            TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
            TO_CHAR(Te.JOUR,'MM') MOIS, 
            REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
            
            FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
            
 WHERE TO_DATE(Te.JOUR,'DD/MM/RR') = TO_DATE(E.JOUR,'DD/MM/RR')
   AND Te.ANNEEC = '{annee}' 
    AND Te.MOISC = '{mois}'
   AND T.OPERATEUR LIKE (CASE WHEN J.IDJEUX=313 THEN 'SUNUBET ONLINE REDEVANCE' ELSE '22BET SPORT' END)
   --AND T.IDSYSTEME = 168
   AND UPPER(J.LIBELLEJEUX) = UPPER(E.PARTENAIRE) 
   AND UPPER(E.PARTENAIRE) IN ('SUNUBET','22BET') 
   
GROUP BY T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, TO_CHAR(Te.JOUR,'YYYY'), TO_CHAR(Te.JOUR,'MM'), REPLACE(TO_CHAR(Te.JOUR),'/','')
""")
conn.commit()


# In[ ]:


print("REMONTEE SUNUBET ET 22BET au niveau de fait_lots")

cur.execute(f"""
INSERT INTO USER_DWHPR.FAIT_LOTS
 SELECT '' IDVENTE, 7181 IDVENDEUR, 
            T.IDTERMINAL, 
            Te.IDTEMPS, 
            J.IDJEUX,
            COALESCE(SUM(E.REDEVANCE),0) MONTANT,
            0 MONTANT_ANNULE,
            0 PAIEMENTS, 
            TO_CHAR(Te.JOUR,'YYYY') ANNEE, 
            TO_CHAR(Te.JOUR,'MM') MOIS, 
            REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
            
            FROM USER_DWHPR.DTM_AFITECH_REDEVANCE E, DIM_TERMINAL T, DIM_TEMPS Te, DIM_JEUX J
            
 WHERE TO_DATE(Te.JOUR,'DD/MM/RR') = TO_DATE(E.JOUR,'DD/MM/RR')
   AND Te.ANNEEC = '{annee}' 
    AND Te.MOISC = '{mois}'
   AND T.OPERATEUR LIKE (CASE WHEN J.IDJEUX=313 THEN 'SUNUBET ONLINE REDEVANCE' ELSE '22BET SPORT' END)
   --AND T.IDSYSTEME = 168
   AND UPPER(J.LIBELLEJEUX) = UPPER(E.PARTENAIRE) 
   AND UPPER(E.PARTENAIRE) IN ('SUNUBET','22BET') 
   
GROUP BY T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, TO_CHAR(Te.JOUR,'YYYY'), TO_CHAR(Te.JOUR,'MM'), REPLACE(TO_CHAR(Te.JOUR),'/','')
""")
conn.commit()


# In[ ]:


print("END REMONTEE SUNUBET ET 22BET")


# In[ ]:


print(f"La remontee mensuelle des produit XBET, BETCLIC, BETMOMO, SUNUBET et 22BET de {month} '{annee}' est un succes")


# In[ ]:


print("MONTANT ENCAISSE DTM_CHARGES_CONVENTIONNELLES")

cur.execute(f"""
MERGE INTO  DTM_CHARGES_CONVENTIONNELLES R0 USING (

      SELECT Te.IDTEMPS,Te.ANNEEC,Te.MOISC,
            CASE WHEN UPPER(TRIM(C.NOMCCS)) like UPPER('Acacia') THEN 'ACAJOU' ELSE TRIM(C.NOMCCS) END AS NOMCCS, 
            J.LIBELLEJEUX,
           CASE WHEN UPPER(J.LIBELLEJEUX)IN ('XBET','SUNUBET','BETMOMO','BETCLIC','22BET','ACAJOU') THEN 0 ELSE COALESCE(SUM(F.MONTANT),0)-COALESCE(SUM(F.MONTANT_ANNULE),0) END  AS MONTANT_ENCAISSE
      FROM FAIT_VENTE F, DIM_CCS C, DIM_TERMINAL T, DIM_JEUX J, DIM_TEMPS Te 
      WHERE F.IDTERMINAL=T.IDTERMINAL 
          AND Te.IDTEMPS=F.IDTEMPS 
          AND F.IDJEUX= J.IDJEUX
          AND C.IDCCS=T.IDCCS
          AND Te.ANNEEC = '{annee}' 
          AND Te.MOISC = '{mois}'
      GROUP BY Te.IDTEMPS,Te.ANNEEC,Te.MOISC,C.NOMCCS, J.LIBELLEJEUX
)R1 ON (R0.IDTEMPS=R1.IDTEMPS AND R0.ANNEE=R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.AGENCE=R1.NOMCCS AND R0.PRODUIT=R1.LIBELLEJEUX)
WHEN MATCHED THEN UPDATE SET R0.MONTANT_ENCAISSE=R1.MONTANT_ENCAISSE 
WHEN NOT MATCHED THEN INSERT (R0.IDTEMPS,R0.ANNEE,R0.MOIS,R0.AGENCE,R0.PRODUIT,R0.MONTANT_ENCAISSE)
VALUES(R1.IDTEMPS,R1.ANNEEC,R1.MOISC,R1.NOMCCS,R1.LIBELLEJEUX,R1.MONTANT_ENCAISSE)

""")
conn.commit()


# In[ ]:


print("CA LONASE DTM_CHARGES_CONVENTIONNELLES")

cur.execute(f"""
MERGE INTO  DTM_CHARGES_CONVENTIONNELLES R0 USING 
(
    SELECT IDTEMPS,ANNEE, MOIS, NOMCCS, LIBELLEJEUX, SUM(CA_LONASE) CA_LONASE
      FROM (
 
                     SELECT Te.IDTEMPS,to_char(te.jour, 'yyyy') AS ANNEE, to_char(te.jour, 'mm') AS MOIS, C.NOMCCS, J.LIBELLEJEUX,
                                CASE 
                                    WHEN F.IDJEUX IN (27,123,310) AND T.IDCCS=181 THEN (COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0))*3/100
                                    WHEN F.IDJEUX IN (124) THEN (COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0))*3/100
                                    WHEN T.OPERATEUR='SPORT BETTING ONLINE' THEN (COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0))*4/100
                                    WHEN T.OPERATEUR='CASINO ONLINE' THEN (COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0))*1.5/100
                                    WHEN F.IDJEUX = 312 AND Te.IDTEMPS >= 8402  THEN 0
                                    ELSE COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0)
                                END CA_LONASE
                      FROM FAIT_VENTE F, DIM_TEMPS Te, DIM_TERMINAL T, DIM_CCS C, DIM_JEUX J
                      WHERE F.IDTEMPS=Te.IDTEMPS 
                      AND Te.ANNEEC = '{annee}' 
                        AND Te.MOISC = '{mois}'
                        AND T.IDTERMINAL=F.IDTERMINAL AND C.IDCCS=T.IDCCS AND J.IDJEUX=F.IDJEUX
                      GROUP BY Te.IDTEMPS,to_char(te.jour, 'yyyy'), to_char(te.jour, 'mm'),T.IDCCS, T.OPERATEUR,F.IDJEUX,C.NOMCCS, J.LIBELLEJEUX
                      
                      UNION ALL
                      
                      SELECT Te.IDTEMPS,to_char(te.jour, 'yyyy') AS ANNEE, to_char(te.jour, 'mm') AS MOIS, C.NOMCCS, J.LIBELLEJEUX,
                                CASE 
                                    WHEN F.IDJEUX = 312 AND Te.IDTEMPS >= 8402 THEN ( COALESCE(SUM(F.MONTANT),0) - COALESCE(SUM(F.MONTANT_ANNULE),0) - COALESCE(SUM(F.PAIEMENTS),0) )*18/100
                                    ELSE 0 
                                END CA_LONASE
                      FROM FAIT_LOTS F, DIM_TEMPS Te, DIM_TERMINAL T, DIM_CCS C, DIM_JEUX J
                      WHERE F.IDTEMPS=Te.IDTEMPS 
                      AND Te.ANNEEC = '{annee}' 
                        AND Te.MOISC = '{mois}'
                        AND T.IDTERMINAL=F.IDTERMINAL AND C.IDCCS=T.IDCCS AND J.IDJEUX=F.IDJEUX AND J.IDJEUX = 312
                      GROUP BY Te.IDTEMPS,to_char(te.jour, 'yyyy'), to_char(te.jour, 'mm'),T.IDCCS, T.OPERATEUR,F.IDJEUX,C.NOMCCS, J.LIBELLEJEUX
                      
                   
            )
  GROUP BY IDTEMPS,ANNEE, MOIS, NOMCCS, LIBELLEJEUX
)R1 ON (R0.IDTEMPS=R1.IDTEMPS AND R0.ANNEE=R1.ANNEE AND R0.MOIS=R1.MOIS AND R0.AGENCE=R1.NOMCCS AND R0.PRODUIT=R1.LIBELLEJEUX)
WHEN MATCHED THEN UPDATE SET R0.CA_LONASE=R1.CA_LONASE 
WHEN NOT MATCHED THEN INSERT (R0.IDTEMPS,R0.ANNEE,R0.MOIS,R0.AGENCE,R0.PRODUIT,R0.CA_LONASE)
VALUES(R1.IDTEMPS,R1.ANNEE,R1.MOIS,R1.NOMCCS,R1.LIBELLEJEUX,R1.CA_LONASE)
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


# In[ ]:





# In[ ]:




