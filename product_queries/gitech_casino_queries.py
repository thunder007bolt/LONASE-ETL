QUERIES = {
    'truncate_temp': """TRUNCATE TABLE OPTIWARETEMP.src_prd_casino_gitech""", # Le script original truncate GITECH, mais insère dans src_prd_casino_gitech
    'insert_temp': """INSERT INTO OPTIWARETEMP.src_prd_casino_gitech( "IDJEU","NOMJEU","DATEVENTE","VENTE","PAIEMENT","POURCENTAGEPAIEMENT") VALUES(:1, :2, :3, :4, :5, :6)""",
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE IDJEUX = 316
AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 81) -- Casino Gitech utilise idsysteme 81
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE IDJEUX = 316
AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 81) -- Casino Gitech utilise idsysteme 81
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'insert_main_fait_vente': """INSERT INTO user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            316 IDJEUX,
            CASE WHEN TO_NUMBER(TRIM(w.vente)) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(w.vente))
            END AS MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS,
            0 TICKET_ANNULE,
            TO_CHAR(m.jour,'YYYY') ANNEE,
            TO_CHAR(m.jour,'MM') MOIS,
            REPLACE(m.jour,'/') JOUR
    FROM optiwaretemp.src_prd_casino_gitech w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    WHERE UPPER(TRIM(te.operateur)) LIKE 'CASINO GITECH'
        AND te.idsysteme=81 AND TO_DATE(m.jour,'DD/MM/RR') = TO_DATE(w.DATEVENTE,'DD/MM/RR')
)""",
    'insert_main_fait_lots': """INSERT INTO user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            316 IDJEUX,
            CASE WHEN TO_NUMBER(TRIM(w.vente)) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(w.vente))
            END AS MONTANT,
            0 MONTANT_ANNULE,
            CASE WHEN TO_NUMBER(TRIM(w.PAIEMENT)) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(w.PAIEMENT))
            END AS PAIEMENTS,
            TO_CHAR(m.jour,'YYYY') ANNEE,
            TO_CHAR(m.jour,'MM') MOIS,
            REPLACE(m.jour,'/') JOUR
    FROM optiwaretemp.src_prd_casino_gitech w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    WHERE UPPER(TRIM(te.operateur)) LIKE 'CASINO GITECH'
        AND te.idsysteme=81 AND TO_DATE(m.jour,'DD/MM/RR') = TO_DATE(w.DATEVENTE,'DD/MM/RR')
)""",
    'cleanup_temp': """DELETE FROM optiwaretemp.src_prd_casino_gitech""",
    'merge_dtm_ca_daily': """MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_CASINO_GITECH
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR BETWEEN :date_debut AND :date_fin
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 316
            AND F.idterminal=T.idterminal
            AND T.idsysteme  = 81
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_CASINO_GITECH=g.CA_CASINO_GITECH"""
}

def get_queries():
    return QUERIES
