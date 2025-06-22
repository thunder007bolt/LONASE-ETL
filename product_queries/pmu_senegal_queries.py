QUERIES = {
    # Initial Truncates for temp tables before CSV load
    'truncate_temp_ca': """TRUNCATE TABLE optiwaretemp.SRC_PRD_PMUSENEGAL_CA""",
    'truncate_temp_lots': """TRUNCATE TABLE optiwaretemp.SRC_PRD_PMUSENEGAL_LOTS""",

    # Inserts into temp tables from CSV data
    'insert_temp_ca': """INSERT INTO optiwaretemp.SRC_PRD_PMUSENEGAL_CA("PRODUIT", "CA", "SHARING", "JOUR", "ANNEE", "MOIS") VALUES(:1, :2, :3, :4, :5, :6)""",
    'insert_temp_lots': """INSERT INTO optiwaretemp.SRC_PRD_PMUSENEGAL_LOTS("JOUEUR", "NOMBRE_DE_FOIS_GAGNE", "MONTANT", "TYPE", "COMBINAISON", "OFFRE", "PRODUIT", "JOUR", "ANNEE", "MOIS") VALUES(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10)""",

    # Deletes from main tables
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE idjeux IN (468)
AND IDTERMINAL IN (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL WHERE IDSYSTEME = 173)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE idjeux IN (468)
AND IDTERMINAL IN (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL WHERE IDSYSTEME = 173)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",

    # Inserts into main tables
    'insert_main_fait_vente': """INSERT INTO USER_DWHPR.FAIT_VENTE (IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
(
SELECT
    7181 AS IDVENDEUR,
    TO_NUMBER(te.idterminal) AS IDTERMINAL,
    TO_NUMBER(m.idtemps) AS IDTEMPS,
    468 AS IDJEUX,
    TO_NUMBER(COALESCE(TRIM(REPLACE(REPLACE(w.CA, '.', ','), ' ', '')), '0')) AS MONTANT,
    0 AS MONTANT_ANNULE,
    NULL AS TICKET_EMIS,
    NULL AS TICKET_ANNULE,
    m.ANNEEC AS ANNEE,
    m.MOISC AS MOIS,
    REPLACE(m.jour, '/', '') AS JOUR
FROM
    OPTIWARETEMP.SRC_PRD_PMUSENEGAL_CA w
JOIN
    USER_DWHPR.DIM_TERMINAL te
    ON UPPER(TRIM(w.PRODUIT)) = UPPER(TRIM(te.operateur))
JOIN
    USER_DWHPR.DIM_TEMPS m
    ON m.jour = w.JOUR
WHERE
    te.idsysteme = 173
)""",
    'insert_main_fait_lots': """INSERT INTO USER_DWHPR.FAIT_LOTS (IDVENDEUR, IDTERMINAL, IDTEMPS, IDJEUX, MONTANT, MONTANT_ANNULE, PAIEMENTS, ANNEE, MOIS, JOUR)
(
    SELECT
        7181 AS IDVENDEUR,
        TO_NUMBER(te.idterminal) AS IDTERMINAL,
        TO_NUMBER(m.idtemps) AS IDTEMPS,
        468 AS IDJEUX,
        L.CA, -- This comes from the subquery joining CA and LOTS tables
        0 AS MONTANT_ANNULE,
        L.PAIEMENTS,
        m.ANNEEC AS ANNEE,
        m.MOISC AS MOIS,
        REPLACE(m.jour, '/', '') AS JOUR
    FROM
        (
            SELECT
                JOUR,
                produit,
                CA,
                PAIEMENTS
            FROM
                (
                    SELECT
                        w.JOUR,
                        w.produit,
                        COALESCE(TO_NUMBER(TRIM(REPLACE(REPLACE(w.CA, '.', ','), ' ', ''))), 0) AS CA,
                        NULL AS PAIEMENTS
                    FROM OPTIWARETEMP.SRC_PRD_PMUSENEGAL_CA w
                    UNION ALL
                    SELECT
                        l.JOUR,
                        l.produit,
                        NULL AS CA,
                        COALESCE(TO_NUMBER(TRIM(REPLACE(REPLACE(l.Montant, '.', ','), ' ', ''))), 0) AS PAIEMENTS
                    FROM OPTIWARETEMP.SRC_PRD_PMUSENEGAL_LOTS l
                )
        ) L
JOIN
    USER_DWHPR.DIM_TERMINAL te
    ON UPPER(TRIM(L.PRODUIT)) = UPPER(TRIM(te.operateur))
JOIN
    USER_DWHPR.DIM_TEMPS m
    ON m.jour = L.JOUR
WHERE
    te.idsysteme = 173
)""",

    # Merges
    'merge_dtm_ca_daily': """MERGE INTO DTM_CA_DAILY R0 USING
(
SELECT Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(COALESCE(F.MONTANT,0)) - SUM(COALESCE(F.MONTANT_ANNULE,0)) as CA_PMU_SENEGAL
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE F.IDJEUX=J.IDJEUX
  AND F.IDTEMPS=Te.IDTEMPS
  AND F.IDJEUX=468
  AND Te.JOUR BETWEEN :date_debut AND :date_fin
GROUP BY Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_PMU_SENEGAL=R1.CA_PMU_SENEGAL""",

    # ATTENTION: La requête originale met à jour CA_MINI_SHOP. Ceci est probablement une erreur.
    # Je la reproduis telle quelle avec un commentaire. Idéalement, elle devrait cibler CA_PMU_SENEGAL dans DTM_CA si cette colonne existe.
    'merge_dtm_ca_original': """MERGE INTO user_dwhpr.dtm_ca t
USING (
    SELECT F.ANNEE ANNEE, F.MOIS MOIS, SUM(COALESCE(MONTANT,0))-SUM(COALESCE(MONTANT_ANNULE,0)) CA_MINI_SHOP
    FROM USER_DWHPR.FAIT_VENTE F, USER_DWHPR.DIM_TERMINAL Ter, USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
        AND Te.ANNEEC IN (:year_debut, :year_fin) -- year_debut et year_fin doivent être passés en paramètres
        AND F.IDJEUX=J.IDJEUX
        AND F.IDJEUX = 468
        AND F.idterminal=Ter.idterminal -- Assurez-vous que DIM_TERMINAL est aliasé Ter si c'est le cas dans la requête originale
    GROUP BY F.ANNEE , F.MOIS
) g
ON (t.annee = g.annee AND t.mois=g.mois)
WHEN MATCHED THEN UPDATE SET t.CA_MINI_SHOP = g.CA_MINI_SHOP -- Cible CA_MINI_SHOP
""",

    # Archive and cleanup temp tables
    'delete_archive_ca': """DELETE FROM OPTIWARETEMP.AR_PMUSEGAL_CA
WHERE jour IN (SELECT DISTINCT jour FROM OPTIWARETEMP.SRC_PRD_PMUSENEGAL_CA)""",
    'delete_archive_lots': """DELETE FROM OPTIWARETEMP.AR_PMUSEGAL_LOTS
WHERE jour IN (SELECT DISTINCT jour FROM OPTIWARETEMP.SRC_PRD_PMUSENEGAL_LOTS)""",
    'insert_archive_ca': """INSERT INTO OPTIWARETEMP.AR_PMUSEGAL_CA
SELECT *  FROM OPTIWARETEMP.SRC_PRD_PMUSENEGAL_CA""",
    'insert_archive_lots': """INSERT INTO OPTIWARETEMP.AR_PMUSEGAL_LOTS
SELECT * FROM OPTIWARETEMP.SRC_PRD_PMUSENEGAL_LOTS""",
    # Final Truncates are the same as initial ones
}

def get_queries():
    return QUERIES
