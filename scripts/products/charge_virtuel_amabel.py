import cx_Oracle
import pandas as pd
import numpy as np

def chargeVirtuelAmabel(data, debut, fin, conn, cur):
    """
    Charge les données Virtuel Amabel dans la base de données Oracle.
    """
    data = data.replace(np.nan, '')
    data_list = data.astype(str) # Renommé pour éviter conflit
    data_list = list(data_list.to_records(index=False))

    # Vider la table temporaire optiwaretemp.SRC_PRD_SUNUBET
    cur.execute("""delete from optiwaretemp.SRC_PRD_SUNUBET""")
    conn.commit()

    # Remplir la table temporaire optiwaretemp.SRC_PRD_SUNUBET de donnees
    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_SUNUBET("NOM", "Total enjeu", "Total Ticket Virtuel", "Total Paiement","Date Vente") VALUES(:1,:2,:3,:4,:5)""", data_list)
    conn.commit()

    # MAJ des terminaux
    cur.execute("""INSERT INTO "USER_DWHPR"."DIM_TERMINAL"
SELECT DISTINCT '' IDTERMINAL, 241 IDCCS, NOM AS OPERATEURS, '' STATUT, 141 IDSYSTEME
    FROM OPTIWARETEMP.SRC_PRD_SUNUBET
    WHERE TRIM(NOM) NOT IN (SELECT OPERATEUR FROM DIM_TERMINAL WHERE IDSYSTEME=141)
    ORDER BY SUBSTR(REPLACE(NOM,' ',''),INSTR(REPLACE(NOM,' ',''),'(')+1,7)
    """)
    conn.commit()

    # Mettre a jour le montant annule
    cur.execute("""update optiwaretemp.SRC_PRD_SUNUBET set "Total annulation" = '0' """)
    conn.commit()

    # Suppression de la periode sur le fait vente
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 261
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Suppression de la periode sur le fait lots
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE idjeux = 261
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Insertion de la periode sur le fait vente
    cur.execute("""INSERT INTO "USER_DWHPR"."FAIT_VENTE"
SELECT   '' as IDVENTE,
        (SELECT IDVENDEUR FROM "USER_DWHPR"."DIM_VENDEUR") as IDVENDEUR,
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
                S."Total enjeu" as MONTANT,
                T.IDTERMINAL,Te.JOUR,
                S."Total annulation" as MONTANT_ANNULE,
                S."Total Ticket Virtuel" as TICKET_EMIS,
                '' as TICKET_ANNULE,
                'VIRTUEL AMABEL' PRODUIT
            FROM "OPTIWARETEMP"."SRC_PRD_SUNUBET" S,  "USER_DWHPR"."DIM_TEMPS" Te ,USER_DWHPR.DIM_TERMINAL T
            WHERE  T.OPERATEUR=S.NOM
            AND IDSYSTEME= 141
            AND Te.JOUR=TO_DATE(S."Date Vente",'DD/MM/RR')
        ) SRC , "USER_DWHPR"."DIM_JEUX" J
    WHERE J.IDJEUX=261
    and UPPER(J.LIBELLEJEUX)=UPPER(SRC.PRODUIT)
    AND UPPER(SRC.PRODUIT)='VIRTUEL AMABEL'
""")
    conn.commit()

    # Insertion de la periode sur le fait lots
    cur.execute("""INSERT INTO FAIT_LOTS
SELECT   '' as IDLOTS,
        (SELECT IDVENDEUR FROM "USER_DWHPR"."DIM_VENDEUR") as IDVENDEUR,
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
                S."Total enjeu" as MONTANT,
                T.IDTERMINAL,Te.JOUR,
                S."Total annulation" as MONTANT_ANNULE,
                S."Total Paiement" as PAIEMENTS,
                'VIRTUEL AMABEL' PRODUIT
            FROM "OPTIWARETEMP"."SRC_PRD_SUNUBET" S,  "USER_DWHPR"."DIM_TEMPS" Te ,USER_DWHPR.DIM_TERMINAL T
            WHERE  T.OPERATEUR=S.NOM
            AND IDSYSTEME= 141
            AND Te.JOUR=TO_DATE(S."Date Vente",'DD/MM/RR')
        ) SRC , "USER_DWHPR"."DIM_JEUX" J
    WHERE J.IDJEUX=261
    and UPPER(J.LIBELLEJEUX)=UPPER(SRC.PRODUIT)
    AND UPPER(SRC.PRODUIT)='VIRTUEL AMABEL'
""")
    conn.commit()

    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING
(
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_VIRTUEL_AMABEL
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE F.IDJEUX=J.IDJEUX
    AND F.IDTEMPS=Te.IDTEMPS
    AND F.IDJEUX=261
    AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_VIRTUEL_AMABEL=R1.CA_VIRTUEL_AMABEL
""")
    conn.commit()

    # Doublon AR_sunubet_PRD
    cur.execute("""DELETE
    FROM OPTIWARETEMP.AR_SUNUBET_PRD
    WHERE  "Date Vente" IN (
                                SELECT DISTINCT "Date Vente"
                                FROM OPTIWARETEMP.SRC_PRD_SUNUBET
                            )""")
    conn.commit()

    # Insertion AR_sunubet_PRD
    cur.execute("""INSERT INTO OPTIWARETEMP.AR_SUNUBET_PRD
SELECT *
    FROM OPTIWARETEMP.SRC_PRD_SUNUBET""")
    conn.commit()

    # Vider la table temporaire optiwaretemp.SRC_PRD_SUNUBET
    cur.execute("""delete from optiwaretemp.SRC_PRD_SUNUBET""")
    conn.commit()

    print("La procedure d'insertion Virtuel Amabel s'est bien deroulee")
