import pandas as pd
from pathlib import Path # Pour le type hint

from base.loader import Loader, LoaderConfigurationError, DataLoaderError
# load_env() et numpy ne sont plus nécessaires ici.

JOB_NAME = "gitech"

class GitechLoader(Loader): # Renommé pour convention
    """
    Chargeur pour les données transformées de Gitech (PMU Online).
    """
    def __init__(self):
        job_name = JOB_NAME
        log_file_path = f"logs/load_{JOB_NAME}.log"

        # Colonnes attendues par la base de données (self.target_columns dans la classe de base)
        # Ces noms doivent correspondre à ceux de la table SQL [DWHPR_TEMP].[OPTIWARETEMP].[GITECH]
        db_target_columns = [
            "Agences", "Operateurs", "date_de_vente",
            "Recette_CFA", "Annulation_CFA", "Paiements_CFA"
        ]

        # Noms des colonnes dans le fichier CSV transformé (sortie du GitechTransformer)
        # D'après la refactorisation de GitechTransformer, les colonnes sont:
        # ['Agences', 'Operateur', 'Date vente', 'Vente', 'Annulation', 'Remboursement', 'Paiement', 'Resultat']
        # Il y a un décalage entre ces colonnes et db_target_columns.
        # Il faut mapper:
        #   'Operateur' (CSV) -> 'Operateurs' (DB)
        #   'Date vente' (CSV) -> 'date_de_vente' (DB)
        #   'Vente' (CSV) -> 'Recette_CFA' (DB)
        #   'Annulation' (CSV) -> 'Annulation_CFA' (DB)
        #   'Paiement' (CSV) -> 'Paiements_CFA' (DB)
        # Les colonnes 'Remboursement' et 'Resultat' du CSV ne sont pas dans db_target_columns.

        self.csv_columns_from_transformer = [
            'Agences', 'Operateur', 'Date vente', 'Vente',
            'Annulation', 'Remboursement', 'Paiement', 'Resultat'
        ]

        self.csv_to_db_column_map = {
            'Agences': 'Agences',       # Identique
            'Operateur': 'Operateurs',  # Changement de nom
            'Date vente': 'date_de_vente', # Changement de nom et casse
            'Vente': 'Recette_CFA',     # Changement de nom
            'Annulation': 'Annulation_CFA',# Changement de nom
            'Paiement': 'Paiements_CFA'   # Changement de nom
            # 'Remboursement' et 'Resultat' du CSV sont ignorés pour le chargement en BD.
        }

        target_table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[GITECH]"

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
            target_columns=db_target_columns # Les colonnes attendues par la BD après mapping
        )

        # Comportement de suppression/troncation avant chargement.
        # L'ancien script ne spécifiait pas de suppression.
        # Si un TRUNCATE est souhaité :
        if "truncate_table_before_load" not in self.job_config:
            self.job_config["truncate_table_before_load"] = True

    def _read_and_convert_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier CSV transformé, sélectionne et renomme les colonnes nécessaires.
        """
        self.logger.info(f"Lecture du fichier transformé: {file_path.name}")
        try:
            # Le GitechTransformer sauvegarde en CSV avec sep=';' et toutes colonnes en str.
            dataframe_raw = pd.read_csv(file_path, sep=';', index_col=False, dtype=str)
            self.logger.info(f"Fichier {file_path.name} lu. {len(dataframe_raw)} lignes. Colonnes: {list(dataframe_raw.columns)}")

            # Vérifier que les colonnes attendues du CSV sont présentes
            missing_csv_cols = [col for col in self.csv_to_db_column_map.keys() if col not in dataframe_raw.columns]
            if missing_csv_cols:
                self.logger.error(f"Colonnes CSV attendues pour le mapping manquantes dans {file_path.name}: {missing_csv_cols}")
                raise DataLoaderError(f"Colonnes CSV manquantes pour mapping: {missing_csv_cols}")

            # Sélectionner uniquement les colonnes nécessaires du CSV (clés du map) et les renommer
            df_renamed = dataframe_raw[list(self.csv_to_db_column_map.keys())].rename(columns=self.csv_to_db_column_map)

            # Remplacer les chaînes vides par None (pour NULL en BD) car le Transformer a tout mis en str.
            # La classe Loader de base s'attend à des NaN pour les remplacer par None pour la BD.
            # Ici, on convertit les chaînes vides en np.nan pour que la classe de base fasse le travail.
            df_final = df_renamed.replace({'': pd.NA}) # pd.NA est plus moderne que np.nan pour cela

            self.logger.debug(f"Colonnes après sélection et renommage: {list(df_final.columns)}")
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

def run_gitech_loader():
    """Fonction principale pour lancer le chargement des données Gitech."""
    loader_job = None
    try:
        loader_job = GitechLoader()
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
    run_gitech_loader()