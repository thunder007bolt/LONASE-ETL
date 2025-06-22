import cx_Oracle
import pandas as pd
import numpy as np

def chargeGitechAlr(data, debut, fin, conn, cur):
    """
    Charge les données Gitech ALR et PMU Online dans la base de données Oracle.
    """
    data_list = data.astype(str) # Renommé pour éviter conflit
    data_list = list(data_list.to_records(index=False))

    cur.execute("""TRUNCATE TABLE OPTIWARETEMP.GITECH """)
    conn.commit()

    cur.executemany("""INSERT INTO OPTIWARETEMP.GITECH( "Agences","Operateurs","date_de_vente","Recette_CFA","Annulation_CFA","Paiements_CFA") VALUES(:1, :2, :3, :4, :5, :6)""", data_list)
    conn.commit()

    # Suppression ALR
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX = 25
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 81)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE IDJEUX = 25
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 81)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Suppression PMU Online
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX = 223
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 123)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE IDJEUX = 223
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 123)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    cur.execute(f"""
    insert into dim_terminal
select distinct '' idterminal, c.idccs,operateurs,'' statut,81 idsysteme from
( select case when "Agences" like 'KOLDA' then 'ZIGUINCHOR' when
    "Agences" like 'TAMBACOUNDA' then 'TAMBA' when "Agences" like 'MATAM' then 'TAMBA'
    when "Agences" like 'MBACKE' then 'DIOURBEL'
    when "Agences" like 'SAINT LOUIS' then 'SAINT-LOUIS'
    when "Agences" like 'RICHARD TOLL' then 'SAINT-LOUIS'
    when "Agences" like 'FATICK' then 'KAOLACK'
    when "Agences" like 'BAMBEY' then 'DIOURBEL'
    when "Agences" like 'KAFFRINE' then 'KAOLACK'
    when "Agences" like 'KEDOUGOU' then 'TAMBA'
    when "Agences" like 'Lonase Head Office' then 'INCONNU'
    else "Agences" end as agences,"Operateurs" as operateurs
    from optiwaretemp.gitech) s ,dim_ccs c
    where UPPER(trim(s.agences))= UPPER(trim(nomccs)) and s.operateurs not in (select distinct operateur from dim_terminal
    where idsysteme=81)
""")
    conn.commit()

    # Insertion Fait Vente ALR
    cur.execute(f"""
    insert into fait_vente
select '',7181 as idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" as montant_annule,
0 as ticket_emis,0 as ticket_annule,to_char(te.jour,'yyyy') as annee,
to_char(jour,'mm') as mois,te.jour
from optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
where s."Operateurs"=t.operateur and t.idsysteme=81
and j.libellejeux='ALR' and to_date(s."date_de_vente",'dd/mm/yy')=to_date(te.jour,'dd/mm/yy')
""")
    conn.commit()

    # Insertion Fait Vente PMU Online
    cur.execute(f"""
    insert into fait_vente
select '',7181 as idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" as montant_annule,
0 as ticket_emis,0 as ticket_annule,to_char(te.jour,'yyyy') as annee,
to_char(jour,'mm') as mois,te.jour
from optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
where s."Operateurs"=t.operateur and t.idsysteme=123
and j.libellejeux='PMU ONLINE' and to_date(s."date_de_vente",'dd/mm/yy')=to_date(te.jour,'dd/mm/yy')
""")
    conn.commit()

    # Insertion Fait Lots ALR
    cur.execute(f"""
    insert into fait_lots
select '',7181 as idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" as montant_annule,
s."Paiements_CFA" paiements,to_char(te.jour,'yyyy') as annee,
to_char(jour,'mm') as mois,te.jour
from optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
where s."Operateurs"=t.operateur and t.idsysteme=81
and j.libellejeux='ALR' and to_date(s."date_de_vente",'dd/mm/yy')=to_date(te.jour,'dd/mm/yy')
""")
    conn.commit()

    # Insertion Fait Lots PMU Online
    cur.execute(f"""
    insert into fait_lots
select '',7181 as idvendeur,t.idterminal , te.idtemps,j.idjeux,s."Recette_CFA",s."Annulation_CFA" as montant_annule,
0 as paiements,to_char(te.jour,'yyyy') as annee,
to_char(jour,'mm') as mois,te.jour
from optiwaretemp.gitech  s, dim_terminal t, dim_jeux j, dim_temps te
where s."Operateurs"=t.operateur and t.idsysteme=123
and j.libellejeux='PMU ONLINE' and to_date(s."date_de_vente",'dd/mm/yy')=to_date(te.jour,'dd/mm/yy')
""")
    conn.commit()

    cur.execute(f"""
    DELETE
    FROM OPTIWARETEMP.AR_GITECH_PRD
    WHERE  DATE_OP IN (
                            SELECT DISTINCT "date_de_vente"
                            FROM OPTIWARETEMP.GITECH
                        )
""")
    conn.commit()

    cur.execute(f"""
    INSERT INTO OPTIWARETEMP.AR_GITECH_PRD
SELECT "Agences" AGENCES, "Operateurs" OPERATEURS, "date_de_vente" DATE_OP, "Recette_CFA" RECETTE, "Annulation_CFA" ANNULATION, "Recette_CFA"-"Annulation_CFA" VENTES_RESULTANT, "Paiements_CFA" PAIEMENT
            , "Recette_CFA"-"Annulation_CFA"-"Paiements_CFA" RESULTATS
FROM OPTIWARETEMP.GITECH
""")
    conn.commit()

    # DTM_CA_DAILY ALR Gitech
    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING
(
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_ALR_GITECH
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE  F.IDJEUX=J.IDJEUX
    AND F.IDTEMPS=Te.IDTEMPS
    AND F.IDTERMINAL IN (SELECT IDTERMINAL FROM DIM_TERMINAL WHERE IDSYSTEME=81)
    AND F.IDJEUX=25
    AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_ALR_GITECH=R1.CA_ALR_GITECH
""")
    conn.commit()

    # DTM_CA_DAILY PMU Online
    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING
(
select Te.ANNEEC,Te.MOISC,Te.JOUR, SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE) as CA_PMU_ONLINE
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE F.IDJEUX=J.IDJEUX AND F.IDTEMPS=Te.IDTEMPS AND F.IDJEUX=223
AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
group by Te.ANNEEC,Te.MOISC,Te.JOUR
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_PMU_ONLINE=R1.CA_PMU_ONLINE
""")
    conn.commit()

    cur.execute("""TRUNCATE TABLE OPTIWARETEMP.GITECH """)
    conn.commit()

    print("La procedure d'insertion Gitech ALR et PMU Online s'est bien deroulee")

def chargeGitechCasino(data, debut, fin, conn, cur):
    """
    Charge les données Gitech Casino dans la base de données Oracle.
    """
    data_list = data.astype(str) # Renommé pour éviter conflit
    data_list = list(data_list.to_records(index=False))

    # Note: GITECH table is also used by chargeGitechAlr. Consider separate temp tables if conflicts arise.
    # For now, assuming it's truncated before this specific load if needed, or handled by caller.
    # cur.execute("""TRUNCATE TABLE OPTIWARETEMP.GITECH """)
    # conn.commit()

    cur.execute("""TRUNCATE TABLE OPTIWARETEMP.src_prd_casino_gitech """) # Specific temp table for casino
    conn.commit()

    cur.executemany("""INSERT INTO OPTIWARETEMP.src_prd_casino_gitech( "IDJEU","NOMJEU","DATEVENTE","VENTE","PAIEMENT","POURCENTAGEPAIEMENT") VALUES(:1, :2, :3, :4, :5, :6)""", data_list)
    conn.commit()

    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE IDJEUX = 316
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 81)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE IDJEUX = 316
AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 81)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    cur.execute(f"""
    insert into user_dwhpr.fait_vente(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
( select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            316 IDJEUX,
            case when to_number(trim(w.vente)) is null then 0
                else to_number(trim(w.vente))
            end as MONTANT,
            0 MONTANT_ANNULE,
            0 TICKET_EMIS,
            0 TICKET_ANNULE,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    from optiwaretemp.src_prd_casino_gitech w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    where upper(trim(te.operateur)) like 'CASINO GITECH' and
        te.idsysteme=81 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATEVENTE,'DD/MM/RR')
)
""")
    conn.commit()

    cur.execute(f"""
    insert into user_dwhpr.fait_lots(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
( select
            to_number(7181) IDVENDEUR,
            to_number(te.idterminal) IDTERMINAL,
            to_number(m.idtemps) IDTEMPS,
            316 IDJEUX,
            case when to_number(trim(w.vente)) is null then 0
                else to_number(trim(w.vente))
            end as MONTANT,
            0 MONTANT_ANNULE,
            case when to_number(trim(w.PAIEMENT)) is null then 0
                else to_number(trim(w.PAIEMENT))
            end as PAIEMENTS,
            to_char(m.jour,'YYYY') ANNEE,
            to_char(m.jour,'MM') MOIS,
            replace(m.jour,'/') JOUR
    from optiwaretemp.src_prd_casino_gitech w, user_dwhpr.dim_terminal te, user_dwhpr.dim_temps m
    where upper(trim(te.operateur)) like 'CASINO GITECH' and
        te.idsysteme=81 and to_date(m.jour,'DD/MM/RR') = to_date(w.DATEVENTE,'DD/MM/RR')
)
""")
    conn.commit()

    cur.execute(f"""delete from optiwaretemp.src_prd_casino_gitech""")
    conn.commit()

    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca_daily t
USING (
    SELECT Te.ANNEEC ANNEE, Te.MOISC MOIS, Te.JOUR, SUM(NVL(MONTANT,0))-SUM(NVL(MONTANT_ANNULE,0)) CA_CASINO_GITECH
        FROM user_dwhpr.FAIT_VENTE F, DIM_TERMINAL T, user_dwhpr.DIM_TEMPS Te, DIM_JEUX J
    WHERE Te.IDTEMPS=F.IDTEMPS
            AND F.IDJEUX=J.IDJEUX
            AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
            AND F.IDJEUX=J.IDJEUX
            AND F.IDJEUX = 316
            AND F.idterminal=T.idterminal
            AND T.idsysteme  = 81
    GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour)
WHEN MATCHED THEN UPDATE SET t.CA_CASINO_GITECH=g.CA_CASINO_GITECH
""")
    conn.commit()

    print("La procedure d'insertion Gitech Casino s'est bien deroulee")
