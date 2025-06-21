import pandas as pd
from pathlib import Path # Pour le type hint

from base.loader import Loader, LoaderConfigurationError, DataLoaderError
# load_env() et numpy ne sont plus nécessaires ici.

JOB_NAME = "gitech_casino"

class GitechCasinoLoader(Loader): # Renommé pour convention
    """
    Chargeur pour les données transformées de Gitech Casino.
    """
    def __init__(self):
        job_name = JOB_NAME
        log_file_path = f"logs/load_{JOB_NAME}.log"

        # Colonnes attendues par la base de données (self.target_columns)
        db_target_columns = [
            "idjeu", "nomjeu", "datevente", "vente", "paiement", "pourcentagepaiement"
        ]

        # Noms des colonnes dans le fichier CSV transformé (sortie du GitechCasinoTransformer)
        # D'après GitechCasinoTransformer, les colonnes sont:
        # ['IdJeu','NomJeu', 'Date vente', 'Vente','Paiement','PourcentagePaiement'] (après suppression de 'No')
        self.csv_columns_from_transformer = [
            'IdJeu','NomJeu','Date vente','Vente','Paiement','PourcentagePaiement'
        ]

        # Mapping pour renommer les colonnes du CSV vers les colonnes de la BD
        self.csv_to_db_column_map = {
            'IdJeu': 'idjeu',
            'NomJeu': 'nomjeu',
            'Date vente': 'datevente', # L'ancien load avait "datevente", le transfo produit "Date vente"
                                       # Le target_columns original du load était "datevente"
                                       # Mais la table SQL est probablement "date_de_vente" ou "date_vente"
                                       # Pour l'instant, je mappe à "datevente" comme dans l'ancien script.
                                       # A VERIFIER: le nom réel de la colonne dans la table SQL.
                                       # Si c'est "date_de_vente", il faut changer db_target_columns et ce mapping.
            'Vente': 'vente',
            'Paiement': 'paiement',
            'PourcentagePaiement': 'pourcentagepaiement'
        }

        target_table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_CASINO_GITECH]"

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
            target_columns=db_target_columns
        )

        if "truncate_table_before_load" not in self.job_config:
            self.job_config["truncate_table_before_load"] = True # TRUNCATE par défaut pour ce loader

    def _read_and_convert_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier CSV transformé, le nettoie et le renomme pour le chargement.
        """
        self.logger.info(f"Lecture du fichier transformé: {file_path.name}")
        try:
            # GitechCasinoTransformer sauvegarde en CSV avec sep=';', toutes colonnes en str.
            dataframe_raw = pd.read_csv(file_path, sep=';', index_col=False, dtype=str, header=0)
            self.logger.info(f"Fichier {file_path.name} lu. {len(dataframe_raw)} lignes. Colonnes: {list(dataframe_raw.columns)}")

            # Vérifier que les colonnes attendues du CSV sont présentes (clés du map)
            missing_csv_cols = [col for col in self.csv_to_db_column_map.keys() if col not in dataframe_raw.columns]
            if missing_csv_cols:
                self.logger.error(f"Colonnes CSV attendues pour mapping manquantes dans {file_path.name}: {missing_csv_cols}. "
                                  f"Colonnes CSV lues: {list(dataframe_raw.columns)}")
                raise DataLoaderError(f"Colonnes CSV manquantes pour mapping: {missing_csv_cols}")

            # Renommer les colonnes
            df_renamed = dataframe_raw.rename(columns=self.csv_to_db_column_map)

            # Remplacer les chaînes vides par pd.NA pour que la classe Loader les gère comme NULL
            df_final = df_renamed.replace({'': pd.NA})

            self.logger.debug(f"Colonnes après renommage et nettoyage: {list(df_final.columns)}")
            return df_final

        except FileNotFoundError:
            self.logger.error(f"Fichier transformé non trouvé: {file_path}", exc_info=True)
            return None
        except pd.errors.EmptyDataError:
            self.logger.warning(f"Le fichier transformé {file_path.name} est vide.")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture/préparation du fichier {file_path.name}: {e}", exc_info=True)
            return None

def run_gitech_casino_loader():
    """Fonction principale pour lancer le chargement des données Gitech Casino."""
    loader_job = None
    try:
        loader_job = GitechCasinoLoader()
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
    run_gitech_casino_loader()