QUERIES = {
    # Utilise src_prd_acacia, mais filtre pour ne pas impacter Pick3/Grattage avant leur propre traitement
    'truncate_temp': """DELETE FROM optiwaretemp.src_prd_acacia WHERE PRODUIT NOT IN ('Pick3','Grattage')""",
    'insert_temp': """INSERT INTO optiwaretemp.src_prd_acacia("DATE_HEURE", "REFERENCE_TICKET", "TELEPHONE", "PURCHASE_METHOD", "MONTANT", "LOTS_A_PAYES","STATUS") VALUES(:1,:2,:3,:4,:5,:6,:7)""",
    'update_temp_produit': """UPDATE optiwaretemp.src_prd_acacia SET PRODUIT = 'Pari Sportif' WHERE PRODUIT IS NULL OR PRODUIT NOT IN ('Pick3','Grattage')""", # S'assure que le produit est bien 'Pari Sportif' pour les nouvelles insertions
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE IDJEUX = 305
AND IDTERMINAL = 50073 -- Spécifique à Acajou Pari Sportif
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE IDJEUX = 305
AND IDTERMINAL = 50073 -- Spécifique à Acajou Pari Sportif
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'insert_main_fait_vente': """INSERT INTO FAIT_VENTE (IDVENTE, IDVENDEUR, IDTERMINAL, IDTEMPS, IDJEUX, MONTANT, MONTANT_ANNULE, TICKET_EMIS, TICKET_ANNULE, ANNEE, MOIS, JOUR)
SELECT '' IDVENTE, 7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, MISE_TOTAL MONTANT, 0 MONTANT_ANNULE,
        MISE_TICKET TICKET_EMIS, 0 TICKET_ANNULE, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
FROM (
        SELECT DATE_HEURE, PRODUIT, SUM(MISE_TOTAL) MISE_TOTAL, SUM(MISE_TICKET) MISE_TICKET, SUM(LOTS_TOTAL) LOTS_TOTAL
        FROM (
                SELECT DATE_HEURE,TELEPHONE,'' OPERATEUR, '' NUMERO_JOUER,REFERENCE_TICKET,PRODUIT,PURCHASE_METHOD,STATUT, -- Ajout colonnes manquantes avec valeurs par défaut
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
AND J.LIBELLEJEUX='ACAJOU'""",
    'insert_main_fait_lots': """INSERT INTO FAIT_LOTS (IDLOTS, IDVENDEUR, IDTERMINAL, IDTEMPS, IDJEUX, MONTANT, MONTANT_ANNULE, PAIEMENTS, ANNEE, MOIS, JOUR)
SELECT '' IDLOTS, 7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, J.IDJEUX, MISE_TOTAL MONTANT, 0 MONTANT_ANNULE,
        LOTS_PAYES PAIEMENTS, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, REPLACE(TO_CHAR(Te.JOUR),'/','') JOUR
    FROM (
            SELECT DATE_HEURE, PRODUIT, SUM(MISE_TOTAL) MISE_TOTAL, SUM(MISE_TICKET) MISE_TICKET, SUM(LOTS_TOTAL) LOTS_PAYES
            FROM (
                    SELECT DATE_HEURE,TELEPHONE,'' OPERATEUR, '' NUMERO_JOUER,REFERENCE_TICKET,PRODUIT,PURCHASE_METHOD,STATUT, -- Ajout colonnes manquantes
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
    AND J.LIBELLEJEUX='ACAJOU'""",
    'merge_dtm_ca_daily': """MERGE INTO DTM_CA_DAILY R0 USING
(
    SELECT Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) AS CA_ACAJOU_PARIFOOT
    FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
    WHERE IDTERMINAL=50073 AND F.IDJEUX=J.IDJEUX
    AND F.IDTEMPS=Te.IDTEMPS AND F.IDJEUX=305
    AND Te.JOUR BETWEEN :date_debut AND :date_fin
    GROUP BY Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ACAJOU_PARIFOOT=R1.CA_ACAJOU_PARIFOOT""",
    'cleanup_temp': """DELETE FROM optiwaretemp.src_prd_acacia WHERE PRODUIT NOT IN ('Pick3','Grattage')""" # Nettoyage final pour ce produit spécifique
}

def get_queries():
    return QUERIES
