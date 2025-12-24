"""
Transformer pour gitech_parifoot.
Wrapper autour du transformer existant.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from scripts.gitech_parifoot.transform import run_gitech_parifoot_transformer


def run_transform(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute la transformation pour gitech_parifoot.
    
    Args:
        context: Contexte du pipeline (contient les résultats de l'extraction)
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de la transformation
    """
    # Exécuter la transformation existante
    run_gitech_parifoot_transformer()
    
    # Retourner un résultat
    return {
        "status": "success",
        "source": config.source_name,
        "transformed_files": []  # Peut être enrichi si nécessaire
    }

