QUERIES = {
    'truncate_temp': """DELETE FROM optiwaretemp.SRC_PRD_SUNUBET""", # Note: Uses SRC_PRD_SUNUBET table
    'insert_temp': """INSERT INTO optiwaretemp.SRC_PRD_SUNUBET("NOM", "Total enjeu", "Total Ticket Virtuel", "Total Paiement","Date Vente") VALUES(:1,:2,:3,:4,:5)""",
    'insert_dim_terminal': """INSERT INTO "USER_DWHPR"."DIM_TERMINAL"
SELECT DISTINCT '' IDTERMINAL, 241 IDCCS, NOM AS OPERATEURS, '' STATUT, 141 IDSYSTEME
    FROM OPTIWARETEMP.SRC_PRD_SUNUBET
    WHERE TRIM(NOM) NOT IN (SELECT OPERATEUR FROM DIM_TERMINAL WHERE IDSYSTEME=141)
    ORDER BY SUBSTR(REPLACE(NOM,' ',''),INSTR(REPLACE(NOM,' ',''),'(')+1,7)""",
    'update_temp_annulations': """UPDATE optiwaretemp.SRC_PRD_SUNUBET SET "Total annulation" = '0'""",
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE idjeux = 261
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE idjeux = 261
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'insert_main_fait_vente': """INSERT INTO "USER_DWHPR"."FAIT_VENTE"
SELECT   '' AS IDVENTE,
        (SELECT IDVENDEUR FROM "USER_DWHPR"."DIM_VENDEUR") AS IDVENDEUR,
        SRC.IDTERMINAL,
        SRC.IDTEMPS,
        J.IDJEUX,
        SRC.MONTANT,
        SRC.MONTANT_ANNULE,
        SRC.TICKET_EMIS,
        SRC.TICKET_ANNULE,
        TRIM(TO_CHAR(SRC.JOUR,'yyyy')) AS ANNEE,
        TRIM(TO_CHAR(SRC.JOUR,'mm')) AS MOIS,
        TRIM(TO_CHAR(SRC.JOUR,'ddmmyyyy')) AS JOUR
    FROM (
            SELECT
                Te.IDTEMPS,
                S."Total enjeu" AS MONTANT,
                T.IDTERMINAL,Te.JOUR,
                S."Total annulation" AS MONTANT_ANNULE,
                S."Total Ticket Virtuel" AS TICKET_EMIS,
                '' AS TICKET_ANNULE,
                'VIRTUEL AMABEL' PRODUIT
            FROM "OPTIWARETEMP"."SRC_PRD_SUNUBET" S,  "USER_DWHPR"."DIM_TEMPS" Te ,USER_DWHPR.DIM_TERMINAL T
            WHERE  T.OPERATEUR=S.NOM
            AND IDSYSTEME= 141
            AND Te.JOUR=TO_DATE(S."Date Vente",'DD/MM/RR')
        ) SRC , "USER_DWHPR"."DIM_JEUX" J
    WHERE J.IDJEUX=261
    AND UPPER(J.LIBELLEJEUX)=UPPER(SRC.PRODUIT)
    AND UPPER(SRC.PRODUIT)='VIRTUEL AMABEL'""",
    'insert_main_fait_lots': """INSERT INTO FAIT_LOTS
SELECT   '' AS IDLOTS,
        (SELECT IDVENDEUR FROM "USER_DWHPR"."DIM_VENDEUR") AS IDVENDEUR,
        SRC.IDTERMINAL,
        SRC.IDTEMPS,
        J.IDJEUX,
        SRC.MONTANT,
        SRC.MONTANT_ANNULE,
        SRC.PAIEMENTS,
        TRIM(TO_CHAR(SRC.JOUR,'yyyy')) AS ANNEE,
        TRIM(TO_CHAR(SRC.JOUR,'mm')) AS MOIS,
        TRIM(TO_CHAR(SRC.JOUR,'ddmmyyyy')) AS JOUR
    FROM (
            SELECT
                Te.IDTEMPS,
                S."Total enjeu" AS MONTANT,
                T.IDTERMINAL,Te.JOUR,
                S."Total annulation" AS MONTANT_ANNULE,
                S."Total Paiement" AS PAIEMENTS,
                'VIRTUEL AMABEL' PRODUIT
            FROM "OPTIWARETEMP"."SRC_PRD_SUNUBET" S,  "USER_DWHPR"."DIM_TEMPS" Te ,USER_DWHPR.DIM_TERMINAL T
            WHERE  T.OPERATEUR=S.NOM
            AND IDSYSTEME= 141
            AND Te.JOUR=TO_DATE(S."Date Vente",'DD/MM/RR')
        ) SRC , "USER_DWHPR"."DIM_JEUX" J
    WHERE J.IDJEUX=261
    AND UPPER(J.LIBELLEJEUX)=UPPER(SRC.PRODUIT)
    AND UPPER(SRC.PRODUIT)='VIRTUEL AMABEL'""",
    'merge_dtm_ca_daily': """MERGE INTO DTM_CA_DAILY R0 USING
(
    SELECT Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) AS CA_VIRTUEL_AMABEL
    FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
    WHERE F.IDJEUX=J.IDJEUX
    AND F.IDTEMPS=Te.IDTEMPS
    AND F.IDJEUX=261
    AND Te.JOUR BETWEEN :date_debut AND :date_fin
    GROUP BY Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_VIRTUEL_AMABEL=R1.CA_VIRTUEL_AMABEL""",
    'delete_ar_sunubet_prd': """DELETE
    FROM OPTIWARETEMP.AR_SUNUBET_PRD
    WHERE  "Date Vente" IN (
                                SELECT DISTINCT "Date Vente"
                                FROM OPTIWARETEMP.SRC_PRD_SUNUBET
                            )""",
    'insert_ar_sunubet_prd': """INSERT INTO OPTIWARETEMP.AR_SUNUBET_PRD
SELECT *
    FROM OPTIWARETEMP.SRC_PRD_SUNUBET"""
}

def get_queries():
    return QUERIES
