TEMP_DIR = r"C:\Users\OPTIWA~1\AppData\Local\Temp\gen_py\3.13"
import shutil
shutil.rmtree(TEMP_DIR)
'''

 c:/anaconda/anaconda3/python.exe

import os
os.system("taskkill /im chrome.exe /f")

import pyodbc

# Connexion à SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=nom_ou_ip_du_serveur;'
    'DATABASE=msdb;'
    'UID=ton_utilisateur;'
    'PWD=ton_mot_de_passe;'
)

cursor = conn.cursor()

# Nom du job SQL Server à lancer
job_name = 'NomDeTonJob'

try:
    cursor.execute(f"EXEC msdb.dbo.sp_start_job N'{job_name}'")
    conn.commit()
    print(f"Le job '{job_name}' a été lancé avec succès.")
except Exception as e:
    print("Erreur lors du lancement du job :", e)
finally:
    cursor.close()
    conn.close()
'''
import win32com.client.gencache
win32com.client.gencache.is_readonly = False
win32com.client.gencache.Rebuild()
TEMP_DIR = r"C:\Users\OPTIWA~1\AppData\Local\Temp\gen_py\3.13"
SCRIPTS_DIR = r"C:\ETL\Base"
JOURNALIER_DIR = r"C:\ETL\Base\journalier"

processes = []
try:
    import os
    os.system("taskkill /im excel.exe /f")
except Exception as e:
    print(f"Erreur lors de la fermeture d'Excel : {e}")

try:
    shutil.rmtree(TEMP_DIR)
except OSError as o:
    print(f"Erreur : {o.strerror}")
"""
04-27 Jour non viable
04-20 
04-10
04-08
04-04
"""
