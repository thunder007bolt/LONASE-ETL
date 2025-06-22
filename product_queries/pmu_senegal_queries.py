# Ce fichier est un placeholder.
# La logique d'insertion et les requêtes pour PmuSenegal
# se trouvent dans un script externe appelé via exec():
# C:\Batchs\scripts_python\extractions\journalier\insertPmuSenegal.py

QUERIES = {
    "external_script_path": "C:\\Batchs\\scripts_python\\extractions\\journalier\\insertPmuSenegal.py",
    # Les requêtes spécifiques ne sont pas extraites ici car elles sont dans le script ci-dessus.
    # Si des opérations post-exec étaient nécessaires (ex: aggrégations spécifiques non faites par le script externe),
    # elles pourraient être ajoutées ici.
    # Exemple:
    # 'update_aggregates': """ MERGE ... """
}

def get_queries():
    return QUERIES

def get_external_script_path():
    return QUERIES.get("external_script_path")
