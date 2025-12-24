"""
Extractor pour lonasebet_online.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.lonasebet_online.extract import run_lonasebet_online


def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute l'extraction pour lonasebet_online.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de l'extraction
    """
    wrapper = create_simple_wrapper(
        run_lonasebet_online,
        "extract",
        "lonasebet_online"
    )
    return wrapper(context, config)
