import os
import subprocess
import time
import shutil, sys
import gc
from datetime import date, datetime, timedelta

TEMP_DIR = r"C:\Users\OPTIWA~1\AppData\Local\Temp\gen_py\3.13"
SCRIPTS_DIR = r"C:\ETL\Base"
JOURNALIER_DIR = r"C:\ETL\Base\journalier"

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
    print(f"\n--- Lancement (séquentiel) : {os.path.basename(path)} ---\n")
    try:
        result = subprocess.run(["python", path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Erreurs pour {path} :\n{result.stderr}")
    except Exception as e:
        print(f"Erreur d'exécution pour {path} : {e}")

def exec_script(path):
    print(f"\n--- Execution : {os.path.basename(path)} ---\n")
    try:
        exec(open(path, encoding='utf-8').read())
    except Exception as e:
        print(f"Erreur d'exécution pour {path} : {e}")

script_afitech_daily = os.path.join(SCRIPTS_DIR, "extract_afitech - DailyPaymentActivity.py")
script_afitech_commission = os.path.join(SCRIPTS_DIR, "extract_afitech - CommissionHistory.py")
script_bwinners = os.path.join(SCRIPTS_DIR, "extract_Bwinners.py")
script_bwinner_gambie = os.path.join(SCRIPTS_DIR, "extract_Bwinner_GAMBIE.py")
script_digitain_acajou = os.path.join(SCRIPTS_DIR, "extract_DigitainAcajou.py")
script_gitech = os.path.join(SCRIPTS_DIR, "extract_gitech.py")
script_casino_gitech = os.path.join(SCRIPTS_DIR, "extract_CASINO_gitech.py")
script_gitech_physique = os.path.join(SCRIPTS_DIR, "extract_gitech_physique.py")
script_virtuel_amabel = os.path.join(SCRIPTS_DIR, "extract_virtuelAmabel.py")
script_casino_lonasebett = os.path.join(SCRIPTS_DIR, "extract_CasinoLonasebett.py")
script_online_lonasebett = os.path.join(SCRIPTS_DIR, "extract_OnlineLonasebett.py")
script_mini_shop = os.path.join(SCRIPTS_DIR, "extract_Mini_Shop.py")
script_parifoot_online = os.path.join(SCRIPTS_DIR, "extract_parifoot_online.py")
script_pmu_senegal_ca = os.path.join(SCRIPTS_DIR, "extract_Pmu_Senegal_CA.py")
script_pmu_senegal_lot = os.path.join(SCRIPTS_DIR, "extract_Pmu_Senegal_Lot.py")
script_zeturf = os.path.join(SCRIPTS_DIR, "extract_zeturf.py")
#script_honore_gaming = os.path.join(SCRIPTS_DIR, "extract_HonoreGaming.py")
#script_insert_honore_oracle = os.path.join(JOURNALIER_DIR, "insertHonoregamingOnOracleDatabase.py")
#script_hg_ticket_pari = os.path.join(SCRIPTS_DIR, "HG_ticket_pari.py")
script_casino_sunubett = os.path.join(SCRIPTS_DIR, "extract_CasinoSunubett.py")
script_online_sunubett = os.path.join(SCRIPTS_DIR, "extract_OnlineSunubett.py")
script_ussd = os.path.join(SCRIPTS_DIR, "extract_ussd_irv.py")

def main_cycle():
    print("\n=== Debut ===\n")
    # Définir tous les chemins des scripts comme des variables

    ps = 10  # Durée en secondes pour les pauses

    # Exécution des scripts avec les variables de chemin
    # afitech
    run_script(script_afitech_daily)
    run_script(script_afitech_commission)
    '''
    #'''

    # bwinners
    run_script(script_bwinners)
    run_script(script_bwinner_gambie)
    
    #'''
    run_script(script_digitain_acajou)
    #'''

    # gitech
    #run_script(script_gitech)
    #run_script(script_casino_gitech)
    run_script(script_gitech_physique)
    
    run_script(script_virtuel_amabel)

    # lonasebet
    run_script(script_casino_lonasebett)
    #run_script(script_online_lonasebett)

    run_script(script_mini_shop)
    run_script(script_parifoot_online)
    run_script(script_zeturf)

    # sunubet
    run_script(script_casino_sunubett)
    run_script(script_online_sunubett)
    
    # pmu
    #run_script(script_pmu_senegal_ca)


    '''
    run_script(script_pmu_senegal_lot)
    run_script(script_hg_ticket_pari)
    run_script(script_honore_gaming)
    run_script(script_insert_honore_oracle)
    '''
    run_script(script_ussd)
    print("\n=== Fin ===\n")
    exit(0)


if __name__ == "__main__":
    main_cycle()


