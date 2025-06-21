from pathlib import Path
import numpy as np # Gardé pour np.nan
import pandas as pd
# Imports non utilisés (os, re, shutil, win32com.client, datetime, etc.) supprimés

from base.tranformer import Transformer, TransformationError # Importer l'exception

JOB_NAME = "afitech_daily_payment_activity"

class AfitechDailyPaymentActivityTransformer(Transformer):
    """
    Transformateur pour les fichiers "Daily Payment Activity" d'Afitech.
    Source: Excel (.xls*), Sortie: CSV.
    """
    def __init__(self):
        super().__init__(job_name=JOB_NAME, log_file_path=f"logs/transform_{JOB_NAME}.log")

    def _read_source_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """Lit un fichier source Excel (feuille 'Data') dans un DataFrame."""
        self.logger.info(f"Lecture du fichier Excel source: {file_path.name}")
        try:
            dataframe = pd.read_excel(file_path, sheet_name='Data', engine=None)
            self.logger.info(f"Fichier {file_path.name} lu. {len(dataframe)} lignes trouvées.")
            return dataframe
        except FileNotFoundError:
            self.logger.error(f"Fichier source Excel non trouvé: {file_path}", exc_info=True)
            return None
        except pd.errors.EmptyDataError:
            self.logger.warning(f"Le fichier Excel {file_path.name} (feuille 'Data') est vide.")
            return pd.DataFrame()
        except ValueError as ve:
            if "Worksheet named 'Data' not found" in str(ve):
                 self.logger.error(f"Feuille 'Data' non trouvée dans {file_path.name}.", exc_info=True)
            else:
                self.logger.error(f"Erreur de valeur lecture Excel {file_path.name}: {ve}", exc_info=True)
            return None
        except Exception as e:
            self.logger.error(f"Erreur lecture Excel {file_path.name}: {e}", exc_info=True)
            return None

    def _apply_transformation(self, source_file_path: Path, source_dataframe: pd.DataFrame) -> pd.DataFrame | None:
        """Applique les transformations spécifiques aux données "Daily Payment Activity"."""
        self.logger.info(f"Application des transformations sur les données de {source_file_path.name}...")
        df_transformed = source_dataframe.copy()

        try:
            # 1. Remplacement des NaN par des chaînes vides (fait tôt pour simplifier les manips de chaînes)
            df_transformed = df_transformed.replace({np.nan: ''})
            self.logger.debug("NaN remplacés par des chaînes vides.")

            # 2. Remplacer '.' par ',' globalement (pour formats numériques européens)
            # Convertit tout en str au passage si ce n'est pas déjà fait par le replace précédent.
            df_transformed = df_transformed.applymap(lambda x: str(x).replace('.', ','))
            self.logger.debug("Caractères '.' remplacés par ',' (après conversion en str).")

            # 3. Correction spécifique pour 'Partner' (remettre '.' comme décimal ou séparateur)
            # Cette logique est conservée de l'ancien script.
            if 'Partner' in df_transformed.columns:
                df_transformed['Partner'] = df_transformed['Partner'].astype(str).str.replace(',', '.', regex=False)
                self.logger.debug("Caractères ',' remplacés par '.' dans la colonne 'Partner'.")
            else:
                self.logger.warning("Colonne 'Partner' non trouvée pour la transformation spécifique.")


            # 4. Reformater la colonne 'Date' (remplacer '-' par '/')
            if 'Date' in df_transformed.columns:
                df_transformed['Date'] = df_transformed['Date'].astype(str).str.replace('-', '/', regex=False)
                self.logger.debug("Caractères '-' remplacés par '/' dans la colonne 'Date'.")
            else:
                self.logger.error(f"Colonne 'Date' manquante dans {source_file_path.name}, nécessaire pour le renommage.")
                # Lever une erreur si 'Date' est cruciale, par exemple pour le nom du fichier de sortie.
                # Pour l'instant, on logue une erreur et on continue, mais le nom de fichier de sortie
                # pourrait être affecté si _build_transformed_filename dépend de cette colonne.
                # La logique actuelle de _build_transformed_filename dans la classe de base
                # tente d'extraire une date du nom du fichier source, pas de son contenu.

            # 5. Ajout de colonnes avec des valeurs par défaut (0)
            df_transformed['t_amount_of_partner_deposits'] = '0' # Mettre comme chaîne car tout est converti en str à la fin
            df_transformed['t_am_of_partner_withdrawals'] = '0'  # Idem
            self.logger.debug("Colonnes 't_amount_of_partner_deposits' et 't_am_of_partner_withdrawals' ajoutées avec '0'.")

            # 6. Renommer les colonnes
            # Attention: df.rename() retourne un nouveau DataFrame si inplace=False (défaut).
            # Il faut réassigner: df_transformed = df_transformed.rename(...)
            rename_map = {
                "Date": "jour",
                "Partner": "partner",
                "Payment Provider": "payment_provider",
                "Total Amount of Deposit": "total_amount_of_deposit",
                "Total Number of Deposit": "total_number_of_deposit",
                "Total Amount of Withdrawals": "total_amount_of_withdrawals",
                "Total Number of Withdrawals": "total_number_of_withdrawals",
                "Total Commissions": "total_commissions"
                # Les nouvelles colonnes 't_amount_of_partner_deposits', 't_am_of_partner_withdrawals'
                # ne sont pas dans ce mapping, donc elles gardent leur nom.
            }
            # S'assurer que seules les colonnes existantes sont renommées pour éviter les KeyErrors
            actual_rename_map = {k: v for k, v in rename_map.items() if k in df_transformed.columns}
            df_transformed = df_transformed.rename(columns=actual_rename_map)
            self.logger.debug(f"Colonnes renommées: {actual_rename_map}")

            # 7. S'assurer que toutes les colonnes sont de type string pour la sortie CSV.
            # Cette étape était à la fin dans l'ancien script.
            df_transformed = df_transformed.astype(str)
            self.logger.debug("Toutes les colonnes converties en type str pour la sortie.")

            self.logger.info(f"Transformations appliquées avec succès pour {source_file_path.name}.")
            return df_transformed

        except Exception as e:
            self.logger.error(f"Erreur inattendue durant l'application des transformations sur {source_file_path.name}: {e}", exc_info=True)
            return None


def run_afitech_daily_payment_activity_transformer():
    """Fonction principale pour lancer le transformateur."""
    transformer_job = None
    try:
        transformer_job = AfitechDailyPaymentActivityTransformer()
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
    run_afitech_daily_payment_activity_transformer()