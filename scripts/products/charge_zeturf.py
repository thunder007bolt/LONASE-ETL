import cx_Oracle
import pandas as pd
import numpy as np

def chargeZeturf(data, debut, fin, conn, cur):
    """
    Charge les données Zeturf dans la base de données Oracle.
    """
    data = data.replace(np.nan, '')
    data_list = data.astype(str) # Renommé pour éviter conflit
    data_list = list(data_list.to_records(index=False))

    # Vider la table temporaire optiwaretemp.src_prd_zeturf
    cur.execute("""delete from optiwaretemp.src_prd_zeturf""")
    conn.commit()

    # Remplir la table temporaire optiwaretemp.src_prd_zeturf de donnees
    cur.executemany("""INSERT INTO optiwaretemp.src_prd_zeturf("HIPPODROME","COURSE", "DEPART", "PARIS", "ENJEUX", "ANNULATIONS", "MARGE","DATE_DU_DEPART") VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""", data_list)
    conn.commit()

    # Suppression de la periode sur le fait vente
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 311
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Suppression de la periode sur le fait lots
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE idjeux = 311
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Insertion de la periode sur le fait vente
    cur.execute("""insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            311 IDJEUX,
            case when to_number(trim(replace(replace(w.enjeux,'FCFA'),' '))) is null then 0
                else to_number(trim(replace(replace(w.enjeux,'FCFA'),' ')))
            end as MONTANT,
            case when to_number(trim(replace(replace(w.annulations,'FCFA'),' '))) is null then 0
                else to_number(trim(replace(replace(w.annulations,'FCFA'),' ')))
            end as MONTANT_ANNULE,
            null TICKET_EMIS,
            null TICKET_ANNULE,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR

    from optiwaretemp.src_prd_zeturf w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m

    where upper(trim(te.operateur)) like 'ZETURF TERMINAL' and
        te.idsysteme=169 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATE_DU_DEPART,'DD/MM/RR')
)
""")
    conn.commit()

    # Insertion de la periode sur le fait lots
    cur.execute("""insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            311 IDJEUX,
            case when to_number(trim(replace(replace(w.enjeux,'FCFA'),' '))) is null then 0
                else to_number(trim(replace(replace(w.enjeux,'FCFA'),' ')))
            end as MONTANT,
            case when to_number(trim(replace(replace(w.annulations,'FCFA'),' '))) is null then 0
                else to_number(trim(replace(replace(w.annulations,'FCFA'),' ')))
            end as MONTANT_ANNULE,
            ABS(NVL(to_number(trim(replace(replace(w.enjeux,'FCFA'),' '))),0) - NVL(to_number(trim(replace(replace(w.marge,'FCFA'),' '))),0)) PAIEMENTS,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR

    from optiwaretemp.src_prd_zeturf w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m

    where upper(trim(te.operateur)) like 'ZETURF TERMINAL' and
        te.idsysteme=169 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATE_DU_DEPART,'DD/MM/RR')
)
""")
    conn.commit()

    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_ZETURF
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR  between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 311
            AND F.idterminal=T.idterminal
            AND T.idsysteme  = 169
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_ZETURF=g.CA_ZETURF
""")
    conn.commit()

    # Vider la table temporaire optiwaretemp.src_prd_zeturf
    cur.execute("""delete from optiwaretemp.src_prd_zeturf""")
    conn.commit()

    print("La procedure d'insertion Zeturf s'est bien deroulee")
