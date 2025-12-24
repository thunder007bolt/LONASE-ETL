"""
Factory pour créer des orchestrators automatiquement.
Simplifie la création d'orchestrators en auto-détectant les fonctions extract/transform/load.
"""
import importlib
from pathlib import Path
from base.orchestrator import Orchestrator
from utils.path_utils import setup_project_paths


def create_orchestrator(source_name: str, config_path: str = None) -> Orchestrator:
    """
    Crée un orchestrator pour une source en auto-détectant les fonctions.
    
    Args:
        source_name: Nom de la source (ex: 'afitech_daily_betting')
        config_path: Chemin de configuration optionnel
    
    Returns:
        Orchestrator: Orchestrator configuré et prêt à l'emploi
    
    Raises:
        ImportError: Si les modules extract/transform/load ne peuvent pas être importés
        AttributeError: Si les fonctions run_* ne sont pas trouvées
    """
    # Setup des paths du projet
    setup_project_paths()
    
    # Import des modules
    try:
        extract_module = importlib.import_module(f'scripts.{source_name}.extract')
        transform_module = importlib.import_module(f'scripts.{source_name}.transform')
        load_module = importlib.import_module(f'scripts.{source_name}.load')
    except ImportError as e:
        raise ImportError(f"Impossible d'importer les modules pour {source_name}: {e}")
    
    # Détection des fonctions
    # Pattern 1: run_{source_name}
    extract_func = getattr(extract_module, f'run_{source_name}', None)
    if not extract_func:
        # Pattern 2: run_{source_name}_activity, run_{source_name}_extract, etc.
        for attr_name in dir(extract_module):
            if attr_name.startswith('run_') and not attr_name.endswith('_orchestrator'):
                extract_func = getattr(extract_module, attr_name)
                break
    
    # Pattern standard: run_{source_name}_transformer
    transform_func = getattr(transform_module, f'run_{source_name}_transformer', None)
    if not transform_func:
        # Chercher toute fonction run_* dans transform
        for attr_name in dir(transform_module):
            if attr_name.startswith('run_') and 'transformer' in attr_name:
                transform_func = getattr(transform_module, attr_name)
                break
    
    # Pattern standard: run_{source_name}_loader
    load_func = getattr(load_module, f'run_{source_name}_loader', None)
    if not load_func:
        # Chercher toute fonction run_* dans load
        for attr_name in dir(load_module):
            if attr_name.startswith('run_') and 'loader' in attr_name:
                load_func = getattr(load_module, attr_name)
                break
    
    if not extract_func:
        raise AttributeError(f"Fonction extract non trouvée pour {source_name}")
    if not transform_func:
        raise AttributeError(f"Fonction transform non trouvée pour {source_name}")
    if not load_func:
        raise AttributeError(f"Fonction load non trouvée pour {source_name}")
    
    # Création de l'orchestrator
    return Orchestrator(
        name=source_name,
        extractor=extract_func,
        transformer=transform_func,
        loader=load_func
    )


def run_orchestrator(source_name: str, config_path: str = None):
    """
    Crée et exécute un orchestrator pour une source.
    
    Args:
        source_name: Nom de la source
        config_path: Chemin de configuration optionnel
    
    Usage:
        run_orchestrator("afitech_daily_betting")
    """
    orchestrator = create_orchestrator(source_name, config_path)
    orchestrator.run()

