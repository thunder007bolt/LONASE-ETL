QUERIES = {
    'truncate_temp': """DELETE FROM optiwaretemp.src_prd_zeturf""",
    'insert_temp': """INSERT INTO optiwaretemp.src_prd_zeturf("HIPPODROME","COURSE", "DEPART", "PARIS", "ENJEUX", "ANNULATIONS", "MARGE","DATE_DU_DEPART") VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""",
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE idjeux = 311
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE idjeux = 311
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'insert_main_fait_vente': """INSERT INTO user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            311 IDJEUX,
            CASE WHEN TO_NUMBER(TRIM(REPLACE(REPLACE(w.enjeux,'FCFA'),' '))) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(REPLACE(REPLACE(w.enjeux,'FCFA'),' ')))
            END AS MONTANT,
            CASE WHEN TO_NUMBER(TRIM(REPLACE(REPLACE(w.annulations,'FCFA'),' '))) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(REPLACE(REPLACE(w.annulations,'FCFA'),' ')))
            END AS MONTANT_ANNULE,
            NULL TICKET_EMIS,
            NULL TICKET_ANNULE,
            TO_CHAR(m.jour,'YYYY') ANNEE,
            TO_CHAR(m.jour,'MM') MOIS,
            REPLACE(m.jour,'/') JOUR

    FROM optiwaretemp.src_prd_zeturf w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m

    WHERE UPPER(TRIM(te.operateur)) LIKE 'ZETURF TERMINAL'
        AND te.idsysteme=169 AND TO_DATE(m.jour,'DD/MM/RR') = TO_DATE(w.DATE_DU_DEPART,'DD/MM/RR')
)""",
    'insert_main_fait_lots': """INSERT INTO user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            311 IDJEUX,
            CASE WHEN TO_NUMBER(TRIM(REPLACE(REPLACE(w.enjeux,'FCFA'),' '))) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(REPLACE(REPLACE(w.enjeux,'FCFA'),' ')))
            END AS MONTANT,
            CASE WHEN TO_NUMBER(TRIM(REPLACE(REPLACE(w.annulations,'FCFA'),' '))) IS NULL THEN 0
                ELSE TO_NUMBER(TRIM(REPLACE(REPLACE(w.annulations,'FCFA'),' ')))
            END AS MONTANT_ANNULE,
            ABS(NVL(TO_NUMBER(TRIM(REPLACE(REPLACE(w.enjeux,'FCFA'),' '))),0) - NVL(TO_NUMBER(TRIM(REPLACE(REPLACE(w.marge,'FCFA'),' '))),0)) PAIEMENTS,
            TO_CHAR(m.jour,'YYYY') ANNEE,
            TO_CHAR(m.jour,'MM') MOIS,
            REPLACE(m.jour,'/') JOUR

    FROM optiwaretemp.src_prd_zeturf w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m

    WHERE UPPER(TRIM(te.operateur)) LIKE 'ZETURF TERMINAL'
        AND te.idsysteme=169 AND TO_DATE(m.jour,'DD/MM/RR') = TO_DATE(w.DATE_DU_DEPART,'DD/MM/RR')
)""",
    'merge_dtm_ca_daily': """MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_ZETURF
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR BETWEEN :date_debut AND :date_fin
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 311
            AND F.idterminal=T.idterminal
            AND T.idsysteme  = 169
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_ZETURF=g.CA_ZETURF"""
}

def get_queries():
    return QUERIES
