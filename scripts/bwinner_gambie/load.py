import pandas as pd
from pathlib import Path # Pour le type hint

from base.loader import Loader, LoaderConfigurationError, DataLoaderError
# load_env() et numpy ne sont plus nécessaires ici.

JOB_NAME = "bwinner_gambie"

class BwinnerGambieLoader(Loader): # Renommé pour convention
    """
    Chargeur pour les données transformées de Bwinner Gambie.
    """
    def __init__(self):
        job_name = JOB_NAME
        log_file_path = f"logs/load_{JOB_NAME}.log"

        # Colonnes attendues par la base de données (self.target_columns dans la classe de base)
        db_target_columns = [
            "no", "agences", "operateurs", "date_de_vente", "recette", "annulation",
            "ventes_resultant", "comm_vente", "paiements", "resultats"
        ]

        # Noms des colonnes dans le fichier CSV transformé (sortie du BwinnerGambieTransformer)
        # D'après la refactorisation de BwinnerGambieTransformer, les noms de colonnes sont:
        # ['No','Agences','Operateurs','date de vente','Recette','Annulation',
        #  'Ventes Resultant','comm vente','Paiements','Resultats']
        # Il y a une différence de casse pour 'No' et d'autres.
        self.csv_columns_from_transformer = [
            'No','Agences','Operateurs','date de vente','Recette','Annulation',
            'Ventes Resultant','comm vente','Paiements','Resultats'
        ]

        # Mapping pour renommer les colonnes du CSV vers les colonnes de la BD
        self.csv_to_db_column_map = dict(zip(self.csv_columns_from_transformer, db_target_columns))

        target_table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_BWINNERS_GAMBIE]"

        db_env_mapping = {
            'SQL_SERVER_HOST': 'SQL_SERVER_HOST',
            'SQL_SERVER_TEMPDB_NAME': 'SQL_SERVER_TEMPDB_NAME',
            'SQL_SERVER_TEMPDB_USERNAME': 'SQL_SERVER_TEMPDB_USERNAME',
            'SQL_SERVER_TEMPDB_PASSWORD': 'SQL_SERVER_TEMPDB_PASSWORD'
        }

        super().__init__(
            job_name=job_name,
            log_file_path=log_file_path,
            db_env_vars_mapping=db_env_mapping,
            target_table_name=target_table_name,
            target_columns=db_target_columns # Les colonnes attendues par la BD
        )

        # Comportement de suppression/troncation avant chargement.
        # L'ancien script ne spécifiait pas de suppression.
        # Si un TRUNCATE est souhaité :
        if "truncate_table_before_load" not in self.job_config: # Evite d'écraser si déjà dans config.yml
            self.job_config["truncate_table_before_load"] = True

    def _read_and_convert_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier CSV transformé et le charge dans un DataFrame.
        Renomme les colonnes pour correspondre à celles attendues par la base de données.
        """
        self.logger.info(f"Lecture du fichier transformé: {file_path.name}")
        try:
            # Les fichiers transformés par BwinnerGambieTransformer sont des CSV avec sep=';'.
            # Toutes les colonnes ont été converties en str par le transformer.
            # On lit la première ligne comme header pour obtenir les noms de colonnes du CSV.
            dataframe = pd.read_csv(file_path, sep=';', index_col=False, dtype=str, header=0)
            self.logger.info(f"Fichier {file_path.name} lu. {len(dataframe)} lignes trouvées. Colonnes lues: {list(dataframe.columns)}")

            # Vérifier si les colonnes lues correspondent à self.csv_columns_from_transformer
            # Ceci est plus une vérification de cohérence qu'une nécessité si le Transformer est fiable.
            if list(dataframe.columns) != self.csv_columns_from_transformer:
                self.logger.warning(f"Les en-têtes du CSV {file_path.name} ne correspondent pas exactement à ceux attendus "
                                    f"par 'csv_columns_from_transformer'. Actuel: {list(dataframe.columns)}, "
                                    f"Attendu: {self.csv_columns_from_transformer}. "
                                    "Tentative de renommage basée sur le mapping fourni.")
                # On pourrait ajouter une logique pour tenter un mapping plus flexible si nécessaire.

            # Renommer les colonnes pour correspondre à self.target_columns (db_target_columns)
            # en utilisant self.csv_to_db_column_map.
            # Il faut s'assurer que les clés de csv_to_db_column_map sont bien les colonnes lues du CSV.
            current_df_columns = list(dataframe.columns)
            rename_map_for_current_df = {
                csv_col: db_col
                for csv_col, db_col in self.csv_to_db_column_map.items()
                if csv_col in current_df_columns
            }

            if len(rename_map_for_current_df) != len(self.csv_to_db_column_map):
                 self.logger.warning(f"Certaines colonnes définies dans 'csv_columns_from_transformer' "
                                     f"n'ont pas été trouvées dans le fichier CSV {file_path.name} pour le renommage. "
                                     f"Colonnes CSV lues: {current_df_columns}")


            dataframe = dataframe.rename(columns=rename_map_for_current_df)
            self.logger.debug(f"Colonnes après tentative de renommage pour la BD: {list(dataframe.columns)}")

            # Vérifier si toutes les target_columns (pour la BD) sont maintenant présentes
            missing_db_cols = [col for col in self.target_columns if col not in dataframe.columns]
            if missing_db_cols:
                self.logger.error(f"Après renommage, colonnes BD manquantes dans DataFrame de {file_path.name}: {missing_db_cols}. "
                                  f"Colonnes DataFrame actuelles: {list(dataframe.columns)}")
                raise DataLoaderError(f"Colonnes BD manquantes après renommage: {missing_db_cols}")

            return dataframe

        except FileNotFoundError:
            self.logger.error(f"Fichier transformé non trouvé: {file_path}", exc_info=True)
            return None
        except pd.errors.EmptyDataError:
            self.logger.warning(f"Le fichier transformé {file_path.name} est vide.")
            return pd.DataFrame() # Retourner un DataFrame vide
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture ou du renommage des colonnes du fichier {file_path.name}: {e}", exc_info=True)
            return None

def run_bwinner_gambie_loader():
    """Fonction principale pour lancer le chargement des données Bwinner Gambie."""
    loader_job = None
    try:
        loader_job = BwinnerGambieLoader()
        loader_job.process_loading_from_files()
    except (LoaderConfigurationError, ConnectionError, DataLoaderError) as e:
        log_msg = f"Échec critique du job de chargement {JOB_NAME}: {e}"
        if loader_job and loader_job.logger: loader_job.logger.critical(log_msg, exc_info=True)
        else: print(f"ERREUR CRITIQUE (logger non dispo) pour {JOB_NAME}: {log_msg}")
    except Exception as e:
        log_msg = f"Erreur inattendue et non gérée dans l'exécution du chargeur {JOB_NAME}: {e}"
        if loader_job and loader_job.logger: loader_job.logger.critical(log_msg, exc_info=True)
        else: print(log_msg)
    finally:
        if loader_job and loader_job.logger:
             loader_job.logger.info(f"Fin du script de chargement pour {JOB_NAME}.")

if __name__ == "__main__":
    # from load_env import load_env
    # load_env()
    run_bwinner_gambie_loader()