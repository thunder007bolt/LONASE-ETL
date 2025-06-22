import cx_Oracle
import pandas as pd
import numpy as np

def chargeAcajouDigitain(data, debut, fin, conn, cur):
    """
    Charge les données Acajou Digitain (Pari Sportif) dans la base de données Oracle.
    """
    data_list = data.astype(str) # Renommé pour éviter conflit
    data_list = list(data_list.to_records(index=False))

    # Vider la table temporaire optiwaretemp.src_prd_acacia pour les produits non Pick3/Grattage
    cur.execute("""delete from optiwaretemp.src_prd_acacia where PRODUIT not in ('Pick3','Grattage')""")
    conn.commit()

    # Remplir la table temporaire optiwaretemp.src_prd_acacia de donnees
    cur.executemany("""INSERT INTO optiwaretemp.src_prd_acacia("DATE_HEURE", "REFERENCE_TICKET", "TELEPHONE", "PURCHASE_METHOD", "MONTANT", "LOTS_A_PAYES","STATUS") VALUES(:1,:2,:3,:4,:5,:6,:7)""", data_list)
    conn.commit()

    # Mettre a jour le produit
    cur.execute("""update optiwaretemp.src_prd_acacia set PRODUIT = 'Pari Sportif' where PRODUIT not in ('Pick3','Grattage')""")
    conn.commit()

    # Suppression de la periode sur le fait vente
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX = 305
AND IDTERMINAL = 50073
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Suppression de la periode sur le fait lots
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE IDJEUX = 305
AND IDTERMINAL = 50073
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Insertion de la periode sur le fait vente
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

    # Insertion de la periode sur le fait lots
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
    conn.commit()

    # Vider la table temporaire optiwaretemp.src_prd_acacia pour ce produit
    cur.execute("""delete from optiwaretemp.src_prd_acacia where PRODUIT = 'Pari Sportif'""")
    conn.commit()

    print("La procedure d'insertion Acajou Digitain s'est bien deroulee")

def load_acajou_pick3_data(generalDirectory, start_date, conn, cur):
    """
    Charge les données Acajou Pick3 depuis un fichier CSV dans une table temporaire Oracle.
    """
    directory = generalDirectory + r"ACAJOU\PICK3\\"
    file_pattern = directory + f"**\\Listing_Tickets_Pick3 {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv"
    files = glob.glob(file_pattern, recursive=True)

    if not files:
        print(f"Le fichier Acajou Pick3 du {start_date} n'a pas ete extrait ")
        return False

    file_path = files[0]
    try:
        data = pd.read_csv(file_path, sep=';', index_col=False)
        data = pd.DataFrame(data, columns=['Date Created', 'Msisdn', 'Ticket ID', 'Purchase Method','Collection', 'Status', 'Gross Payout', 'Produit'])

        cur.execute("delete from OPTIWARETEMP.SRC_PRD_ACACIA where UPPER(TRIM(PRODUIT)) in (UPPER('Pick3'))")
        conn.commit()

        data_list = data.replace(np.nan, '').astype(str)
        data_list = list(data_list.to_records(index=False))

        cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_ACACIA( "DATE_HEURE","TELEPHONE","REFERENCE_TICKET","PURCHASE_METHOD","MONTANT","STATUS","LOTS_A_PAYES","PRODUIT") VALUES(:1, :2, :3, :4, :5, :6, :7, :8)""", data_list)
        conn.commit()
        print(f"Données Acajou Pick3 chargées depuis {file_path}")
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier Acajou Pick3 {file_path}: {e}")
        return False

def load_acajou_grattage_data(generalDirectory, start_date, conn, cur):
    """
    Charge les données Acajou Grattage depuis un fichier CSV dans une table temporaire Oracle.
    """
    directory = generalDirectory + r"ACAJOU\GRATTAGE\\"
    file_pattern = directory + f"**\\Listing_Tickets_Grattage {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv"
    files = glob.glob(file_pattern, recursive=True)

    if not files:
        print(f"Le fichier Acajou Grattage du {start_date} n'a pas ete extrait ")
        return False

    file_path = files[0]
    try:
        data = pd.read_csv(file_path, sep=';', index_col=False)
        data = pd.DataFrame(data, columns=['Date Created', 'Msisdn', 'Ticket ID', 'Purchase Method','Collection', 'Status', 'Gross Payout', 'Produit'])

        cur.execute("delete from OPTIWARETEMP.SRC_PRD_ACACIA where UPPER(TRIM(PRODUIT)) in (UPPER('grattage'))")
        conn.commit()

        data_list = data.replace(np.nan, '').astype(str)
        data_list = list(data_list.to_records(index=False))

        cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_ACACIA( "DATE_HEURE","TELEPHONE","REFERENCE_TICKET","PURCHASE_METHOD","MONTANT","STATUS","LOTS_A_PAYES","PRODUIT") VALUES(:1, :2, :3, :4, :5, :6, :7, :8)""", data_list)
        conn.commit()
        print(f"Données Acajou Grattage chargées depuis {file_path}")
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier Acajou Grattage {file_path}: {e}")
        return False

def chargeAcajouPick3Grattage(debut, fin, conn, cur):
    """
    Charge et traite les données Acajou Pick3 et Grattage dans la base de données Oracle.
    Dépend des données chargées par load_acajou_pick3_data et load_acajou_grattage_data.
    """
    # Suppression de la periode sur le fait vente
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX = 305
AND IDTERMINAL not in (50073)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Suppression de la periode sur le fait lots
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE IDJEUX = 305
AND IDTERMINAL not in (50073)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

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

    cur.execute("""delete FROM OPTIWARETEMP.SRC_PRD_ACACIA WHERE PRODUIT IN ('Grattage','Pick3')""")
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

    print("La procedure d'insertion Acajou Pick3 et Grattage s'est bien deroulee")

# Nécessite glob pour les fonctions load_*
import glob
