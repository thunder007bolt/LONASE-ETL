import os
import subprocess
import time
import shutil, sys
import gc
from datetime import date, datetime, timedelta
import pause
import glob

TEMP_DIR = r"C:\Users\optiware\AppData\Local\Temp\gen_py\3.7"
SCRIPTS_DIR = r"C:\ETL\old_scripts"
JOURNALIER_DIR = os.path.join(SCRIPTS_DIR, "journalier")

processes = []

def kill_excel():
    try:
        os.system("taskkill /im excel.exe /f")
    except Exception as e:
        print(f"Erreur lors de la fermeture d'Excel : {e}")

def clear_temp():
    try:
        shutil.rmtree(TEMP_DIR)
    except OSError as o:
        print(f"Erreur : {o.strerror}")

def run_script(path):
    print(f"\n--- Lancement (parallèle) : {os.path.basename(path)} ---\n")
    try:
        process = subprocess.Popen(["python", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append((path, process))
    except Exception as e:
        print(f"Erreur d'exécution pour {path} : {e}")

def exec_script(path):
    print(f"\n--- Execution : {os.path.basename(path)} ---\n")
    try:
        exec(open(path, encoding='utf-8').read())
    except Exception as e:
        print(f"Erreur d'exécution pour {path} : {e}")

def main_cycle():
    while True:
        kill_excel()
        #clear_temp()

        pause.until(datetime.combine(date.today(), datetime.min.time()).replace(hour=5))

        run_script(os.path.join(SCRIPTS_DIR, "extract_DigitainAcajou.py"))
        exec_script(os.path.join(SCRIPTS_DIR, "extract_HonoreGaming.py"))
        exec_script(os.path.join(JOURNALIER_DIR, "insertHonoregamingOnOracleDatabase.py"))

        # Pause avant les scripts de 4h45
        pause.until(datetime.combine(date.today(), datetime.min.time()).replace(hour=4, minute=45))

        # Afitech
        #run_script(os.path.join(SCRIPTS_DIR, "extract_afitech - DailyPaymentActivity.py"))

        ps =60*3
        time.sleep(ps)
        # Autres extractions
        run_script(os.path.join(SCRIPTS_DIR, "extract_Bwinners.py"))
        run_script(os.path.join(SCRIPTS_DIR, "extract_Bwinner_GAMBIE.py"))
        run_script(os.path.join(SCRIPTS_DIR, "extract_DigitainAcajou.py"))

        time.sleep(ps)  # Pause de 3 minutes

        run_script(os.path.join(SCRIPTS_DIR, "extract_gitech.py"))
        run_script(os.path.join(SCRIPTS_DIR, "extract_CASINO_gitech.py"))
        
        time.sleep(ps)
        run_script(os.path.join(SCRIPTS_DIR, "extract_gitech_physique.py"))
        run_script(os.path.join(SCRIPTS_DIR, "extract_virtuelAmabel.py"))

        time.sleep(ps)  # Pause de 3 minutes
        # Lonase et Sunubet
        run_script(os.path.join(SCRIPTS_DIR, "extract_CasinoLonasebett.py"))
        run_script(os.path.join(SCRIPTS_DIR, "extract_OnlineLonasebett.py"))

        time.sleep(ps)
        run_script(os.path.join(SCRIPTS_DIR, "extract_OnlineSunubett.py"))
        run_script(os.path.join(SCRIPTS_DIR, "extract_CasinoSunubett.py"))

        time.sleep(ps)
        # Lonase et Sunubet
        run_script(os.path.join(SCRIPTS_DIR, "extract_Mini_Shop.py"))
        run_script(os.path.join(SCRIPTS_DIR, "extract_parifoot_online.py"))
        
        time.sleep(ps)
        run_script(os.path.join(SCRIPTS_DIR, "extract_Pmu_Senegal_CA.py"))
        run_script(os.path.join(SCRIPTS_DIR, "extract_zeturf.py"))

        run_script(os.path.join(SCRIPTS_DIR, "HG_ticket_pari.py"))
        #run_script(os.path.join(SCRIPTS_DIR, "extract_Mojabet.py"))

        print("\n=== Fin du cycle, attente 5 min avant redémarrage ===\n")
        time.sleep(300)

if __name__ == "__main__":
    main_cycle()
