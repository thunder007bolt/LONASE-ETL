QUERIES = {
    'truncate_temp': """DELETE FROM optiwaretemp.SRC_PRD_CASINO_LONASEBET""",
    'insert_temp': """INSERT INTO optiwaretemp.SRC_PRD_CASINO_LONASEBET(DATE_VENTE,MISE_TOTALE, SOMME_PAYEE) VALUES(:1,:2,:3)""",
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE idjeux = 316
AND IDTERMINAL IN (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL WHERE IDSYSTEME = 167) -- Casino Lonasebet utilise idsysteme 167
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE idjeux = 316
AND IDTERMINAL IN (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL WHERE IDSYSTEME = 167) -- Casino Lonasebet utilise idsysteme 167
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'insert_main_fait_vente': """INSERT INTO user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            316 IDJEUX,
            CASE WHEN TO_NUMBER(TRIM(REPLACE(REPLACE(w.MISE_TOTALE,'XOF'),' '))) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(REPLACE(REPLACE(w.MISE_TOTALE,'XOF'),' ')))
            END AS MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS,
            0 TICKET_ANNULE,
            TO_CHAR(m.jour,'YYYY') ANNEE,
            TO_CHAR(m.jour,'MM') MOIS,
            REPLACE(m.jour,'/') JOUR
    FROM optiwaretemp.src_prd_casino_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    WHERE UPPER(TRIM(te.operateur)) LIKE 'CASINO LONASEBET'
        AND te.idsysteme=167 AND TO_DATE(m.jour,'DD/MM/RR') = TO_DATE(w.DATE_VENTE,'DD/MM/RR')
)""",
    'insert_main_fait_lots': """INSERT INTO user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            316 IDJEUX,
            CASE WHEN TO_NUMBER(TRIM(REPLACE(REPLACE(w.MISE_TOTALE,'XOF'),' '))) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(REPLACE(REPLACE(w.MISE_TOTALE,'XOF'),' ')))
            END AS MONTANT,
            0 MONTANT_ANNULE,
            CASE WHEN TO_NUMBER(TRIM(REPLACE(REPLACE(w.SOMME_PAYEE,'XOF'),' '))) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(REPLACE(REPLACE(w.SOMME_PAYEE,'XOF'),' ')))
            END AS PAIEMENTS,
            TO_CHAR(m.jour,'YYYY') ANNEE,
            TO_CHAR(m.jour,'MM') MOIS,
            REPLACE(m.jour,'/') JOUR
    FROM optiwaretemp.src_prd_casino_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    WHERE UPPER(TRIM(te.operateur)) LIKE 'CASINO LONASEBET'
        AND te.idsysteme=167 AND TO_DATE(m.jour,'DD/MM/RR') = TO_DATE(w.DATE_VENTE,'DD/MM/YYYY') -- Attention YYYY ici
)""",
    'merge_dtm_ca_daily': """MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_CASINO_LONASEBET
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR BETWEEN :date_debut AND :date_fin
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 316
            AND F.idterminal=T.idterminal
            AND T.idsysteme  = 167
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_CASINO_LONASEBET=g.CA_CASINO_LONASEBET""",
    'cleanup_temp': """DELETE FROM optiwaretemp.SRC_PRD_CASINO_LONASEBET"""
}

def get_queries():
    return QUERIES
