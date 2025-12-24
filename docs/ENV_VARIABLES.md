# Variables d'environnement pour Jenkins

Ce document décrit toutes les variables d'environnement que Jenkins peut transmettre au pipeline ETL.

## Variables requises

Ces variables doivent être définies pour que le job fonctionne :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `ETL_JOB_NAME` | Nom du job (utilisé pour les logs) | `gitech_parifoot_daily` |
| `ETL_SOURCE_NAME` | Nom de la source de données | `gitech_parifoot` |

## Variables optionnelles - Dates

| Variable | Description | Format | Exemple |
|----------|-------------|--------|---------|
| `ETL_START_DATE` | Date de début pour l'extraction | `YYYY-MM-DD` | `2025-01-15` |
| `ETL_END_DATE` | Date de fin pour l'extraction | `YYYY-MM-DD` | `2025-01-15` |

**Note:** Si ces variables ne sont pas définies, les dates seront lues depuis `config.yml` ou utilisent la date d'hier par défaut.

## Variables optionnelles - Flags de contrôle

| Variable | Description | Valeurs possibles | Défaut |
|----------|-------------|-------------------|--------|
| `ETL_SKIP_EXTRACT` | Ignorer l'étape d'extraction | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `ETL_SKIP_TRANSFORM` | Ignorer l'étape de transformation | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `ETL_SKIP_LOAD` | Ignorer l'étape de chargement | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `ETL_DRY_RUN` | Mode simulation (ne fait rien) | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `ETL_DEBUG` | Mode debug (logs détaillés) | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |

## Variables optionnelles - Paramètres de retry

| Variable | Description | Type | Défaut |
|----------|-------------|------|--------|
| `ETL_RETRY_COUNT` | Nombre de tentatives en cas d'échec | Entier | `3` |
| `ETL_RETRY_DELAY` | Délai entre les tentatives (secondes) | Entier | `5` |
| `ETL_BATCH_SIZE` | Taille des lots pour le chargement | Entier | `1000` |

## Variables optionnelles - Paramètres supplémentaires

| Variable | Description | Format | Exemple |
|----------|-------------|--------|---------|
| `ETL_EXTRA_PARAMS` | Paramètres supplémentaires en JSON | JSON string | `{"custom_param": "value"}` |

## Variables optionnelles - Chemins

| Variable | Description | Exemple |
|----------|-------------|---------|
| `ETL_DATA_PATH` | Chemin vers le répertoire de données | `K:/ETL/DATA_FICHIERS/` |
| `ETL_PROJECT_PATH` | Chemin vers le projet | `C:/ETL/` |

**Note:** Si ces variables ne sont pas définies, les chemins seront lus depuis `config/base_config.yml`.

## Variables de base de données

Ces variables sont déjà utilisées par le système existant :

| Variable | Description |
|----------|-------------|
| `SQL_SERVER_HOST` | Hôte SQL Server |
| `SQL_SERVER_TEMPDB_NAME` | Nom de la base de données temporaire |
| `SQL_SERVER_TEMPDB_USERNAME` | Nom d'utilisateur SQL Server |
| `SQL_SERVER_TEMPDB_PASSWORD` | Mot de passe SQL Server |
| `ORACLE_TARGET_USERNAME` | Nom d'utilisateur Oracle |
| `ORACLE_TARGET_PASSWORD` | Mot de passe Oracle |
| `ORACLE_TARGET_HOST` | Hôte Oracle |
| `ORACLE_TARGET_PORT` | Port Oracle |
| `ORACLE_TARGET_SERVICE` | Service Oracle |
| `ORACLE_CLIENT_LIB_DIR` | Répertoire des bibliothèques client Oracle |

## Exemples d'utilisation

### Exemple 1 : Job complet avec dates spécifiques

```bash
export ETL_JOB_NAME=gitech_parifoot_daily
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_START_DATE=2025-01-15
export ETL_END_DATE=2025-01-15
python scripts/run_job.py
```

### Exemple 2 : Job avec seulement la transformation et le chargement

```bash
export ETL_JOB_NAME=gitech_parifoot_transform_load
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_SKIP_EXTRACT=true
python scripts/run_job.py
```

### Exemple 3 : Mode debug avec retry personnalisé

```bash
export ETL_JOB_NAME=gitech_parifoot_debug
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_DEBUG=true
export ETL_RETRY_COUNT=5
export ETL_RETRY_DELAY=10
python scripts/run_job.py
```

### Exemple 4 : Dry run (simulation)

```bash
export ETL_JOB_NAME=gitech_parifoot_test
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_DRY_RUN=true
python scripts/run_job.py
```

## Pipeline Jenkins

**Important :** Chaque job Jenkins est indépendant et traite une seule source de données à la fois.

### Exemple 1 : Job Jenkins pour une source spécifique

**Job Jenkins : "gitech_parifoot_daily"**

```groovy
pipeline {
    agent any
    
    environment {
        ETL_JOB_NAME = "gitech_parifoot_daily"
        ETL_SOURCE_NAME = "gitech_parifoot"  // Source fixe pour ce job
        ETL_START_DATE = "${params.START_DATE}"
        ETL_END_DATE = "${params.END_DATE}"
    }
    
    parameters {
        string(
            name: 'START_DATE',
            defaultValue: '',
            description: 'Date de début (YYYY-MM-DD)'
        )
        string(
            name: 'END_DATE',
            defaultValue: '',
            description: 'Date de fin (YYYY-MM-DD)'
        )
    }
    
    stages {
        stage('ETL') {
            steps {
                sh '''
                    python scripts/run_job.py
                '''
            }
        }
    }
}
```

### Exemple 2 : Job Jenkins générique avec choix de source

Si vous voulez un job qui peut traiter plusieurs sources :

```groovy
pipeline {
    agent any
    
    environment {
        ETL_JOB_NAME = "${env.JOB_NAME}"
        ETL_SOURCE_NAME = "${params.SOURCE_NAME}"  // Source choisie via paramètre
        ETL_START_DATE = "${params.START_DATE}"
        ETL_END_DATE = "${params.END_DATE}"
        ETL_RETRY_COUNT = "${params.RETRY_COUNT ?: '3'}"
        ETL_DEBUG = "${params.DEBUG ?: 'false'}"
    }
    
    parameters {
        choice(
            name: 'SOURCE_NAME',
            choices: ['gitech_parifoot', 'afitech_daily_betting', 'bwinner_gambie'],
            description: 'Source de données'
        )
        string(
            name: 'START_DATE',
            defaultValue: '',
            description: 'Date de début (YYYY-MM-DD)'
        )
        string(
            name: 'END_DATE',
            defaultValue: '',
            description: 'Date de fin (YYYY-MM-DD)'
        )
        string(
            name: 'RETRY_COUNT',
            defaultValue: '3',
            description: 'Nombre de tentatives'
        )
        booleanParam(
            name: 'DEBUG',
            defaultValue: false,
            description: 'Mode debug'
        )
    }
    
    stages {
        stage('ETL') {
            steps {
                sh '''
                    python scripts/run_job.py
                '''
            }
        }
    }
}
```

### Exemple 3 : Plusieurs jobs indépendants

**Recommandé :** Créer un job Jenkins par source pour plus de clarté et de contrôle.

- **Job "gitech_parifoot_daily"** : `ETL_SOURCE_NAME=gitech_parifoot`
- **Job "afitech_daily_betting_daily"** : `ETL_SOURCE_NAME=afitech_daily_betting`
- **Job "bwinner_gambie_daily"** : `ETL_SOURCE_NAME=bwinner_gambie`

Chaque job peut avoir sa propre configuration, ses propres triggers, ses propres dépendances dans Jenkins.

### Gestion des dépendances entre jobs

Si un job doit s'exécuter après un autre, configurez cela dans Jenkins :

```groovy
// Job "afitech_daily_betting" qui dépend de "gitech_parifoot"
pipeline {
    agent any
    
    triggers {
        // S'exécute après le job "gitech_parifoot_daily"
        upstream(upstreamProjects: 'gitech_parifoot_daily', threshold: hudson.model.Result.SUCCESS)
    }
    
    environment {
        ETL_JOB_NAME = "afitech_daily_betting_daily"
        ETL_SOURCE_NAME = "afitech_daily_betting"
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

