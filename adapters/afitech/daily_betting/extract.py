"""
Extractor pour afitech_daily_betting.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_wrapper_with_dates
from scripts.afitech_daily_betting.extract import run_afitech_daily_betting_activity


def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute l'extraction pour afitech_daily_betting.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de l'extraction
    """
    # Utiliser le helper pour créer un wrapper avec support des dates
    wrapper = create_wrapper_with_dates(
        run_afitech_daily_betting_activity,
        "extract",
        "afitech_daily_betting"
    )
    return wrapper(context, config)

