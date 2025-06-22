from datetime import date, timedelta
import calendar
import datetime
import pandas as pd
import numpy as np
import glob
import cx_Oracle
import pause # type: ignore
import shutil
import gc
import time

# Importation des fonctions de chargement spécifiques aux produits
from scripts.products.charge_bwinner import chargeBwinner
from scripts.products.charge_zeturf import chargeZeturf
from scripts.products.charge_virtuel_editec import chargeVirtuelEditec, load_financial_data, load_zone_betting_data, load_premier_sn_data
from scripts.products.charge_virtuel_amabel import chargeVirtuelAmabel
from scripts.products.charge_acajou import chargeAcajouDigitain, load_acajou_pick3_data, load_acajou_grattage_data, chargeAcajouPick3Grattage
from scripts.products.charge_gitech import chargeGitechAlr, chargeGitechCasino
from scripts.products.charge_lonasebet import chargeLonasebetCasino, chargeLonasebetAlrParifoot
from scripts.products.charge_honoregaming import chargeHonoregaming
from scripts.products.charge_afitech import chargeAFITECHCommissionHistory, chargeAFITECHDailyPaymentActivity
from scripts.products.charge_parifoot_online import chargeParifootonline
from scripts.products.charge_sunubet import load_sunubet_casino_data, load_sunubet_online_data, process_sunubet_data
from scripts.products.charge_ussd import LoadUSSDData, ChargeUSSD


delta = timedelta(days=1)
end_date = date.today()
start_date = end_date - delta
end_date = start_date + delta # Recalcul pour s'assurer que end_date est bien start_date + 1 jour

print(f"Date de début: {start_date}, Date de fin: {end_date}")

debut = start_date
fin = start_date # Les fonctions utilisent 'fin' comme la date de fin de la période à traiter, souvent start_date

#generalDirectory = r"X:\\DATA_FICHIERS\\"
generalDirectory = r"K:\\DATA_FICHIERS\\" # S'assurer que ce chemin est accessible

# Configuration de la connexion Oracle
username = 'USER_DWHPR'
password = 'optiware2016'
dsn_string = cx_Oracle.makedsn('192.168.1.237', 1521, service_name='DWHPR') # Renommé pour clarté

conn = None # Initialiser à None
cur = None  # Initialiser à None

try:
    try:
        # Tenter d'initialiser le client Oracle seulement si ce n'est pas déjà fait dans l'environnement
        # ou si cx_Oracle.clientversion() lève une exception si non initialisé.
        # La vérification cx_Oracle.clientversion() peut être plus robuste.
        client_version = cx_Oracle.clientversion()
        print(f"Client Oracle déjà initialisé, version: {client_version}")
    except cx_Oracle.DatabaseError as e:
        # Cette exception peut survenir si le client n'est pas du tout trouvé ou mal configuré.
        # L'initialisation est tentée si cx_Oracle.clientversion() échoue spécifiquement parce qu'il n'est pas initialisé.
        # Cependant, init_oracle_client doit être appelé avant toute autre fonction cx_Oracle.
        # Le bloc try/except original pour init_oracle_client est plus direct.
        pass # Garder le bloc original ci-dessous

    try:
        cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_6")
        print("Client Oracle initialisé avec succès.")
    except cx_Oracle.DatabaseError as e:
        if "already been initialized" in str(e):
            print("Le client Oracle a déjà été initialisé.")
        else:
            raise # Relancer si c'est une autre erreur d'initialisation
    except Exception as e: # Capturer d'autres exceptions potentielles (ex: NameError si cx_Oracle non importé)
        print(f"Erreur non attendue lors de l'initialisation du client Oracle: {e}")
        # Quitter ou gérer l'erreur de manière appropriée
        exit()


    conn = cx_Oracle.connect(username, password, dsn_string)
    cur = conn.cursor()
    print("Connexion à la base de données Oracle établie avec succès.")

    # BWINNER
    bwinner_directory = generalDirectory + r"BWINNERS\\"
    bwinner_file_pattern = bwinner_directory + f"**\\Bwinner_{str(start_date)}_{str(start_date)}.csv"
    bwinner_files = glob.glob(bwinner_file_pattern, recursive=True)
    print(f"Recherche fichiers Bwinner: {bwinner_file_pattern}, Trouvés: {len(bwinner_files)}")
    if not bwinner_files:
        print(f"Le fichier Bwinner du {start_date} n'a pas ete extrait.")
    else:
        bwinner_data = pd.read_csv(bwinner_files[0], sep=';', index_col=False)
        print("\n--- Traitement BWINNER ---")
        chargeBwinner(bwinner_data, debut, fin, conn, cur)

    # ZETURF
    zeturf_directory = generalDirectory + r"ZETURF\\"
    zeturf_file_pattern = zeturf_directory + f"**\\ZEturf {str(start_date)}.csv"
    zeturf_files = glob.glob(zeturf_file_pattern, recursive=True)
    print(f"Recherche fichiers Zeturf: {zeturf_file_pattern}, Trouvés: {len(zeturf_files)}")
    if not zeturf_files:
        print(f"Le fichier ZEturf du {start_date} n'a pas ete extrait.")
    else:
        zeturf_data = pd.read_csv(zeturf_files[0], sep=';', index_col=False)
        zeturf_data = pd.DataFrame(zeturf_data, columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du dÃ©part']) # Correction nom colonne
        print("\n--- Traitement ZETURF ---")
        chargeZeturf(zeturf_data, debut, fin, conn, cur)

    # VIRTUEL EDITEC (dépend de Financial, Zone Betting, PremierSN)
    print("\n--- Chargement des données sources pour VIRTUEL EDITEC ---")
    financial_loaded = load_financial_data(generalDirectory, start_date, conn, cur)
    zone_betting_loaded = load_zone_betting_data(generalDirectory, start_date, conn, cur)
    premier_sn_loaded = load_premier_sn_data(generalDirectory, start_date, conn, cur)

    if financial_loaded and zone_betting_loaded and premier_sn_loaded: # Ou une logique plus fine si certains peuvent manquer
        print("\n--- Traitement VIRTUEL EDITEC ---")
        chargeVirtuelEditec(debut, fin, conn, cur)
    else:
        print("Skipping VIRTUEL EDITEC due to missing source files.")

    # VIRTUEL AMABEL
    vamabel_directory = generalDirectory + r"VIRTUEL_AMABEL\\"
    vamabel_file_pattern = vamabel_directory + f"**\\virtuelAmabel{str(start_date)}.csv"
    vamabel_files = glob.glob(vamabel_file_pattern, recursive=True)
    print(f"Recherche fichiers Virtuel Amabel: {vamabel_file_pattern}, Trouvés: {len(vamabel_files)}")
    if not vamabel_files:
        print(f"Le fichier virtuelAmabel du {start_date} n'a pas ete extrait.")
    else:
        vamabel_data = pd.read_csv(vamabel_files[0], sep=';', index_col=False)
        print("\n--- Traitement VIRTUEL AMABEL ---")
        chargeVirtuelAmabel(vamabel_data, debut, fin, conn, cur)

    # ACAJOU DIGITAIN (Pari Sportif)
    acajou_digitain_dir = generalDirectory + r"ACAJOU\DIGITAIN\\"
    acajou_digitain_pattern = acajou_digitain_dir + f"**\\Listing_Tickets_Sports_betting {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv"
    acajou_digitain_files = glob.glob(acajou_digitain_pattern, recursive=True)
    print(f"Recherche fichiers Acajou Digitain: {acajou_digitain_pattern}, Trouvés: {len(acajou_digitain_files)}")
    if not acajou_digitain_files:
        print(f"Le fichier Acajou DIGITAIN du {start_date} n'a pas ete extrait.")
    else:
        acajou_digitain_data = pd.read_csv(acajou_digitain_files[0], sep=';', index_col=False)
        acajou_digitain_data = pd.DataFrame(acajou_digitain_data, columns=['Date Created', 'Ticket ID', 'Msisdn', 'Purchase Method', 'Collection','Gross Payout', 'Status'])
        print("\n--- Traitement ACAJOU DIGITAIN ---")
        chargeAcajouDigitain(acajou_digitain_data, debut, fin, conn, cur)

    # ACAJOU PICK3 & GRATTAGE
    print("\n--- Chargement des données sources pour ACAJOU PICK3 & GRATTAGE ---")
    pick3_loaded = load_acajou_pick3_data(generalDirectory, start_date, conn, cur)
    grattage_loaded = load_acajou_grattage_data(generalDirectory, start_date, conn, cur)
    if pick3_loaded or grattage_loaded: # Traiter si au moins un des fichiers est là
        print("\n--- Traitement ACAJOU PICK3 & GRATTAGE ---")
        chargeAcajouPick3Grattage(debut, fin, conn, cur) # La fonction interne gère les données de SRC_PRD_ACACIA
    else:
        print("Skipping ACAJOU PICK3 & GRATTAGE due to missing source files.")

    # GITECH ALR (+ PMU Online via Gitech)
    gitech_alr_dir = generalDirectory + r"GITECH\ALR\\"
    gitech_alr_pattern = gitech_alr_dir + f"**\\GITECH {str(start_date)}.csv"
    gitech_alr_files = glob.glob(gitech_alr_pattern, recursive=True)
    print(f"Recherche fichiers Gitech ALR: {gitech_alr_pattern}, Trouvés: {len(gitech_alr_files)}")
    if not gitech_alr_files:
        print(f"Le fichier ALR GITECH du {start_date} n'a pas ete extrait.")
    else:
        gitech_alr_data = pd.read_csv(gitech_alr_files[0], sep=';', index_col=False)
        gitech_alr_data = pd.DataFrame(gitech_alr_data, columns=['Agences', 'Operateur', 'Date vente', 'Vente', 'Annulation', 'Paiement'])
        print("\n--- Traitement GITECH ALR & PMU ONLINE (via Gitech) ---")
        chargeGitechAlr(gitech_alr_data, debut, fin, conn, cur)

    # GITECH CASINO
    gitech_casino_dir = generalDirectory + r"GITECH\CASINO\\"
    gitech_casino_pattern = gitech_casino_dir + f"**\\GITECH CASINO {str(start_date)}.csv"
    gitech_casino_files = glob.glob(gitech_casino_pattern, recursive=True)
    print(f"Recherche fichiers Gitech Casino: {gitech_casino_pattern}, Trouvés: {len(gitech_casino_files)}")
    if not gitech_casino_files:
        print(f"Le fichier CASINO GITECH du {start_date} n'a pas ete extrait.")
    else:
        gitech_casino_data = pd.read_csv(gitech_casino_files[0], sep=';', index_col=False)
        # Pas de renommage de colonnes explicite ici, la fonction chargeGitechCasino s'en charge
        print("\n--- Traitement GITECH CASINO ---")
        chargeGitechCasino(gitech_casino_data, debut, fin, conn, cur)

    # LONASEBET CASINO
    lonasebet_casino_dir = generalDirectory + r"LONASEBET\CASINO\\"
    lonasebet_casino_pattern = lonasebet_casino_dir + f"**\\casinoLonasebet {str(start_date)}.csv"
    lonasebet_casino_files = glob.glob(lonasebet_casino_pattern, recursive=True)
    print(f"Recherche fichiers Lonasebet Casino: {lonasebet_casino_pattern}, Trouvés: {len(lonasebet_casino_files)}")
    if not lonasebet_casino_files:
        print(f"Le fichier CASINO Lonasebet du {start_date} n'a pas ete extrait.")
    else:
        lonasebet_casino_data = pd.read_csv(lonasebet_casino_files[0], sep=';', index_col=False)
        lonasebet_casino_data = pd.DataFrame(lonasebet_casino_data, columns=["JOUR", "Stake", "PaidAmount"])
        print("\n--- Traitement LONASEBET CASINO ---")
        chargeLonasebetCasino(lonasebet_casino_data, debut, fin, conn, cur)

    # HONORE GAMING
    honore_dir = generalDirectory + r"HONORE_GAMING\\"
    # La date dans le nom de fichier est end_date (start_date + 1 jour)
    honore_pattern = honore_dir + f"**\\daily-modified-horse-racing-tickets-detailed_{str(end_date).replace('-','')}.csv"
    honore_files = glob.glob(honore_pattern, recursive=True)
    print(f"Recherche fichiers Honore Gaming: {honore_pattern}, Trouvés: {len(honore_files)}")
    if not honore_files:
        print(f"Le fichier HONORE_GAMING pour la date de rapport {end_date} (basé sur start_date {start_date}) n'a pas ete extrait.")
    else:
        # Le prétraitement des dates (commenté dans l'original) est omis ici,
        # en supposant que la fonction chargeHonoregaming peut gérer le format CSV brut
        # ou que le format est déjà correct.
        honore_data = pd.read_csv(honore_files[0], sep=';', index_col=False)
        # S'assurer que toutes les colonnes attendues par chargeHonoregaming sont présentes
        # (le code original ne spécifiait pas de colonnes pour Honore Gaming avant l'appel)
        print("\n--- Traitement HONORE GAMING ---")
        chargeHonoregaming(honore_data, debut, fin, conn, cur)

    # AFITECH COMMISSION HISTORY
    afitech_comm_dir = generalDirectory + r"AFITECH\CommissionHistory\\"
    firstDayOfMonth = date(start_date.year, start_date.month, 1)
    afitech_comm_pattern = afitech_comm_dir + f"**\\AFITECH_CommissionHistory {str(firstDayOfMonth)}_{str(start_date)}.csv"
    afitech_comm_files = glob.glob(afitech_comm_pattern, recursive=True)
    print(f"Recherche fichiers Afitech Commission: {afitech_comm_pattern}, Trouvés: {len(afitech_comm_files)}")
    if not afitech_comm_files:
        print(f"Le fichier AFITECH_CommissionHistory du {start_date} (période depuis {firstDayOfMonth}) n'a pas ete extrait.")
    else:
        afitech_comm_data = pd.read_csv(afitech_comm_files[0], sep=';', index_col=False)
        print("\n--- Traitement AFITECH COMMISSION HISTORY ---")
        chargeAFITECHCommissionHistory(afitech_comm_data, debut, fin, conn, cur, firstDayOfMonth)

    # AFITECH DAILY PAYMENT ACTIVITY
    afitech_daily_dir = generalDirectory + r"AFITECH\DailyPaymentActivity\\"
    afitech_daily_pattern = afitech_daily_dir + f"**\\AFITECH_DailyPaymentActivity {str(start_date)}_{str(start_date)}.csv"
    afitech_daily_files = glob.glob(afitech_daily_pattern, recursive=True)
    print(f"Recherche fichiers Afitech Daily Payment: {afitech_daily_pattern}, Trouvés: {len(afitech_daily_files)}")
    if not afitech_daily_files:
        print(f"Le fichier AFITECH_DailyPaymentActivity du {start_date} n'a pas ete extrait.")
    else:
        afitech_daily_data = pd.read_csv(afitech_daily_files[0], sep=';', index_col=False)
        print("\n--- Traitement AFITECH DAILY PAYMENT ACTIVITY ---")
        chargeAFITECHDailyPaymentActivity(afitech_daily_data, debut, fin, conn, cur)

    # LONASEBET ALR/PARIFOOT/VIRTUEL (OnlineLonasebet)
    lonasebet_online_dir = generalDirectory + r"LONASEBET\ALR_PARIFOOT\\"
    lonasebet_online_pattern = lonasebet_online_dir + f"**\\OnlineLonasebet {str(start_date)}.csv"
    lonasebet_online_files = glob.glob(lonasebet_online_pattern, recursive=True)
    print(f"Recherche fichiers Lonasebet Online: {lonasebet_online_pattern}, Trouvés: {len(lonasebet_online_files)}")
    if not lonasebet_online_files:
        print(f"Le fichier OnlineLonasebet du {start_date} n'a pas ete extrait.")
    else:
        lonasebet_online_data = pd.read_csv(lonasebet_online_files[0], sep=';', index_col=False)
        lonasebet_online_data = pd.DataFrame(lonasebet_online_data, columns=["BetId", "JOUR", "Stake", "BetCategory", "State", "PaidAmount", "CustomerLogin", "Freebet"])
        print("\n--- Traitement LONASEBET ALR/PARIFOOT/VIRTUEL ---")
        chargeLonasebetAlrParifoot(lonasebet_online_data, debut, fin, conn, cur)

    # PARIFOOT ONLINE (Premierbet)
    parifoot_online_dir = generalDirectory + r"PARIFOOT_ONLINE\\"
    parifoot_online_pattern = parifoot_online_dir + f"**\\ParifootOnline {str(start_date)}.csv"
    parifoot_online_files = glob.glob(parifoot_online_pattern, recursive=True)
    print(f"Recherche fichiers Parifoot Online: {parifoot_online_pattern}, Trouvés: {len(parifoot_online_files)}")
    if not parifoot_online_files:
        print(f"Le fichier ParifootOnline du {start_date} n'a pas ete extrait.")
    else:
        parifoot_online_data = pd.read_csv(parifoot_online_files[0], sep=';', index_col=False)
        parifoot_online_data = pd.DataFrame(parifoot_online_data,columns=['Unnamed: 0','Username', 'Balance', 'Total Players','Total Players Date Range', 'SB Bets No.', 'SB Stake','SB Closed Stake', 'SB Wins No.', 'SB Wins', 'SB Ref No.', 'SB Refunds','SB GGR', 'Cas.Bets No.', 'Cas.Stake', 'Cas.Wins No.', 'Cas.Wins','Cas.Ref No.', 'Cas.Refunds', 'Cas.GGR', 'Total GGR', 'Adjustments','Deposits', 'Financial Deposits', 'Financial Withdrawals','Transaction Fee', 'date'])
        print("\n--- Traitement PARIFOOT ONLINE ---")
        chargeParifootonline(parifoot_online_data, debut, fin, conn, cur)

    # SUNUBET (Casino et Online)
    print("\n--- Chargement et Traitement SUNUBET ---")
    # Vider les tables temporaires avant de commencer
    if cur:
        cur.execute("""truncate table OPTIWARETEMP.src_prd_sunubet_online""")
        cur.execute("""truncate table OPTIWARETEMP.SRC_PRD_SUNUBET_CASINO""")
        conn.commit()

    casino_loaded = load_sunubet_casino_data(generalDirectory, start_date, conn, cur)
    online_loaded = load_sunubet_online_data(generalDirectory, start_date, conn, cur)
    if casino_loaded or online_loaded: # Traiter si au moins un est chargé
        process_sunubet_data(conn, cur)
    else:
        print("Skipping SUNUBET processing due to missing source files.")

    # USSD
    print("\n--- Chargement et Traitement USSD ---")
    # Vider la table temporaire principale pour USSD si nécessaire avant LoadUSSDData
    # La fonction LoadUSSDData tronque TEMP_USSD_IVR
    if LoadUSSDData(generalDirectory, start_date, conn, cur): # LoadUSSDData retourne True/False
        ChargeUSSD(debut, fin, conn, cur) # ChargeUSSD utilise les données de TEMP_USSD_IVR
    else:
        print(f"Le fichier USSD du {start_date} n'a pas ete chargé, skip du traitement USSD.")


    # Scripts externes existants (conservés tels quels)
    print("\n--- Exécution des scripts externes ---")
    try:
        print("\nExécution insertPmuSenegal.py")
        # Il faut s'assurer que ce script peut accéder à conn, cur, debut, fin s'il en a besoin
        # ou qu'il gère sa propre connexion et ses propres dates.
        # Pour l'instant, on suppose qu'il est autonome ou utilise des variables globales
        # qui seraient définies dans son propre scope lors de l'exec.
        # Si ces scripts modifiés attendent conn, cur, etc., il faudra les passer.
        with open("C:\\Batchs\\scripts_python\\extractions\\journalier\\insertPmuSenegal.py") as f:
            exec(f.read(), {"conn": conn, "cur": cur, "debut": debut, "fin": fin, "generalDirectory": generalDirectory, "start_date":start_date, "end_date":end_date}) # Example de passage de variables
    except FileNotFoundError:
        print("Erreur: Le fichier insertPmuSenegal.py est introuvable.")
    except Exception as e:
        print(f"Erreur lors de l'exécution de insertPmuSenegal.py: {e}")

    try:
        print("\nExécution insertMiniShopOracle_bis.py")
        with open("C:\\Batchs\\scripts_python\\extractions\\journalier\\insertMiniShopOracle_bis.py") as f:
             exec(f.read(), {"conn": conn, "cur": cur, "debut": debut, "fin": fin, "generalDirectory": generalDirectory, "start_date":start_date, "end_date":end_date})
    except FileNotFoundError:
        print("Erreur: Le fichier insertMiniShopOracle_bis.py est introuvable.")
    except Exception as e:
        print(f"Erreur lors de l'exécution de insertMiniShopOracle_bis.py: {e}")


    print("\nFin de toutes les insertions sur Oracle.")

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"Erreur Oracle: {error.code} - {error.message}")
except FileNotFoundError as e:
    print(f"Erreur de fichier non trouvé: {e}")
except Exception as e:
    print(f"Une erreur générale est survenue: {e}")
    import traceback
    traceback.print_exc()
finally:
    if cur:
        cur.close()
        print("Curseur Oracle fermé.")
    if conn:
        conn.close()
        print("Connexion Oracle fermée.")

    # Nettoyage de la mémoire
    gc.collect()
    print("Garbage collection effectuée.")

# Pause jusqu'au lendemain (logique originale commentée, conservée pour référence)
# nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=0, minute=10, second=0, microsecond=0)
# pause.until(nextday)
# print(f"----------FIN:{str(datetime.now())}--------------------------")
