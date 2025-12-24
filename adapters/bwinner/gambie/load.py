"""
Loader pour bwinner_gambie.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.bwinner_gambie.load import run_bwinner_gambie_loader


def run_load(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute le chargement pour bwinner_gambie.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat du chargement
    """
    wrapper = create_simple_wrapper(
        run_bwinner_gambie_loader,
        "load",
        "bwinner_gambie"
    )
    return wrapper(context, config)

