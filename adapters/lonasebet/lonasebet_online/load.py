"""
Loader pour lonasebet_online.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.lonasebet_online.load import run_lonasebet_online_loader


def run_load(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute le chargement pour lonasebet_online.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat du chargement
    """
    wrapper = create_simple_wrapper(
        run_lonasebet_online_loader,
        "load",
        "lonasebet_online"
    )
    return wrapper(context, config)
