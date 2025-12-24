"""
Transformer pour pmu_ca.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.pmu_ca.transform import run_pmu_ca_transformer


def run_transform(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute la transformation pour pmu_ca.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de la transformation
    """
    # pmu_ca_transformer accepte des paramètres optionnels
    wrapper = create_simple_wrapper(
        lambda: run_pmu_ca_transformer(),  # Appel sans paramètres
        "transform",
        "pmu_ca"
    )
    return wrapper(context, config)
