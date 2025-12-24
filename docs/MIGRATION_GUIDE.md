# Guide de migration vers la nouvelle architecture

Ce guide explique comment migrer progressivement vers la nouvelle architecture basée sur les variables d'environnement et Jenkins.

## Pourquoi migrer ?

La nouvelle architecture offre :
- ✅ Flexibilité maximale via variables d'environnement
- ✅ Point d'entrée unique (`scripts/run_job.py`)
- ✅ Retry automatique en cas d'échec
- ✅ Possibilité de skipper des étapes
- ✅ Mode dry-run pour les tests
- ✅ Meilleure intégration avec Jenkins

## Migration progressive

### Étape 1 : Tester avec une source pilote

Choisissez une source simple pour tester (ex: `gitech_parifoot`).

1. L'adapter est déjà créé dans `adapters/gitech/parifoot/`
2. Testez avec les variables d'environnement :

```bash
export ETL_JOB_NAME=test_gitech_parifoot
export ETL_SOURCE_NAME=gitech_parifoot
python scripts/run_job.py
```

### Étape 2 : Créer des adapters pour d'autres sources

Pour chaque source à migrer :

1. Créer le dossier dans `adapters/` :
   ```bash
   mkdir -p adapters/ma_source
   ```

2. Créer `adapters/ma_source/extract.py` :
   ```python
   from typing import Dict, Any
   from core.config.env_config import JobConfig
   from scripts.ma_source.extract import run_ma_source
   
   def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
       run_ma_source()
       return {"status": "success"}
   ```

3. Créer `adapters/ma_source/transform.py` :
   ```python
   from typing import Dict, Any
   from core.config.env_config import JobConfig
   from scripts.ma_source.transform import run_ma_source_transformer
   
   def run_transform(context: Dict[str, Any], config: JobConfig) -> Any:
       run_ma_source_transformer()
       return {"status": "success"}
   ```

4. Créer `adapters/ma_source/load.py` :
   ```python
   from typing import Dict, Any
   from core.config.env_config import JobConfig
   from scripts.ma_source.load import run_ma_source_loader
   
   def run_load(context: Dict[str, Any], config: JobConfig) -> Any:
       run_ma_source_loader()
       return {"status": "success"}
   ```

5. Créer `adapters/ma_source/__init__.py` :
   ```python
   from adapters import AdapterFactory
   from adapters.ma_source.extract import run_extract
   from adapters.ma_source.transform import run_transform
   from adapters.ma_source.load import run_load
   
   def register_adapters():
       AdapterFactory.register_extractor("ma_source", run_extract)
       AdapterFactory.register_transformer("ma_source", run_transform)
       AdapterFactory.register_loader("ma_source", run_load)
   ```

### Étape 3 : Configurer Jenkins

1. Créer un pipeline Jenkins qui définit les variables d'environnement
2. Voir [ENV_VARIABLES.md](ENV_VARIABLES.md) pour la liste complète des variables
3. Exemple de pipeline dans `docs/ENV_VARIABLES.md`

### Étape 4 : Tester en production

1. Tester avec une source en mode dry-run :
   ```bash
   export ETL_DRY_RUN=true
   export ETL_SOURCE_NAME=ma_source
   python scripts/run_job.py
   ```

2. Tester avec une source réelle mais en skippant certaines étapes :
   ```bash
   export ETL_SKIP_EXTRACT=true  # Tester seulement transform + load
   export ETL_SOURCE_NAME=ma_source
   python scripts/run_job.py
   ```

3. Exécuter le job complet

### Étape 5 : Migrer progressivement

- Migrer les sources une par une
- Garder l'ancienne méthode en parallèle pendant la transition
- Une fois toutes les sources migrées, vous pouvez supprimer les anciens orchestrators

## Compatibilité

**L'ancienne architecture continue de fonctionner !**

Les adapters wrappent simplement les fonctions existantes, donc :
- ✅ Aucune modification nécessaire dans les scripts existants
- ✅ Les anciens orchestrators continuent de fonctionner
- ✅ Migration progressive possible

## Avantages de la migration

### Avant (ancienne architecture)
```bash
# Chaque source a son propre script
python scripts/gitech_parifoot/orchestrator.py
python scripts/afitech_daily_betting/orchestrator.py
# ...
```

### Après (nouvelle architecture)
```bash
# Point d'entrée unique, configuration via variables d'environnement
export ETL_SOURCE_NAME=gitech_parifoot
python scripts/run_job.py

export ETL_SOURCE_NAME=afitech_daily_betting
python scripts/run_job.py
```

### Avec Jenkins
```groovy
// Un seul pipeline Jenkins pour toutes les sources
pipeline {
    parameters {
        choice(name: 'SOURCE_NAME', choices: ['gitech_parifoot', 'afitech_daily_betting', ...])
    }
    environment {
        ETL_SOURCE_NAME = "${params.SOURCE_NAME}"
    }
    steps {
        sh 'python scripts/run_job.py'
    }
}
```

## Checklist de migration

- [ ] Tester avec une source pilote
- [ ] Créer les adapters pour les sources prioritaires
- [ ] Configurer Jenkins avec les variables d'environnement
- [ ] Tester en mode dry-run
- [ ] Tester avec skip des étapes
- [ ] Exécuter en production
- [ ] Migrer progressivement les autres sources
- [ ] Documenter les spécificités de chaque source

## Support

Pour toute question, consultez :
- [ARCHITECTURE.md](ARCHITECTURE.md) : Détails de l'architecture
- [ENV_VARIABLES.md](ENV_VARIABLES.md) : Documentation des variables d'environnement
- Les logs dans `logs/run_job.log`

