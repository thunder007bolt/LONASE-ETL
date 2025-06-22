import sys
import os
from datetime import date, timedelta, datetime
import glob
import logging
import pandas as pd # Gardé pour une éventuelle lecture directe si un inserter le requiert

# Ajout du chemin du projet au sys.path pour permettre les importations relatives
# Supposons que ce script est dans scripts/autres/ et que les modules sont à la racine ou dans utils/ etc.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from product_inserters import (
    BwinnerInserter,
    ZeturfInserter,
    VirtuelEditecInserter,
    VirtuelAmabelInserter,
    AcajouDigitainInserter,
    AcajouPick3GrattageInserter,
    GitechAlrInserter,
    GitechCasinoInserter,
    LonasebetCasinoInserter,
    HonoreGamingInserter,
    AfitechCommissionHistoryInserter,
    AfitechDailyPaymentActivityInserter,
    LonasebetAlrParifootInserter,
    ParifootOnlineInserter,
    SunubetInserter,
    UssdInserter,
    PmuSenegalInserter,
    MiniShopInserter
)
from utils.logger import setup_logger # Supposons un module logger simple

# --- Configuration Globale ---
LOG_LEVEL = logging.INFO # ou logging.DEBUG pour plus de détails
main_logger = setup_logger('insert_all_products_main', 'insert_all_products_main.log', level=LOG_LEVEL)

# Dates - Identique à la logique originale
delta_one_day = timedelta(days=1)
current_day = date.today()
start_date_param = current_day - delta_one_day # J-1, pour les données
end_date_param = current_day # J, pour la borne supérieure des requêtes (souvent J-1 inclus)

# Convertir les dates en chaînes format DD/MM/YYYY pour les inserters
# Les inserters s'attendent à ce que date_debut soit J-1 et date_fin soit J-1 (ou J pour la borne de requête)
# Le script original utilise `debut` (start_date) et `fin` (end_date - delta = start_date) pour les plages de données.
# Et `start_date` pour les noms de fichiers (qui est J-1).
# `end_date` (J) est parfois utilisé comme borne sup.

# date_debut_inserter: Date de début pour les requêtes (format 'DD/MM/YYYY') -> correspond à `debut` du script original
date_debut_str = start_date_param.strftime('%d/%m/%Y')
# date_fin_inserter: Date de fin pour les requêtes (format 'DD/MM/YYYY') -> correspond à `fin` du script original (qui est aussi start_date)
# Cependant, les requêtes MERGE utilisent souvent une plage incluant le jour même (end_date original).
# Clarifions:
# - Fichiers sont nommés avec `start_date_param` (J-1).
# - Données à supprimer/insérer concernent la période de `start_date_param`.
# - Les merges dans DTM_CA_DAILY se font sur `start_date_param`.
# ProductInserter attend date_debut et date_fin pour définir la période à traiter.
# Pour la plupart des cas, date_debut = date_fin = start_date_param (J-1).
date_fin_str = start_date_param.strftime('%d/%m/%Y')

# Pour les cas spécifiques comme AFITECH Commission History qui utilise une plage plus large pour le delete
# ou HonoreGaming qui utilise end_date (current_day) pour le nom du fichier,
# les inserters devront gérer cela en interne ou recevoir des dates ajustées.
# Pour l'instant, on passe J-1 comme date_debut et date_fin à la plupart des inserters.

main_logger.info(f"Date de début (données J-1): {start_date_param.strftime('%Y-%m-%d')}")
main_logger.info(f"Date de fin (borne requêtes, souvent J-1): {start_date_param.strftime('%Y-%m-%d')}")
main_logger.info(f"Date actuelle (J, pour certains noms de fichiers): {current_day.strftime('%Y-%m-%d')}")


general_directory = r"K:\\DATA_FICHIERS\\" # Chemin Windows
# Pour la portabilité, envisager os.path.join ou Pathlib si possible, mais K:\ est spécifique.

# Configuration de la base de données Oracle
db_config = {
    'username': 'USER_DWHPR',
    'password': 'optiware2016', # Idéalement, à gérer via des variables d'environnement ou un fichier de config sécurisé
    'host': '192.168.1.237',
    'port': 1521,
    'service_name': 'DWHPR',
    'lib_dir': r"C:\instantclient_21_6" # Chemin du client Oracle
}

# Initialisation du client Oracle (une seule fois)
# La classe ProductInserter s'en charge maintenant via db_utils.get_oracle_connection
# try:
#     import cx_Oracle
#     if db_config.get('lib_dir') and not os.environ.get("PATH", "").startswith(db_config.get('lib_dir')):
#          cx_Oracle.init_oracle_client(lib_dir=db_config['lib_dir'])
#          main_logger.info(f"Oracle client initialized with lib_dir: {db_config['lib_dir']}")
# except Exception as e:
#     main_logger.warning(f"Oracle client initialization issue (might be already initialized or path issue): {e}")


# --- Structure principale de traitement des produits ---
# Chaque produit sera traité dans un bloc try/except pour isoler les erreurs.

product_processors = {
    "BWINNER": {
        "inserter_class": BwinnerInserter,
        "file_pattern": general_directory + rf"BWINNERS/**/Bwinner_{start_date_param.strftime('%Y-%m-%d')}_{start_date_param.strftime('%Y-%m-%d')}.csv",
        "requires_file": True,
    },
    "ZETURF": {
        "inserter_class": ZeturfInserter,
        "file_pattern": general_directory + rf"ZETURF/**/ZEturf {start_date_param.strftime('%Y-%m-%d')}.csv",
        "requires_file": True,
    },
    "VIRTUEL_EDITEC": { # Cet inserter gère ses propres fichiers
        "inserter_class": VirtuelEditecInserter,
        "base_path_param": general_directory, # Passe le chemin de base à l'inserter
        "requires_file": False, # Les fichiers sont cherchés par l'inserter lui-même
    },
    "VIRTUEL_AMABEL": {
        "inserter_class": VirtuelAmabelInserter,
        "file_pattern": general_directory + rf"VIRTUEL_AMABEL/**/virtuelAmabel{start_date_param.strftime('%Y-%m-%d')}.csv",
        "requires_file": True,
    },
    "ACAJOU_DIGITAIN": { # Pari Sportif
        "inserter_class": AcajouDigitainInserter,
        "file_pattern": general_directory + rf"ACAJOU/DIGITAIN/**/Listing_Tickets_Sports_betting {start_date_param.strftime('%Y%m%d')}_{start_date_param.strftime('%Y%m%d')}.csv",
        "requires_file": True,
    },
    "ACAJOU_PICK3_GRATTAGE": { # Gère Pick3 et Grattage
        "inserter_class": AcajouPick3GrattageInserter,
        "base_path_param": general_directory,
        "requires_file": False, # Les fichiers sont cherchés par l'inserter
    },
    "GITECH_ALR_PMUONLINE": { # Gère ALR Gitech et PMU Online Gitech
        "inserter_class": GitechAlrInserter,
        "file_pattern": general_directory + rf"GITECH/ALR/**/GITECH {start_date_param.strftime('%Y-%m-%d')}.csv",
        "requires_file": True,
    },
    "GITECH_CASINO": {
        "inserter_class": GitechCasinoInserter,
        "file_pattern": general_directory + rf"GITECH/CASINO/**/GITECH CASINO {start_date_param.strftime('%Y-%m-%d')}.csv",
        "requires_file": True,
    },
    "LONASEBET_CASINO": {
        "inserter_class": LonasebetCasinoInserter,
        "file_pattern": general_directory + rf"LONASEBET/CASINO/**/casinoLonasebet {start_date_param.strftime('%Y-%m-%d')}.csv",
        "requires_file": True,
    },
    "HONORE_GAMING": { # Gère ses propres fichiers et dates complexes
        "inserter_class": HonoreGamingInserter,
        "base_path_param": general_directory,
        # date_debut pour HonoreGaming est J-1, date_fin est J (pour le nom de fichier daily-modified...)
        "date_debut_override": start_date_param.strftime('%d/%m/%Y'),
        "date_fin_override": current_day.strftime('%d/%m/%Y'),
        "requires_file": False,
    },
    "AFITECH_COMMISSION_HISTORY": {
        "inserter_class": AfitechCommissionHistoryInserter,
        "base_path_param": general_directory,
        # date_debut est J-1, date_fin est J-1 (utilisé pour la requête delete)
        # L'inserter calcule firstDayOfMonth pour le nom de fichier.
        "requires_file": False, # L'inserter trouve son fichier
    },
    "AFITECH_DAILY_PAYMENT_ACTIVITY": {
        "inserter_class": AfitechDailyPaymentActivityInserter,
        "base_path_param": general_directory,
        "requires_file": False, # L'inserter trouve son fichier
    },
    "LONASEBET_ALR_PARIFOOT": {
        "inserter_class": LonasebetAlrParifootInserter,
        "file_pattern": general_directory + rf"LONASEBET/ALR_PARIFOOT/**/OnlineLonasebet {start_date_param.strftime('%Y-%m-%d')}.csv",
        "requires_file": True,
    },
    "PARIFOOT_ONLINE": { # PremierBet
        "inserter_class": ParifootOnlineInserter,
        "file_pattern": general_directory + rf"PARIFOOT_ONLINE/**/ParifootOnline {start_date_param.strftime('%Y-%m-%d')}.csv",
        "requires_file": True,
    },
    "SUNUBET": { # Gère Online et Casino
        "inserter_class": SunubetInserter,
        "base_path_param": general_directory,
        "requires_file": False, # L'inserter trouve ses fichiers
    },
    "USSD": {
        "inserter_class": UssdInserter,
        "base_path_param": general_directory,
        "requires_file": False, # L'inserter trouve son fichier
    },
    "PMU_SENEGAL": {
        "inserter_class": PmuSenegalInserter,
        "requires_file": False, # Script externe
    },
    "MINI_SHOP": {
        "inserter_class": MiniShopInserter,
        "requires_file": False, # Script externe
    }
}

if __name__ == "__main__":
    main_logger.info(" === Début du script d'insertion de tous les produits ===")

    for product_name, config in product_processors.items():
        main_logger.info(f"--- Traitement de: {product_name} ---")

        inserter_date_debut = config.get("date_debut_override", date_debut_str)
        inserter_date_fin = config.get("date_fin_override", date_fin_str)

        try:
            # Initialisation de l'inserter
            inserter_args = {
                "db_config": db_config,
                "date_debut": inserter_date_debut,
                "date_fin": inserter_date_fin,
                "logger": setup_logger(f"inserter_{product_name.lower()}", f"inserter_{product_name.lower()}.log", level=LOG_LEVEL)
            }
            if "base_path_param" in config:
                inserter_args["base_path"] = config["base_path_param"]
            
            inserter_instance = config["inserter_class"](**inserter_args)

            file_to_process = None
            if config["requires_file"]:
                files_found = glob.glob(config["file_pattern"], recursive=True)
                if not files_found:
                    main_logger.warning(f"Fichier non trouvé pour {product_name} avec le pattern: {config['file_pattern']}. Traitement sauté.")
                    continue
                file_to_process = files_found[0]
                main_logger.info(f"Fichier trouvé pour {product_name}: {file_to_process}")
            
            # Appel de la méthode process
            # Si requires_file est True, file_to_process est le chemin du fichier.
            # Si requires_file est False, l'inserter gère la recherche de fichier(s) ou n'en a pas besoin (scripts externes).
            # La méthode process de l'inserter doit accepter `source_file_path` même s'il est None.
            inserter_instance.process(source_file_path=file_to_process)
            main_logger.info(f"Traitement de {product_name} terminé avec succès.")

        except FileNotFoundError as fnf_err:
            main_logger.error(f"Erreur de fichier non trouvé pour {product_name}: {fnf_err}")
        except Exception as e:
            main_logger.error(f"Erreur inattendue lors du traitement de {product_name}: {e}", exc_info=True)
            # Selon la criticité, on pourrait vouloir arrêter tout le script ici.
            # Pour l'instant, on continue avec les autres produits.

        main_logger.info(f"--- Fin du traitement de: {product_name} ---")

    main_logger.info(" === Fin du script d'insertion de tous les produits ===")

    # Nettoyage de cx_Oracle et autres ressources si nécessaire (par exemple, si cx_Oracle.init_oracle_client avait été appelé globalement)
    # Cependant, la gestion de la connexion est maintenant dans chaque inserter, qui la ferme.
    # `gc.collect()` était dans le script original, on peut le garder si des problèmes de mémoire sont suspectés.
    import gc
    gc.collect()
    main_logger.info("Garbage collection effectuée.")
