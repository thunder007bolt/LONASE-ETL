QUERIES = {
    # Sunubet Online data
    'truncate_temp_online': """TRUNCATE TABLE OPTIWARETEMP.src_prd_sunubet_online""",
    'insert_temp_online': """INSERT INTO OPTIWARETEMP.SRC_PRD_SUNUBET_ONLINE( "ISSUEDATETIME","STAKE", "PAIDAMOUNT","BETCATEGORYTYPE", "FREEBET") VALUES(:1, :2, :3, :4, :5)""",

    # Sunubet Casino data
    'truncate_temp_casino': """TRUNCATE TABLE OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO""",
    'insert_temp_casino': """INSERT INTO OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO("ISSUEDATETIME","STAKE", "PAIDAMOUNT") VALUES(:1, :2, :3)""",

    # Merging data into DTM_MISE_SUNUBET_ONLINE
    'merge_dtm_mise_sunubet_online_from_online': """MERGE INTO user_dwhpr.DTM_MISE_SUNUBET_ONLINE t USING
(
    SELECT
        m.idtemps AS IDTEMPS,
        m.anneec AS ANNEE,
        m.moisc AS MOIS,
        TO_CHAR(TRIM(SUBSTR(w.issuedatetime,1,10))) JOUR,
        SUM(CASE WHEN UPPER(w.FREEBET) IN ('FALSE') THEN TO_NUMBER(REGEXP_REPLACE(REPLACE(w.stake,'.',','), '[^0-9,]+', '')) ELSE 0 END) AS CA,
        UPPER(w.BetCategoryType) AS CATEGORIE,
        SUM(NVL(TO_NUMBER(REGEXP_REPLACE(REPLACE(w.PAIDAMOUNT,'.',','), '[^0-9,]+', '')),0)) AS LOT,
        0 AS MONTANT_ANNULE
    FROM optiwaretemp.src_prd_sunubet_online w ,user_dwhpr.dim_temps m
    WHERE  m.jour = TO_CHAR( TO_DATE(TRIM(SUBSTR(w.issuedatetime,1,10))),'DD/MM/YYYY')
    AND m.jour BETWEEN :date_debut AND :date_fin -- Ajout filtre de date
    GROUP BY IDTEMPS, m.anneec, m.moisc, TO_CHAR(TRIM(SUBSTR(w.issuedatetime,1,10))), UPPER(w.BetCategoryType)
) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour AND T.CATEGORIE = G.CATEGORIE)
WHEN MATCHED THEN UPDATE SET t.CA=g.CA, T.LOTS = G.LOT, t.MONTANT_ANNULE = g.MONTANT_ANNULE
WHEN NOT MATCHED THEN
INSERT (IDTEMPS,ANNEE,MOIS,JOUR,CA,LOTS,CATEGORIE,MONTANT_ANNULE)
VALUES (G.IDTEMPS, G.ANNEE,G.MOIS,G.JOUR,G.CA,G.LOT,G.CATEGORIE,g.MONTANT_ANNULE)""",

    'merge_dtm_mise_sunubet_online_from_casino': """MERGE INTO user_dwhpr.DTM_MISE_SUNUBET_ONLINE t USING
(
    SELECT
        m.idtemps AS IDTEMPS,
        m.anneec AS ANNEE,
        m.moisc AS MOIS,
        TO_CHAR(TRIM(SUBSTR(w.issuedatETIME,1,10))) JOUR, -- issuedatETIME au lieu de issuedatetime
        SUM(NVL(TO_NUMBER(REGEXP_REPLACE(REPLACE(w.stake,'.',','), '[^0-9,]+', '')),0)) AS CA,
        UPPER('CASINO') AS CATEGORIE,
        SUM(NVL(TO_NUMBER(REGEXP_REPLACE(REPLACE(w.PAIDAMOUNT,'.',','), '[^0-9,]+', '')),0)) AS LOT,
        0 AS MONTANT_ANNULE
    FROM optiwaretemp.SRC_PRD_SUNUBET_CASINO w ,user_dwhpr.dim_temps m
    WHERE  m.jour = TO_CHAR( TO_DATE(TRIM(SUBSTR(w.issuedatETIME,1,10))),'DD/MM/YYYY') -- issuedatETIME
    AND m.jour BETWEEN :date_debut AND :date_fin -- Ajout filtre de date
    GROUP BY IDTEMPS, m.anneec, m.moisc, TO_CHAR(TRIM(SUBSTR(w.issuedatETIME,1,10))) -- issuedatETIME
) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour AND T.CATEGORIE = G.CATEGORIE)
WHEN MATCHED THEN UPDATE SET t.CA=g.CA, T.LOTS = G.LOT, t.MONTANT_ANNULE = g.MONTANT_ANNULE
WHEN NOT MATCHED THEN
INSERT (IDTEMPS,ANNEE,MOIS,JOUR,CA,LOTS,CATEGORIE,MONTANT_ANNULE)
VALUES (G.IDTEMPS, G.ANNEE,G.MOIS,G.JOUR,G.CA,G.LOT,G.CATEGORIE,g.MONTANT_ANNULE)""",

    # Pas de MERGE DTM_CA_DAILY explicite pour Sunubet dans le script original,
    # les données sont aggrégées dans DTM_MISE_SUNUBET_ONLINE.
    # Les FAIT_VENTE/LOTS ne sont pas directement alimentés pour Sunubet Online/Casino
    # à partir de ces tables temporaires dans le script fourni.
}

def get_queries():
    return QUERIES
