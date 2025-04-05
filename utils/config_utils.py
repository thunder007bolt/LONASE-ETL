from os import getenv, getcwd
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

from base.logger import Logger
from load_env import load_env
from utils.constants import TEMP_DB_ENV_VARIABLES_LIST

load_env()

def load_yaml_config(file_path: Path) -> Dict[str, Any]:
    try:
        with file_path.open('r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"Config file not found: {file_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"YAML error in {file_path}: {e}")
        raise

def get_config(job_name: str = None) -> Dict[str, Any]:
    project_path = Path(getenv('ABSOLUTE_PROJECT_PATH'))

    base_config_path = project_path / 'config' / 'base_config.yml'
    base_config = load_yaml_config(base_config_path)

    job_config = {}
    if job_name:
        #todo: définir proprement ce chemin
        job_config_path = project_path / 'scripts'/ job_name / 'config.yml'
        if job_config_path.exists():
            job_config = load_yaml_config(job_config_path)
        else:
            logging.warning(f"Aucune configuration trouvée pour {job_name}")

    return {**base_config, **job_config}

def get_secret(keys):
    return {key: getenv(key) for key in keys}

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
