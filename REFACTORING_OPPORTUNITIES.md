# Pistes de Refactoring - LONASE-ETL

## Analyse complète des opportunités de refactoring

Ce document identifie les principales opportunités de refactoring dans le projet LONASE-ETL après analyse de tous les scripts.

---

## 🔴 CRITIQUE - Duplications majeures

### 1. Méthode `convert_xls_to_xlsx()` dupliquée (9 occurrences)

**Fichiers concernés :**
- `scripts/gitech_lotto/transform.py`
- `scripts/gitech_parifoot/transform.py`
- `scripts/gitech_lotto_ca/transform.py`
- `scripts/gitech_casino/transform.py`
- `scripts/gitech/transform.py`
- `scripts/bwinner_gambie/transform.py`
- `scripts/solidicon/transform.py`
- `scripts/pmu_online/transform.py`
- `scripts/ussd_irv/extract.py`

**Problème :** Code identique copié-collé dans 9 fichiers différents avec un chemin hardcodé `TEMP_DIR = r"C:\Users\optiware2\AppData\Local\Temp\gen_py\3.7"`

**Solution :**
- Créer `utils/excel_utils.py` avec une fonction `convert_xls_to_xlsx(xls_file: Path, logger) -> Path`
- Utiliser `tempfile.gettempdir()` au lieu d'un chemin hardcodé
- Remplacer toutes les occurrences par un import

**Impact :** Réduction de ~50 lignes × 9 = 450 lignes de code dupliqué

---

### 2. Méthode `process_numeric_column()` dupliquée (8 occurrences)

**Fichiers concernés :**
- `scripts/gitech_lotto/transform.py`
- `scripts/gitech_parifoot/transform.py`
- `scripts/gitech_lotto_ca/transform.py`
- `scripts/gitech_casino/transform.py`
- `scripts/gitech/transform.py`
- `scripts/bwinner_gambie/transform.py`
- `scripts/solidicon/transform.py`
- `scripts/pmu_online/transform.py`

**Problème :** Logique identique de nettoyage des colonnes numériques dupliquée

**Solution :**
- Créer `utils/data_cleaning_utils.py` avec `clean_numeric_value(value) -> int`
- Ajouter cette méthode dans `base/transformer.py` comme méthode utilitaire

**Impact :** Réduction de ~15 lignes × 8 = 120 lignes de code dupliqué

---

### 3. Pattern de transformation Gitech très similaire (5 fichiers)

**Fichiers concernés :**
- `scripts/gitech_lotto/transform.py`
- `scripts/gitech_parifoot/transform.py`
- `scripts/gitech_lotto_ca/transform.py`
- `scripts/gitech_casino/transform.py`
- `scripts/gitech/transform.py`

**Problème :** 
- Même logique de transformation (col_mapping, filtrage, nettoyage)
- Seule différence : pattern regex et quelques colonnes spécifiques

**Solution :**
- Créer `base/gitech_transformer.py` avec une classe `GitechBaseTransformer(Transformer)`
- Paramétrer les différences via configuration ou paramètres de classe
- Les transformers spécifiques héritent et surchargent uniquement les parties différentes

**Impact :** Réduction de ~150 lignes × 5 = 750 lignes de code dupliqué

---

### 4. Chemins hardcodés `filesInitialDirectory` (48 occurrences)

**Fichiers concernés :** Presque tous les scripts de transformation

**Problème :** Chemins hardcodés comme :
```python
filesInitialDirectory = r"K:\DATA_FICHIERS\LONASEBET\CASINO\\"
data.to_csv(filesInitialDirectory + "casinoLonasebet "+ date.strftime('%Y-%m-%d') + ".csv", ...)
```

**Solution :**
- Déplacer ces chemins dans `config.yml` de chaque source
- Créer une méthode utilitaire `utils/file_manipulation.py::save_to_archive_path()`
- Centraliser la logique de sauvegarde d'archive

**Impact :** 
- Meilleure maintenabilité
- Configuration centralisée
- Facilite les changements d'environnement

---

## 🟡 IMPORTANT - Améliorations structurelles

### 5. Pattern orchestrator répétitif (43 occurrences)

**Fichiers concernés :** Tous les `scripts/*/orchestrator.py`

**Problème :** Structure identique dans tous les orchestrators :
```python
def run_xxx_orchestrator():
    orchestrator = Orchestrator(
        name="xxx",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()
```

**Solution :**
- Créer un décorateur ou factory dans `base/orchestrator.py`
- Simplifier à : `create_orchestrator("xxx", extract, transform, load).run()`
- Ou utiliser un fichier de configuration centralisé pour les mappings

**Impact :** Réduction de ~10 lignes × 43 = 430 lignes de code répétitif

---

### 6. Pattern Load très similaire (39 fichiers)

**Fichiers concernés :** Tous les `scripts/*/load.py`

**Problème :** Structure presque identique :
```python
class XxxLoad(Loader):
    def __init__(self):
        name = 'xxx'
        log_file = 'logs/loader_xxx.log'
        columns = [...]
        table_name = "[...]"
        super().__init__(name, log_file, columns, table_name)
    
    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df
```

**Solution :**
- Créer `base/csv_loader.py` avec `CSVLoader(Loader)` qui implémente `_convert_file_to_dataframe` par défaut
- Les loaders spécifiques héritent et ne surchargent que si nécessaire
- Déplacer `columns` et `table_name` dans `config.yml`

**Impact :** Réduction de ~20 lignes × 39 = 780 lignes de code répétitif

---

### 7. Gestion d'erreurs incohérente

**Problème :**
- Certains scripts utilisent `self.set_error()` et `self.check_error()`
- D'autres utilisent `move_file(file, self.error_path)` directement
- Pas de standardisation

**Solution :**
- Standardiser dans `base/transformer.py` et `base/loader.py`
- Créer un contexte manager pour la gestion d'erreurs
- Améliorer `check_error()` pour lister réellement les fichiers en erreur (TODO actuel)

**Impact :** Meilleure traçabilité et debugging

---

### 8. Extraction de date dupliquée

**Problème :** Plusieurs transformers ont leur propre logique d'extraction de date depuis les fichiers Excel

**Solution :**
- Centraliser dans `utils/date_utils.py` avec plusieurs stratégies
- Utiliser `parse_date_multi()` comme recommandé dans le README
- Créer des helpers spécifiques pour les patterns Excel courants

**Impact :** Cohérence et réutilisabilité

---

### 9. Imports inutiles et non utilisés

**Problème :** Beaucoup de scripts importent des modules non utilisés :
- `import os` (non utilisé dans plusieurs fichiers)
- `import shutil` (seulement pour `convert_xls_to_xlsx`)
- `import win32com.client` (non utilisé)
- `import numpy as np` (parfois non utilisé)

**Solution :**
- Nettoyer les imports avec un linter (flake8, pylint)
- Utiliser `isort` pour organiser les imports
- Créer un script de vérification automatique

**Impact :** Code plus propre et maintenable

---

## 🟢 AMÉLIORATIONS - Qualité de code

### 10. Commentaires TODO non résolus

**Problèmes identifiés :**
- `# Todo: A supprimer` dans `scripts/honore_gaming/extract.py`
- `# TODO : déplacer le fichier dans un dossier d'erreur` (plusieurs fichiers)
- `# todo: get date from file or current date`
- `# todo: +1 if include_sup equals true`

**Solution :**
- Créer un ticket/issue pour chaque TODO
- Résoudre ou supprimer les TODOs obsolètes
- Documenter les TODOs restants

---

### 11. Code commenté (fichiers d'archive)

**Problème :** Beaucoup de lignes commentées comme :
```python
# filesInitialDirectory = r"K:\DATA_FICHIERS\GITECH\ALR\\"
# data.to_csv(filesInitialDirectory + "GITECH "+ date.strftime('%Y-%m-%d') + ".csv", ...)
```

**Solution :**
- Supprimer le code commenté si non utilisé
- Si nécessaire pour référence, déplacer dans un fichier `ARCHIVE.md` ou `HISTORY.md`

**Impact :** Code plus lisible

---

### 12. Noms de variables incohérents

**Problème :**
- `filesInitialDirectory` (camelCase) vs `file_path` (snake_case)
- `data` vs `df` vs `dataframe`
- Mélange de français et anglais

**Solution :**
- Standardiser sur snake_case (PEP 8)
- Utiliser des noms cohérents : `df` pour DataFrame, `file_path` pour Path
- Documenter les conventions dans le README

---

### 13. Gestion des dates inconsistante

**Problème :**
- Certains scripts utilisent `date.strftime("%d/%m/%Y")`
- D'autres utilisent `date.strftime('%Y-%m-%d')`
- Pas de format standardisé

**Solution :**
- Créer des constantes dans `utils/date_utils.py` :
  - `DATE_FORMAT_DISPLAY = "%d/%m/%Y"`
  - `DATE_FORMAT_STORAGE = "%Y-%m-%d"`
- Utiliser ces constantes partout

**Impact :** Cohérence et facilité de changement

---

### 14. `base/loader2.py` obsolète

**Problème :** Le fichier `base/loader2.py` existe mais ne fait qu'importer `base/loader.py`

**Solution :**
- Supprimer `base/loader2.py`
- Vérifier qu'aucun script ne l'importe encore
- Mettre à jour la documentation

---

### 15. Logique de consolidation dupliquée

**Fichier concerné :** `scripts/lonasebet_global/load.py`

**Problème :** Logique de consolidation de plusieurs fichiers avant chargement qui pourrait être réutilisée

**Solution :**
- Créer `base/consolidated_loader.py` avec cette logique
- Autres loaders qui ont besoin de consolidation peuvent en hériter

---

## 📊 Résumé des gains estimés

| Catégorie | Lignes de code à réduire | Fichiers impactés |
|-----------|-------------------------|-------------------|
| **Duplications critiques** | ~1,320 lignes | 20+ fichiers |
| **Patterns répétitifs** | ~1,210 lignes | 82+ fichiers |
| **Code mort/commenté** | ~200 lignes | 30+ fichiers |
| **TOTAL** | **~2,730 lignes** | **100+ fichiers** |

---

## 🎯 Plan d'action recommandé (par priorité)

### Phase 1 - Quick wins (1-2 jours)
1. ✅ Créer `utils/excel_utils.py` avec `convert_xls_to_xlsx()`
2. ✅ Créer `utils/data_cleaning_utils.py` avec `clean_numeric_value()`
3. ✅ Supprimer `base/loader2.py` et vérifier les imports
4. ✅ Nettoyer les imports inutiles

### Phase 2 - Refactoring structurel (3-5 jours)
5. ✅ Créer `base/gitech_transformer.py` pour factoriser les transformers Gitech
6. ✅ Créer `base/csv_loader.py` pour factoriser les loaders CSV
7. ✅ Déplacer les chemins hardcodés dans `config.yml`
8. ✅ Standardiser la gestion d'erreurs

### Phase 3 - Améliorations qualité (2-3 jours)
9. ✅ Résoudre/supprimer les TODOs
10. ✅ Supprimer le code commenté
11. ✅ Standardiser les noms de variables
12. ✅ Créer des constantes pour les formats de date

### Phase 4 - Optimisations avancées (optionnel)
13. ✅ Créer un factory pour les orchestrators
14. ✅ Créer `base/consolidated_loader.py`
15. ✅ Améliorer la documentation

---

## 🔍 Fichiers à examiner en priorité

1. `scripts/gitech_lotto/transform.py` - Contient beaucoup de code dupliqué
2. `scripts/gitech_parifoot/transform.py` - Même logique que gitech_lotto
3. `scripts/lonasebet_online/transform.py` - Chemins hardcodés
4. `scripts/lonasebet_casino/transform.py` - Chemins hardcodés
5. `scripts/honore_gaming/extract.py` - TODO à supprimer

---

## 📝 Notes importantes

- **Tests :** Avant chaque refactoring, s'assurer que les tests existants passent
- **Migration progressive :** Refactorer un script à la fois pour éviter les régressions
- **Documentation :** Mettre à jour le README après chaque changement structurel
- **Backup :** Créer une branche Git pour chaque phase de refactoring

---

*Document généré le : 2025-01-XX*
*Analyse basée sur : 100+ fichiers de scripts ETL*

