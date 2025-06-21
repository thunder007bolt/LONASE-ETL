import pandas as pd
from pathlib import Path # Pour le type hint

from base.loader import Loader, LoaderConfigurationError, DataLoaderError
# load_env() et numpy ne sont plus nécessaires ici.

JOB_NAME = "bwinner"

class BwinnerLoader(Loader): # Renommé pour convention
    """
    Chargeur pour les données transformées de Bwinner.
    """
    def __init__(self):
        job_name = JOB_NAME
        log_file_path = f"logs/load_{JOB_NAME}.log"

        # Les noms de colonnes ici doivent correspondre EXACTEMENT (casse incluse)
        # aux noms de colonnes dans les fichiers CSV produits par BwinnerTransformer.
        # D'après BwinnerTransformer, les colonnes finales sont:
        # ['Report Date', 'Name', 'Total Stakes', 'Total Paid Win']
        # Il y a une différence avec les colonnes listées dans l'ancien script de load :
        # ["create_time", "product", "stake", "max payout"]
        # Il est CRUCIAL de clarifier quelles sont les bonnes colonnes.
        # Pour l'instant, je vais utiliser celles de l'ancien script de load,
        # mais cela DOIT être vérifié et aligné avec la sortie réelle du transformateur.
        # **Hypothèse pour cette refactorisation : les colonnes de l'ancien load script sont celles attendues pour la BD.**
        # Cela implique que BwinnerTransformer devrait produire ces colonnes.
        # Si BwinnerTransformer produit ['Report Date', 'Name', ...], alors target_columns ici doit changer.

        target_columns = [
            "create_time", # Correspond à 'Report Date' du transformateur?
            "product",     # Correspond à 'Name' du transformateur?
            "stake",       # Correspond à 'Total Stakes'?
            "max_payout"   # Correspond à 'Total Paid Win'? (espace remplacé par _)
        ]
        # Le nom de la table cible
        target_table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_BWINNERS]"

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
            target_columns=target_columns # Utiliser les colonnes définies ci-dessus
        )

        # Comportement de suppression/troncation avant chargement.
        # L'ancien script ne spécifiait pas de suppression.
        # Si un TRUNCATE est souhaité :
        self.job_config["truncate_table_before_load"] = True
        # Si un DELETE spécifique est nécessaire, surcharger _truncate_target_table().

    def _read_and_convert_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier CSV transformé (séparateur ';') et le charge dans un DataFrame.
        """
        self.logger.info(f"Lecture du fichier transformé: {file_path.name}")
        try:
            # Les fichiers transformés par BwinnerTransformer sont des CSV avec sep=';'.
            # Le transformer convertit toutes les colonnes en str par défaut à la sauvegarde CSV.
            dataframe = pd.read_csv(file_path, sep=';', index_col=False, dtype=str)
            self.logger.info(f"Fichier {file_path.name} lu. {len(dataframe)} lignes trouvées.")

            # **Alignement des Noms de Colonnes du DataFrame avec target_columns**
            # Le DataFrame lu aura les colonnes telles que sauvegardées par le Transformer,
            # qui sont (selon la refactorisation de BwinnerTransformer):
            # ['Report Date', 'Name', 'Total Stakes', 'Total Paid Win']
            # Ces noms doivent être mappés à self.target_columns si différents.

            column_rename_map = {
                'Report Date': 'create_time',
                'Name': 'product',
                'Total Stakes': 'stake',
                'Total Paid Win': 'max_payout' # S'assurer que 'max payout' devient 'max_payout'
            }

            # Renommer seulement les colonnes qui existent pour éviter les erreurs
            # et vérifier si toutes les colonnes attendues sont présentes après renommage.
            rename_map_for_existing_cols = {k: v for k, v in column_rename_map.items() if k in dataframe.columns}
            if len(rename_map_for_existing_cols) < len(column_rename_map):
                self.logger.warning(f"Certaines colonnes à renommer n'ont pas été trouvées dans {file_path.name}. "
                                    f"Mapping: {rename_map_for_existing_cols}, Attendu: {column_rename_map.keys()}")

            dataframe = dataframe.rename(columns=rename_map_for_existing_cols)

            # Vérifier si toutes les target_columns sont maintenant présentes
            missing_target_cols = [col for col in self.target_columns if col not in dataframe.columns]
            if missing_target_cols:
                self.logger.error(f"Après renommage, colonnes cibles manquantes dans DataFrame de {file_path.name}: {missing_target_cols}")
                raise DataLoaderError(f"Colonnes cibles manquantes après renommage: {missing_target_cols}")

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

def run_bwinner_loader():
    """Fonction principale pour lancer le chargement des données Bwinner."""
    loader_job = None
    try:
        loader_job = BwinnerLoader()
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
    run_bwinner_loader()