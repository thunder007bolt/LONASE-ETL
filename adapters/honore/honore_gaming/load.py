"""
Loader pour honore_gaming.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.honore_gaming.load import run_honore_gaming_loader


def run_load(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute le chargement pour honore_gaming.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat du chargement
    """
    wrapper = create_simple_wrapper(
        run_honore_gaming_loader,
        "load",
        "honore_gaming"
    )
    return wrapper(context, config)
