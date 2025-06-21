import pandas as pd
# numpy n'est plus explicitement utilisé ici, pd.NA ou None sont préférés pour les valeurs manquantes.
from pathlib import Path # Pour le type hint de file_path

from base.loader import Loader, LoaderConfigurationError, DataLoaderError # Importer les exceptions
# load_env() est maintenant appelé dans config_utils.py, pas besoin de l'appeler ici.
# from utils.other_utils import load_env

JOB_NAME = "acajou_digital" # Constante pour le nom du job

class AcajouDigitalLoader(Loader): # Renommé pour suivre la convention Transformer
    """
    Chargeur pour les données transformées d'Acajou Digital dans la base de données.
    Hérite de la classe Loader de base.
    """
    def __init__(self):
        # Nom du job
        job_name = JOB_NAME

        # Chemin du fichier de log spécifique à ce chargeur
        log_file_path = f"logs/load_{JOB_NAME}.log" # Convention de nommage

        # Colonnes cibles dans la base de données (doivent correspondre à celles du fichier transformé)
        # L'ordre est important.
        target_columns = [
            "date_heure", "reference_ticket", "telephone", "purchase_method",
            "montant", "lots_a_payes", "status", "produit"
        ]

        # Nom complet de la table de destination
        target_table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_ACACIA]" # Attention aux noms de table codés en dur.
                                                                        # Pourrait être mis dans config.yml si changeant.

        # Mapping des variables d'environnement pour la connexion à la BD
        # Ces clés (ex: 'SQL_SERVER_HOST') sont celles attendues par get_loading_configurations
        # qui les utilise pour appeler get_secret.
        db_env_mapping = {
            'SQL_SERVER_HOST': 'SQL_SERVER_HOST', # Nom de la clé dans secret_config : Nom de la variable d'env
            'SQL_SERVER_TEMPDB_NAME': 'SQL_SERVER_TEMPDB_NAME',
            'SQL_SERVER_TEMPDB_USERNAME': 'SQL_SERVER_TEMPDB_USERNAME',
            'SQL_SERVER_TEMPDB_PASSWORD': 'SQL_SERVER_TEMPDB_PASSWORD'
        }

        super().__init__(
            job_name=job_name,
            log_file_path=log_file_path,
            db_env_vars_mapping=db_env_mapping,
            target_table_name=target_table_name,
            target_columns=target_columns
        )

        # Personnalisation du comportement de TRUNCATE pour ce loader spécifique.
        # Si True, la méthode _truncate_target_table de la classe Loader sera appelée.
        # Si False (ou non défini), elle ne le sera pas.
        # Ici, on surcharge _truncate_target_table pour une logique de DELETE spécifique.
        # La config "truncate_table_before_load" de la classe de base ne sera pas utilisée
        # si on surcharge la méthode.
        # self.job_config["truncate_table_before_load"] = False # Exemple pour désactiver le TRUNCATE de base

    def _truncate_target_table(self): # Surcharge de la méthode de la classe Loader
        """
        Supprime les données spécifiques d'Acajou Digital de la table cible
        avant de charger de nouvelles données.
        Ici, on ne supprime que les données qui ne sont PAS 'Pick3' ou 'Grattage'.
        """
        if not self.db_cursor or not self.db_connection:
            self.logger.error("Connexion BD non disponible pour la suppression des données.")
            raise ConnectionError("Connexion BD non disponible pour la suppression de données.")

        delete_query = f"""
            DELETE FROM {self.target_table_name}
            WHERE produit NOT IN ('Pick3', 'Grattage')
                  AND produit = 'Pari Sportif' -- Condition ajoutée pour cibler uniquement ce type de produit
        """
        # La condition `produit = 'Pari Sportif'` est ajoutée car ce loader
        # ne charge que des données avec `Produit = "Pari Sportif"`.
        # Cela évite de supprimer d'autres produits Acajou qui pourraient être dans la même table
        # mais gérés par un autre loader.
        # Si le but est de remplacer TOUTES les données "Pari Sportif" chaque jour,
        # alors `DELETE FROM ... WHERE produit = 'Pari Sportif'` serait plus direct.
        # La logique originale `WHERE produit NOT IN ('Pick3', 'Grattage')` est conservée
        # mais affinée avec `AND produit = 'Pari Sportif'`.

        self.logger.info(f"Suppression des données existantes de '{self.name}' (Pari Sportif) de la table {self.target_table_name}...")
        try:
            self.db_cursor.execute(delete_query)
            self.db_connection.commit()
            self.logger.info(f"{self.db_cursor.rowcount} lignes supprimées de la table {self.target_table_name} pour le produit 'Pari Sportif'.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression des données de {self.target_table_name}: {e}", exc_info=True)
            raise DataLoaderError(f"Échec de la suppression des données de {self.target_table_name}.") from e


    def _read_and_convert_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier CSV transformé et le charge dans un DataFrame pandas.
        Les fichiers transformés par AcajouDigitalTransformer utilisent ';' comme séparateur.
        """
        self.logger.info(f"Lecture du fichier transformé: {file_path.name}")
        try:
            # S'assurer que les options de lecture correspondent à la sortie du Transformer
            # Le Transformer sauvegardait avec sep=';', index=False, encoding='utf8'
            dataframe = pd.read_csv(file_path, sep=';', index_col=False, dtype=str)
            # dtype=str pour lire toutes les colonnes comme des chaînes initialement,
            # car le Transformer convertissait tout en str.
            # Cela évite les erreurs de parsing de types si des valeurs '' existent.
            self.logger.info(f"Fichier {file_path.name} lu. {len(dataframe)} lignes trouvées.")
            return dataframe
        except FileNotFoundError:
            self.logger.error(f"Fichier transformé non trouvé: {file_path}", exc_info=True)
            return None
        except pd.errors.EmptyDataError:
            self.logger.warning(f"Le fichier transformé {file_path.name} est vide.")
            return pd.DataFrame() # Retourner un DataFrame vide
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture du fichier {file_path.name}: {e}", exc_info=True)
            return None

    # La méthode _prepare_dataframe_for_loading de la classe Loader de base devrait convenir ici,
    # car elle gère déjà la réorganisation des colonnes et la conversion en tuples.
    # Si des préparations spécifiques sont nécessaires (ex: conversion de types avant tuple),
    # cette méthode peut être surchargée.
    # def _prepare_dataframe_for_loading(self, df: pd.DataFrame) -> list[tuple]:
    #     # ... logique spécifique ...
    #     return super()._prepare_dataframe_for_loading(df)


def run_acajou_digital_loader():
    """Fonction principale pour lancer le chargement des données Acajou Digital."""
    loader_job = None
    try:
        loader_job = AcajouDigitalLoader()
        # La méthode principale de la classe Loader de base
        loader_job.process_loading_from_files()
    except (LoaderConfigurationError, ConnectionError, DataLoaderError) as e:
        log_msg = f"Échec critique du job de chargement {JOB_NAME}: {e}"
        if loader_job and loader_job.logger:
            loader_job.logger.critical(log_msg, exc_info=True)
        else:
            print(f"ERREUR CRITIQUE (logger non dispo) pour {JOB_NAME}: {log_msg}") # Fallback
    except Exception as e:
        log_msg = f"Erreur inattendue et non gérée dans l'exécution du chargeur {JOB_NAME}: {e}"
        if loader_job and loader_job.logger:
            loader_job.logger.critical(log_msg, exc_info=True)
        else:
            print(log_msg)
    finally:
        # La fermeture de la connexion est gérée dans le `finally` de process_loading_from_files
        # et aussi dans le __del__ de la classe Loader.
        if loader_job and loader_job.logger:
             loader_job.logger.info(f"Fin du script de chargement pour {JOB_NAME}.")
        # else:
        #     print(f"Fin du script de chargement pour {JOB_NAME} (logger non disponible).")


if __name__ == "__main__":
    # Assurez-vous que load_env.py a été appelé si les variables d'env sont dans un .env
    # from load_env import load_env
    # load_env() # Normalement fait une seule fois au début de l'application ou dans config_utils
    run_acajou_digital_loader()