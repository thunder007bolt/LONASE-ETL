from pathlib import Path
import numpy as np # Gardé pour np.nan, bien que pd.NA soit une alternative moderne.
import pandas as pd
# datetime n'est plus explicitement utilisé ici.
# Les imports os, re, shutil, win32com.client, base.logger, utils.config_utils, utils.file_manipulation
# ne sont plus nécessaires directement si la classe de base gère la config et le déplacement.

from base.tranformer import Transformer, TransformationError # Importer l'exception personnalisée

JOB_NAME = "afitech_commission_history"

class AfitechCommissionHistoryTransformer(Transformer):
    """
    Transformateur pour les fichiers "Commission History" d'Afitech.
    Les fichiers sources sont des Excel (.xls ou .xlsx), la sortie est CSV.
    """
    def __init__(self):
        super().__init__(job_name=JOB_NAME, log_file_path=f"logs/transform_{JOB_NAME}.log")

    def _read_source_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier source Excel (feuille 'Data') et le charge dans un DataFrame pandas.
        """
        self.logger.info(f"Lecture du fichier source Excel: {file_path.name}")
        try:
            # Les fichiers peuvent être .xls ou .xlsx. Pandas devrait gérer cela avec l'engine approprié.
            # Si des erreurs surviennent à cause du format .xls plus ancien,
            # l'installation de `xlrd` pourrait être nécessaire (pandas >= 1.2.0 utilise openpyxl par défaut).
            dataframe = pd.read_excel(file_path, sheet_name='Data', engine=None) # engine=None laisse pandas choisir
            self.logger.info(f"Fichier {file_path.name} lu avec succès. {len(dataframe)} lignes trouvées.")
            return dataframe
        except FileNotFoundError:
            self.logger.error(f"Fichier source Excel non trouvé: {file_path}", exc_info=True)
            return None
        except pd.errors.EmptyDataError: # Moins probable pour Excel, mais par sécurité
            self.logger.warning(f"Le fichier source Excel {file_path.name} (feuille 'Data') est vide.")
            return pd.DataFrame()
        except ValueError as ve: # Peut arriver si sheet_name='Data' n'existe pas
            if "Worksheet named 'Data' not found" in str(ve):
                 self.logger.error(f"La feuille 'Data' n'a pas été trouvée dans le fichier Excel {file_path.name}.", exc_info=True)
            else:
                self.logger.error(f"Erreur de valeur lors de la lecture du fichier Excel {file_path.name}: {ve}", exc_info=True)
            return None
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture du fichier Excel {file_path.name}: {e}", exc_info=True)
            return None

    def _apply_transformation(self, source_file_path: Path, source_dataframe: pd.DataFrame) -> pd.DataFrame | None:
        """
        Applique les transformations spécifiques aux données "Commission History" d'Afitech.
        """
        self.logger.info(f"Application des transformations sur les données de {source_file_path.name}...")
        df_transformed = source_dataframe.copy()

        try:
            # 1. Renommer les colonnes (si nécessaire, ou s'assurer qu'elles sont correctes)
            expected_columns = [
                'Debut de la periode', 'Fin de la periode', 'Partner',
                'Payement Provider', 'Total Commisson', 'Deposit Total Amount',
                'Deposit Count', 'Withdrawal Total Amount', 'Withdrawal Count'
            ]
            if len(df_transformed.columns) == len(expected_columns):
                df_transformed.columns = expected_columns
                self.logger.debug("Colonnes renommées selon la liste attendue.")
            else:
                self.logger.error(f"Nombre de colonnes inattendu dans {source_file_path.name}. "
                                  f"Attendu: {len(expected_columns)}, Obtenu: {len(df_transformed.columns)}. "
                                  f"Colonnes actuelles: {list(df_transformed.columns)}")
                raise TransformationError(f"Nombre de colonnes incorrect pour {source_file_path.name}.")

            # 2. Remplacer np.nan par une chaîne vide
            df_transformed = df_transformed.replace({np.nan: ''})
            self.logger.debug("NaN remplacés par des chaînes vides.")

            # 3. Remplacer '.' par ',' pour les formats numériques (séparateur décimal)
            df_transformed = df_transformed.applymap(lambda x: str(x).replace('.', ','))
            self.logger.debug("Caractères '.' remplacés par ',' dans toutes les cellules (après conversion en str).")

            # 4. Correction spécifique pour la colonne 'Partner'
            if 'Partner' in df_transformed.columns:
                df_transformed['Partner'] = df_transformed['Partner'].str.replace(',', '.', regex=False)
                self.logger.debug("Caractères ',' remplacés par '.' dans la colonne 'Partner'.")

            # 5. Reformater les dates (remplacer '-' par '/')
            if 'Debut de la periode' in df_transformed.columns:
                df_transformed['Debut de la periode'] = df_transformed['Debut de la periode'].str.replace('-', '/', regex=False)
            if 'Fin de la periode' in df_transformed.columns:
                df_transformed['Fin de la periode'] = df_transformed['Fin de la periode'].str.replace('-', '/', regex=False)
            self.logger.debug("Caractères '-' remplacés par '/' dans les colonnes de dates.")

            # 6. Conversion finale de toutes les colonnes en type 'str'
            df_transformed = df_transformed.astype(str)
            self.logger.debug("Toutes les colonnes converties en type str pour la sortie.")

            self.logger.info(f"Transformations appliquées avec succès pour {source_file_path.name}.")
            return df_transformed

        except TransformationError:
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue durant l'application des transformations sur {source_file_path.name}: {e}", exc_info=True)
            return None


def run_afitech_commission_history_transformer():
    """Fonction principale pour lancer le transformateur Afitech Commission History."""
    transformer_job = None
    try:
        transformer_job = AfitechCommissionHistoryTransformer()
        transformer_job.process_files_transformation()
    except TransformerConfigurationError as e:
        print(f"ERREUR CRITIQUE de configuration du Transformer {JOB_NAME}: {e}")
        if transformer_job and transformer_job.logger:
             transformer_job.logger.critical(f"Erreur de configuration: {e}", exc_info=True)
    except Exception as e:
        log_msg = f"Erreur inattendue et non gérée dans l'exécution du transformateur {JOB_NAME}: {e}"
        if transformer_job and transformer_job.logger:
            transformer_job.logger.critical(log_msg, exc_info=True)
        else:
            print(log_msg)


if __name__ == '__main__':
    # from load_env import load_env
    # load_env()
    run_afitech_commission_history_transformer()