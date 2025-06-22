import cx_Oracle
import pandas as pd
import numpy as np

def load_sunubet_casino_data(generalDirectory, start_date, conn, cur):
    """
    Charge les données Sunubet Casino depuis un fichier CSV dans une table temporaire Oracle.
    """
    directory = generalDirectory + r"SUNUBET\CASINO\\"
    file_pattern = directory + f"**\\casinoSunubet {str(start_date)}.csv"
    files = glob.glob(file_pattern, recursive=True)

    if not files:
        print(f"Le fichier sunubet casino du {start_date} n'a pas ete extrait ")
        return False

    file_path = files[0]
    try:
        data = pd.read_csv(file_path, sep=';', index_col=False)
        data = pd.DataFrame(data, columns=["JOUR", "Stake", "PaidAmount"])
        data = data.replace(np.nan, '').astype(str)
        data_list = list(data.to_records(index=False))

        cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO("ISSUEDATETIME","STAKE", "PAIDAMOUNT") VALUES(:1, :2, :3)""", data_list)
        conn.commit()
        print(f"Données Sunubet Casino chargées depuis {file_path}")
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier Sunubet Casino {file_path}: {e}")
        return False

def load_sunubet_online_data(generalDirectory, start_date, conn, cur):
    """
    Charge les données Sunubet Online depuis un fichier CSV dans une table temporaire Oracle.
    """
    directory = generalDirectory + r"SUNUBET\ONLINE\\"
    file_pattern = directory + f"**\\onlineSunubet {str(start_date)}.csv"
    files = glob.glob(file_pattern, recursive=True)

    if not files:
        print(f"Le fichier sunubet online du {start_date} n'a pas ete extrait ")
        return False

    file_path = files[0]
    try:
        data = pd.read_csv(file_path, sep=';', index_col=False)
        data = pd.DataFrame(data, columns=["JOUR", "Stake", "PaidAmount", "BetCategory", "Freebet"])
        data = data.replace(np.nan, '').astype(str)
        data_list = list(data.to_records(index=False))

        # Diviser l'insertion en deux pour éviter les problèmes de taille potentiels avec executemany
        mid_point = len(data_list) // 2
        cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_SUNUBET_ONLINE( "ISSUEDATETIME","STAKE", "PAIDAMOUNT","BETCATEGORYTYPE", "FREEBET") VALUES(:1, :2, :3, :4, :5)""", data_list[:mid_point])
        if mid_point < len(data_list): # S'assurer qu'il y a des données dans la deuxième moitié
             cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_SUNUBET_ONLINE( "ISSUEDATETIME","STAKE", "PAIDAMOUNT","BETCATEGORYTYPE", "FREEBET") VALUES(:1, :2, :3, :4, :5)""", data_list[mid_point:])
        conn.commit()
        print(f"Données Sunubet Online chargées depuis {file_path}")
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier Sunubet Online {file_path}: {e}")
        return False

def process_sunubet_data(conn, cur):
    """
    Traite les données Sunubet Online et Casino chargées dans les tables temporaires
    pour mettre à jour DTM_MISE_SUNUBET_ONLINE.
    """
    # Traitement Sunubet Online
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
                upper(w.BetCategoryType) as CATEGORIE,
        sum ( NVL(to_number(regexp_replace(replace(w.PAIDAMOUNT,'.',','), '[^0-9,]+', '')),0) ) as LOT,
        to_number(0) as MONTANT_ANNULE
from optiwaretemp.src_prd_sunubet_online w ,user_dwhpr.dim_temps m
where  m.jour = to_char( to_date(trim(substr(w.issuedatetime,1,10))),'DD/MM/YYYY')
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

    # Traitement Sunubet Casino
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

    # Nettoyage des tables temporaires
    cur.execute("""truncate table OPTIWARETEMP.src_prd_sunubet_online""")
    conn.commit()
    cur.execute("""truncate table OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO""")
    conn.commit()
    print("Traitement des données Sunubet Online et Casino terminé.")

# Nécessite glob pour les fonctions load_*
import glob
