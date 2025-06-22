QUERIES = {
    'truncate_temp': """DELETE FROM optiwaretemp.src_prd_lonasebet""",
    'insert_temp': """INSERT INTO OPTIWARETEMP.src_prd_lonasebet( "ID","ISSUEDATETIME","STAKE","BETCATEGORYTYPE","STATE","PAIDAMOUNT","CUSTOMERLOGIN","FREEBET") VALUES(:1, :2, :3, :4, :5, :6,:7,:8)""",
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE IDJEUX IN (25,27,467) -- ALR, Parifoot, Virtuel Lonasebet
AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 167)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE IDJEUX IN (25,27,467) -- ALR, Parifoot, Virtuel Lonasebet
AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 167)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'insert_main_fait_vente': """INSERT INTO user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            CASE
                WHEN UPPER(w.betcategorytype) LIKE '%SPORTS%' THEN 27
                WHEN UPPER(w.betcategorytype) LIKE '%HORSERACING%' THEN 25
                WHEN UPPER(w.betcategorytype) LIKE '%VIRTUAL%' THEN 467
            END AS IDJEUX,
            CASE WHEN UPPER(TRIM(w.freebet)) IN ('FALSE') THEN TO_NUMBER(TRIM(REPLACE(w.stake,'.',','))) ELSE 0 END AS MONTANT,
            0 AS MONTANT_ANNULE,
            NULL TICKET_EMIS,
            NULL TICKET_ANNULE,
            TO_CHAR(TO_DATE(TRIM(SUBSTR(w.issuedatetime,1,10)),'DD/MM/YYYY'),'YYYY') ANNEE,
            TO_CHAR(TO_DATE(TRIM(SUBSTR(w.issuedatetime,1,10)),'DD/MM/YYYY'),'MM')MOIS,
            REPLACE(TRIM(SUBSTR(w.issuedatetime,1,10)),'/','') JOUR
    FROM optiwaretemp.src_prd_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    WHERE UPPER(TRIM(te.operateur)) = UPPER(TRIM(w.betcategorytype)) AND te.idsysteme=167
        AND m.jour = TO_CHAR( TO_DATE(TRIM(SUBSTR(w.issuedatetime,1,10))),'DD/MM/YYYY')
)""",
    'insert_main_fait_lots': """INSERT INTO user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            CASE
                WHEN UPPER(w.betcategorytype) LIKE '%SPORTS%' THEN 27
                WHEN UPPER(w.betcategorytype) LIKE '%HORSERACING%' THEN 25
                WHEN UPPER(w.betcategorytype) LIKE '%VIRTUAL%' THEN 467
            END AS IDJEUX,
            CASE WHEN UPPER(TRIM(w.freebet)) IN ('FALSE') THEN TO_NUMBER(TRIM(REPLACE(w.stake,'.',','))) ELSE 0 END AS MONTANT,
            0 AS MONTANT_ANNULE,
            CASE WHEN w.paidamount IS NULL THEN 0 ELSE TO_NUMBER(TRIM(REPLACE(w.paidamount,'.',','))) END AS PAIEMENTS,
            TO_CHAR(TO_DATE(TRIM(SUBSTR(w.issuedatetime,1,10)),'DD/MM/YYYY'),'YYYY') ANNEE,
            TO_CHAR(TO_DATE(TRIM(SUBSTR(w.issuedatetime,1,10)),'DD/MM/YYYY'),'MM')MOIS,
            REPLACE(TRIM(SUBSTR(w.issuedatetime,1,10)),'/','') JOUR
    FROM optiwaretemp.src_prd_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    WHERE UPPER(TRIM(te.operateur)) = UPPER(TRIM(w.betcategorytype)) AND te.idsysteme=167
        AND m.jour = TO_CHAR( TO_DATE(TRIM(SUBSTR(w.issuedatetime,1,10))),'DD/MM/YYYY')
)""",
    'cleanup_temp': """DELETE FROM optiwaretemp.src_prd_lonasebet""",
    'merge_dtm_ca_daily_alr': """MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(MONTANT)-SUM(MONTANT_ANNULE) CA_ALR_LONASEBET
        FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS AND F.IDJEUX=J.IDJEUX AND Te.JOUR BETWEEN :date_debut AND :date_fin
        AND F.IDJEUX=25 AND F.idterminal IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 167)
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_ALR_LONASEBET=g.CA_ALR_LONASEBET""",
    'merge_dtm_ca_daily_parifoot': """MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(MONTANT)-SUM(MONTANT_ANNULE) CA_PARIFOOT_LONASEBET
        FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS AND F.IDJEUX=J.IDJEUX AND Te.JOUR BETWEEN :date_debut AND :date_fin
        AND F.IDJEUX=27 AND F.idterminal IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 167)
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_PARIFOOT_LONASEBET=g.CA_PARIFOOT_LONASEBET""",
    'merge_dtm_ca_daily_virtuel': """MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(MONTANT)-SUM(MONTANT_ANNULE) CA_LONASEBET_VIRTUEL
        FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS AND F.IDJEUX=J.IDJEUX AND Te.JOUR BETWEEN :date_debut AND :date_fin
        AND F.IDJEUX=467 AND F.idterminal IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 167)
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_LONASEBET_VIRTUEL=g.CA_LONASEBET_VIRTUEL""",
    'merge_dtm_ca_virtuel': """MERGE INTO user_dwhpr.dtm_ca t
    USING (
              SELECT F.ANNEE ANNEE, F.MOIS MOIS, SUM(COALESCE(MONTANT,0))-SUM(COALESCE(MONTANT_ANNULE,0)) CA_LONASEBET_VIRTUEL
              FROM USER_DWHPR.FAIT_VENTE F, USER_DWHPR.DIM_TERMINAL T,USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
              WHERE Te.IDTEMPS=F.IDTEMPS
                      AND Te.ANNEEC IN (:year_debut, :year_fin)
                      AND F.IDJEUX=J.IDJEUX AND F.IDJEUX = 467
                      AND F.idterminal=T.idterminal AND T.idsysteme = 167
              GROUP BY F.ANNEE , F.MOIS
           ) g
    ON (t.annee = g.annee AND t.mois=g.mois)
    WHEN MATCHED THEN UPDATE SET t.CA_LONASEBET_VIRTUEL= g.CA_LONASEBET_VIRTUEL"""
}

def get_queries():
    return QUERIES
