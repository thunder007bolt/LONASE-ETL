from os import getenv
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

from base.logger import Logger # Assurez-vous que ce chemin d'importation est correct ou ajustez-le
from load_env import load_env, PROJECT_ROOT # Import PROJECT_ROOT
from utils.constants import TEMP_DB_ENV_VARIABLES_LIST

# Charger les variables d'environnement au moment de l'importation de ce module
# Cela garantit qu'elles sont disponibles lorsque les fonctions de ce module sont appelées.
if not load_env():
    # Gérer le cas où le chargement de .env échoue, par exemple, lever une exception
    # ou enregistrer une erreur critique et potentiellement s'arrêter.
    logging.critical("Échec du chargement des variables d'environnement. Le programme risque de ne pas fonctionner correctement.")
    # raise EnvironmentError("Impossible de charger les variables d'environnement depuis .env")

def load_yaml_config(file_path: Path) -> Dict[str, Any]:
    try:
        with file_path.open('r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"Fichier de configuration non trouvé : {file_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Erreur YAML dans {file_path}: {e}")
        raise

def get_project_path() -> Path:
    """Récupère le chemin du projet à partir de la variable d'environnement PROJECT_PATH,
       ou utilise PROJECT_ROOT (détecté à partir de l'emplacement de load_env.py) comme fallback."""
    project_path_str = getenv('PROJECT_PATH')
    if project_path_str:
        return Path(project_path_str).resolve()
    logging.warning("La variable d'environnement PROJECT_PATH n'est pas définie. "
                    f"Utilisation du chemin détecté comme racine du projet : {PROJECT_ROOT}")
    return PROJECT_ROOT

def get_data_path() -> Path:
    """Récupère le chemin des données à partir de la variable d'environnement DATA_PATH."""
    data_path_str = getenv('DATA_PATH')
    if not data_path_str:
        # Fallback si DATA_PATH n'est pas défini : le sous-dossier 'DATA_FICHIERS' dans PROJECT_PATH
        logging.warning("La variable d'environnement DATA_PATH n'est pas définie. "
                        "Utilisation de PROJECT_PATH / 'DATA_FICHIERS' par défaut.")
        return get_project_path() / 'DATA_FICHIERS'
    return Path(data_path_str).resolve()

def get_download_path() -> Path:
    """Récupère le chemin de téléchargement à partir de la variable d'environnement DOWNLOAD_PATH."""
    download_path_str = getenv('DOWNLOAD_PATH')
    if not download_path_str:
        # Fallback si DOWNLOAD_PATH n'est pas défini : le sous-dossier 'Downloads' dans PROJECT_PATH
        logging.warning("La variable d'environnement DOWNLOAD_PATH n'est pas définie. "
                        "Utilisation de PROJECT_PATH / 'Downloads' par défaut.")
        return get_project_path() / 'Downloads'
    return Path(download_path_str).resolve()


def get_config(job_name: str = None) -> Dict[str, Any]:
    """
    Charge la configuration de base et la fusionne avec la configuration spécifique au job.
    Les chemins de base (project, data, download) sont maintenant déterminés par les variables d'environnement
    ou des valeurs par défaut intelligentes.
    """
    project_path = get_project_path()
    base_config_path = project_path / 'config' / 'base_config.yml'

    try:
        base_config_content = load_yaml_config(base_config_path)
    except FileNotFoundError:
        logging.error(f"Le fichier de configuration de base 'base_config.yml' est introuvable à {base_config_path}.")
        # Retourner un dictionnaire vide ou une configuration minimale si cela a du sens, ou lever l'erreur.
        # Pour l'instant, on suppose qu'il doit exister.
        raise

    # Remplacer les placeholders par les chemins réels obtenus des variables d'environnement
    # ou des valeurs par défaut.
    # Il est important que base_config_content['base']['paths'] existe.
    if 'base' in base_config_content and 'paths' in base_config_content['base']:
        base_config_content['base']['paths']['project_absolute_path'] = str(project_path)
        base_config_content['base']['paths']['data_path'] = str(get_data_path())
        base_config_content['base']['paths']['download_path'] = str(get_download_path())
    else:
        logging.warning("'base' ou 'base.paths' non trouvé dans base_config.yml. "
                        "Les chemins dynamiques ne seront pas injectés.")

    job_config = {}
    if job_name:
        # Le chemin vers les scripts est relatif au chemin du projet
        job_config_path = project_path / 'scripts' / job_name / 'config.yml'
        if job_config_path.exists():
            try:
                job_config = load_yaml_config(job_config_path)
            except FileNotFoundError: # Devrait être géré par .exists() mais par sécurité
                logging.warning(f"Fichier de configuration pour le job '{job_name}' non trouvé à {job_config_path} (ceci ne devrait pas arriver si .exists() est vrai).")
            except Exception as e:
                logging.error(f"Erreur lors du chargement de la configuration pour le job '{job_name}' depuis {job_config_path}: {e}")
                # Décider comment gérer cela : ignorer, utiliser des valeurs par défaut, ou lever une erreur.
        else:
            logging.warning(f"Aucune configuration spécifique trouvée pour le job '{job_name}' à {job_config_path}.")

    # Fusionner les configurations. job_config peut écraser des valeurs de base_config_content si les clés sont identiques.
    # Utiliser deepcopy si les configurations contiennent des dictionnaires imbriqués qui pourraient être modifiés.
    # from copy import deepcopy
    # final_config = deepcopy(base_config_content)
    # final_config.update(deepcopy(job_config)) # ou une fusion plus intelligente si nécessaire

    final_config = {**base_config_content}
    # Fusionner job_config de manière à ce que ses valeurs écrasent celles de base_config_content,
    # y compris pour les dictionnaires imbriqués si nécessaire (nécessiterait une fonction de fusion profonde)
    # Pour une fusion simple au premier niveau :
    final_config.update(job_config)


    # Assurer que la section pour le job_name existe dans final_config.
    # Si job_name est fourni et qu'il n'y a pas de section correspondante dans job_config,
    # elle ne sera pas créée automatiquement par {**base_config_content, **job_config}
    # si job_name n'est pas une clé de haut niveau dans job_config.
    # La logique actuelle semble supposer que job_name est une clé dans le dict retourné par load_yaml_config(job_config_path)
    # et que configs[name] dans les fonctions get_X_configurations s'attend à cela.

    # Exemple: si job_config.yml pour 'mon_job' contient:
    # mon_job:
    #   param: valeur
    # Alors job_config sera {'mon_job': {'param': 'valeur'}}
    # et final_config aura {'base': {...}, 'mon_job': {'param': 'valeur'}}

    # Si la structure attendue est que la config du job soit directement sous une clé job_name:
    # configs = get_config("mon_job") -> attend que configs["mon_job"] existe.
    # La fusion actuelle {**base_config_content, **job_config} est correcte si job_config
    # est un dict comme {'mon_job': data}.
    # Si job_config est juste data (sans la clé job_name au premier niveau), alors il faut l'insérer:
    # if job_name and job_config: # S'il y a une config de job chargée
    #    final_config[job_name] = job_config # Assigner la config du job à sa clé

    # Clarification: La structure actuelle de get_config charge le contenu de job_config_path
    # et le fusionne. Si ce fichier contient `specific_param: value`, alors final_config
    # aura `specific_param: value` au premier niveau.
    # Les fonctions comme get_transformation_configurations font ensuite `config = configs[name]`,
    # ce qui implique qu'elles s'attendent à ce que la config spécifique au job soit sous une clé
    # portant le nom du job dans le dictionnaire de configuration global.
    # Il faut donc s'assurer que job_config est bien structuré ou que la fusion le place correctement.

    # Si job_config_path contient:
    #   key1: val1
    #   key2: val2
    # et job_name est "mon_job", alors job_config = {"key1":"val1", "key2":"val2"}
    # final_config sera {**base_config_content, "key1":"val1", "key2":"val2"}
    # Si get_transformation_configurations("mon_job", ...) est appelé, il fera:
    #   configs = get_config("mon_job")
    #   config = configs["mon_job"]  <--- KeyError ici si "mon_job" n'est pas une clé dans final_config

    # Pour corriger cela, la configuration spécifique au job devrait être chargée sous sa propre clé:
    if job_name and job_config: # Si job_config a été chargé et n'est pas vide
        temp_job_specific_config = job_config # Sauvegarder la config chargée pour le job
        job_config = {job_name: temp_job_specific_config} # Envelopper dans une clé job_name
        final_config.update(job_config) # Mettre à jour final_config
    elif job_name and job_name not in final_config:
        # Si aucune config spécifique au job n'a été chargée mais qu'on s'attend à une section pour ce job_name
        final_config[job_name] = {}
        logging.info(f"Section de configuration pour '{job_name}' initialisée comme vide car non trouvée ou vide après fusion.")


    return final_config

def get_secret(keys: list) -> Dict[str, str]:
    return {key: getenv(key) for key in keys}

def get_secret_v2(dict):
    return {key: getenv(env_var) for key, env_var in dict.items()}

def get_transformation_configurations(name, log_file):
    """
    Lit la configuration et renvoie le logger, le chemin de destination pour la transformation,
    le chemin pour les fichiers traités et le chemin complet du fichier téléchargé.
    """
    configs = get_config(name)
    config = configs[name]
    base_config = configs['base']

    data_path = Path(base_config["paths"]["data_path"])

    transformation_dest_path = data_path / config["transformation_dest_relative_path"]
    processed_dest_path = data_path / config["processed_dest_relative_path"]
    source_path = data_path / config["extraction_dest_relative_path"]
    error_dest_path = data_path / config["error_dest_relative_path"]

    files_to_transform_pattern = config["files_to_transform_pattern"]

    logger = Logger(log_file=log_file).get_logger()

    return (
        config,
        base_config,
        logger,
        transformation_dest_path,
        processed_dest_path,
        source_path,
        files_to_transform_pattern,
        error_dest_path
    )

def get_loading_configurations(name, log_file, env_variables_list = TEMP_DB_ENV_VARIABLES_LIST ):
    configs = get_config(name)
    secret_config = get_secret(env_variables_list)
    logger = Logger(log_file=log_file).get_logger()

    #### Récupération des confiurations ####
    config = configs[name]
    base_config = configs['base']
    data_path = Path(base_config["paths"]["data_path"])

    transformation_dest_path = data_path / config["transformation_dest_relative_path"]
    source_path = transformation_dest_path
    loaded_path = data_path / config['loaded_dest_relative_path']
    error_path = data_path / config['error_dest_relative_path']

    files_pattern = config['files_to_load_pattern']

    return (
        secret_config,
        logger,
        loaded_path,
        source_path,
        error_path,
        files_pattern
    )

def get_database_extractor_configurations(name, log_file, env_variables_list = TEMP_DB_ENV_VARIABLES_LIST ):
    configs = get_config(name)
    secret_config = get_secret_v2(env_variables_list)
    logger = Logger(log_file=log_file).get_logger()

    #### Récupération des confiurations ####
    config = configs[name]
    base_config = configs['base']
    data_path = Path(base_config["paths"]["data_path"])

    extraction_dest_path = data_path / config["extraction_dest_relative_path"]

    return (
        secret_config,
        config,
        logger,
        extraction_dest_path
    )


