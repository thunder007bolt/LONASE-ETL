from datetime import date,timedelta #,datetime,timedelta
import calendar
import datetime

import pandas as pd
import numpy as np


import time


hour = 3600


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()#-5*delta
currentYear = end_date.strftime("%Y")
#currentYear = '2024'
currentDay = end_date.strftime("%d/%m/%y")
print(currentDay)

print(datetime.datetime.now())

jour = ''

if int(end_date.strftime("%d")) < 15 :
    jour = datetime.date((end_date).year, (end_date).month, 1) -  delta
else:
    jour = datetime.date((end_date -  delta).year, (end_date -  delta).month, 15)

jour = datetime.date(2025, 4, 15)
annee = (jour).year
mois = jour.strftime("%m")

jour = jour.strftime("%d")

print(jour,mois,annee)


#debut = '01-02-2025'
#fin = '15-02-2025'

#start_date = datetime.date(2025, 2, 1)
#end_date = start_date+delta
#end_date = datetime.date(2025, 2, 16)


#debut = start_date
#fin = end_date-delta
**
def wait_until_day_is_valid():
    while True:
        # Get the current date and day
        current_day = datetime.now().day
        
        # Check if it's the 18th or the 3rd
        if current_day == 18 or current_day == 3:
            #print(f"Today is {current_day}, continuing the script.")
            break
        
        # If not, sleep for a while before checking again (e.g., 1 hour)
        #print(f"Today is {current_day}, waiting for the right day...")
        time.sleep(hour)  # sleep for 1 hour (3600 seconds)

# Call the function to pause the script
#wait_until_day_is_valid()

import pyodbc
SERVER = 'SRVSQLDWHPRD'
DATABASE = 'DWHPR'
USERNAME = 'USER_DWHPR'
PASSWORD = 'optiware2016'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
conn2 = pyodbc.connect(connectionString)
cursor2 = conn2.cursor()

#print("insertion des donnees au niveau de la table temporaire")

query = f"""
SELECT *
FROM [SRVBDD3\LONASE].[LONASE_SIC].[dbo].[commission_bi]
WHERE year([QUINZAINE])= '{annee}'  
  AND MONTH([QUINZAINE])= '{mois}' 
  AND DAY([QUINZAINE]) = '{jour}'

  """
data = pd.read_sql(query, con=conn2)

#cursor2.execute(""" """)
#conn2.commit()

#data['MONTANT'] = [str(i).replace('.',',') for i in data['MONTANT']]
#data['QUINZAINE'] = [datetime.datetime.strptime(str(i)[:10], "%Y-%m-%d").strftime("%d/%m/%Y") for i in data['QUINZAINE']]
data['QUINZAINE'] = [datetime.datetime.strptime(str(i)[:10], "%d-%m-%Y").strftime("%d/%m/%Y") for i in data['QUINZAINE']]

#print(data.columns)

cursor2.execute("{CALL [USER_DWHPR].[PROC_COMMISSION](?, ?, ?)}", (annee, mois, jour))
conn2.commit()
#print("insertion des donnees au niveau de la table temporaire")

query = f"""
SELECT *
FROM [SRVBDD3\LONASE].[LONASE_SIC].[dbo].[commission_bi]
WHERE year([QUINZAINE])= '{annee}'  
  AND MONTH([QUINZAINE])= '{mois}' 
  AND DAY([QUINZAINE]) = '{jour}'

  """
data = pd.read_sql(query, con=conn2)

#cursor2.execute(""" """)
#conn2.commit()

#data['MONTANT'] = [str(i).replace('.',',') for i in data['MONTANT']]
#data['QUINZAINE'] = [datetime.datetime.strptime(str(i)[:10], "%Y-%m-%d").strftime("%d/%m/%Y") for i in data['QUINZAINE']]
data['QUINZAINE'] = [datetime.datetime.strptime(str(i)[:10], "%d-%m-%Y").strftime("%d/%m/%Y") for i in data['QUINZAINE']]

#print(data.columns)

cursor2.execute("{CALL [USER_DWHPR].[PROC_COMMISSION](?, ?, ?)}", (annee, mois, jour))
conn2.commit()

username = 'USER_DWHPR'
password = 'optiware2016'

#dsn = '192.168.1.237/OPTIWARE_TEMP'
dsn = cx_Oracle.makedsn('192.168.1.237', 1521, service_name='DWHPR')
port = 1521
encoding = 'UTF-8'

try:
    cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_6")
except:
    print("La base de donnee a deja ete initialisee")

conn1 = cx_Oracle.connect(username,password,dsn)
cur1 = conn1.cursor() #creates a cursor object

data = data.replace(np.nan, '')
data = data.applymap(lambda x: str(x).replace('.',','))
#data['Date'] = data['Date'].str.replace('-', '/',regex=False)
data=data.astype(str)
data = list(data.to_records(index=False))


cur1.execute("""truncate table OPTIWARETEMP.SRC_COMMISSION_PRD """)
conn1.commit()

        
cur1.executemany("""INSERT INTO OPTIWARETEMP.SRC_COMMISSION_PRD("QUINZAINE"
      ,"AGENCE"
      ,"PRODUIT"
      ,"IDENTIFIANT"
      ,"PRENOM"
      ,"NOM"
      ,"CA_CAL"
      ,"CA_V"
      ,"REMB"
      ,"COM_B"
      ,"ECART"
      ,"RET_F"
      ,"DEC_AN"
      ,"ENG"
      ,"MUS"
      ,"DEC_AC"
      ,"REGUL"
      ,"COM_N") VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18)""", data)
conn1.commit()

cur1.execute("""
delete from USER_DWHPR.SIC_COMMISSION
where IDTEMPS in (select distinct IDTEMPS from USER_DWHPR.DIM_TEMPS, OPTIWARETEMP.SRC_COMMISSION_PRD where JOUR = QUINZAINE)
""")
conn1.commit()

        
cur1.execute("""
INSERT INTO "USER_DWHPR"."SIC_COMMISSION" (IDENTIFIANT, IDTEMPS, AGENCE, SHOPS, PRODUIT, CA_CAL, CA_V, REMB, COM_B, ECART, RET_F, DEC_AN, ENG, MUS, DEC_AC, REGUL, COM_N)

 SELECT F.IDENTIFIANT, Te.IDTEMPS, F.AGENCE, F.SHOPS, F.PRODUIT, F.CA_CAL, F.CA_V, F.REMB, F.COM_B, F.ECART, F.RET_F, F.DEC_AN, F.ENG, F.MUS, F.DEC_AC, F.REGUL, F.COM_N
   FROM (
             SELECT  QUINZAINE, CASE
                    WHEN AGENCE LIKE 'SAINT LOUIS'	 THEN 	'Saint-Louis'
                    WHEN AGENCE LIKE 'RICHARD TOLL'	 THEN 	'Saint-Louis'
                    WHEN AGENCE LIKE 'KEDOUGOU'	 THEN 	'Tamba'
                    WHEN AGENCE LIKE 'KOLDA'	 THEN 	'Ziguinchor'
                    WHEN AGENCE LIKE 'MATAM'	 THEN 	'Tamba'
                    WHEN AGENCE LIKE 'ZIGUINCHOR'	 THEN 	'Ziguinchor'
                    WHEN AGENCE LIKE 'THIES'	 THEN 	'Thies'
                    WHEN AGENCE LIKE 'FATICK'	 THEN 	'Fatick'
                    WHEN AGENCE LIKE 'PLATEAU'	 THEN 	'Plateau'
                    WHEN AGENCE LIKE 'PIKINE'	 THEN 	'Pikine'
                    WHEN AGENCE LIKE 'MBACKE'	 THEN 	'Diourbel'
                    WHEN AGENCE LIKE 'RUFISQUE'	 THEN 	'Rufisque'
                    WHEN AGENCE LIKE 'DAHRA'	 THEN 	'Louga'
                    WHEN AGENCE LIKE 'TAMBA'	 THEN 	'Tamba'
                    WHEN AGENCE LIKE 'MEDINA'	 THEN 	'Medina'
                    WHEN AGENCE LIKE 'LOUGA'	 THEN 	'Louga'
                    WHEN AGENCE LIKE 'DIOURBEL'	 THEN 	'Diourbel'
                    WHEN AGENCE LIKE 'KAFFRINE'	 THEN 	'Kaolack'
                    WHEN AGENCE LIKE 'PARCELLES'	 THEN 	'Parcelles'
                    WHEN AGENCE LIKE 'KAOLACK'	 THEN 	'Kaolack'
                    WHEN AGENCE LIKE 'GRAND DAKAR'	 THEN 	'Grand Dakar'
                    WHEN AGENCE LIKE 'BAMBEY'	 THEN 	'Diourbel'
                    WHEN AGENCE LIKE 'GUEDIAWAYE'	 THEN 	'Guediawaye'
                    WHEN AGENCE LIKE 'MBOUR'	 THEN 	'Mbour' END AGENCE
                    ,AGENCE SHOPS, PRODUIT, IDENTIFIANT, PRENOM, NOM, CA_CAL,CA_V, REMB, COM_B, ECART, RET_F, DEC_AN, ENG, MUS, DEC_AC, REGUL, COM_N
              FROM  OPTIWARETEMP.SRC_COMMISSION_PRD  
         ) F, DIM_CCS C, DIM_TEMPS Te
WHERE F.AGENCE= C.NOMCCS
  AND F.QUINZAINE= Te.JOUR
  """)
conn1.commit()
print("Processus effectué")
cur1.close()
conn1.close()  