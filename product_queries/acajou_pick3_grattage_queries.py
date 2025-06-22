QUERIES = {
    # Pick3 data loading
    'truncate_temp_pick3': """DELETE FROM OPTIWARETEMP.SRC_PRD_ACACIA WHERE UPPER(TRIM(PRODUIT)) IN (UPPER('Pick3'))""",
    'insert_temp_pick3': """INSERT INTO OPTIWARETEMP.SRC_PRD_ACACIA( "DATE_HEURE","TELEPHONE","REFERENCE_TICKET","PURCHASE_METHOD","MONTANT","STATUS","LOTS_A_PAYES","PRODUIT") VALUES(:1, :2, :3, :4, :5, :6, :7, :8)""",

    # Grattage data loading
    'truncate_temp_grattage': """DELETE FROM OPTIWARETEMP.SRC_PRD_ACACIA WHERE UPPER(TRIM(PRODUIT)) IN (UPPER('grattage'))""",
    'insert_temp_grattage': """INSERT INTO OPTIWARETEMP.SRC_PRD_ACACIA( "DATE_HEURE","TELEPHONE","REFERENCE_TICKET","PURCHASE_METHOD","MONTANT","STATUS","LOTS_A_PAYES","PRODUIT") VALUES(:1, :2, :3, :4, :5, :6, :7, :8)""",

    # Common queries for Pick3 & Grattage after data is in src_prd_acacia
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE IDJEUX = 305
AND IDTERMINAL NOT IN (50073) -- Exclut Pari Sportif
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE IDJEUX = 305
AND IDTERMINAL NOT IN (50073) -- Exclut Pari Sportif
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",

    'insert_main_fait_vente': """INSERT INTO USER_DWHPR.FAIT_VENTE(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
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
                SELECT DATE_HEURE,TELEPHONE,'' OPERATEUR,'' NUMERO_JOUER,REFERENCE_TICKET,PRODUIT,PURCHASE_METHOD,STATUT, -- Ajout colonnes manquantes
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
    AND J.LIBELLEJEUX='ACAJOU'""",

    'insert_main_fait_lots': """INSERT INTO FAIT_LOTS (IDLOTS, IDVENDEUR, IDTERMINAL, IDTEMPS, IDJEUX, MONTANT, MONTANT_ANNULE, PAIEMENTS, ANNEE, MOIS, JOUR)
SELECT '' IDLOTS, 7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, MISE_TOTAL MONTANT, 0 MONTANT_ANNULE,
        LOTS_PAYES PAIEMENTS, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
    FROM (
            SELECT DATE_HEURE, PRODUIT, SUM(MISE_TOTAL) MISE_TOTAL, SUM(MISE_TICKET) MISE_TICKET, SUM(LOTS_TOTAL) LOTS_PAYES
            FROM (
                    SELECT DATE_HEURE,TELEPHONE,'' OPERATEUR,'' NUMERO_JOUER,REFERENCE_TICKET,PRODUIT,PURCHASE_METHOD,STATUT, -- Ajout colonnes manquantes
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
    AND J.LIBELLEJEUX='ACAJOU'""",

    'insert_ar_acacia_prd': """INSERT INTO OPTIWARETEMP.AR_ACACIA_PRD
    SELECT '' ID_ACACIA, DATE_HEURE, TELEPHONE, '' OPERATEUR, '' NUMERO_JOUER, REFERENCE_TICKET, MONTANT, STATUT, LOTS_A_PAYES, PRODUIT -- Ajout colonnes manquantes
        FROM (  SELECT *
                FROM OPTIWARETEMP.SRC_PRD_ACACIA
                WHERE PRODUIT IN ('Grattage','Pick3')
            ORDER BY DATE_HEURE
            )""",

    # AR_ACACIA_PRD_2 semble plus complexe et potentiellement aggrège sur des données déjà existantes.
    # Pour l'instant, je vais la laisser de côté ou la simplifier si elle est essentielle pour la période traitée.
    # 'insert_ar_acacia_prd_2': """...""",

    'cleanup_temp': """DELETE FROM OPTIWARETEMP.SRC_PRD_ACACIA WHERE PRODUIT IN ('Grattage','Pick3')""",

    'merge_dtm_ca_daily_pick3': """MERGE INTO DTM_CA_DAILY R0 USING
(
    SELECT Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) AS CA_ACAJOU_PICK3
    FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
    WHERE IDTERMINAL=50074 AND F.IDJEUX=J.IDJEUX -- Spécifique Pick3
    AND F.IDTEMPS=Te.IDTEMPS AND F.IDJEUX=305
    AND Te.JOUR BETWEEN :date_debut AND :date_fin
    GROUP BY Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ACAJOU_PICK3=R1.CA_ACAJOU_PICK3""",

    'merge_dtm_ca_daily_grattage': """MERGE INTO DTM_CA_DAILY R0 USING
(
    SELECT Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) AS CA_ACAJOU_GRATTAGE
    FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
    WHERE IDTERMINAL=50075 AND F.IDJEUX=J.IDJEUX -- Spécifique Grattage
    AND F.IDTEMPS=Te.IDTEMPS AND F.IDJEUX=305
    AND Te.JOUR BETWEEN :date_debut AND :date_fin
    GROUP BY Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ACAJOU_GRATTAGE=R1.CA_ACAJOU_GRATTAGE"""
}

def get_queries():
    return QUERIES
