# LONASE-ETL

Système ETL (Extract, Transform, Load) pour le traitement de données de différentes sources de paris et jeux en ligne.

## Structure du projet

```
LONASE-ETL/
├── base/                    # Modules de base réutilisables
│   ├── orchestrator.py     # Classe orchestrator principale
│   ├── logger.py           # Système de logging
│   ├── transformer.py      # Classe de base pour transformation
│   ├── loader.py           # Classe de base pour chargement (SQL Server)
│   ├── loader2.py          # Classe de base pour chargement (SQL Server + Oracle)
│   ├── web_scrapper.py     # Classe de base pour scraping web
│   ├── ftp.py              # Classe de base pour FTP
│   └── database_extractor.py  # Classe de base pour extraction depuis BDD
├── scripts/                # Scripts ETL organisés par source
│   └── [source_name]/      # Chaque source a son propre répertoire
│       ├── extract.py      # Script d'extraction
│       ├── transform.py    # Script de transformation
│       ├── load.py         # Script de chargement
│       ├── orchestrator.py  # Orchestrator pour cette source
│       └── config.yml      # Configuration spécifique
├── utils/                  # Utilitaires
│   ├── path_utils.py       # Gestion des chemins du projet
│   ├── config_utils.py     # Gestion de la configuration
│   ├── db_utils.py         # Utilitaires de base de données
│   ├── date_utils.py       # Utilitaires de dates
│   ├── file_manipulation.py  # Manipulation de fichiers
│   └── ...
├── config/                 # Configuration globale
│   └── base_config.yml     # Configuration de base
├── requirements.txt        # Dépendances Python
└── .env.example           # Template des variables d'environnement
```

## Installation

### Prérequis

- Python 3.7+
- Accès aux bases de données SQL Server et Oracle
- ChromeDriver (pour le web scraping)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Configuration

1. Copiez le fichier `.env.example` en `.env` :
```bash
cp .env.example .env
```

2. Modifiez le fichier `.env` avec vos valeurs :
   - Chemins du projet
   - Identifiants des bases de données
   - Identifiants des sources externes (FTP, APIs, etc.)

3. Modifiez `config/base_config.yml` avec vos chemins de données :
   - `project_absolute_path` : Chemin absolu du projet
   - `data_path` : Chemin où sont stockées les données
   - `download_path` : Chemin pour les téléchargements

## Utilisation

### 🆕 Nouvelle architecture avec Jenkins (Recommandé)

La nouvelle architecture permet à Jenkins de contrôler l'exécution via des variables d'environnement.

**Important :** Chaque job Jenkins appelle individuellement `run_job.py` avec une source de données spécifique. Les jobs sont indépendants - les dépendances sont gérées par Jenkins.

**Point d'entrée unique :**
```bash
# Définir les variables d'environnement requises
export ETL_JOB_NAME=gitech_parifoot_daily
export ETL_SOURCE_NAME=gitech_parifoot

# Exécuter le job
python scripts/run_job.py
```

Voir [docs/JENKINS_INTEGRATION.md](docs/JENKINS_INTEGRATION.md) pour la documentation complète de l'intégration Jenkins.

**📋 Prochaines étapes :** Consultez [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md) pour un plan d'action détaillé.

**Avec dates personnalisées :**
```bash
export ETL_JOB_NAME=gitech_parifoot_daily
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_START_DATE=2025-01-15
export ETL_END_DATE=2025-01-15
python scripts/run_job.py
```

**Skipper des étapes :**
```bash
export ETL_JOB_NAME=transform_only
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_SKIP_EXTRACT=true
python scripts/run_job.py
```

Voir [docs/ENV_VARIABLES.md](docs/ENV_VARIABLES.md) pour la documentation complète des variables d'environnement et [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) pour les détails de l'architecture.

### Ancienne méthode (toujours supportée)

Chaque source a son propre orchestrator dans `scripts/[source_name]/orchestrator.py` :

```bash
# Exemple : Exécuter l'orchestrator pour Honore Gaming
python scripts/honore_gaming/orchestrator.py
```

### Structure d'un orchestrator

Tous les orchestrators utilisent maintenant la classe `base.Orchestrator` :

```python
from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_source_name as extract
from transform import run_source_name_transformer as transform
from load import run_source_name_loader as load

def run_source_name_orchestrator():
    orchestrator = Orchestrator(
        name="source_name",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_source_name_orchestrator()
```

## Sources disponibles

Le projet supporte de nombreuses sources de données :

- **Afitech** : Betting operations, commission history, daily betting, daily payment activity
- **Bwinner** : Bwinner, Bwinner Gambie, Bwinner from Afitech
- **Gitech** : Gitech, Gitech Casino, Gitech Lotto, Gitech Parifoot, Gitech Physique, Gitech Tirage
- **Honore Gaming** : Honore Gaming, Honore Gaming New, Honore Gaming Ticket
- **Lonasebet** : Lonasebet Casino, Lonasebet Global, Lonasebet Online
- **PMU** : PMU CA, PMU Lots, PMU Online, PMU Senegal
- **Sunubet** : Sunubet Casino, Sunubet Online, Sunubet Paiement
- Et bien d'autres...

## Architecture

### 🆕 Nouvelle architecture (Jenkins + Variables d'environnement)

La nouvelle architecture offre plus de flexibilité et permet à Jenkins de contrôler complètement l'exécution :

- **Point d'entrée unique** : `scripts/run_job.py`
- **Configuration via variables d'environnement** : Jenkins transmet toute la config
- **Pipeline avec retry automatique** : Gestion robuste des erreurs
- **Factory d'adapters** : Ajout facile de nouvelles sources
- **Mode dry-run et debug** : Facilite les tests

Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) pour plus de détails.

### Pattern ETL standard

Chaque source suit le pattern Extract → Transform → Load :

1. **Extract** : Extraction des données depuis la source (FTP, Web scraping, Base de données)
2. **Transform** : Transformation et nettoyage des données
3. **Load** : Chargement des données dans les bases de données cibles

### Classes de base

- **Orchestrator** : Coordonne les étapes ETL
- **BaseScrapper** : Classe de base pour le web scraping (Selenium)
- **BaseFTP** : Classe de base pour les connexions FTP
- **DatabaseExtractor** : Classe de base pour l'extraction depuis bases de données
- **Transformer** : Classe de base pour la transformation de données
- **Loader** : Classe de base pour le chargement dans SQL Server uniquement
- **Loader2** : Classe de base pour le chargement dans SQL Server ET Oracle

#### Différence entre Loader et Loader2

- **Loader** (`base/loader.py`) : 
  - Supporte uniquement SQL Server
  - Nécessite `columns` et `table_name` dans le constructeur
  - Utilisé pour les sources qui chargent uniquement dans SQL Server

- **Loader2** (`base/loader2.py`) :
  - Supporte SQL Server ET Oracle simultanément
  - Permet de charger dans les deux bases de données en une seule exécution
  - Nécessite des variables d'environnement Oracle supplémentaires
  - Utilisé pour les sources qui doivent charger dans Oracle en plus de SQL Server

## Configuration

### Variables d'environnement

Les variables d'environnement sont chargées depuis le fichier `.env`. Voir `.env.example` pour la liste complète.

### Fichiers de configuration

Chaque source a son propre fichier `config.yml` dans `scripts/[source_name]/config.yml` qui définit :
- Chemins de stockage des fichiers
- Patterns de fichiers
- Configuration spécifique à la source

## Logs

Les logs sont générés dans le répertoire `logs/` avec le format :
- `logs/extract_[source_name].log`
- `logs/transformer_[source_name].log`
- `logs/loader_[source_name].log`
- `logs/orchestrator_[source_name].log`

## Développement

### Ajouter une nouvelle source

1. Créer un nouveau répertoire dans `scripts/[nouvelle_source]/`
2. Créer les fichiers :
   - `extract.py` : Implémenter la classe d'extraction
   - `transform.py` : Implémenter la classe de transformation
   - `load.py` : Implémenter la classe de chargement
   - `orchestrator.py` : Créer l'orchestrator utilisant `base.Orchestrator`
   - `config.yml` : Configuration spécifique

3. Suivre le pattern des sources existantes

### Bonnes pratiques

- Utiliser `utils.path_utils.setup_project_paths()` au lieu de `sys.path.append()`
- Utiliser `base.Orchestrator` pour tous les orchestrators
- Suivre les conventions de nommage : `run_[source]_[type]`
- Documenter les configurations spécifiques dans les fichiers `config.yml`
- Centraliser les connexions BD avec `utils.db_utils.sql_server_connection`/`oracle_connection` ou `base.loader.Loader` (support SQL Server + Oracle dans une seule classe)
- Factoriser les loaders via `base/loader.py` (ne plus utiliser `base/loader2.py`)
- Parser les dates avec `utils.date_utils.parse_date_multi` pour gérer plusieurs formats
- Ajouter des tests unitaires simples dans `tests/` (ex. `tests/test_date_utils.py`) pour valider les helpers critiques
- Logguer systématiquement les erreurs avec `exc_info=True` quand c'est pertinent, éviter les `except:` génériques

## Dépannage

### Problèmes de chemins

Si vous rencontrez des erreurs d'import, vérifiez que :
- `utils.path_utils.setup_project_paths()` est appelé en premier dans chaque script
- Le fichier `.env` contient `ABSOLUTE_PROJECT_PATH` avec le bon chemin

### Problèmes de connexion

Vérifiez que toutes les variables d'environnement dans `.env` sont correctement configurées :
- Identifiants des bases de données
- Identifiants FTP
- Identifiants des sources externes

## Support

Pour toute question ou problème, consultez les logs dans le répertoire `logs/`.

