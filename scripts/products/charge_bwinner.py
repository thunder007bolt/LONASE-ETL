import cx_Oracle
import pandas as pd
import numpy as np

def chargeBwinner(data, debut, fin, conn, cur):
    """
    Charge les données Bwinner dans la base de données Oracle.
    """
    data = data.astype(str)
    data_list = list(data.to_records(index=False)) # Renommé pour éviter conflit avec paramètre

    # Vider la table temporaire optiwaretemp.SRC_PRD_BWINNERS
    cur.execute("""truncate table optiwaretemp.SRC_PRD_BWINNERS""")

    # Remplir la table temporaire optiwaretemp.SRC_PRD_BWINNERS de donnees
    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_BWINNERS(CREATE_TIME,PRODUCT,STAKE,"MAX PAYOUT") VALUES(:1,:2,:3,:4)""", data_list)
    conn.commit()

    # Mettre a jour le status
    cur.execute("""update optiwaretemp.SRC_PRD_BWINNERS set status = 'LOST'""")
    conn.commit()

    # Suppression de la periode sur le fait vente
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 312
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Suppression de la periode sur le fait lots
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE idjeux = 312
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Insertion de la periode sur le fait vente
    cur.execute("""insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            312 IDJEUX,
            case when to_number(replace(trim(w.stake),'.',',')) is not null then to_number(replace(trim(w.stake),'.',','))
                else 0
            end as MONTANT,
            0  MONTANT_ANNULE,
            null TICKET_EMIS,
            null TICKET_ANNULE,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR

    from optiwaretemp.src_prd_bwinners w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m

    where upper(trim(te.operateur)) = case when upper(trim(w.product))='SN.BWINNERS.NET' then 'BWINNERS ONLINE' else 'BWINNERS PHYSIQUE' end
        and te.idsysteme=170
        and m.jour = to_date(w.CREATE_TIME,'DD/MM/YYYY')
)
""")
    conn.commit()

    # Insertion de la periode sur le fait lots
    cur.execute("""insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            312 IDJEUX,
            case when to_number(replace(trim(w.stake),'.',',')) is not null then to_number(replace(trim(w.stake),'.',','))
                else 0
            end as MONTANT,
            0  MONTANT_ANNULE,
            case when to_number(replace(trim(w."MAX PAYOUT"),'.',',')) is not null then to_number(replace(trim(w."MAX PAYOUT"),'.',','))
                else 0
            end as PAIEMENTS,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR

    from optiwaretemp.src_prd_bwinners w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m

    where upper(trim(te.operateur)) = case when upper(trim(w.product))='SN.BWINNERS.NET' then 'BWINNERS ONLINE' else 'BWINNERS PHYSIQUE' end
        and m.jour = to_date(w.CREATE_TIME,'DD/MM/YYYY')
)
""")
    conn.commit()

    # Vider la table temporaire optiwaretemp.SRC_PRD_BWINNERS
    cur.execute("""truncate table optiwaretemp.SRC_PRD_BWINNERS""")
    conn.commit()

    # Mise a jour dtm_ca_daily
    cur.execute(f"""MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_BWINNERS_ONLINE
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'

            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 312
            AND F.idterminal=T.idterminal
            AND upper(trim(T.operateur)) like 'BWINNERS ONLINE'
            AND T.idsysteme  = 170
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_BWINNERS_ONLINE=g.CA_BWINNERS_ONLINE
""")
    conn.commit()

    cur.execute(f"""MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_BWINNERS_PHYSIQUE
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR  between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'

            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 312
            AND F.idterminal=T.idterminal
            AND upper(trim(T.operateur)) like 'BWINNERS PHYSIQUE'
            AND T.idsysteme  = 170
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_BWINNERS_PHYSIQUE=g.CA_BWINNERS_PHYSIQUE
""")
    conn.commit()

    # Merge dtm_mise_bwinner
    cur.execute(f"""MERGE INTO user_dwhpr.DTM_MISE_BWINNER t
USING (
    SELECT F.IDTEMPS TEMPS,Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR,upper(trim(T.operateur)) OPERATEUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA, SUM(NVL(PAIEMENTS,0)) LOT
        FROM user_dwhpr.FAIT_LOTS F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'

            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 312
            AND F.idterminal=T.idterminal
            AND T.idsysteme  = 170
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR,F.IDTEMPS, upper(trim(T.operateur))
    ) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour AND T.CATEGORIE = G.OPERATEUR)
WHEN MATCHED THEN UPDATE SET t.CA=g.CA, T.LOTS = G.LOT, t.MONTANT_ANNULE = 0
WHEN NOT MATCHED THEN
    INSERT (IDTEMPS,ANNEE,MOIS,JOUR,CA,LOTS,CATEGORIE,MONTANT_ANNULE)
    VALUES (G.TEMPS, G.ANNEE,G.MOIS,G.JOUR,G.CA,G.LOT,G.OPERATEUR,0)
""")
    conn.commit()

    print("La procedure d'insertion Bwinner s'est bien deroulee")
