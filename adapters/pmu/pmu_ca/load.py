"""
Loader pour pmu_ca.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.pmu_ca.load import run_pmu_ca_loader


def run_load(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute le chargement pour pmu_ca.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat du chargement
    """
    # pmu_ca_loader accepte des paramètres optionnels
    wrapper = create_simple_wrapper(
        lambda: run_pmu_ca_loader(),  # Appel sans paramètres
        "load",
        "pmu_ca"
    )
    return wrapper(context, config)
