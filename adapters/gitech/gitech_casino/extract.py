"""
Extractor pour gitech_casino.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.gitech_casino.extract import run_gitech_casino


def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute l'extraction pour gitech_casino.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de l'extraction
    """
    wrapper = create_simple_wrapper(
        run_gitech_casino,
        "extract",
        "gitech_casino"
    )
    return wrapper(context, config)
