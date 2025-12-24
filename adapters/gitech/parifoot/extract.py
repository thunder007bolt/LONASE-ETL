"""
Extractor pour gitech_parifoot.
Wrapper autour de l'extractor existant.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from scripts.gitech_parifoot.extract import run_gitech_parifoot


def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute l'extraction pour gitech_parifoot.
    
    Args:
        context: Contexte du pipeline (peut contenir des données des étapes précédentes)
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de l'extraction (peut être None ou des métadonnées)
    """
    # Les dates peuvent venir de config.start_date et config.end_date
    # ou être définies dans config.yml
    # Pour l'instant, on utilise la fonction existante qui lit depuis config.yml
    # TODO: Adapter pour utiliser config.start_date et config.end_date si fournis
    
    # Exécuter l'extraction existante
    run_gitech_parifoot()
    
    # Retourner un résultat (peut être None, les fichiers sont dans le système de fichiers)
    return {
        "status": "success",
        "source": config.source_name,
        "extracted_files": []  # Peut être enrichi si nécessaire
    }

