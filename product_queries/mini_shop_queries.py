# Ce fichier est un placeholder.
# La logique d'insertion et les requêtes pour MiniShop
# se trouvent dans un script externe appelé via exec():
# C:\Batchs\scripts_python\extractions\journalier\insertMiniShopOracle_bis.py

QUERIES = {
    "external_script_path": "C:\\Batchs\\scripts_python\\extractions\\journalier\\insertMiniShopOracle_bis.py",
    # Les requêtes spécifiques ne sont pas extraites ici car elles sont dans le script ci-dessus.
}

def get_queries():
    return QUERIES

def get_external_script_path():
    return QUERIES.get("external_script_path")
