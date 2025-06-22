import cx_Oracle
import pandas as pd
import numpy as np

def chargeParifootonline(data, debut, fin, conn, cur):
    """
    Charge les données Parifoot Online (Premierbet) dans la base de données Oracle.
    """
    data = data.replace(np.nan, '')

    # Convertir les colonnes numériques en nombres, puis remplacer . par , pour Oracle
    numeric_cols = [
        'Balance', 'SB Bets No.', 'SB Stake', 'SB Closed Stake',
        'SB Wins No.', 'SB Wins', 'SB Ref No.', 'SB Refunds', 'SB GGR',
        'Cas.Bets No.', 'Cas.Stake', 'Cas.Wins No.', 'Cas.Wins',
        'Cas.Ref No.', 'Cas.Refunds', 'Cas.GGR', 'Total GGR',
        'Adjustments', 'Deposits', 'Financial Deposits',
        'Financial Withdrawals', 'Transaction Fee'
    ]
    for col in numeric_cols:
        if col in data.columns:
            # Remplacer les virgules par des points pour la conversion en float, puis reconvertir en chaîne avec virgule pour Oracle
            data[col] = pd.to_numeric(data[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            #data[col] = data[col].astype(str).str.replace('.', ',') # Cette ligne est problématique si Oracle attend des nombres

    # Transformer la colonne 'date' au format DD/MM/YYYY si elle est présente et dans un autre format
    if 'date' in data.columns:
         try:
            data['date'] = pd.to_datetime(data['date']).dt.strftime('%d/%m/%Y')
         except Exception as e:
            print(f"Avertissement: Impossible de convertir la colonne 'date' au format DD/MM/YYYY: {e}")
            # Garder le format original si la conversion échoue, ou gérer l'erreur autrement


    data_list = data.astype(str) # Convertir tout en str avant to_records
    data_list = list(data_list.to_records(index=False))

    cur.execute("""delete  from OPTIWARETEMP.SRC_PRD_PREMIERBET""")
    conn.commit()

    cur.executemany("""INSERT INTO OPTIWARETEMP.SRC_PRD_PREMIERBET( "ID","Username", "Balance", "Total Players","Total Players Date Range", "SB Bets No.", "SB Stake","SB Closed Stake", "SB Wins No.", "SB Wins", "SB Ref No.", "SB Refunds","SB GGR", "Cas.Bets No.", "Cas.Stake", "Cas.Wins No.", "Cas.Wins","Cas.Ref No.", "Cas.Refunds", "Cas.GGR", "Total GGR", "Adjustments","Deposits", "Financial Deposits", "Financial Withdrawals","Transaction Fee", "Date") VALUES(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27)""", data_list)
    conn.commit()

    # Suppression fait_vente et fait_lots
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 281
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE idjeux = 281
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    cur.execute(f"""DELETE FROM OPTIWARETEMP.SRC_PRD_PREMIERBET WHERE ID IN ('Total:','Total: ')""")
    conn.commit()

    # Insertion FAIT_VENTE
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

    # Insertion FAIT_LOTS
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

    # Insertion FACT_PARIFOOT_ONLINE
    cur.execute(f"""
    INSERT INTO FACT_PARIFOOT_ONLINE
    SELECT "ID" SB_USER_ID,
        "Username" TELEPHONE,
        SUM(TO_NUMBER(REPLACE("SB Stake",'.',',')))+SUM(TO_NUMBER(REPLACE("Cas.Stake",'.',','))) AS MONTANT,
        SUM(TO_NUMBER(REPLACE("SB Refunds",'.',',')))+SUM(TO_NUMBER(REPLACE("Cas.Refunds",'.',','))) AS MONTANT_ANNULE,
        SUM(TO_NUMBER(REPLACE("SB Bets No.",'.',',')))+SUM(TO_NUMBER(REPLACE("Cas.Bets No.",'.',','))) TICKET_EMIS,
        SUM(TO_NUMBER(REPLACE("SB Ref No.",'.',',')))+SUM(TO_NUMBER(REPLACE("Cas.Ref No.",'.',','))) TICKET_ANNULE,
        SUM(TO_NUMBER(REPLACE("SB Wins",'.',',')))+SUM(TO_NUMBER(REPLACE("Cas.Wins",'.',','))) AS LOTS_PAYÉS,
        SUM(TO_NUMBER(REPLACE("SB Wins No.",'.',',')))+SUM(TO_NUMBER(REPLACE("Cas.Wins No.",'.',','))) AS TICKET_PAYÉS,
        SUM(TO_NUMBER(REPLACE("SB GGR",'.',','))) AS SB_BENEFICE,
        SUM(TO_NUMBER(REPLACE("Cas.GGR",'.',','))) AS CAS_BENEFICE,
        SUM(TO_NUMBER(REPLACE("Total GGR",'.',','))) AS BENEFICE,
        SUM(TO_NUMBER(REPLACE("Balance",'.',','))) AS SOLDE_CLIENT,
        SUM(TO_NUMBER(REPLACE("Deposits",'.',','))) AS DEPOTS,
        SUM(TO_NUMBER(REPLACE("Financial Withdrawals",'.',','))) AS RETRAIT_CLIENT,
        TRIM(TO_CHAR(Te.JOUR,'yyyy')) AS ANNEE,
        TRIM(TO_CHAR(Te.JOUR,'mm')) AS MOIS,
        TRIM(TO_CHAR(Te.JOUR,'dd/mm/yyyy')) AS JOUR
    FROM OPTIWARETEMP.SRC_PRD_PREMIERBET F, DIM_TEMPS Te
    WHERE Te.JOUR= F."Date"
GROUP BY "ID" ,
        "Username",
            TRIM(TO_CHAR(Te.JOUR,'yyyy')),
            TRIM(TO_CHAR(Te.JOUR,'mm')),
            TRIM(TO_CHAR(Te.JOUR,'dd/mm/yyyy'))
""")
    conn.commit()

    # Insertion FACT_VOUCHER
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

    # Archivage
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

    cur.execute(f"""truncate table OPTIWARETEMP.SRC_PRD_PREMIERBET""")
    conn.commit()

    # DTM_CA_DAILY
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

    print("La procedure d'insertion Parifoot Online (Premierbet) s'est bien deroulee")
