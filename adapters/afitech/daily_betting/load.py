"""
Loader pour afitech_daily_betting.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.afitech_daily_betting.load import run_afitech_daily_betting_loader


def run_load(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute le chargement pour afitech_daily_betting.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat du chargement
    """
    wrapper = create_simple_wrapper(
        run_afitech_daily_betting_loader,
        "load",
        "afitech_daily_betting"
    )
    return wrapper(context, config)

