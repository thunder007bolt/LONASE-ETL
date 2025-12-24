# Guide de démarrage rapide

Ce guide vous permet de démarrer rapidement avec la nouvelle architecture.

## Installation

Aucune installation supplémentaire n'est nécessaire. L'architecture utilise les mêmes dépendances que le projet existant.

## Utilisation de base

### 1. Configuration minimale

```bash
export ETL_JOB_NAME=mon_job
export ETL_SOURCE_NAME=gitech_parifoot
python scripts/run_job.py
```

### 2. Avec dates personnalisées

```bash
export ETL_JOB_NAME=mon_job
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_START_DATE=2025-01-15
export ETL_END_DATE=2025-01-15
python scripts/run_job.py
```

### 3. Skipper des étapes

```bash
# Exécuter seulement transform + load
export ETL_JOB_NAME=mon_job
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_SKIP_EXTRACT=true
python scripts/run_job.py
```

## Sources disponibles

Les sources suivantes ont déjà des adapters créés :

- ✅ `gitech_parifoot`
- ✅ `afitech_daily_betting`
- ✅ `bwinner_gambie`

## Créer un adapter pour une nouvelle source

### Méthode 1 : Script automatique (Recommandé)

```bash
python scripts/generate_adapter.py <source_name>
```

Exemple :
```bash
python scripts/generate_adapter.py lonasebet_casino
```

Le script génère automatiquement tous les fichiers nécessaires.

### Méthode 2 : Manuel

1. Créer la structure :
   ```bash
   mkdir -p adapters/category/source_name
   ```

2. Créer les fichiers en suivant le pattern des adapters existants

3. Voir [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) pour plus de détails

## Variables d'environnement essentielles

| Variable | Description | Exemple |
|----------|-------------|---------|
| `ETL_JOB_NAME` | Nom du job | `gitech_parifoot_daily` |
| `ETL_SOURCE_NAME` | Nom de la source | `gitech_parifoot` |
| `ETL_START_DATE` | Date de début | `2025-01-15` |
| `ETL_END_DATE` | Date de fin | `2025-01-15` |
| `ETL_SKIP_EXTRACT` | Ignorer extract | `true` ou `false` |
| `ETL_SKIP_TRANSFORM` | Ignorer transform | `true` ou `false` |
| `ETL_SKIP_LOAD` | Ignorer load | `true` ou `false` |
| `ETL_DEBUG` | Mode debug | `true` ou `false` |
| `ETL_DRY_RUN` | Mode simulation | `true` ou `false` |

Voir [ENV_VARIABLES.md](ENV_VARIABLES.md) pour la liste complète.

## Exemples pratiques

### Exemple 1 : Job complet quotidien

```bash
export ETL_JOB_NAME=gitech_parifoot_daily
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_START_DATE=$(date -d "yesterday" +%Y-%m-%d)
export ETL_END_DATE=$(date -d "yesterday" +%Y-%m-%d)
python scripts/run_job.py
```

### Exemple 2 : Recharger seulement les données transformées

```bash
export ETL_JOB_NAME=reload_data
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_SKIP_EXTRACT=true
export ETL_SKIP_TRANSFORM=true
python scripts/run_job.py
```

### Exemple 3 : Mode debug avec retry personnalisé

```bash
export ETL_JOB_NAME=debug_job
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_DEBUG=true
export ETL_RETRY_COUNT=5
export ETL_RETRY_DELAY=10
python scripts/run_job.py
```

### Exemple 4 : Test sans exécution (dry-run)

```bash
export ETL_JOB_NAME=test_job
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_DRY_RUN=true
python scripts/run_job.py
```

## Intégration avec Jenkins

**Modèle d'exécution :** Chaque job Jenkins appelle individuellement `run_job.py` avec une source spécifique.

### Créer un job Jenkins pour une source

1. **Créer un nouveau job Jenkins** (Pipeline ou Freestyle)
2. **Définir les variables d'environnement** :
   - `ETL_JOB_NAME` : Nom du job (ex: `gitech_parifoot_daily`)
   - `ETL_SOURCE_NAME` : Nom de la source (ex: `gitech_parifoot`)
   - `ETL_START_DATE` : Date de début (optionnel)
   - `ETL_END_DATE` : Date de fin (optionnel)
3. **Exécuter la commande** : `python scripts/run_job.py`

### Exemple minimal de job Jenkins

```groovy
pipeline {
    agent any
    
    environment {
        ETL_JOB_NAME = "gitech_parifoot_daily"
        ETL_SOURCE_NAME = "gitech_parifoot"
    }
    
    stages {
        stage('ETL') {
            steps {
                sh 'python scripts/run_job.py'
            }
        }
    }
}
```

### Gérer plusieurs sources

**Recommandation :** Créer un job Jenkins par source pour plus de clarté :
- Job "gitech_parifoot_daily" → `ETL_SOURCE_NAME=gitech_parifoot`
- Job "afitech_daily_betting_daily" → `ETL_SOURCE_NAME=afitech_daily_betting`
- Job "bwinner_gambie_daily" → `ETL_SOURCE_NAME=bwinner_gambie`

Chaque job est indépendant. Les dépendances entre jobs sont gérées dans Jenkins (triggers, upstream, etc.).

Voir [ENV_VARIABLES.md](ENV_VARIABLES.md) pour des exemples complets de pipelines Jenkins.

## Dépannage

### Erreur : "Variables d'environnement requises manquantes"

Assurez-vous d'avoir défini :
- `ETL_JOB_NAME`
- `ETL_SOURCE_NAME`

### Erreur : "Extractor non trouvé pour: <source>"

L'adapter pour cette source n'existe pas encore. Créez-le avec :
```bash
python scripts/generate_adapter.py <source_name>
```

### Les dates ne sont pas prises en compte

Les dates peuvent être définies via :
- Variables d'environnement : `ETL_START_DATE` et `ETL_END_DATE`
- Variables d'environnement legacy : `start_date` et `end_date`
- Configuration YAML : `config.yml`

## Ressources

- [ARCHITECTURE.md](ARCHITECTURE.md) : Détails de l'architecture
- [ENV_VARIABLES.md](ENV_VARIABLES.md) : Documentation complète des variables
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) : Guide de migration
- [JENKINS_INTEGRATION.md](JENKINS_INTEGRATION.md) : Guide d'intégration Jenkins
- [NEXT_STEPS.md](NEXT_STEPS.md) : **Prochaines étapes à suivre**
- Logs : `logs/run_job.log`

