import cx_Oracle
import pandas as pd
import numpy as np
import datetime # Ajouté pour datetime.strptime

def chargeAFITECHCommissionHistory(data, debut, fin, conn, cur, firstDay): # firstDay ajouté comme paramètre
    """
    Charge les données AFITECH Commission History dans la base de données Oracle.
    'firstDay' est le premier jour du mois pour la période de commission.
    """
    data = data.replace(np.nan, '')
    # Assurer que les colonnes numériques sont bien formatées avant conversion en str
    cols_to_format = ["Total Commission", "Deposit Total Amount", "Deposit Count", "Withdrawal Total Amount", "Withdrawal Count"]
    for col in cols_to_format:
        if col in data.columns:
            # Tenter de convertir en numérique, puis remplacer . par , si nécessaire pour Oracle
            # La conversion directe en str puis replace('.', ',') peut mal gérer les nombres déjà avec des virgules.
             data[col] = pd.to_numeric(data[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)


    data = data.applymap(lambda x: str(x).replace('.', ',')) # Remplacer . par , pour Oracle

    if 'Partner' in data.columns:
        data['Partner'] = data['Partner'].str.replace(',', '.', regex=False) # Rétablir le . pour Partner si besoin
    if 'Début de la période' in data.columns:
        data['Début de la période'] = data['Début de la période'].str.replace('-', '/', regex=False)
    if 'Fin de la période' in data.columns:
        data['Fin de la période'] = data['Fin de la période'].str.replace('-', '/', regex=False)

    data_list = data.astype(str)
    data_list = list(data_list.to_records(index=False))

    cur.execute("""delete  from optiwaretemp.SRC_PRD_AFITECH_COMMISSION""")
    conn.commit()

    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_AFITECH_COMMISSION("DEBUT_PERIODE"
,"FIN_PERIODE"
,"PARTNER"
,"PAYEMENT_PROVIDER"
,"TOTAL_COMMISSON"
,"DEPOSIT_TOTAL_AMOUNT"
,"DEPOSIT_COUNT"
,"WITHDRAWAL_TOTAL_AMOUNT"
,"WITHDRAWAL_COUNT") VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9)""", data_list)
    conn.commit()

    # Suppression de la periode sur le DTM_MISE_AFITECH_COMMISSION
    cur.execute(f"""delete  from  user_dwhpr.DTM_MISE_AFITECH_COMMISSION
WHERE idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(firstDay.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""") # Utilisation de firstDay ici
    conn.commit()

    # Insertion de la periode sur le DTM_MISE_AFITECH_COMMISSION
    cur.execute("""insert into user_dwhpr.DTM_MISE_AFITECH_COMMISSION(
DEBUT_PERIODE
,FIN_PERIODE
,PARTNER
,PAYEMENT_PROVIDER
,TOTAL_COMMISSON
,DEPOSIT_TOTAL_AMOUNT
,DEPOSIT_COUNT
,WITHDRAWAL_TOTAL_AMOUNT
,WITHDRAWAL_COUNT
,IDTEMPS,MOIS, ANNEE
)
(
SELECT to_char(to_date(trim(substr(DEBUT_PERIODE,1,10)),'YYYY/mm/dd'),'DD/MM/YYYY'),
        to_char(to_date(trim(substr(FIN_PERIODE,1,10)),'YYYY/mm/dd'),'DD/MM/YYYY') as JOUR,
            PARTNER,
            PAYEMENT_PROVIDER,
            NVL(TOTAL_COMMISSON,0),
            NVL(DEPOSIT_TOTAL_AMOUNT,0),
            NVL(DEPOSIT_COUNT,0),
            NVL(WITHDRAWAL_TOTAL_AMOUNT,0),
            NVL(WITHDRAWAL_COUNT,0),Te.idtemps as IDTEMPS,Te.MOISC as MOIS,Te.ANNEEC as ANNEE
        FROM optiwaretemp.SRC_PRD_AFITECH_COMMISSION F, user_dwhpr.DIM_TEMPS Te
    where to_date(trim(substr(f.FIN_PERIODE,1,10)),'YYYY/mm/dd') = to_date(trim(substr(Te.jour,1,10)),'DD/MM/rr')
)
""")
    conn.commit()

    cur.execute("""delete  from optiwaretemp.SRC_PRD_AFITECH_COMMISSION""")
    conn.commit()
    print("La procedure d'insertion AFITECH Commission History s'est bien deroulee")

def chargeAFITECHDailyPaymentActivity(data, debut, fin, conn, cur):
    """
    Charge les données AFITECH Daily Payment Activity dans la base de données Oracle.
    """
    format_string_input = '%d/%m/%Y' # Format d'entrée des dates dans le CSV
    format_string_output_db = '%Y/%m/%d' # Format attendu pour la conversion en YYYY/MM/DD pour Oracle

    if 'Date' in data.columns:
        # Convertit la colonne 'Date' en objets datetime, puis en chaînes formatées
        data['Date'] = pd.to_datetime(data['Date'], format=format_string_input, errors='coerce').dt.strftime(format_string_output_db)

    data = data.replace(np.nan, '')

    cols_to_format = ["Total Amount of Deposit", "Total Number of Deposit",
                      "Total Amount of Withdrawals", "Total Number of Withdrawals", "Total Commissions"]
    for col in cols_to_format:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

    data = data.applymap(lambda x: str(x).replace('.', ','))

    if 'Partner' in data.columns:
        data['Partner'] = data['Partner'].str.replace(',', '.', regex=False)
    # La colonne 'Date' est déjà au format YYYY/MM/DD, pas besoin de replace ici si c'est pour Oracle DATE type
    # Si c'est pour une comparaison de string, le format doit être cohérent.

    data_list = data.astype(str)
    data_list = list(data_list.to_records(index=False))

    cur.execute("""delete  from optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT""")
    conn.commit()

    cur.executemany("""INSERT INTO optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT("JOUR"
,"PARTNER"
,"PAYMENT_PROVIDER"
,"TOTAL_AMOUNT_OF_DEPOSIT"
,"TOTAL_NUMBER_OF_DEPOSIT"
,"TOTAL_AMOUNT_OF_WITHDRAWALS"
,"TOTAL_NUMBER_OF_WITHDRAWALS"
,"TOTAL_COMMISSIONS"
) VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""", data_list) # Retiré :9,:10 pour correspondre aux colonnes
    conn.commit()

    cur.execute(f"""delete  from  user_dwhpr.DTM_MISE_AFITECH_DAILYPAYMENT
WHERE idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
""")
    conn.commit()

    cur.execute("""insert into user_dwhpr.DTM_MISE_AFITECH_DAILYPAYMENT(
JOUR
,PARTNER
,PAYMENT_PROVIDER
,TOTAL_AMOUNT_OF_DEPOSIT
,TOTAL_NUMBER_OF_DEPOSIT
,TOTAL_AMOUNT_OF_WITHDRAWALS
,TOTAL_NUMBER_OF_WITHDRAWALS
,TOTAL_COMMISSIONS
,IDTEMPS,MOIS, ANNEE
)
(
SELECT to_char(to_date(trim(substr(f.jour,1,10)),'YYYY/mm/dd'),'DD/MM/YYYY') JOUR
        ,PARTNER
        ,PAYMENT_PROVIDER
        ,NVL(TOTAL_AMOUNT_OF_DEPOSIT,0)
        ,NVL(TOTAL_NUMBER_OF_DEPOSIT,0)
        ,NVL(TOTAL_AMOUNT_OF_WITHDRAWALS,0)
        ,NVL(TOTAL_NUMBER_OF_WITHDRAWALS,0)
        ,NVL(TOTAL_COMMISSIONS,0)
        ,Te.idtemps as IDTEMPS,Te.MOISC as MOIS,Te.ANNEEC as ANNEE
        FROM optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT F, user_dwhpr.DIM_TEMPS Te
        where to_date(trim(substr(f.jour,1,10)),'YYYY/mm/dd') = to_date(trim(substr(Te.jour,1,10)),'DD/MM/rr')
)
""")
    conn.commit()

    cur.execute("""delete  from optiwaretemp.SRC_PRD_AFITECH_DAILYPAYMENT""")
    conn.commit()
    print("La procedure d'insertion AFITECH Daily Payment Activity s'est bien deroulee")
