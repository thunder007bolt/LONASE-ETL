import cx_Oracle
import pandas as pd
import numpy as np

def chargeLonasebetCasino(data, debut, fin, conn, cur):
    """
    Charge les données Lonasebet Casino dans la base de données Oracle.
    """
    data = data.replace(np.nan, '')
    data_list = data.astype(str) # Renommé
    data_list = list(data_list.to_records(index=False))

    cur.execute("""delete  from optiwaretemp.SRC_PRD_CASINO_LONASEBET""")
    conn.commit()

    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_CASINO_LONASEBET(DATE_VENTE,MISE_TOTALE, SOMME_PAYEE) VALUES(:1,:2,:3)""", data_list)
    conn.commit()

    # Suppression de la periode sur le fait vente
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 316
AND  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 167)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Suppression de la periode sur le fait lots
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE idjeux = 316
AND  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 167)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Insertion de la periode sur le fait vente
    cur.execute("""insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            316 IDJEUX,
            case when to_number(trim(replace(replace(w.MISE_TOTALE,'XOF'),' '))) is null then 0
                else to_number(trim(replace(replace(w.MISE_TOTALE,'XOF'),' ')))
            end as MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS,
            0 TICKET_ANNULE,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    from optiwaretemp.src_prd_casino_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    where upper(trim(te.operateur)) like 'CASINO LONASEBET' and
        te.idsysteme=167 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATE_VENTE,'DD/MM/RR')
)
""")
    conn.commit()

    # Insertion de la periode sur le fait lots
    cur.execute("""insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            316 IDJEUX,
            case when to_number(trim(replace(replace(w.MISE_TOTALE,'XOF'),' '))) is null then 0
                else to_number(trim(replace(replace(w.MISE_TOTALE,'XOF'),' ')))
            end as MONTANT,
            0 MONTANT_ANNULE,
            case when to_number(trim(replace(replace(w.SOMME_PAYEE,'XOF'),' '))) is null then 0
                else to_number(trim(replace(replace(w.SOMME_PAYEE,'XOF'),' ')))
            end as PAIEMENTS,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    from optiwaretemp.src_prd_casino_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    where upper(trim(te.operateur)) like 'CASINO LONASEBET' and
        te.idsysteme=167 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATE_VENTE,'DD/MM/YYYY')
)
""")
    conn.commit()

    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_CASINO_LONASEBET
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 316
            AND F.idterminal=T.idterminal
            AND T.idsysteme  = 167
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_CASINO_LONASEBET=g.CA_CASINO_LONASEBET
    """)
    conn.commit()

    cur.execute("""delete from optiwaretemp.SRC_PRD_CASINO_LONASEBET""")
    conn.commit()
    print("La procedure d'insertion Lonasebet Casino s'est bien deroulee")

def chargeLonasebetAlrParifoot(data, debut, fin, conn, cur):
    """
    Charge les données Lonasebet ALR et Parifoot dans la base de données Oracle.
    """
    data = data.replace(np.nan, '')
    data_list = data.astype(str) # Renommé
    data_list = list(data_list.to_records(index=False))

    cur.execute("""delete from optiwaretemp.src_prd_lonasebet """)
    conn.commit()

    cur.executemany("""INSERT INTO OPTIWARETEMP.src_prd_lonasebet( "ID","ISSUEDATETIME","STAKE","BETCATEGORYTYPE","STATE","PAIDAMOUNT","CUSTOMERLOGIN","FREEBET") VALUES(:1, :2, :3, :4, :5, :6,:7,:8)""", data_list)
    conn.commit()

    # Suppression fait_vente et fait_lots
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX in (25,27,467)
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 167)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE IDJEUX in (25,27,467)
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 167)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Insertion fait_vente
    cur.execute(f"""
    insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            case when upper(w.betcategorytype) like '%SPORTS%' then to_number(27)
                when upper(w.betcategorytype) like '%HORSERACING%' then to_number(25)
                when upper(w.betcategorytype) like '%VIRTUAL%' then to_number(467)
            end as IDJEUX,
            case when upper(trim(w.freebet)) in ('FALSE') then to_number(trim(replace(w.stake,'.',',')))
            else to_number(0)
        end as MONTANT,
        to_number(0) as MONTANT_ANNULE,
    null TICKET_EMIS,
            null TICKET_ANNULE,
            to_char(to_date(trim(substr(w.issuedatetime,1,10)),'DD/MM/YYYY'),'YYYY') ANNEE,
            to_char(to_date(trim(substr(w.issuedatetime,1,10)),'DD/MM/YYYY'),'MM')MOIS,
            replace(trim(substr(w.issuedatetime,1,10)),'/','') JOUR
    from optiwaretemp.src_prd_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    where upper(trim(te.operateur)) like upper(trim(w.betcategorytype)) and te.idsysteme=167
        and m.jour = to_char( to_date(trim(substr(w.issuedatetime,1,10))),'DD/MM/YYYY')
)
""")
    conn.commit()

    # Insertion fait_lots
    cur.execute(f"""
    insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
(
    select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
        case when upper(w.betcategorytype) like '%SPORTS%' then to_number(27)
                when upper(w.betcategorytype) like '%HORSERACING%' then to_number(25)
                when upper(w.betcategorytype) like '%VIRTUAL%' then to_number(467)
        end as IDJEUX,
        case when upper(trim(w.freebet)) in ('FALSE') then to_number(trim(replace(w.stake,'.',',')))
            else to_number(0)
        end as MONTANT,
        to_number(0) as MONTANT_ANNULE,
    case when w.paidamount is null then to_number(0) else to_number(trim(replace(w.paidamount,'.',','))) end as PAIEMENTS,
        to_char(to_date(trim(substr(w.issuedatetime,1,10)),'DD/MM/YYYY'),'YYYY') ANNEE,
        to_char(to_date(trim(substr(w.issuedatetime,1,10)),'DD/MM/YYYY'),'MM')MOIS,
        replace(trim(substr(w.issuedatetime,1,10)),'/','') JOUR
    from optiwaretemp.src_prd_lonasebet w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    where upper(trim(te.operateur)) like upper(trim(w.betcategorytype)) and te.idsysteme=167
        and m.jour = to_char( to_date(trim(substr(w.issuedatetime,1,10))),'DD/MM/YYYY')
)
""")
    conn.commit()

    cur.execute(f"""delete from optiwaretemp.src_prd_lonasebet""")
    conn.commit()

    # DTM_CA_DAILY ALR Lonasebet
    cur.execute(f"""
MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(MONTANT)-SUM(MONTANT_ANNULE) CA_ALR_LONASEBET
        FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=25
            AND F.idterminal in (select idterminal from user_dwhpr.dim_terminal where idsysteme  = 167)
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_ALR_LONASEBET=g.CA_ALR_LONASEBET
""")
    conn.commit()

    # DTM_CA_DAILY Parifoot Lonasebet
    cur.execute(f"""
MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(MONTANT)-SUM(MONTANT_ANNULE) CA_PARIFOOT_LONASEBET
        FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=27
            AND F.idterminal in (select idterminal from user_dwhpr.dim_terminal where idsysteme  = 167)
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_PARIFOOT_LONASEBET=g.CA_PARIFOOT_LONASEBET
""")
    conn.commit()

    # DTM_CA_DAILY Virtuel Lonasebet
    cur.execute(f"""
MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(MONTANT)-SUM(MONTANT_ANNULE) CA_LONASEBET_VIRTUEL
        FROM user_dwhpr.FAIT_VENTE F, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=467
            AND F.idterminal in (select idterminal from user_dwhpr.dim_terminal where idsysteme  = 167)
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_LONASEBET_VIRTUEL=g.CA_LONASEBET_VIRTUEL
""")
    conn.commit()

    # DTM_CA Virtuel Lonasebet (mensuel)
    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca t
    USING (
              SELECT F.ANNEE ANNEE, F.MOIS MOIS, SUM(COALESCE(MONTANT,0))-SUM(COALESCE(MONTANT_ANNULE,0)) CA_LONASEBET_VIRTUEL
              FROM USER_DWHPR.FAIT_VENTE F, USER_DWHPR.DIM_TERMINAL T,USER_DWHPR.DIM_TEMPS Te, USER_DWHPR.DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
                      AND Te.ANNEEC in ('{str(debut.year)}','{str(fin.year)}')
                      AND F.IDJEUX=J.IDJEUX
                      AND F.IDJEUX = 467
                      AND F.idterminal=T.idterminal
                      AND T.idsysteme  = 167
              GROUP BY F.ANNEE , F.MOIS
           ) g
    ON (t.annee = g.annee and t.mois=g.mois)
        WHEN MATCHED THEN UPDATE SET t.CA_LONASEBET_VIRTUEL= g.CA_LONASEBET_VIRTUEL
    """)
    conn.commit()

    print("La procedure d'insertion Lonasebet ALR/Parifoot/Virtuel s'est bien deroulee")
