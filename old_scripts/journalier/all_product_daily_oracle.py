#!/usr/bin/env python
# coding: utf-8

# In[11]:


import cx_Oracle

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

conn1 = cx_Oracle.connect(username,password,dsn)
cur1 = conn1.cursor() #creates a cursor object


# In[12]:


try:
    cur1.execute("""
    CREATE GLOBAL TEMPORARY TABLE temp_sys_jeu 
    (NOMSYSTEME VARCHAR2(254 BYTE) , IDSYSTEME VARCHAR2(254 BYTE), IDTERMINAL VARCHAR2(254 BYTE), 
    IDJEUX VARCHAR2(254 BYTE), LIBELLEJEUX VARCHAR2(254 BYTE)) 
    ON COMMIT PRESERVE ROWS
    """)
except:
    cur1.execute("""
    drop TABLE temp_sys_jeu 
    """)
    
    cur1.execute("""
    CREATE GLOBAL TEMPORARY TABLE temp_sys_jeu 
    (NOMSYSTEME VARCHAR2(254 BYTE) , IDSYSTEME VARCHAR2(254 BYTE), IDTERMINAL VARCHAR2(254 BYTE), 
    IDJEUX VARCHAR2(254 BYTE), LIBELLEJEUX VARCHAR2(254 BYTE)) 
    ON COMMIT PRESERVE ROWS
    """)


cur1.execute("""


    insert into temp_sys_jeu (NOMSYSTEME , IDSYSTEME, IDTERMINAL, IDJEUX, LIBELLEJEUX) (
    SELECT 
        s.NOMSYSTEME AS NOMSYSTEME,
        s.IDSYSTEME,
        t.IDTERMINAL as IDTERMINAL,
        v.IDJEUX as IDJEUX,
        j.LIBELLEJEUX AS LIBELLEJEUX
    FROM 
        user_dwhpr.DIM_JEUX j
    JOIN 
        user_dwhpr.FAIT_VENTE v ON v.IDJEUX = j.IDJEUX and v.annee >= '2022' --in ('2022','2023','2024')
        and j.LIBELLEJEUX not in 
    ('TELEMILLION','TEBBI','NOPALE','DARE-DARE','CashChrono','Inconnu','RakTak','AMKO','TAF_TAF',
    'INST2','BONUS PLUS','LAMB','GUEUSSEUM','NUMBERS','KENO','PARIFOOT BET221','VIRTUEL BET221','AUTRES','MAX2CASH','VIRTUEL EDITEC'
    )
    JOIN 
        user_dwhpr.DIM_TERMINAL t ON v.IDTERMINAL = t.IDTERMINAL
    JOIN 
        user_dwhpr.DIM_SYSTEME s ON t.IDSYSTEME = s.IDSYSTEME 
        and s.NOMSYSTEME not in ('PMC','PMU_MOBILE','RAKTAK','MAX2 CASH','BET221','SEN_PREMIER_GAMES','GUEUSSEUM','HONORE GAMING','ACACIA')
    group by s.IDSYSTEME,s.NOMSYSTEME,t.IDTERMINAL, v.IDJEUX, j.LIBELLEJEUX
    )

    """)
#conn1.commit()

    


# In[13]:


cur1.execute("""
    truncate table OPTIWARETEMP.ALL_PRODUCT_DAILY
    """)


cur1.execute("""


    insert into OPTIWARETEMP.ALL_PRODUCT_DAILY (systeme,produit,mc,lot,jour)

select sys_jeu.NOMSYSTEME , sys_jeu.LIBELLEJEUX,
sum(coalesce(montant,0))-sum(coalesce(montant_annule,0)) as ca ,
sum(coalesce(paiements,0)) as lot,
te.jour
from temp_sys_jeu sys_jeu cross join USER_DWHPR.DIM_TEMPS Te
left join user_dwhpr.FAIT_LOTS F on Te.idtemps = f.idtemps and sys_jeu.IDTERMINAL = f.IDTERMINAL
where te.anneec in ('2024','2025') 
and te.jour < TRUNC(SYSDATE)
group by te.jour,sys_jeu.NOMSYSTEME , sys_jeu.LIBELLEJEUX

UNION ALL

        select 'HONORE GAMING',
        case when IDJEUX = 25 then 'ALR' when IDJEUX = 26 then 'PLR' end,
        sum(coalesce(montant,0))-sum(coalesce(montant_annule,0)) as ca ,sum(coalesce(paiements,0)) as lot,te.jour 
        from user_dwhpr.FAIT_LOTS f right join USER_DWHPR.DIM_TEMPS Te on f.idtemps = Te.idtemps 
        where idjeux in (25,26)
        and idterminal in (select idterminal from user_dwhpr.DIM_TERMINAL where idsysteme = 166)
        and te.anneec in ('2024','2025')
        and te.jour < TRUNC(SYSDATE)
        group by IDJEUX,te.jour

		UNION ALL

        select 'ACACIA',
        case when IDTERMINAL = 50074 then 'ACAJOU PICK3'
when IDTERMINAL = 50075 then 'ACAJOU GRATTAGE'
when IDTERMINAL = 50073 then 'ACAJOU PARIFOOT' end,
        sum(coalesce(montant,0))-sum(coalesce(montant_annule,0)) as ca ,sum(coalesce(paiements,0)) as lot,te.jour 
        from user_dwhpr.FAIT_LOTS f right join USER_DWHPR.DIM_TEMPS Te on f.idtemps = Te.idtemps 
        where idjeux in (305)
        --and idterminal in (select idterminal from user_dwhpr.DIM_TERMINAL where idsysteme = 166)
        and te.anneec in ('2024','2025')
        and te.jour < TRUNC(SYSDATE)
        group by IDTERMINAL,te.jour

    """)
conn1.commit()


# In[14]:


cur1.close()
conn1.close()  


# In[15]:


#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]


# In[ ]:




