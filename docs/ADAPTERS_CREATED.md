# Adapters créés

Ce document liste tous les adapters créés pour la nouvelle architecture.

## ✅ Adapters disponibles

### Sources Gitech
- ✅ `gitech_parifoot` - Exemple complet avec documentation
- ✅ `gitech_casino` - Généré automatiquement

### Sources Afitech
- ✅ `afitech_daily_betting` - Avec support des dates

### Sources Bwinner
- ✅ `bwinner_gambie` - Exemple simple

### Sources Lonasebet
- ✅ `lonasebet_casino` - Généré automatiquement
- ✅ `lonasebet_online` - Généré automatiquement

### Sources Honore Gaming
- ✅ `honore_gaming` - Généré automatiquement

### Sources PMU
- ✅ `pmu_ca` - Généré automatiquement (avec gestion des paramètres optionnels)

## 📊 Statistiques

- **Total d'adapters créés** : 9
- **Adapters avec support dates** : 1 (afitech_daily_betting)
- **Adapters simples** : 8

## 🔧 Utilisation

Pour utiliser un adapter, il suffit de définir la variable d'environnement `ETL_SOURCE_NAME` :

```bash
export ETL_SOURCE_NAME=gitech_parifoot
python scripts/run_job.py
```

## ➕ Créer un nouvel adapter

Pour créer un adapter pour une nouvelle source :

```bash
python scripts/generate_adapter_simple.py <source_name>
```

Exemple :
```bash
python scripts/generate_adapter_simple.py sunubet_casino
```

## 📝 Notes

- Les adapters sont auto-détectés lors de l'exécution
- Chaque adapter enregistre automatiquement ses fonctions dans la factory
- Les adapters wrappent les fonctions existantes, aucune modification nécessaire dans les scripts originaux

