"""
Loader pour lonasebet_casino.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.lonasebet_casino.load import run_lonasebet_casino_loader


def run_load(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute le chargement pour lonasebet_casino.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat du chargement
    """
    wrapper = create_simple_wrapper(
        run_lonasebet_casino_loader,
        "load",
        "lonasebet_casino"
    )
    return wrapper(context, config)
