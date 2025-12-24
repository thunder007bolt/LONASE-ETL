"""
Extractor pour bwinner_gambie.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.bwinner_gambie.extract import run_bwinner_gambie


def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute l'extraction pour bwinner_gambie.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de l'extraction
    """
    wrapper = create_simple_wrapper(
        run_bwinner_gambie,
        "extract",
        "bwinner_gambie"
    )
    return wrapper(context, config)

