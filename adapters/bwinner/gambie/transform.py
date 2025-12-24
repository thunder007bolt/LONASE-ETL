"""
Transformer pour bwinner_gambie.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.bwinner_gambie.transform import run_bwinner_gambie_transformer


def run_transform(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute la transformation pour bwinner_gambie.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de la transformation
    """
    wrapper = create_simple_wrapper(
        run_bwinner_gambie_transformer,
        "transform",
        "bwinner_gambie"
    )
    return wrapper(context, config)

