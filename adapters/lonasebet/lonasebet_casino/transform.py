"""
Transformer pour lonasebet_casino.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.lonasebet_casino.transform import run_lonasebet_casino_transformer


def run_transform(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute la transformation pour lonasebet_casino.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de la transformation
    """
    wrapper = create_simple_wrapper(
        run_lonasebet_casino_transformer,
        "transform",
        "lonasebet_casino"
    )
    return wrapper(context, config)
