QUERIES = {
    'truncate_temp': """TRUNCATE TABLE optiwaretemp.SRC_PRD_BWINNERS""",
    'insert_temp': """INSERT INTO optiwaretemp.SRC_PRD_BWINNERS(CREATE_TIME,PRODUCT,STAKE,"MAX PAYOUT") VALUES(:1,:2,:3,:4)""",
    'update_status_temp': """UPDATE optiwaretemp.SRC_PRD_BWINNERS SET status = 'LOST'""",
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE idjeux = 312
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE idjeux = 312
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'insert_main_fait_vente': """INSERT INTO user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            312 IDJEUX,
            CASE WHEN TO_NUMBER(REPLACE(TRIM(w.stake),'.',',')) IS NOT NULL THEN TO_NUMBER(REPLACE(TRIM(w.stake),'.',','))
                ELSE 0
            END AS MONTANT,
            0  MONTANT_ANNULE,
            NULL TICKET_EMIS,
            NULL TICKET_ANNULE,
            TO_CHAR(m.jour,'YYYY') ANNEE,
            TO_CHAR(m.jour,'MM') MOIS,
            REPLACE(m.jour,'/') JOUR

    FROM optiwaretemp.src_prd_bwinners w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m

    WHERE UPPER(TRIM(te.operateur)) = CASE WHEN UPPER(TRIM(w.product))='SN.BWINNERS.NET' THEN 'BWINNERS ONLINE' ELSE 'BWINNERS PHYSIQUE' END
        AND te.idsysteme=170
        AND m.jour = TO_DATE(w.CREATE_TIME,'DD/MM/YYYY')
)""",
    'insert_main_fait_lots': """INSERT INTO user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( SELECT
            TO_NUMBER(7181) IDVENDEUR,
            TO_NUMBER(te.idterminal) IDTERMINAL,
            TO_NUMBER(m.idtemps) IDTEMPS,
            312 IDJEUX,
            CASE WHEN TO_NUMBER(REPLACE(TRIM(w.stake),'.',',')) IS NOT NULL THEN TO_NUMBER(REPLACE(TRIM(w.stake),'.',','))
                ELSE 0
            END AS MONTANT,
            0  MONTANT_ANNULE,
            CASE WHEN TO_NUMBER(REPLACE(TRIM(w."MAX PAYOUT"),'.',',')) IS NOT NULL THEN TO_NUMBER(REPLACE(TRIM(w."MAX PAYOUT"),'.',','))
                ELSE 0
            END AS PAIEMENTS,
            TO_CHAR(m.jour,'YYYY') ANNEE,
            TO_CHAR(m.jour,'MM') MOIS,
            REPLACE(m.jour,'/') JOUR

    FROM optiwaretemp.src_prd_bwinners w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m

    WHERE UPPER(TRIM(te.operateur)) = CASE WHEN UPPER(TRIM(w.product))='SN.BWINNERS.NET' THEN 'BWINNERS ONLINE' ELSE 'BWINNERS PHYSIQUE' END
        AND m.jour = TO_DATE(w.CREATE_TIME,'DD/MM/YYYY')
)""",
    'merge_dtm_ca_daily_online': """MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_BWINNERS_ONLINE
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR BETWEEN :date_debut AND :date_fin
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 312
            AND F.idterminal=T.idterminal
            AND UPPER(TRIM(T.operateur)) LIKE 'BWINNERS ONLINE'
            AND T.idsysteme  = 170
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_BWINNERS_ONLINE=g.CA_BWINNERS_ONLINE""",
    'merge_dtm_ca_daily_physique': """MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_BWINNERS_PHYSIQUE
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR BETWEEN :date_debut AND :date_fin
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 312
            AND F.idterminal=T.idterminal
            AND UPPER(TRIM(T.operateur)) LIKE 'BWINNERS PHYSIQUE'
            AND T.idsysteme  = 170
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_BWINNERS_PHYSIQUE=g.CA_BWINNERS_PHYSIQUE""",
    'merge_dtm_mise_bwinner': """MERGE INTO user_dwhpr.DTM_MISE_BWINNER t
USING (
    SELECT F.IDTEMPS TEMPS,Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR,UPPER(TRIM(T.operateur)) OPERATEUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA, SUM(NVL(PAIEMENTS,0)) LOT
        FROM user_dwhpr.FAIT_LOTS F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR BETWEEN :date_debut AND :date_fin
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 312
            AND F.idterminal=T.idterminal
            AND T.idsysteme  = 170
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR,F.IDTEMPS, UPPER(TRIM(T.operateur))
    ) g
ON (t.annee = g.annee AND t.mois=g.mois AND t.jour=g.jour AND T.CATEGORIE = G.OPERATEUR)
WHEN MATCHED THEN UPDATE SET t.CA=g.CA, T.LOTS = G.LOT, t.MONTANT_ANNULE = 0
WHEN NOT MATCHED THEN
    INSERT (IDTEMPS,ANNEE,MOIS,JOUR,CA,LOTS,CATEGORIE,MONTANT_ANNULE)
    VALUES (G.TEMPS, G.ANNEE,G.MOIS,G.JOUR,G.CA,G.LOT,G.OPERATEUR,0)"""
}

def get_queries():
    return QUERIES
