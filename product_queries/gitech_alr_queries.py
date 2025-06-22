QUERIES = {
    'truncate_temp': """TRUNCATE TABLE OPTIWARETEMP.GITECH""",
    'insert_temp': """INSERT INTO OPTIWARETEMP.GITECH( "Agences","Operateurs","date_de_vente","Recette_CFA","Annulation_CFA","Paiements_CFA") VALUES(:1, :2, :3, :4, :5, :6)""",

    # ALR Gitech (IDJEUX = 25, IDSYSTEME = 81)
    'delete_main_fait_vente_alr': """DELETE FROM user_dwhpr.fait_vente
WHERE IDJEUX = 25
AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 81)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots_alr': """DELETE FROM user_dwhpr.fait_lots
WHERE IDJEUX = 25
AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 81)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",

    # PMU Online (IDJEUX = 223, IDSYSTEME = 123) - Semble être un autre type de produit Gitech
    'delete_main_fait_vente_pmu_online': """DELETE FROM user_dwhpr.fait_vente
WHERE IDJEUX = 223
AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 123)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",
    'delete_main_fait_lots_pmu_online': """DELETE FROM user_dwhpr.fait_lots
WHERE IDJEUX = 223
AND IDTERMINAL IN (SELECT idterminal FROM user_dwhpr.dim_terminal WHERE idsysteme = 123)
AND idtemps IN (SELECT idtemps FROM user_dwhpr.dim_temps WHERE jour BETWEEN :date_debut AND :date_fin )""",

    'insert_dim_terminal_gitech': """
    INSERT INTO dim_terminal
    SELECT DISTINCT '' idterminal, c.idccs,operateurs,'' statut,81 idsysteme FROM
    ( SELECT CASE
        WHEN "Agences" LIKE 'KOLDA' THEN 'ZIGUINCHOR'
        WHEN "Agences" LIKE 'TAMBACOUNDA' THEN 'TAMBA'
        WHEN "Agences" LIKE 'MATAM' THEN 'TAMBA'
        WHEN "Agences" LIKE 'MBACKE' THEN 'DIOURBEL'
        WHEN "Agences" LIKE 'SAINT LOUIS' THEN 'SAINT-LOUIS'
        WHEN "Agences" LIKE 'RICHARD TOLL' THEN 'SAINT-LOUIS'
        WHEN "Agences" LIKE 'FATICK' THEN 'KAOLACK'
        WHEN "Agences" LIKE 'BAMBEY' THEN 'DIOURBEL'
        WHEN "Agences" LIKE 'KAFFRINE' THEN 'KAOLACK'
        WHEN "Agences" LIKE 'KEDOUGOU' THEN 'TAMBA'
        WHEN "Agences" LIKE 'Lonase Head Office' THEN 'INCONNU'
        ELSE "Agences"
      END AS agences, "Operateurs" AS operateurs
      FROM optiwaretemp.gitech
    ) s ,dim_ccs c
    WHERE UPPER(TRIM(s.agences))= UPPER(TRIM(nomccs))
      AND s.operateurs NOT IN (SELECT DISTINCT operateur FROM dim_terminal WHERE idsysteme=81)
    """, # IDSYSTEME 123 pour PMU Online n'est pas géré ici, il faut peut-être une autre requête ou une logique adaptée
        # si PMU Online utilise les mêmes "Operateurs" mais un IDSYSTEME différent.
        # Le script original ne semble pas insérer de terminaux pour PMU Online (idsysteme=123) de cette manière.

    'insert_main_fait_vente_alr': """INSERT INTO fait_vente
SELECT '',7181 AS idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" AS montant_annule,
0 AS ticket_emis,0 AS ticket_annule,TO_CHAR(te.jour,'yyyy') AS annee,
TO_CHAR(jour,'mm') AS mois,te.jour
FROM optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
WHERE s."Operateurs"=t.operateur AND t.idsysteme=81
AND j.libellejeux='ALR' AND TO_DATE(s."date_de_vente",'dd/mm/yy')=TO_DATE(te.jour,'dd/mm/yy')""",

    'insert_main_fait_vente_pmu_online': """INSERT INTO fait_vente
SELECT '',7181 AS idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" AS montant_annule,
0 AS ticket_emis,0 AS ticket_annule,TO_CHAR(te.jour,'yyyy') AS annee,
TO_CHAR(jour,'mm') AS mois,te.jour
FROM optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
WHERE s."Operateurs"=t.operateur AND t.idsysteme=123 -- Differs by idsysteme
AND j.libellejeux='PMU ONLINE' AND TO_DATE(s."date_de_vente",'dd/mm/yy')=TO_DATE(te.jour,'dd/mm/yy')""",

    'insert_main_fait_lots_alr': """INSERT INTO fait_lots
SELECT '',7181 AS idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" AS montant_annule,
s."Paiements_CFA" paiements,TO_CHAR(te.jour,'yyyy') AS annee,
TO_CHAR(jour,'mm') AS mois,te.jour
FROM optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
WHERE s."Operateurs"=t.operateur AND t.idsysteme=81
AND j.libellejeux='ALR' AND TO_DATE(s."date_de_vente",'dd/mm/yy')=TO_DATE(te.jour,'dd/mm/yy')""",

    'insert_main_fait_lots_pmu_online': """INSERT INTO fait_lots
SELECT '',7181 AS idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" AS montant_annule,
0 AS paiements,TO_CHAR(te.jour,'yyyy') AS annee, -- PMU Online a 0 pour paiements ici
TO_CHAR(jour,'mm') AS mois,te.jour
FROM optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
WHERE s."Operateurs"=t.operateur AND t.idsysteme=123 -- Differs by idsysteme
AND j.libellejeux='PMU ONLINE' AND TO_DATE(s."date_de_vente",'dd/mm/yy')=TO_DATE(te.jour,'dd/mm/yy')""",

    'delete_ar_gitech_prd': """DELETE
    FROM OPTIWARETEMP.AR_GITECH_PRD
    WHERE  DATE_OP IN (
                            SELECT DISTINCT "date_de_vente"
                            FROM OPTIWARETEMP.GITECH
                        )""",
    'insert_ar_gitech_prd': """INSERT INTO OPTIWARETEMP.AR_GITECH_PRD
SELECT "Agences" AGENCES, "Operateurs" OPERATEURS, "date_de_vente" DATE_OP, "Recette_CFA" RECETTE, "Annulation_CFA" ANNULATION, "Recette_CFA"-"Annulation_CFA" VENTES_RESULTANT, "Paiements_CFA" PAIEMENT
            , "Recette_CFA"-"Annulation_CFA"-"Paiements_CFA" RESULTATS
FROM OPTIWARETEMP.GITECH""",

    'merge_dtm_ca_daily_alr': """MERGE INTO DTM_CA_DAILY R0 USING
(
    SELECT Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) AS CA_ALR_GITECH
    FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
    WHERE  F.IDJEUX=J.IDJEUX
    AND F.IDTEMPS=Te.IDTEMPS
    AND F.IDTERMINAL IN (SELECT IDTERMINAL FROM DIM_TERMINAL WHERE IDSYSTEME=81)
    AND F.IDJEUX=25
    AND Te.JOUR BETWEEN :date_debut AND :date_fin
    GROUP BY Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ALR_GITECH=R1.CA_ALR_GITECH""",

    'merge_dtm_ca_daily_pmu_online': """MERGE INTO DTM_CA_DAILY R0 USING
(
    SELECT Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) AS CA_PMU_ONLINE
    FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
    WHERE F.IDJEUX=J.IDJEUX AND F.IDTEMPS=Te.IDTEMPS AND F.IDJEUX=223
    AND Te.JOUR BETWEEN :date_debut AND :date_fin
    GROUP BY Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC AND R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_PMU_ONLINE=R1.CA_PMU_ONLINE"""
}

def get_queries():
    return QUERIES
