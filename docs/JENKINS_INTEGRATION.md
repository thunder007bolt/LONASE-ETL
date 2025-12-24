# Intégration avec Jenkins

Ce document explique comment intégrer le pipeline ETL avec Jenkins, en tenant compte que **chaque job Jenkins appelle individuellement `run_job.py` avec une source spécifique**.

## Principe

**Un job Jenkins = Une source de données = Un appel à `run_job.py`**

Chaque job Jenkins est complètement indépendant et traite une seule source de données à la fois. Les dépendances et l'ordre d'exécution sont gérés par Jenkins, pas par le code.

## Structure recommandée

### Option 1 : Un job par source (Recommandé)

Créer un job Jenkins dédié pour chaque source de données :

- **Job "gitech_parifoot_daily"**
  - `ETL_SOURCE_NAME=gitech_parifoot`
  - Exécuté quotidiennement à 2h du matin

- **Job "afitech_daily_betting_daily"**
  - `ETL_SOURCE_NAME=afitech_daily_betting`
  - Exécuté quotidiennement à 3h du matin

- **Job "bwinner_gambie_daily"**
  - `ETL_SOURCE_NAME=bwinner_gambie`
  - Exécuté quotidiennement à 4h du matin

**Avantages :**
- ✅ Clarté : Chaque job a un objectif précis
- ✅ Indépendance : Un job peut échouer sans affecter les autres
- ✅ Logs séparés : Plus facile de suivre les erreurs
- ✅ Configuration spécifique : Chaque job peut avoir ses propres paramètres

### Option 2 : Job générique avec paramètre

Créer un job unique qui accepte la source en paramètre :

- **Job "ETL_Generic"**
  - Paramètre `SOURCE_NAME` pour choisir la source
  - Peut traiter n'importe quelle source

**Avantages :**
- ✅ Moins de jobs à maintenir
- ✅ Réutilisable

**Inconvénients :**
- ❌ Moins de flexibilité pour la configuration spécifique
- ❌ Logs moins clairs

## Exemples de configurations Jenkins

### Exemple 1 : Job dédié pour une source

**Job Jenkins : "gitech_parifoot_daily"**

```groovy
pipeline {
    agent any
    
    // Exécution quotidienne à 2h du matin
    triggers {
        cron('0 2 * * *')
    }
    
    environment {
        ETL_JOB_NAME = "gitech_parifoot_daily"
        ETL_SOURCE_NAME = "gitech_parifoot"
        // Dates par défaut : hier (géré par le code si non spécifié)
    }
    
    stages {
        stage('ETL') {
            steps {
                script {
                    sh '''
                        python scripts/run_job.py
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo 'Job terminé avec succès'
        }
        failure {
            echo 'Job échoué - Vérifier les logs'
            // Optionnel : Envoyer une notification
        }
    }
}
```

### Exemple 2 : Job avec dates personnalisées

**Job Jenkins : "gitech_parifoot_manual"**

```groovy
pipeline {
    agent any
    
    environment {
        ETL_JOB_NAME = "gitech_parifoot_manual"
        ETL_SOURCE_NAME = "gitech_parifoot"
        ETL_START_DATE = "${params.START_DATE}"
        ETL_END_DATE = "${params.END_DATE}"
    }
    
    parameters {
        string(
            name: 'START_DATE',
            defaultValue: '',
            description: 'Date de début (YYYY-MM-DD). Vide = hier'
        )
        string(
            name: 'END_DATE',
            defaultValue: '',
            description: 'Date de fin (YYYY-MM-DD). Vide = hier'
        )
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

### Exemple 3 : Job avec dépendance

**Job "afitech_daily_betting_daily" qui s'exécute après "gitech_parifoot_daily"**

```groovy
pipeline {
    agent any
    
    triggers {
        // S'exécute après le job "gitech_parifoot_daily" en cas de succès
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

### Exemple 4 : Job avec retry personnalisé

**Job "bwinner_gambie_daily" avec retry configuré**

```groovy
pipeline {
    agent any
    
    triggers {
        cron('0 4 * * *')
    }
    
    environment {
        ETL_JOB_NAME = "bwinner_gambie_daily"
        ETL_SOURCE_NAME = "bwinner_gambie"
        ETL_RETRY_COUNT = "5"
        ETL_RETRY_DELAY = "10"
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

### Exemple 5 : Job générique (toutes sources)

**Job "ETL_Generic" qui peut traiter n'importe quelle source**

```groovy
pipeline {
    agent any
    
    environment {
        ETL_JOB_NAME = "${env.JOB_NAME}"
        ETL_SOURCE_NAME = "${params.SOURCE_NAME}"
        ETL_START_DATE = "${params.START_DATE}"
        ETL_END_DATE = "${params.END_DATE}"
        ETL_DEBUG = "${params.DEBUG ?: 'false'}"
    }
    
    parameters {
        choice(
            name: 'SOURCE_NAME',
            choices: [
                'gitech_parifoot',
                'afitech_daily_betting',
                'bwinner_gambie',
                // ... autres sources
            ],
            description: 'Source de données à traiter'
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
        booleanParam(
            name: 'DEBUG',
            defaultValue: false,
            description: 'Mode debug'
        )
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

## Gestion des erreurs

Le script `run_job.py` retourne :
- **Code 0** : Succès
- **Code 1** : Échec

Jenkins peut utiliser ces codes pour :
- Déclencher des notifications
- Arrêter les jobs dépendants
- Envoyer des alertes

### Exemple avec gestion d'erreur

```groovy
stages {
    stage('ETL') {
        steps {
            script {
                def result = sh(
                    script: 'python scripts/run_job.py',
                    returnStatus: true
                )
                
                if (result != 0) {
                    error("Le job ETL a échoué avec le code ${result}")
                }
            }
        }
    }
}
```

## Logs

Les logs sont générés dans :
- `logs/run_job.log` : Log principal du job
- `logs/extract_<source>.log` : Logs d'extraction (si existants)
- `logs/transformer_<source>.log` : Logs de transformation (si existants)
- `logs/loader_<source>.log` : Logs de chargement (si existants)

## Bonnes pratiques

1. **Un job par source** : Plus facile à maintenir et déboguer
2. **Noms explicites** : `gitech_parifoot_daily` plutôt que `job1`
3. **Variables d'environnement** : Toujours définir `ETL_JOB_NAME` et `ETL_SOURCE_NAME`
4. **Gestion d'erreurs** : Configurer les notifications en cas d'échec
5. **Logs** : Vérifier régulièrement les logs dans `logs/`
6. **Tests** : Utiliser `ETL_DRY_RUN=true` pour tester sans exécuter

## Checklist de création d'un job Jenkins

- [ ] Créer le job Jenkins avec un nom explicite
- [ ] Définir `ETL_JOB_NAME` dans les variables d'environnement
- [ ] Définir `ETL_SOURCE_NAME` dans les variables d'environnement
- [ ] Vérifier que l'adapter existe pour la source (`adapters/<source>/`)
- [ ] Configurer les triggers (cron, upstream, etc.)
- [ ] Configurer les notifications en cas d'échec
- [ ] Tester avec `ETL_DRY_RUN=true` d'abord
- [ ] Documenter les paramètres spécifiques si nécessaire

