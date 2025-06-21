import pandas as pd
from pathlib import Path # Pour le type hint

from base.loader import Loader, LoaderConfigurationError, DataLoaderError
# load_env() et numpy ne sont plus nécessaires ici.

JOB_NAME = "afitech_daily_payment_activity"

class AfitechDailyPaymentActivityLoader(Loader): # Renommé pour convention
    """
    Chargeur pour les données transformées "Daily Payment Activity" d'Afitech.
    """
    def __init__(self):
        job_name = JOB_NAME
        log_file_path = f"logs/load_{JOB_NAME}.log"

        target_columns = [
            "jour", "partner", "payment_provider", "total_amount_of_deposit",
            "total_number_of_deposit", "total_amount_of_withdrawals",
            "total_number_of_withdrawals", "total_commissions",
            "t_amount_of_partner_deposits", "t_am_of_partner_withdrawals"
        ]
        target_table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_AFITECH_DAILYPAYMENT]"

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
            target_columns=target_columns
        )

        # Par défaut, la classe Loader de base ne tronque pas la table.
        # Si un TRUNCATE est souhaité avant chaque chargement pour ce job :
        self.job_config["truncate_table_before_load"] = True
        # Si une logique de DELETE plus spécifique est nécessaire, surcharger _truncate_target_table().
        # L'ancien script n'avait pas de logique de suppression spécifique pour ce loader,
        # donc un TRUNCATE via la config est un bon point de départ si c'est le comportement désiré.

    def _read_and_convert_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier CSV transformé (séparateur ';') et le charge dans un DataFrame.
        """
        self.logger.info(f"Lecture du fichier transformé: {file_path.name}")
        try:
            # Les fichiers transformés par AfitechDailyPaymentActivityTransformer sont des CSV
            # avec sep=';' et toutes les colonnes en str.
            dataframe = pd.read_csv(file_path, sep=';', index_col=False, dtype=str)
            self.logger.info(f"Fichier {file_path.name} lu. {len(dataframe)} lignes trouvées.")
            return dataframe
        except FileNotFoundError:
            self.logger.error(f"Fichier transformé non trouvé: {file_path}", exc_info=True)
            return None
        except pd.errors.EmptyDataError:
            self.logger.warning(f"Le fichier transformé {file_path.name} est vide.")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture du fichier {file_path.name}: {e}", exc_info=True)
            return None

def run_afitech_daily_payment_activity_loader():
    """Fonction principale pour lancer le chargement des données."""
    loader_job = None
    try:
        loader_job = AfitechDailyPaymentActivityLoader()
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
    run_afitech_daily_payment_activity_loader()