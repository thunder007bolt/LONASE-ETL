"""
Extractor pour pmu_ca.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.pmu_ca.extract import run_pmu_ca


def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute l'extraction pour pmu_ca.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de l'extraction
    """
    # pmu_ca accepte des paramètres optionnels config_path et log_file
    # On les ignore car la config vient des variables d'environnement
    wrapper = create_simple_wrapper(
        lambda: run_pmu_ca(),  # Appel sans paramètres
        "extract",
        "pmu_ca"
    )
    return wrapper(context, config)
