# Architecture du Pipeline ETL

## Vue d'ensemble

L'architecture du pipeline ETL a été refactorisée pour offrir plus de flexibilité et permettre à Jenkins de contrôler l'exécution via des variables d'environnement.

**Important :** Chaque job Jenkins est indépendant et appelle individuellement `run_job.py` avec une source de données spécifique. Il n'y a pas de gestion de dépendances entre jobs au niveau du code - cela est géré par Jenkins via la configuration des pipelines.

## Structure

```
LONASE-ETL/
├── core/                          # Cœur métier
│   ├── config/                    # Gestion de configuration
│   │   └── env_config.py          # Lecture des variables d'environnement
│   └── pipeline/                  # Pipeline ETL
│       └── pipeline.py           # Pipeline principal avec retry
│
├── adapters/                      # Adaptateurs pour chaque source
│   └── gitech/
│       └── parifoot/             # Exemple d'adapter
│           ├── extract.py
│           ├── transform.py
│           └── load.py
│
├── infrastructure/                # Infrastructure
│   └── logging/
│       └── logger.py             # Logger amélioré
│
└── scripts/
    └── run_job.py                # Point d'entrée unique
```

## Composants principaux

### 1. Configuration via variables d'environnement

Le module `core/config/env_config.py` charge toute la configuration depuis les variables d'environnement transmises par Jenkins.

**Avantages:**
- Pas de modification de code pour changer la configuration
- Jenkins contrôle complètement l'exécution
- Flexibilité maximale (dates, flags, paramètres)

### 2. Pipeline ETL flexible

Le module `core/pipeline/pipeline.py` implémente un pipeline avec :
- Retry automatique en cas d'échec
- Gestion d'erreurs robuste
- Possibilité de skipper des étapes
- Mode dry-run pour les tests

### 3. Factory d'adapters

Le module `adapters/__init__.py` permet d'enregistrer dynamiquement les extractors, transformers et loaders pour chaque source.

**Avantages:**
- Ajout facile de nouvelles sources
- Découplage entre le pipeline et les implémentations
- Réutilisabilité

### 4. Point d'entrée unique

Le script `scripts/run_job.py` est le seul point d'entrée appelé par Jenkins.

**Fonctionnalités:**
- Charge la configuration depuis les variables d'environnement
- Crée le pipeline avec les étapes appropriées
- Exécute le pipeline avec retry
- Gère les erreurs et retourne les codes de sortie appropriés

## Flux d'exécution

**Modèle d'exécution :** Chaque job Jenkins = Un appel à `run_job.py` = Une source de données

```
Job Jenkins "gitech_parifoot_daily"
  ↓ (définit les variables d'environnement pour cette source)
  ETL_JOB_NAME=gitech_parifoot_daily
  ETL_SOURCE_NAME=gitech_parifoot
  ETL_START_DATE=2025-01-15
  ↓
run_job.py
  ↓ (charge la config)
EnvConfigLoader
  ↓ (crée le pipeline pour cette source)
Pipeline
  ↓ (exécute les étapes)
Extract → Transform → Load
  ↓ (retry en cas d'échec)
Résultat (code de sortie 0 ou 1)
```

**Exemple avec plusieurs jobs :**
- Job Jenkins 1 : `ETL_SOURCE_NAME=gitech_parifoot` → Exécute gitech_parifoot
- Job Jenkins 2 : `ETL_SOURCE_NAME=afitech_daily_betting` → Exécute afitech_daily_betting
- Job Jenkins 3 : `ETL_SOURCE_NAME=bwinner_gambie` → Exécute bwinner_gambie

Chaque job est complètement indépendant. Les dépendances et l'ordre d'exécution sont gérés par Jenkins (via les pipelines, les triggers, etc.).

## Ajout d'une nouvelle source

Pour ajouter une nouvelle source, il suffit de :

1. Créer un dossier dans `adapters/` (ex: `adapters/ma_source/`)

2. Créer les fichiers `extract.py`, `transform.py`, `load.py` qui wrappent les fonctions existantes :

```python
# adapters/ma_source/extract.py
from typing import Dict, Any
from core.config.env_config import JobConfig
from scripts.ma_source.extract import run_ma_source

def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
    run_ma_source()
    return {"status": "success"}
```

3. Créer un fichier `__init__.py` qui enregistre les adapters :

```python
# adapters/ma_source/__init__.py
from adapters import AdapterFactory
from adapters.ma_source.extract import run_extract
from adapters.ma_source.transform import run_transform
from adapters.ma_source.load import run_load

def register_adapters():
    AdapterFactory.register_extractor("ma_source", run_extract)
    AdapterFactory.register_transformer("ma_source", run_transform)
    AdapterFactory.register_loader("ma_source", run_load)
```

4. C'est tout ! Le système détectera automatiquement l'adapter.

## Migration depuis l'ancienne architecture

L'ancienne architecture continue de fonctionner. Les adapters wrappent simplement les fonctions existantes, donc aucune modification n'est nécessaire dans les scripts existants.

Pour migrer progressivement :

1. Créer les adapters pour les sources prioritaires
2. Tester avec Jenkins en utilisant les variables d'environnement
3. Migrer progressivement les autres sources

## Variables d'environnement

Voir [ENV_VARIABLES.md](ENV_VARIABLES.md) pour la documentation complète des variables d'environnement.

## Exemples

### Exécution simple

```bash
export ETL_JOB_NAME=test_job
export ETL_SOURCE_NAME=gitech_parifoot
python scripts/run_job.py
```

### Exécution avec dates

```bash
export ETL_JOB_NAME=test_job
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_START_DATE=2025-01-15
export ETL_END_DATE=2025-01-15
python scripts/run_job.py
```

### Exécution avec skip

```bash
export ETL_JOB_NAME=test_job
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_SKIP_EXTRACT=true
python scripts/run_job.py
```

## Avantages de la nouvelle architecture

1. **Flexibilité** : Jenkins contrôle tout via variables d'environnement
2. **Simplicité** : Point d'entrée unique, pas de duplication
3. **Robustesse** : Retry automatique, gestion d'erreurs
4. **Maintenabilité** : Code organisé, séparation des responsabilités
5. **Testabilité** : Configuration injectée, facile à tester
6. **Extensibilité** : Ajout facile de nouvelles sources

