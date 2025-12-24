# Analyse Approfondie - Nouveau Scan de Refactoring

## 🔍 Analyse Complète - Nouvelles Opportunités Identifiées

Ce document présente les nouvelles opportunités de refactoring découvertes après un scan approfondi du code.

---

## 🔴 CRITIQUE - Patterns Répétitifs Majeurs

### 1. Pattern "Simple CSV Transformer" (15+ fichiers)

**Fichiers concernés :**
- `scripts/lonasebet_online/transform.py`
- `scripts/lonasebet_casino/transform.py`
- `scripts/sunubet_online/transform.py`
- `scripts/sunubet_casino/transform.py`
- `scripts/parifoot_online/transform.py`
- `scripts/pmu_ca/transform.py`
- `scripts/pmu_lots/transform.py`
- `scripts/minishop/transform.py`
- `scripts/acajou_digital/transform.py`
- `scripts/virtual_amabel/transform.py`
- `scripts/virtual_amabel_pivot/transform.py`
- Et d'autres...

**Pattern identique :**
```python
def _transform_file(self, file: Path, date=None):
    self.logger.info(f"Traitement du fichier : {file.name}")
    try:
        data = pd.read_csv(file, sep=';', index_col=False)
    except Exception as e:
        self.set_error(file.name)
        self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
        return
    
    date = self._get_file_date(file)
    # Ajout de colonnes de date (JOUR, ANNEE, MOIS) - optionnel
    data = data.replace(np.nan, '')
    data = data.astype(str)
    
    # Sauvegarde archive (chemins hardcodés)
    filesInitialDirectory = r"K:\..."
    data.to_csv(...)
    
    self._save_file(file, data, type="csv", ...)
```

**Solution :**
- Créer `base/simple_csv_transformer.py` avec `SimpleCSVTransformer(Transformer)`
- Paramètres configurables : colonnes de date, séparateur, encodage, colonnes à sélectionner
- Les transformers spécifiques héritent et ne surchargent que les parties différentes

**Impact :** Réduction de ~40 lignes × 15 = 600 lignes de code dupliqué

---

### 2. Pattern "Date Columns Transformer" (8+ fichiers)

**Fichiers concernés :**
- `scripts/lonasebet_online/transform.py`
- `scripts/lonasebet_casino/transform.py`
- `scripts/sunubet_online/transform.py`
- `scripts/sunubet_casino/transform.py`
- `scripts/virtual_amabel_pivot/transform.py`
- `scripts/pmu_ca/transform.py`
- `scripts/pmu_lots/transform.py`
- `scripts/editec_loto/transform.py`
- `scripts/editec_loto_lots/transform.py`

**Pattern identique :**
```python
date = self._get_file_date(file)
data["JOUR"] = str(date.strftime("%d/%m/%Y"))
data["ANNEE"] = str(date.strftime("%Y"))
data["MOIS"] = str(date.strftime("%m"))
```

**Solution :**
- Créer méthode utilitaire dans `base/transformer.py` : `_add_date_columns(data, date)`
- Utiliser les constantes de `utils/date_utils.py`

**Impact :** Réduction de ~5 lignes × 8 = 40 lignes de code dupliqué

---

### 3. Pattern "Orchestrator Factory" (43 occurrences)

**Fichiers concernés :** Tous les `scripts/*/orchestrator.py`

**Pattern identique :**
```python
from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_xxx as extract
from transform import run_xxx_transformer as transform
from load import run_xxx_loader as load

def run_xxx_orchestrator():
    orchestrator = Orchestrator(
        name="xxx",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_xxx_orchestrator()
```

**Solution :**
- Créer `base/orchestrator_factory.py` avec fonction `create_orchestrator(source_name)`
- Auto-détection des fonctions extract/transform/load depuis le module
- Simplifier à : `create_orchestrator("xxx").run()`

**Impact :** Réduction de ~15 lignes × 43 = 645 lignes de code répétitif

---

### 4. Pattern "Run Functions" (76 occurrences)

**Fichiers concernés :** Tous les `scripts/*/transform.py` et `scripts/*/load.py`

**Pattern identique :**
```python
def run_xxx_transformer():
    transformer = XxxTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_xxx_transformer()
```

**Solution :**
- Créer décorateur `@transformer_entry_point` dans `base/transformer.py`
- Créer décorateur `@loader_entry_point` dans `base/loader.py`
- Auto-génération des fonctions run_*

**Impact :** Réduction de ~5 lignes × 76 = 380 lignes de code répétitif

---

## 🟡 IMPORTANT - Duplications de Code

### 5. Imports inutiles massifs (55+ fichiers)

**Problème :**
- `import numpy as np` dans 55 fichiers, mais souvent non utilisé directement
- `import win32com.client` dans beaucoup de fichiers, jamais utilisé
- `import os, re, shutil` souvent importés mais non utilisés
- `from base.logger import Logger` importé mais jamais utilisé directement (déjà dans Transformer/Loader)

**Solution :**
- Script de nettoyage automatique avec `autoflake` ou `unimport`
- Vérification manuelle des imports restants

**Impact :** Code plus propre, imports plus rapides

---

### 6. Pattern `.replace(np.nan, '')` + `.astype(str)` (34 occurrences)

**Fichiers concernés :** Presque tous les transformers

**Pattern identique :**
```python
data = data.replace(np.nan, '')
data = data.astype(str)
```

**Solution :**
- Créer méthode dans `base/transformer.py` : `_clean_dataframe(data, to_string=True)`
- Ou utiliser directement `df.fillna('').astype(str)`

**Impact :** Réduction de ~2 lignes × 34 = 68 lignes de code répétitif

---

### 7. Pattern de formatage de date `strftime('%d/%m/%Y')` (75 occurrences)

**Fichiers concernés :** Presque tous les scripts

**Problème :** Format hardcodé partout au lieu d'utiliser les constantes

**Solution :**
- Utiliser `utils.date_utils.DATE_FORMAT_DISPLAY` partout
- Créer fonction helper `format_date_display(date)`

**Impact :** Cohérence et facilité de changement

---

### 8. Pattern de lecture CSV répétitif (65 occurrences)

**Patterns identiques :**
```python
# Pattern 1
data = pd.read_csv(file, sep=';', index_col=False)

# Pattern 2
data = pd.read_csv(file, sep=';', index_col=False, encoding='utf-8')

# Pattern 3
data = pd.read_csv(file, sep=';', index_col=False, dtype=str)
```

**Solution :**
- Créer `utils/pandas_utils.py` avec fonctions helpers :
  - `read_csv_safe(file, sep=';', encoding='utf-8', **kwargs)`
  - Gestion d'erreurs standardisée

**Impact :** Cohérence et meilleure gestion d'erreurs

---

## 🟢 AMÉLIORATIONS - Qualité de Code

### 9. Pattern "Gross Payout" dupliqué (4 fichiers)

**Fichiers concernés :**
- `scripts/acajou_digital/transform.py`
- `scripts/acajou_digital/load.py`
- `scripts/mojabet_ussd/transform.py`
- `scripts/mojabet_ussd/load.py`
- `scripts/mojabet_ussd_aggr/load.py`

**Pattern identique :**
```python
data['Gross Payout'] = data['Gross Payout'].astype(float).round(2).astype(str)
```

**Solution :**
- Créer fonction utilitaire `utils/data_cleaning_utils.py::format_gross_payout(series)`

**Impact :** Réduction de duplication

---

### 10. Pattern de sélection de colonnes répétitif

**Problème :** Beaucoup de `pd.DataFrame(data, columns=[...])` avec colonnes hardcodées

**Solution :**
- Déplacer les colonnes dans `config.yml`
- Créer méthode `_select_columns(data, columns_config)`

**Impact :** Configuration centralisée

---

### 11. Noms de fonctions run_* incohérents

**Problèmes identifiés :**
- `scripts/solidicon/transform.py` : `run_gitech_transformer()` (mauvais nom)
- `scripts/mojabet_ussd/transform.py` : `run_acajou_digital_transformer()` (mauvais nom)
- `scripts/pmu_senegal/orchestrator.py` : `run_pmu_ca_orchestrator()` (devrait être pmu_senegal)

**Solution :**
- Standardiser tous les noms de fonctions
- Script de vérification automatique

**Impact :** Cohérence et évite les bugs

---

### 12. Code commenté et TODOs non résolus

**TODOs trouvés :**
- `# todo: get date from file or current date` (plusieurs fichiers)
- `# Todo: A supprimer` dans `scripts/honore_gaming/extract.py`
- `# TODO : déplacer le fichier dans un dossier d'erreur` (plusieurs fichiers)

**Code commenté :**
- Beaucoup de lignes commentées avec `# filesInitialDirectory = ...`
- Code mort à supprimer

**Solution :**
- Créer tickets pour chaque TODO
- Supprimer le code commenté obsolète

---

## 📊 Statistiques du Nouveau Scan

### Patterns Répétitifs Identifiés

| Pattern | Occurrences | Lignes à réduire |
|---------|-------------|------------------|
| Simple CSV Transformer | 15+ | ~600 lignes |
| Orchestrator Factory | 43 | ~645 lignes |
| Run Functions | 76 | ~380 lignes |
| Date Columns | 8+ | ~40 lignes |
| Clean DataFrame | 34 | ~68 lignes |
| **TOTAL** | **176+** | **~1,733 lignes** |

### Imports à Nettoyer

- `numpy as np` : 55 fichiers (beaucoup non utilisés)
- `win32com.client` : ~20 fichiers (jamais utilisé)
- `os, re, shutil` : ~30 fichiers (souvent non utilisés)
- `Logger` direct : ~15 fichiers (déjà dans base classes)

---

## 🎯 Plan d'Action Recommandé

### Phase 1 - Quick Wins (1 jour)
1. ✅ Créer `base/simple_csv_transformer.py`
2. ✅ Créer méthode `_add_date_columns()` dans `base/transformer.py`
3. ✅ Créer méthode `_clean_dataframe()` dans `base/transformer.py`
4. ✅ Nettoyer les imports inutiles

### Phase 2 - Factory Patterns (2 jours)
5. ✅ Créer `base/orchestrator_factory.py`
6. ✅ Créer décorateurs `@transformer_entry_point` et `@loader_entry_point`
7. ✅ Refactorer les orchestrators pour utiliser la factory

### Phase 3 - Refactoring Simple Transformers (2 jours)
8. ✅ Refactorer les transformers simples (lonasebet, sunubet, parifoot, pmu, etc.)
9. ✅ Utiliser les constantes de date partout
10. ✅ Créer `utils/pandas_utils.py` pour les helpers pandas

### Phase 4 - Nettoyage Final (1 jour)
11. ✅ Corriger les noms de fonctions incohérents
12. ✅ Supprimer le code commenté
13. ✅ Résoudre/supprimer les TODOs

---

## 🔍 Fichiers Prioritaires pour Refactoring

### Transformers Simples (à refactorer en priorité)
1. `scripts/lonasebet_online/transform.py` - Pattern simple CSV
2. `scripts/lonasebet_casino/transform.py` - Pattern simple CSV
3. `scripts/sunubet_online/transform.py` - Pattern simple CSV + date columns
4. `scripts/sunubet_casino/transform.py` - Pattern simple CSV + date columns
5. `scripts/parifoot_online/transform.py` - Pattern simple CSV
6. `scripts/pmu_ca/transform.py` - Pattern simple CSV + date columns
7. `scripts/pmu_lots/transform.py` - Pattern simple CSV + date columns
8. `scripts/minishop/transform.py` - Pattern simple CSV
9. `scripts/acajou_digital/transform.py` - Pattern simple CSV + Gross Payout

### Orchestrators (à refactorer)
- Tous les 43 orchestrators peuvent utiliser la factory

---

## 📝 Notes Techniques

### SimpleCSVTransformer - Structure Proposée

```python
class SimpleCSVTransformer(Transformer):
    def __init__(self, name, log_file, 
                 csv_sep=';', csv_encoding='utf-8',
                 add_date_columns=False,
                 select_columns=None,
                 archive_path=None):
        super().__init__(name, log_file)
        self.csv_sep = csv_sep
        self.csv_encoding = csv_encoding
        self.add_date_columns = add_date_columns
        self.select_columns = select_columns
        self.archive_path = archive_path
    
    def _transform_file(self, file: Path, date=None):
        # Lecture CSV
        data = self._read_csv(file)
        
        # Ajout colonnes date si nécessaire
        if self.add_date_columns:
            date = date or self._get_file_date(file)
            data = self._add_date_columns(data, date)
        
        # Sélection colonnes si nécessaire
        if self.select_columns:
            data = data[self.select_columns]
        
        # Nettoyage
        data = self._clean_dataframe(data)
        
        # Archive si nécessaire
        if self.archive_path and date:
            self._save_to_archive(data, date)
        
        # Sauvegarde
        self._save_file(file, data, ...)
```

---

*Scan effectué le : 2025-01-XX*
*Nouvelles opportunités identifiées : 12 patterns majeurs*
*Lignes de code à réduire : ~1,733 lignes*

