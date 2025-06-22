QUERIES = {
    'truncate_temp': """DELETE FROM OPTIWARETEMP.SRC_PRD_PREMIERBET""",
    'insert_temp': """INSERT INTO OPTIWARETEMP.SRC_PRD_PREMIERBET( "ID","Username", "Balance", "Total Players","Total Players Date Range", "SB Bets No.", "SB Stake","SB Closed Stake", "SB Wins No.", "SB Wins", "SB Ref No.", "SB Refunds","SB GGR", "Cas.Bets No.", "Cas.Stake", "Cas.Wins No.", "Cas.Wins","Cas.Ref No.", "Cas.Refunds", "Cas.GGR", "Total GGR", "Adjustments","Deposits", "Financial Deposits", "Financial Withdrawals","Transaction Fee", "Date") VALUES(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27)""",
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE idjeux = 281 -- Parifoot Online (PremierBet)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE idjeux = 281 -- Parifoot Online (PremierBet)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'remove_total_from_temp': """DELETE FROM OPTIWARETEMP.SRC_PRD_PREMIERBET WHERE ID IN ('Total:','Total: ')""",
    'insert_main_fait_vente': """INSERT INTO FAIT_VENTE
    SELECT '' AS IDVENTE, 7181 AS IDVENDEUR, IDTERMINAL, Te.IDTEMPS, 281 AS IDJEUX,
        SUM(VENTES)AS MONTANT, SUM(ANNULATIONS) AS MONTANT_ANNULE, SUM(NB_TKS_BRUT) TICKET_EMIS, SUM(NB_TKS_ANNULE) TICKET_ANNULE,
        TRIM(TO_CHAR(Te.JOUR,'yyyy')) AS ANNEE, TRIM(TO_CHAR(Te.JOUR,'mm')) AS MOIS, TRIM(TO_CHAR(Te.JOUR,'ddmmyyyy')) AS JOUR
    FROM (
        SELECT '52222' TERMINAL, "Date", TO_NUMBER(REPLACE("SB Stake",'.',',')) VENTES, TO_NUMBER(REPLACE("SB Refunds",'.',',')) ANNULATIONS,
            TO_NUMBER(REPLACE("SB Bets No.",'.',',')) NB_TKS_BRUT, TO_NUMBER(REPLACE("SB Ref No.",'.',',')) NB_TKS_ANNULE,
            TO_NUMBER(REPLACE("SB Wins",'.',',')) PAIEMENTS, TO_NUMBER(REPLACE("SB Wins No.",'.',',')) NB_TKS_GAGNE, TO_NUMBER(REPLACE("SB GGR",'.',',')) GGR
        FROM OPTIWARETEMP.SRC_PRD_PREMIERBET
        UNION ALL
        SELECT '52223' TERMINAL, "Date", TO_NUMBER(REPLACE("Cas.Stake",'.',',')) VENTES, TO_NUMBER(REPLACE("Cas.Refunds",'.',',')) ANNULATIONS,
            TO_NUMBER(REPLACE("Cas.Bets No.",'.',',')) NB_TKS_BRUT, TO_NUMBER(REPLACE("Cas.Ref No.",'.',',')) NB_TKS_ANNULE,
            TO_NUMBER(REPLACE("Cas.Wins",'.',',')) PAIEMENTS, TO_NUMBER(REPLACE("Cas.Wins No.",'.',',')) NB_TKS_GAGNE, TO_NUMBER(REPLACE("Cas.GGR",'.',',')) GGR
        FROM OPTIWARETEMP.SRC_PRD_PREMIERBET
    ) F, DIM_TEMPS Te, DIM_TERMINAL T
    WHERE Te.JOUR= F."Date" AND T.IDTERMINAL=F.TERMINAL
    GROUP BY Te.IDTEMPS, IDTERMINAL, TRIM(TO_CHAR(Te.JOUR,'yyyy')), TRIM(TO_CHAR(Te.JOUR,'mm')), TRIM(TO_CHAR(Te.JOUR,'ddmmyyyy'))""",
    'insert_main_fait_lots': """INSERT INTO FAIT_LOTS
    SELECT '' AS IDLOTS, 7181 AS IDVENDEUR, IDTERMINAL, Te.IDTEMPS, 281 AS IDJEUX,
        SUM(VENTES)AS MONTANT, SUM(ANNULATIONS) AS MONTANT_ANNULE, SUM(PAIEMENTS) PAIEMENTS,
        TRIM(TO_CHAR(Te.JOUR,'yyyy')) AS ANNEE, TRIM(TO_CHAR(Te.JOUR,'mm')) AS MOIS, TRIM(TO_CHAR(Te.JOUR,'ddmmyyyy')) AS JOUR
    FROM (
        SELECT '52222' TERMINAL, "Date", TO_NUMBER(REPLACE("SB Stake",'.',',')) VENTES, TO_NUMBER(REPLACE("SB Refunds",'.',',')) ANNULATIONS,
            TO_NUMBER(REPLACE("SB Bets No.",'.',',')) NB_TKS_BRUT, TO_NUMBER(REPLACE("SB Ref No.",'.',',')) NB_TKS_ANNULE,
            TO_NUMBER(REPLACE("SB Wins",'.',',')) PAIEMENTS, TO_NUMBER(REPLACE("SB Wins No.",'.',',')) NB_TKS_GAGNE, TO_NUMBER(REPLACE("SB GGR",'.',',')) GGR
        FROM OPTIWARETEMP.SRC_PRD_PREMIERBET
        UNION ALL
        SELECT '52223' TERMINAL, "Date", TO_NUMBER(REPLACE("Cas.Stake",'.',',')) VENTES, TO_NUMBER(REPLACE("Cas.Refunds",'.',',')) ANNULATIONS,
            TO_NUMBER(REPLACE("Cas.Bets No.",'.',',')) NB_TKS_BRUT, TO_NUMBER(REPLACE("Cas.Ref No.",'.',',')) NB_TKS_ANNULE,
            TO_NUMBER(REPLACE("Cas.Wins",'.',',')) PAIEMENTS, TO_NUMBER(REPLACE("Cas.Wins No.",'.',',')) NB_TKS_GAGNE, TO_NUMBER(REPLACE("Cas.GGR",'.',',')) GGR
        FROM OPTIWARETEMP.SRC_PRD_PREMIERBET
    ) F, DIM_TEMPS Te, DIM_TERMINAL T
    WHERE Te.JOUR= F."Date" AND T.IDTERMINAL=F.TERMINAL
    GROUP BY Te.IDTEMPS, IDTERMINAL, TRIM(TO_CHAR(Te.JOUR,'yyyy')), TRIM(TO_CHAR(Te.JOUR,'mm')), TRIM(TO_CHAR(Te.JOUR,'ddmmyyyy'))""",
    'insert_fact_parifoot_online': """INSERT INTO FACT_PARIFOOT_ONLINE
    SELECT "ID" SB_USER_ID, "Username" TELEPHONE, SUM("SB Stake")+SUM("Cas Stake") AS MONTANT, SUM("SB Refunds")+SUM("Cas Refunds") AS MONTANT_ANNULE,
        SUM("SB Bets No")+SUM("Cas Bets No") TICKET_EMIS, SUM("SB Ref No")+SUM("Cas Ref No") TICKET_ANNULE,
        SUM("SB Wins")+SUM("Cas Wins") AS LOTS_PAYÉS, SUM("SB Wins No.")+SUM("Cas.Wins No.") AS TICKET_PAYÉS,
        SUM("Cas.GGR") AS SB_BENEFICE, SUM("Cas.GGR") AS CAS_BENEFICE, SUM("Total GGR") AS BENEFICE,
        SUM("Balance") AS SOLDE_CLIENT, SUM("Deposits") AS DEPOTS, SUM("Financial Withdrawals") AS RETRAIT_CLIENT,
        TRIM(TO_CHAR(Te.JOUR,'yyyy')) AS ANNEE, TRIM(TO_CHAR(Te.JOUR,'mm')) AS MOIS, TRIM(TO_CHAR(Te.JOUR,'dd/mm/yyyy')) AS JOUR
    FROM (
        SELECT "ID", "Username", "Date", TO_NUMBER(REPLACE("Balance",'.',',')) "Balance",
            TO_NUMBER(REPLACE("SB Stake",'.',',')) "SB Stake", TO_NUMBER(REPLACE("Cas.Stake",'.',',')) "Cas Stake",
            TO_NUMBER(REPLACE("SB Refunds",'.',',')) "SB Refunds", TO_NUMBER(REPLACE("Cas.Refunds",'.',',')) "Cas Refunds",
            TO_NUMBER(REPLACE("SB Bets No.",'.',',')) "SB Bets No", TO_NUMBER(REPLACE("Cas.Bets No.",'.',',')) "Cas Bets No",
            TO_NUMBER(REPLACE("SB Ref No.",'.',',')) "SB Ref No", TO_NUMBER(REPLACE("Cas.Ref No.",'.',',')) "Cas Ref No",
            TO_NUMBER(REPLACE("SB Wins",'.',',')) "SB Wins", TO_NUMBER(REPLACE("Cas.Wins",'.',',')) "Cas Wins",
            TO_NUMBER(REPLACE("SB Wins No.",'.',',')) "SB Wins No.", TO_NUMBER(REPLACE("Cas.Wins No.",'.',',')) "Cas.Wins No.",
            TO_NUMBER(REPLACE("SB GGR",'.',',')) "SB GGR", TO_NUMBER(REPLACE("Cas.GGR",'.',',')) "Cas.GGR",
            TO_NUMBER(REPLACE("Total GGR",'.',',')) "Total GGR", TO_NUMBER(REPLACE("Deposits",'.',',')) "Deposits",
            TO_NUMBER(REPLACE("Financial Withdrawals",'.',',')) "Financial Withdrawals"
        FROM OPTIWARETEMP.SRC_PRD_PREMIERBET
    ) F, DIM_TEMPS Te
    WHERE Te.JOUR= F."Date"
    GROUP BY "ID", "Username", TRIM(TO_CHAR(Te.JOUR,'yyyy')), TRIM(TO_CHAR(Te.JOUR,'mm')), TRIM(TO_CHAR(Te.JOUR,'dd/mm/yyyy'))""",
    'insert_fact_voucher': """INSERT INTO OPTIWARETEMP.FACT_VOUCHER
    SELECT SB_USER_ID, TELEPHONE, SOLDE_CLIENT, TICKET_EMIS NOMBRE_PARIS, MONTANT MISE,
        "TICKET_PAYÉS" NOMBRE_PARIS_GAGNES, LOTS_PAYÉS MONTANT_GAGNES, MONTANT_ANNULE, BENEFICE,
        DEPOTS, MOIS, RETRAIT_CLIENT, JOUR, ANNEE
    FROM USER_DWHPR.FACT_PARIFOOT_ONLINE
    WHERE JOUR NOT IN (SELECT DISTINCT JOUR FROM OPTIWARETEMP.FACT_VOUCHER)""", # Attention, cette condition peut poser problème si on relance pour une même journée.
    'delete_ar_premierbet': """DELETE FROM OPTIWARETEMP.AR_PREMIERBET WHERE "Date" IN (SELECT DISTINCT "Date" FROM OPTIWARETEMP.SRC_PRD_PREMIERBET)""",
    'insert_ar_premierbet': """INSERT INTO OPTIWARETEMP.AR_PREMIERBET SELECT * FROM OPTIWARETEMP.SRC_PRD_PREMIERBET""",
    'cleanup_temp': """TRUNCATE TABLE OPTIWARETEMP.SRC_PRD_PREMIERBET""",
    'merge_dtm_ca_daily': """MERGE INTO DTM_CA_DAILY R0 USING
    (
        SELECT ANNEEC, MOISC, JOUR, SUM(CA_PARIFOOT_ONLINE) CA_PARIFOOT_ONLINE
            FROM (
                    SELECT Te.ANNEEC,Te.MOISC,Te.JOUR,
                            CASE
                                WHEN Te.IDTEMPS>=7945 AND T.OPERATEUR LIKE 'SPORT BETTING ONLINE' THEN (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE))*4/100
                                WHEN Te.IDTEMPS>=7945 AND T.OPERATEUR LIKE 'CASINO ONLINE' THEN (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE))*1.5/100
                                ELSE SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE)
                            END AS CA_PARIFOOT_ONLINE
                    FROM FAIT_VENTE F, DIM_TERMINAL T, DIM_JEUX J , DIM_TEMPS Te
                    WHERE T.IDTERMINAL=F.IDTERMINAL AND F.IDJEUX=J.IDJEUX AND F.IDTEMPS=Te.IDTEMPS
                        AND F.IDJEUX IN (27,281) AND F.IDTERMINAL IN (46864,52222,52223) -- IDJEUX 27 est aussi inclus ici
                        AND Te.JOUR BETWEEN :date_debut AND :date_fin
                    GROUP BY Te.ANNEEC,Te.MOISC,Te.JOUR,T.OPERATEUR,Te.IDTEMPS
                )
        GROUP BY ANNEEC, MOISC, JOUR
    ) R1
    ON ( R0.ANNEE = R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
    WHEN MATCHED THEN UPDATE SET R0.CA_PARIFOOT_ONLINE=R1.CA_PARIFOOT_ONLINE"""
}

def get_queries():
    return QUERIES
