QUERIES = {
    # Financial data
    'truncate_temp_financial': """TRUNCATE TABLE optiwaretemp.GLOB_FINANCIAL""",
    'insert_temp_financial': """INSERT INTO optiwaretemp.GLOB_FINANCIAL("Name","Total_In", "Total_Out", "DATE", "Reversal","Currency") VALUES(:1,:2,:3,:4,:5,:6)""",

    # Zone Betting data
    'truncate_temp_zone_betting': """TRUNCATE TABLE optiwaretemp.GLOB_ZONE_BETTING""",
    'insert_temp_zone_betting': """INSERT INTO optiwaretemp.GLOB_ZONE_BETTING("Shop name","Date", "CANCELLED", "STAKE", "WON") VALUES(:1,:2,:3,:4,:5)""",

    # PremierSN (GLOB_SB_VDR) data
    'truncate_temp_sb_vdr': """TRUNCATE TABLE optiwaretemp.GLOB_SB_VDR""",
    'insert_temp_sb_vdr': """INSERT INTO optiwaretemp.GLOB_SB_VDR("Outlet","Reported", "Sales", "Redeems", "Voided") VALUES(:1,:2,:3,:4,:5)""",

    # Main processing queries
    'delete_main_fait_vente': """DELETE FROM user_dwhpr.fait_vente
WHERE idjeux = 124
AND IDTERMINAL IN (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL WHERE IDSYSTEME = 2)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots': """DELETE FROM user_dwhpr.fait_lots
WHERE idjeux = 124
AND IDTERMINAL IN (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL WHERE IDSYSTEME = 2)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",

    'insert_dim_terminal': """INSERT INTO dim_terminal
SELECT DISTINCT '',241,MAGASIN,'',2 FROM
(
    SELECT "Name" AS Magasin,"DATE" AS DATE_VENTE,
    (CASE WHEN ("Total_In") LIKE '%,%'
    THEN  (REPLACE (("Total_In") ,'.')) ELSE ("Total_In") END)  AS VENTE,
    (CASE WHEN ("Reversal") LIKE '%,%'
    THEN  (REPLACE (("Reversal") ,'.')) ELSE ("Reversal") END)  AS annulation
    FROM optiwaretemp.GLOB_FINANCIAL WHERE "Currency" LIKE 'XOF'
    UNION ALL
    SELECT "Outlet","Reported","Sales","Voided" FROM  optiwaretemp.GLOB_SB_VDR
    UNION ALL
    /* select "Shop_name",DATE_VENTE, "Placed_bets_amount","Cancelled_paid_amount" from  optiwaretemp.GLOB_OVERALL */ -- GLOB_OVERALL n'est pas chargé explicitement dans le script principal fourni
    SELECT "Shop name" MAGASIN, "Date" DATE_VENTE, STAKE, REPLACE(CANCELLED,'.',',') ANNULATION
    FROM OPTIWARETEMP.GLOB_ZONE_BETTING
) L
WHERE L.MAGASIN NOT IN (SELECT DISTINCT operateur FROM dim_terminal WHERE idsysteme=2 OR idsysteme IS NULL)""",

    'insert_main_fait_vente': """INSERT INTO USER_DWHPR.fait_vente
(SELECT '',7781,t.idterminal idterminal,te.idtemps idtemps,124 idjeux,
TO_NUMBER(TRIM(REPLACE(REPLACE(L.VENTE,' '),'.00'))) AS vente ,
TO_NUMBER(TRIM(REPLACE(REPLACE( L.ANNULATION,' '),'.00'))) AS annulation,
0,0,TO_CHAR(te.jour,'yyyy') AS annee,TO_CHAR(te.jour,'mm') AS mois, te.jour
FROM (
        SELECT "Name" AS MAGASIN ,"DATE" AS DATE_VENTE,
            (CASE WHEN ("Total_In") LIKE '%,%' THEN  TO_NUMBER(REPLACE (("Total_In") ,'.')) ELSE  TO_NUMBER(REPLACE(("Total_In"),'.',',')) END)  AS VENTE,
            (CASE WHEN ("Reversal") LIKE '%,%' THEN  TO_NUMBER(REPLACE (("Reversal") ,'.')) ELSE  TO_NUMBER(REPLACE(("Reversal"),'.',',')) END)  AS annulation
        FROM optiwaretemp.GLOB_FINANCIAL WHERE "Currency" LIKE 'XOF'
    UNION ALL
    SELECT "Outlet" AS Magasin
            ,"Reported" AS DATE_VENTE
            ,TO_NUMBER(REPLACE("Sales",'.',',')) AS VENTE
            ,TO_NUMBER(REPLACE("Voided",'.',',')) AS annulation
    FROM  optiwaretemp.GLOB_SB_VDR
    UNION ALL
    SELECT "Shop name" MAGASIN, "Date" DATE_VENTE, TO_NUMBER(REPLACE(STAKE,'.',',')) VENTE, TO_NUMBER(REPLACE(CANCELLED,'.',',')) ANNULATION
    FROM OPTIWARETEMP.GLOB_ZONE_BETTING
) L, dim_terminal t, dim_temps te
WHERE (TRIM(L.magasin)) = (TRIM(t.operateur)) AND TO_DATE(L.DATE_VENTE,'dd/mm/yy')=TO_DATE(te.jour,'dd/mm/yy')
AND t.idsysteme=2 AND (L.magasin) NOT LIKE ('%Senegal%') AND Magasin NOT LIKE '%test%')""",

    'insert_main_fait_lots': """INSERT INTO USER_DWHPR.fait_lots
(
    SELECT '' IDLOTS
        ,7781 AS idvendeur
        ,t.idterminal
        ,te.idtemps
        ,124 AS idjeux
        , L.VENTE AS montant
        , L.ANNULATION AS montant_annule
        , paiements
        ,TO_CHAR(te.jour,'yyyy') AS annee
        ,TO_CHAR(te.jour,'mm') AS mois
        ,TO_CHAR(te.jour) AS jour
FROM (
        SELECT "Name" AS MAGASIN ,
            "DATE" AS DATE_VENTE,
            (CASE WHEN ("Total_In") LIKE '%,%' THEN  TO_NUMBER(REPLACE (("Total_In") ,'.')) ELSE TO_NUMBER(REPLACE(("Total_In"),'.',',')) END)  AS VENTE,
            (CASE WHEN ("Reversal") LIKE '%,%' THEN  TO_NUMBER(REPLACE (("Reversal") ,'.')) ELSE TO_NUMBER(REPLACE(("Reversal"),'.',',')) END)  AS annulation,
            TO_NUMBER(REPLACE("Total_Out",'.',',')) AS paiements
        FROM optiwaretemp.GLOB_FINANCIAL WHERE "Currency" LIKE 'XOF'
        UNION ALL
        SELECT "Outlet" AS Magasin
                ,"Reported" AS DATE_VENTE
                ,TO_NUMBER(REPLACE("Sales",'.',',')) AS VENTE
                ,TO_NUMBER(REPLACE("Voided",'.',',')) AS annulation
                ,TO_NUMBER(REPLACE("Redeems",'.',','))-TO_NUMBER(REPLACE("Voided",'.',',')) AS paiements
        FROM  optiwaretemp.GLOB_SB_VDR
        UNION ALL
        SELECT "Shop name" MAGASIN,
                "Date" DATE_VENTE,
                TO_NUMBER(REPLACE(STAKE,'.',',')) VENTE,
                TO_NUMBER(REPLACE(CANCELLED,'.',',')) ANNULATION,
                TO_NUMBER(REPLACE(WON,'.',',')) PAIEMENTS
        FROM OPTIWARETEMP.GLOB_ZONE_BETTING
    ) L, dim_terminal t, dim_temps te
WHERE (TRIM(L.magasin)) = (TRIM(t.operateur)) AND TO_DATE(L.DATE_VENTE,'dd/mm/yy')=TO_DATE(te.jour,'dd/mm/yy')
AND t.idsysteme=2 AND L.magasin NOT LIKE ('%Senegal%') AND L.magasin NOT LIKE '%test%'
)""",

    'merge_dtm_ca_daily': """MERGE INTO DTM_CA_DAILY R0 USING
(
    SELECT Te.ANNEEC,Te.MOISC,Te.JOUR
        , CASE WHEN Te.IDTEMPS>=7945 THEN (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE))*3/100
            ELSE (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE)) END AS CA_VIRTUELS_EDITEC
    FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
    WHERE  F.IDJEUX=J.IDJEUX
    AND Te.JOUR BETWEEN :date_debut AND :date_fin
    AND F.IDTEMPS=Te.IDTEMPS
    AND F.IDJEUX=124
    GROUP BY Te.ANNEEC,Te.MOISC,Te.JOUR,Te.IDTEMPS
) R1
ON ( R0.ANNEE = R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_VIRTUELS_EDITEC=R1.CA_VIRTUELS_EDITEC""",

    'truncate_temp_zone_betting_final': """TRUNCATE TABLE OPTIWARETEMP.GLOB_ZONE_BETTING""",
    'truncate_temp_financial_final': """TRUNCATE TABLE optiwaretemp.GLOB_FINANCIAL""",
    'truncate_temp_sb_vdr_final': """TRUNCATE TABLE optiwaretemp.GLOB_SB_VDR"""
}

def get_queries():
    return QUERIES
