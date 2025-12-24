"""
Script utilitaire simplifié pour générer automatiquement les adapters pour une source.
Version qui ne nécessite pas tous les imports du projet.
"""
import sys
import re
from pathlib import Path


def generate_adapter(source_name: str):
    """
    Génère les fichiers adapter pour une source.
    
    Args:
        source_name: Nom de la source (ex: 'gitech_parifoot')
    """
    # Déterminer le chemin de la source
    project_root = Path(__file__).parent.parent
    source_path = project_root / "scripts" / source_name
    if not source_path.exists():
        print(f"❌ Erreur: Le dossier {source_path} n'existe pas")
        return
    
    # Vérifier les fonctions existantes
    extract_file = source_path / "extract.py"
    transform_file = source_path / "transform.py"
    load_file = source_path / "load.py"
    
    # Trouver les noms des fonctions
    extract_func = None
    transform_func = None
    load_func = None
    
    if extract_file.exists():
        with open(extract_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Chercher les fonctions run_*
            matches = re.findall(r'^def (run_\w+)', content, re.MULTILINE)
            if matches:
                # Prendre la première fonction qui correspond au pattern
                for match in matches:
                    if source_name.replace('_', '') in match.lower():
                        extract_func = match
                        break
                if not extract_func and matches:
                    extract_func = matches[0]
    
    if transform_file.exists():
        with open(transform_file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.findall(r'^def (run_\w+transformer)', content, re.MULTILINE)
            if matches:
                transform_func = matches[0]
    
    if load_file.exists():
        with open(load_file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.findall(r'^def (run_\w+loader)', content, re.MULTILINE)
            if matches:
                load_func = matches[0]
    
    # Déterminer la catégorie (première partie du nom)
    category = source_name.split('_')[0] if '_' in source_name else source_name
    
    # Créer la structure de dossiers
    adapter_dir = project_root / "adapters" / category / source_name
    adapter_dir.mkdir(parents=True, exist_ok=True)
    
    # Générer extract.py
    extract_func_name = extract_func if extract_func else f'run_{source_name.replace("_", "")}'
    extract_content = f'''"""
Extractor pour {source_name}.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.{source_name}.extract import {extract_func_name}


def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute l'extraction pour {source_name}.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de l'extraction
    """
    wrapper = create_simple_wrapper(
        {extract_func_name},
        "extract",
        "{source_name}"
    )
    return wrapper(context, config)
'''
    
    # Générer transform.py
    transform_func_name = transform_func if transform_func else f'run_{source_name.replace("_", "")}_transformer'
    transform_content = f'''"""
Transformer pour {source_name}.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.{source_name}.transform import {transform_func_name}


def run_transform(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute la transformation pour {source_name}.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de la transformation
    """
    wrapper = create_simple_wrapper(
        {transform_func_name},
        "transform",
        "{source_name}"
    )
    return wrapper(context, config)
'''
    
    # Générer load.py
    load_func_name = load_func if load_func else f'run_{source_name.replace("_", "")}_loader'
    load_content = f'''"""
Loader pour {source_name}.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.{source_name}.load import {load_func_name}


def run_load(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute le chargement pour {source_name}.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat du chargement
    """
    wrapper = create_simple_wrapper(
        {load_func_name},
        "load",
        "{source_name}"
    )
    return wrapper(context, config)
'''
    
    # Générer __init__.py
    init_content = f'''"""
Adapter pour {source_name}.
"""
from adapters import AdapterFactory
from adapters.{category}.{source_name}.extract import run_extract
from adapters.{category}.{source_name}.transform import run_transform
from adapters.{category}.{source_name}.load import run_load


def register_adapters():
    """Enregistre les adapters pour {source_name}"""
    AdapterFactory.register_extractor("{source_name}", run_extract)
    AdapterFactory.register_transformer("{source_name}", run_transform)
    AdapterFactory.register_loader("{source_name}", run_load)
'''
    
    # Créer le __init__.py de la catégorie si nécessaire
    category_init = project_root / "adapters" / category / "__init__.py"
    if not category_init.exists():
        category_init.write_text(f'"""\nAdapters pour les sources {category.capitalize()}.\n"""\n', encoding='utf-8')
    
    # Écrire les fichiers
    (adapter_dir / "extract.py").write_text(extract_content, encoding='utf-8')
    (adapter_dir / "transform.py").write_text(transform_content, encoding='utf-8')
    (adapter_dir / "load.py").write_text(load_content, encoding='utf-8')
    (adapter_dir / "__init__.py").write_text(init_content, encoding='utf-8')
    
    print(f"✅ Adapter généré pour {source_name}")
    print(f"   📁 Dossier: {adapter_dir}")
    print(f"   📝 Fichiers créés:")
    print(f"      - extract.py (utilise {extract_func_name})")
    print(f"      - transform.py (utilise {transform_func_name})")
    print(f"      - load.py (utilise {load_func_name})")
    print(f"      - __init__.py")
    print(f"\n⚠️  Vérifiez les noms des fonctions et ajustez si nécessaire.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_adapter_simple.py <source_name>")
        print("Exemple: python scripts/generate_adapter_simple.py gitech_parifoot")
        sys.exit(1)
    
    source_name = sys.argv[1]
    generate_adapter(source_name)

