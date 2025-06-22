import cx_Oracle
import pandas as pd
import numpy as np

def load_financial_data(generalDirectory, start_date, conn, cur):
    """
    Charge les données Financial depuis un fichier CSV dans une table temporaire Oracle.
    """
    directory = generalDirectory + r"VIRTUEL_EDITEC\FINANCIAL" # Correction: r"..." pour les backslashes
    file_pattern = directory + f"\\**\\Financial {str(start_date)}.csv" # Correction: f"\\**\\"
    files = glob.glob(file_pattern, recursive=True)

    print(f"Recherche de fichiers Financial: {file_pattern}, Trouvés: {len(files)}")

    if not files:
        print(f"Le fichier Financial du {start_date} n'a pas ete extrait ")
        return False

    file_path = files[0]
    try:
        data = pd.read_csv(file_path, sep=';', index_col=False)
        data = pd.DataFrame(data, columns=['Name', 'Total In', 'Total Out', 'date', 'Reversal', 'Currency'])

        cur.execute("""truncate table optiwaretemp.GLOB_FINANCIAL""")
        conn.commit()

        data_list = data.replace(np.nan, '').astype(str)
        data_list = list(data_list.to_records(index=False))

        cur.executemany("""INSERT INTO optiwaretemp.GLOB_FINANCIAL("Name","Total_In", "Total_Out", "DATE", "Reversal","Currency") VALUES(:1,:2,:3,:4,:5,:6)""", data_list)
        conn.commit()
        print(f"Données Financial chargées depuis {file_path}")
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier Financial {file_path}: {e}")
        return False

def load_zone_betting_data(generalDirectory, start_date, conn, cur):
    """
    Charge les données Zone Betting depuis un fichier CSV dans une table temporaire Oracle.
    """
    directory = generalDirectory + r"VIRTUEL_EDITEC\ZONE BETTING" # Correction: r"..." pour les backslashes
    file_pattern = directory + f"\\**\\zone betting {str(start_date)}.csv" # Correction: f"\\**\\"
    files = glob.glob(file_pattern, recursive=True)

    print(f"Recherche de fichiers Zone Betting: {file_pattern}, Trouvés: {len(files)}")

    if not files:
        print(f"Le fichier zone betting du {start_date} n'a pas ete extrait ")
        return False

    file_path = files[0]
    try:
        data = pd.read_csv(file_path, sep=';', index_col=False)
        data = pd.DataFrame(data, columns=['Shop name', 'date', 'Cancelled', 'Stake', 'Won'])

        cur.execute("""truncate table optiwaretemp.GLOB_ZONE_BETTING""")
        conn.commit()

        data_list = data.replace(np.nan, '').astype(str)
        data_list = list(data_list.to_records(index=False))

        cur.executemany("""INSERT INTO optiwaretemp.GLOB_ZONE_BETTING("Shop name","Date", "CANCELLED", "STAKE", "WON") VALUES(:1,:2,:3,:4,:5)""", data_list)
        conn.commit()
        print(f"Données Zone Betting chargées depuis {file_path}")
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier Zone Betting {file_path}: {e}")
        return False

def load_premier_sn_data(generalDirectory, start_date, conn, cur):
    """
    Charge les données Premier SN depuis un fichier CSV dans une table temporaire Oracle.
    """
    directory = generalDirectory + r"VIRTUEL_EDITEC\PREMIERSN" # Correction: r"..." pour les backslashes
    file_pattern = directory + f"\\**\\{str(start_date)}-Premier SN.csv" # Correction: f"\\**\\"
    files = glob.glob(file_pattern, recursive=True)

    print(f"Recherche de fichiers Premier SN: {file_pattern}, Trouvés: {len(files)}")

    if not files:
        print(f"Le fichier Premier SN du {start_date} n'a pas ete extrait ")
        return False

    file_path = files[0]
    try:
        data = pd.read_csv(file_path, sep=';', index_col=False)
        data = pd.DataFrame(data, columns=['Outlet', 'Reported', 'Sales', 'Redeems', 'Voided'])

        cur.execute("""truncate table optiwaretemp.GLOB_SB_VDR""")
        conn.commit()

        data_list = data.replace(np.nan, '').astype(str)
        data_list = list(data_list.to_records(index=False))

        cur.executemany("""INSERT INTO optiwaretemp.GLOB_SB_VDR("Outlet","Reported", "Sales", "Redeems", "Voided") VALUES(:1,:2,:3,:4,:5)""", data_list)
        conn.commit()
        print(f"Données Premier SN chargées depuis {file_path}")
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier Premier SN {file_path}: {e}")
        return False

def chargeVirtuelEditec(debut, fin, conn, cur):
    """
    Charge et traite les données Virtuel Editec dans la base de données Oracle.
    Cette fonction dépend des données chargées par load_financial_data,
    load_zone_betting_data, et load_premier_sn_data.
    """

    # Suppression de la periode sur le fait vente
    cur.execute(f"""delete  from  user_dwhpr.fait_vente
WHERE idjeux = 124
and  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 2)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    # Suppression de la periode sur le fait lots
    cur.execute(f"""delete  from user_dwhpr.fait_lots
WHERE idjeux = 124
and  IDTERMINAL in (SELECT IDTERMINAL FROM user_dwhpr.DIM_TERMINAL where IDSYSTEME = 2)
AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    cur.execute("""
    insert into dim_terminal
select distinct '',241,MAGASIN,'',2 from
(
select "Name" as Magasin,"DATE" as DATE_VENTE,
(case when ("Total_In") like '%,%'
then  (replace (("Total_In") ,'.')) else ("Total_In") end)  as VENTE,
(case when ("Reversal") like '%,%'
then  (replace (("Reversal") ,'.')) else ("Reversal") end)  as annulation
from optiwaretemp.GLOB_FINANCIAL where "Currency" like 'XOF'
UNION ALL
select "Outlet","Reported","Sales","Voided" from  optiwaretemp.GLOB_SB_VDR UNION ALL
select "Shop_name",DATE_VENTE, "Placed_bets_amount","Cancelled_paid_amount"
from  optiwaretemp.GLOB_OVERALL
UNION ALL
SELECT "Shop name" MAGASIN, "Date" DATE_VENTE, STAKE, replace(CANCELLED,'.',',') ANNULATION
FROM OPTIWARETEMP.GLOB_ZONE_BETTING
) L
where L.MAGASIN NOT IN (select distinct operateur from dim_terminal where idsysteme=2 or idsysteme is null)
            """)
    conn.commit()

    cur.execute("""
    insert into USER_DWHPR.fait_vente
(select '',7781,t.idterminal idterminal,te.idtemps idtemps,124 idjeux,
to_number(trim(replace(replace(L.VENTE,' '),'.00'))) as vente ,
to_number(trim(replace(replace( L.ANNULATION,' '),'.00'))) as annulation,
0,0,to_char(te.jour,'yyyy') as annee,to_char(te.jour,'mm') as mois, te.jour
from (
        select "Name" as MAGASIN ,"DATE" as DATE_VENTE,
            (case when ("Total_In") like '%,%' then  to_number(replace (("Total_In") ,'.')) else  to_number(replace(("Total_In"),'.',',')) end)  as VENTE,
            (case when ("Reversal") like '%,%' then  to_number(replace (("Reversal") ,'.')) else  to_number(replace(("Reversal"),'.',',')) end)  as annulation
        from optiwaretemp.GLOB_FINANCIAL where "Currency" like 'XOF'
    UNION ALL
    select "Outlet" as Magasin
            ,"Reported" as DATE_VENTE
            ,to_number(replace("Sales",'.',',')) as VENTE
            ,to_number(replace("Voided",'.',',')) as annulation
    from  optiwaretemp.GLOB_SB_VDR
    UNION ALL
    SELECT "Shop name" MAGASIN, "Date" DATE_VENTE, to_number(replace(STAKE,'.',',')) VENTE, to_number(replace(CANCELLED,'.',',')) ANNULATION
    FROM OPTIWARETEMP.GLOB_ZONE_BETTING
) L, dim_terminal t, dim_temps te
where (trim(L.magasin)) = (trim(t.operateur)) and to_date(L.DATE_VENTE,'dd/mm/yy')=to_date(te.jour,'dd/mm/yy')
        and t.idsysteme=2 and (L.magasin) not like ('%Senegal%' ) and Magasin not like '%test%'
)
    """)
    conn.commit()

    cur.execute("""
    insert into USER_DWHPR.fait_lots
(
    select '' IDLOTS
        ,7781 as idvendeur
        ,t.idterminal
        ,te.idtemps
        ,124 as idjeux
        , L.VENTE as montant
        , L.ANNULATION as montant_annule
        , paiements
        ,to_char(te.jour,'yyyy') as annee
        ,to_char(te.jour,'mm') as mois
        ,to_char(te.jour) as jour
from (
        select "Name" as MAGASIN ,
            "DATE" as DATE_VENTE,
            (case when ("Total_In") like '%,%' then  to_number(replace (("Total_In") ,'.')) else to_number(replace(("Total_In"),'.',',')) end)  as VENTE,
            (case when ("Reversal") like '%,%' then  to_number(replace (("Reversal") ,'.')) else to_number(replace(("Reversal"),'.',',')) end)  as annulation,
            to_number(replace("Total_Out",'.',',')) as paiements
        from optiwaretemp.GLOB_FINANCIAL where "Currency" like 'XOF'

        UNION ALL

        select "Outlet" as Magasin
                ,"Reported" as DATE_VENTE
                ,to_number(replace("Sales",'.',',')) as VENTE
                ,to_number(replace("Voided",'.',',')) as annulation
                ,to_number(replace("Redeems",'.',','))-to_number(replace("Voided",'.',',')) as paiements
        from  optiwaretemp.GLOB_SB_VDR

        UNION ALL

        SELECT "Shop name" MAGASIN,
                "Date" DATE_VENTE,
                to_number(replace(STAKE,'.',',')) VENTE,
                to_number(replace(CANCELLED,'.',',')) ANNULATION,
                to_number(replace(WON,'.',',')) PAIEMENTS

        FROM OPTIWARETEMP.GLOB_ZONE_BETTING


        ) L, dim_terminal t, dim_temps te
where (trim(L.magasin)) = (trim(t.operateur)) and to_date(L.DATE_VENTE,'dd/mm/yy')=to_date(te.jour,'dd/mm/yy')
    and t.idsysteme=2 and L.magasin not like ('%Senegal%') and L.magasin not like '%test%'
)
""")
    conn.commit()

    cur.execute(f"""
    MERGE INTO DTM_CA_DAILY R0 USING
(
select Te.ANNEEC,Te.MOISC,Te.JOUR
        , CASE WHEN Te.IDTEMPS>=7945 THEN (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE))*3/100
            ELSE (SUM(F.MONTANT) - SUM(F.MONTANT_ANNULE)) END as CA_VIRTUELS_EDITEC
FROM FAIT_VENTE F, DIM_JEUX J , DIM_TEMPS Te
WHERE  F.IDJEUX=J.IDJEUX
AND Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
    AND F.IDTEMPS=Te.IDTEMPS
    AND F.IDJEUX=124
group by Te.ANNEEC,Te.MOISC,Te.JOUR,Te.IDTEMPS
) R1
ON ( R0.ANNEE = R1.ANNEEC and R0.MOIS=R1.MOISC AND R0.JOUR=R1.JOUR)
WHEN MATCHED THEN UPDATE SET R0.CA_VIRTUELS_EDITEC=R1.CA_VIRTUELS_EDITEC
""")
    conn.commit()

    cur.execute(""" truncate table OPTIWARETEMP.GLOB_ZONE_BETTING """)
    conn.commit()

    cur.execute(""" truncate table optiwaretemp.GLOB_FINANCIAL """)
    conn.commit()

    cur.execute(""" truncate table optiwaretemp.GLOB_SB_VDR """)
    conn.commit()

    print("La procedure d'insertion Virtuel Editec s'est bien deroulee")

# Nécessite glob pour les fonctions load_*
import glob
