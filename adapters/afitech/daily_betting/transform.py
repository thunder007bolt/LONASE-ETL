"""
Transformer pour afitech_daily_betting.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.afitech_daily_betting.transform import run_afitech_daily_betting_transformer


def run_transform(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute la transformation pour afitech_daily_betting.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de la transformation
    """
    wrapper = create_simple_wrapper(
        run_afitech_daily_betting_transformer,
        "transform",
        "afitech_daily_betting"
    )
    return wrapper(context, config)

