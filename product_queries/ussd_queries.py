QUERIES = {
    'truncate_temp': """TRUNCATE TABLE optiwaretemp.TEMP_USSD_IVR""",
    'insert_temp': """INSERT INTO optiwaretemp.TEMP_USSD_IVR("DATEAPPEL","JOUR","NUMEROSERVEUR","NUMEROAPPELANT","DUREEAPPEL","TOTALAPPELS","TOTALCA") VALUES(:1, :2, :3, :4, :5, :6, :7)""",
    'insert_dim_terminal': """INSERT INTO USER_DWHPR.DIM_TERMINAL(IDCCS,OPERATEUR,STATUT,IDSYSTEME)
    SELECT  389 IDCCS, OPERATEUR, '' STATUT, 175 IDSYSTEME
        FROM (
                   SELECT DISTINCT NumeroServeur OPERATEUR
                    FROM OPTIWARETEMP.TEMP_USSD_IVR
                   WHERE NumeroServeur NOT IN (SELECT OPERATEUR FROM USER_DWHPR.DIM_TERMINAL WHERE IDSYSTEME=175)
             ) S""", # Removed DIM_CCS join as it's not strictly necessary if IDCCS is fixed
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
    WHERE IDJEUX = 471
    AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 175)
    AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
    WHERE IDJEUX = 471
    AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 175)
    AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'insert_main_fait_vente': """INSERT INTO USER_DWHPR.FAIT_VENTE(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
    SELECT  7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, 471 IDJEUX, MONTANT, 0 MONTANT_ANNULE,
       '' TICKET_EMIS, '' TICKET_ANNULE, TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, Te.JOUR
    FROM (
	    SELECT NumeroServeur AS Operateur , TO_DATE(JOUR,'DD/MM/YYYY') JOUR, TO_NUMBER(TRIM(REPLACE(REPLACE(TOTALCA,'.',','),' ',''))) Montant
		FROM OPTIWARETEMP.TEMP_USSD_IVR
    ) F, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te
    WHERE T.OPERATEUR = F.Operateur AND T.IDSYSTEME=175 AND TO_DATE(Te.JOUR,'DD/MM/YY')=F.JOUR""",
    'insert_main_fait_lots': """INSERT INTO USER_DWHPR.FAIT_LOTS(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
    SELECT  7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS, 471 IDJEUX, MONTANT, 0 MONTANT_ANNULE, 0 PAIEMENTS,
		TO_CHAR(Te.JOUR,'YYYY') ANNEE, TO_CHAR(Te.JOUR,'MM') MOIS, Te.JOUR
    FROM (
	    SELECT NumeroServeur AS Operateur , TO_DATE(JOUR,'DD/MM/YYYY') JOUR, TO_NUMBER(TRIM(REPLACE(REPLACE(TOTALCA,'.',','),' ',''))) Montant
		FROM OPTIWARETEMP.TEMP_USSD_IVR
    ) F, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te
    WHERE UPPER(TRIM(T.OPERATEUR ))= UPPER(TRIM(F.Operateur)) AND T.IDSYSTEME=175
    AND TO_DATE(Te.JOUR,'DD/MM/YY')=F.JOUR""",
    'merge_dtm_ca_daily': """MERGE INTO user_dwhpr.dtm_ca_daily t
    USING (
       SELECT Te.ANNEEC AS ANNEE, Te.MOISC AS MOIS, Te.JOUR,
              SUM(NVL(F.MONTANT, 0)) - SUM(NVL(F.MONTANT_ANNULE, 0)) AS CA_USSD
         FROM user_dwhpr.FAIT_VENTE F
         JOIN user_dwhpr.DIM_TERMINAL T ON F.idterminal = T.idterminal
         JOIN user_dwhpr.DIM_TEMPS Te ON Te.IDTEMPS = F.IDTEMPS
         JOIN user_dwhpr.DIM_JEUX J ON F.IDJEUX = J.IDJEUX
         WHERE Te.ANNEEC = :current_year AND F.IDJEUX = 471 AND T.IDSYSTEME = 175
         AND Te.JOUR BETWEEN :date_debut AND :date_fin -- Ajout filtre date
        GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
    ON (t.annee = g.annee AND t.mois = g.mois AND t.jour = g.jour)
    WHEN MATCHED THEN UPDATE SET t.CA_USSD = g.CA_USSD""",
    'merge_dtm_ca': """MERGE INTO user_dwhpr.dtm_ca t
    USING (
       SELECT F.ANNEE AS ANNEE, F.MOIS AS MOIS,
              SUM(NVL(F.MONTANT, 0)) - SUM(NVL(F.MONTANT_ANNULE, 0)) AS CA_USSD
         FROM user_dwhpr.FAIT_VENTE F
         JOIN user_dwhpr.DIM_TERMINAL T ON F.idterminal = T.idterminal
         JOIN user_dwhpr.DIM_TEMPS Te ON Te.IDTEMPS = F.IDTEMPS
         JOIN user_dwhpr.DIM_JEUX J ON F.IDJEUX = J.IDJEUX
        WHERE Te.ANNEEC = :current_year AND F.IDJEUX = 471 AND T.IDSYSTEME = 175
        -- Pas de filtre de date sur dtm_ca, il agrège sur l'année/mois
        GROUP BY F.ANNEE, F.MOIS
     ) g
     ON (t.annee = g.annee AND t.mois = g.mois)
     WHEN MATCHED THEN UPDATE SET t.CA_USSD = g.CA_USSD""",
    'delete_ar_ussd_ivr': """DELETE FROM OPTIWARETEMP.AR_USSD_IVR WHERE jour IN (SELECT DISTINCT jour FROM OPTIWARETEMP.TEMP_USSD_IVR)""",
    'insert_ar_ussd_ivr': """INSERT INTO OPTIWARETEMP.AR_USSD_IVR SELECT * FROM OPTIWARETEMP.TEMP_USSD_IVR"""
}

def get_queries():
    return QUERIES
