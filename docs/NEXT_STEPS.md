# Prochaines étapes

Ce document liste les actions à entreprendre pour mettre en place et utiliser la nouvelle architecture.

## ✅ Ce qui est déjà fait

- ✅ Architecture de base créée (core, pipeline, adapters)
- ✅ 3 adapters créés (gitech_parifoot, afitech_daily_betting, bwinner_gambie)
- ✅ Point d'entrée unique (scripts/run_job.py)
- ✅ Documentation complète
- ✅ Script de génération automatique d'adapters

## 🎯 Prochaines étapes prioritaires

### Phase 1 : Tests et validation (1-2 jours)

#### 1.1 Tester avec les adapters existants

```bash
# Test 1 : gitech_parifoot en mode dry-run
export ETL_JOB_NAME=test_gitech_parifoot
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_DRY_RUN=true
python scripts/run_job.py

# Test 2 : afitech_daily_betting avec dates
export ETL_JOB_NAME=test_afitech
export ETL_SOURCE_NAME=afitech_daily_betting
export ETL_START_DATE=2025-01-15
export ETL_END_DATE=2025-01-15
export ETL_DEBUG=true
python scripts/run_job.py

# Test 3 : bwinner_gambie
export ETL_JOB_NAME=test_bwinner
export ETL_SOURCE_NAME=bwinner_gambie
python scripts/run_job.py
```

**Objectif :** Vérifier que les adapters fonctionnent correctement avec les fonctions existantes.

#### 1.2 Vérifier les logs

- Vérifier que les logs sont générés correctement dans `logs/run_job.log`
- Vérifier que les messages sont clairs et informatifs
- Vérifier que les erreurs sont bien capturées

#### 1.3 Tester les fonctionnalités

- [ ] Test du retry automatique (simuler une erreur)
- [ ] Test du skip d'étapes (ETL_SKIP_EXTRACT=true)
- [ ] Test du mode dry-run
- [ ] Test du mode debug
- [ ] Test avec dates personnalisées

### Phase 2 : Créer des adapters pour les sources prioritaires (2-3 jours)

#### 2.1 Identifier les sources prioritaires

Lister les sources les plus utilisées ou critiques :
- [ ] Source 1 : _______________
- [ ] Source 2 : _______________
- [ ] Source 3 : _______________

#### 2.2 Générer les adapters automatiquement

Pour chaque source prioritaire :

```bash
# Générer l'adapter
python scripts/generate_adapter.py <source_name>

# Vérifier les fichiers générés
# Ajuster si nécessaire (noms de fonctions, paramètres, etc.)

# Tester l'adapter
export ETL_JOB_NAME=test_<source_name>
export ETL_SOURCE_NAME=<source_name>
export ETL_DRY_RUN=true
python scripts/run_job.py
```

**Exemple :**
```bash
python scripts/generate_adapter.py lonasebet_casino
python scripts/generate_adapter.py honore_gaming
python scripts/generate_adapter.py pmu_ca
```

#### 2.3 Vérifier et ajuster les adapters générés

- Vérifier que les noms de fonctions sont corrects
- Ajuster si la source nécessite des dates (utiliser `create_wrapper_with_dates`)
- Tester chaque adapter

### Phase 3 : Configuration Jenkins (1-2 jours)

#### 3.1 Créer un job Jenkins pilote

Créer un job Jenkins pour tester avec une source :

**Job : "ETL_gitech_parifoot_test"**

```groovy
pipeline {
    agent any
    
    environment {
        ETL_JOB_NAME = "gitech_parifoot_test"
        ETL_SOURCE_NAME = "gitech_parifoot"
        ETL_DEBUG = "true"
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

#### 3.2 Tester le job Jenkins

- Exécuter le job depuis Jenkins
- Vérifier les logs dans Jenkins
- Vérifier les logs dans `logs/run_job.log`
- Vérifier que le code de sortie est correct (0 = succès, 1 = échec)

#### 3.3 Créer les jobs pour les sources prioritaires

Pour chaque source prioritaire, créer un job Jenkins :

- [ ] Job "ETL_gitech_parifoot_daily"
- [ ] Job "ETL_afitech_daily_betting_daily"
- [ ] Job "ETL_<source>_daily"

**Template :**
```groovy
pipeline {
    agent any
    
    triggers {
        cron('0 2 * * *')  // Ajuster l'heure selon les besoins
    }
    
    environment {
        ETL_JOB_NAME = "<job_name>"
        ETL_SOURCE_NAME = "<source_name>"
    }
    
    stages {
        stage('ETL') {
            steps {
                sh 'python scripts/run_job.py'
            }
        }
    }
    
    post {
        failure {
            // Optionnel : Envoyer une notification
            echo 'Job échoué - Vérifier les logs'
        }
    }
}
```

### Phase 4 : Migration progressive (1-2 semaines)

#### 4.1 Migrer les sources une par une

Pour chaque source :

1. Créer l'adapter (si pas déjà fait)
2. Tester en local
3. Créer le job Jenkins
4. Tester le job Jenkins
5. Mettre en production
6. Surveiller les logs pendant quelques jours

#### 4.2 Documenter les spécificités

Si une source a des spécificités (dates particulières, paramètres spéciaux, etc.), documenter dans :
- Le fichier adapter
- Un fichier README dans `adapters/<category>/<source>/`

### Phase 5 : Optimisation et amélioration (continue)

#### 5.1 Améliorer les logs

- Ajouter des métriques (durée, nombre de fichiers traités, etc.)
- Améliorer les messages d'erreur

#### 5.2 Ajouter des fonctionnalités si nécessaire

- Monitoring/alerting
- Métriques de performance
- Dashboard (optionnel)

#### 5.3 Nettoyage

Une fois toutes les sources migrées :
- [ ] Supprimer les anciens orchestrators (optionnel, garder pour référence)
- [ ] Documenter les changements
- [ ] Former l'équipe sur la nouvelle architecture

## 📋 Checklist globale

### Tests initiaux
- [ ] Tester gitech_parifoot
- [ ] Tester afitech_daily_betting
- [ ] Tester bwinner_gambie
- [ ] Vérifier les logs
- [ ] Tester toutes les fonctionnalités (retry, skip, dry-run, debug)

### Création d'adapters
- [ ] Identifier les sources prioritaires
- [ ] Générer les adapters avec le script
- [ ] Vérifier et ajuster les adapters
- [ ] Tester chaque adapter

### Configuration Jenkins
- [ ] Créer un job pilote
- [ ] Tester le job pilote
- [ ] Créer les jobs pour les sources prioritaires
- [ ] Configurer les triggers (cron, dépendances)
- [ ] Configurer les notifications

### Migration
- [ ] Migrer les sources prioritaires
- [ ] Surveiller les logs
- [ ] Migrer progressivement les autres sources
- [ ] Documenter les spécificités

### Finalisation
- [ ] Toutes les sources migrées
- [ ] Documentation à jour
- [ ] Équipe formée
- [ ] Nettoyage effectué (si nécessaire)

## 🚨 Points d'attention

1. **Compatibilité** : L'ancienne architecture continue de fonctionner, pas de pression pour tout migrer d'un coup

2. **Tests** : Toujours tester en mode dry-run d'abord, puis avec une date de test

3. **Logs** : Surveiller les logs régulièrement, surtout au début

4. **Dates** : Vérifier que les dates sont bien passées aux fonctions existantes (injection automatique via `date_injector`)

5. **Erreurs** : Si une fonction existante échoue, vérifier d'abord qu'elle fonctionne avec l'ancien orchestrator

## 📞 Support

En cas de problème :

1. Vérifier les logs dans `logs/run_job.log`
2. Vérifier la documentation :
   - [QUICK_START.md](QUICK_START.md)
   - [JENKINS_INTEGRATION.md](JENKINS_INTEGRATION.md)
   - [ENV_VARIABLES.md](ENV_VARIABLES.md)
3. Vérifier que l'adapter existe et est correctement enregistré
4. Tester avec `ETL_DEBUG=true` pour plus de détails

## 🎯 Objectif final

Avoir tous les jobs ETL exécutés via Jenkins avec la nouvelle architecture, en profitant de :
- ✅ Flexibilité via variables d'environnement
- ✅ Retry automatique
- ✅ Logs détaillés
- ✅ Gestion d'erreurs robuste
- ✅ Maintenance simplifiée

