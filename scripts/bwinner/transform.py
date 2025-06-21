from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta # timedelta est utilisé

# win32com.client et sys ne sont plus nécessaires si on lit directement les Excel avec Pandas.
# os, base.logger, utils.config_utils, utils.date_utils.get_yesterday_date, utils.file_manipulation
# ne sont plus nécessaires directement.

from base.tranformer import Transformer, TransformationError # Importer l'exception

JOB_NAME = "bwinner"

# Définir delta ici s'il est constant pour la transformation de date.
DATE_TRANSFORMATION_DELTA = timedelta(days=1)

class BwinnerTransformer(Transformer):
    """
    Transformateur pour les fichiers "Total Tax Report" de Bwinner.
    Source: Excel (.xlsx), Sortie: CSV.
    Tente de lire directement les fichiers Excel avec Pandas, évitant win32com.
    """
    def __init__(self):
        super().__init__(job_name=JOB_NAME, log_file_path=f"logs/transform_{JOB_NAME}.log")
        # La configuration du type de fichier de sortie (CSV, séparateur ';', encodage 'utf8')
        # sera gérée par les paramètres par défaut de _save_transformed_dataframe ou par la config du job.
        # self.job_config["output_file_type"] = "csv" # Par défaut dans la classe de base Transformer
        # self.job_config["csv_separator"] = ";" # Peut être configuré dans config.yml ou ici
        # self.job_config["output_file_encoding"] = "utf8" # Par défaut dans la classe de base

    def _read_source_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier source Excel (.xlsx) directement avec Pandas.
        """
        self.logger.info(f"Lecture du fichier Excel source (via Pandas): {file_path.name}")

        if file_path.suffix.lower() not in [".xlsx", ".xls"]:
            self.logger.error(f"Type de fichier non géré pour lecture directe: {file_path.name}. Attendu .xlsx ou .xls.")
            # Lever une erreur pour que la classe de base déplace le fichier vers error/
            raise TransformationError(f"Type de fichier non géré: {file_path.suffix}")

        try:
            # Pandas utilise openpyxl pour .xlsx par défaut. Peut nécessiter l'installation de openpyxl.
            # Pour .xls, il pourrait utiliser xlrd (peut nécessiter `pip install xlrd`).
            dataframe = pd.read_excel(file_path, engine=None) # engine=None laisse Pandas choisir
            self.logger.info(f"Fichier {file_path.name} lu avec succès via Pandas. {len(dataframe)} lignes trouvées.")
            return dataframe
        except FileNotFoundError:
            self.logger.error(f"Fichier source Excel non trouvé: {file_path}", exc_info=True)
            return None # La classe de base gérera le déplacement vers error/
        except pd.errors.EmptyDataError:
            self.logger.warning(f"Le fichier Excel {file_path.name} est vide (ou la première feuille l'est).")
            return pd.DataFrame() # Traiter comme un fichier vide
        except Exception as e:
            # Cela peut inclure des erreurs si le fichier est corrompu, protégé par mot de passe,
            # ou si les moteurs de lecture Excel (openpyxl, xlrd) ne sont pas installés.
            self.logger.error(f"Erreur lors de la lecture directe du fichier Excel {file_path.name} avec Pandas: {e}", exc_info=True)
            self.logger.info("Si l'erreur persiste, vérifiez que 'openpyxl' (pour .xlsx) ou 'xlrd' (pour .xls) sont installés.")
            return None

    def _apply_transformation(self, source_file_path: Path, source_dataframe: pd.DataFrame) -> pd.DataFrame | None:
        """
        Applique les transformations spécifiques aux données Bwinner.
        """
        self.logger.info(f"Application des transformations sur les données de {source_file_path.name}...")
        df_transformed = source_dataframe.copy()

        try:
            # 1. Filtrer les lignes où 'Name' est null
            if 'Name' not in df_transformed.columns:
                self.logger.error(f"Colonne 'Name' manquante, impossible d'appliquer les filtres. Fichier: {source_file_path.name}")
                raise TransformationError(f"Colonne 'Name' manquante dans {source_file_path.name}")

            df_transformed = df_transformed[~df_transformed['Name'].isnull()]
            self.logger.debug("Lignes avec 'Name' null filtrées.")

            # 2. Filtrer les lignes contenant "Totals" dans 'Name' (ignorer la casse)
            df_transformed = df_transformed[~df_transformed['Name'].astype(str).str.contains("Totals", case=False, na=False)]
            self.logger.debug("Lignes contenant 'Totals' dans 'Name' filtrées.")

            # 3. Transformer 'Report Date'
            # L'ancien code ajoutait 1 jour. On utilise DATE_TRANSFORMATION_DELTA.
            # Il faut s'assurer que la colonne 'Report Date' existe et que son format est 'dd/mm/yyyy'.
            if 'Report Date' not in df_transformed.columns:
                self.logger.error(f"Colonne 'Report Date' manquante, transformation de date impossible. Fichier: {source_file_path.name}")
                raise TransformationError(f"Colonne 'Report Date' manquante dans {source_file_path.name}")

            def transform_report_date(date_val):
                if pd.isna(date_val):
                    return None # Ou une chaîne vide, ou gérer l'erreur
                date_str = str(date_val)[:10] # Prendre les 10 premiers caractères (ex: de "dd/mm/yyyy HH:MM:SS")
                try:
                    # Pandas peut lire les dates Excel comme des objets datetime.datetime directement.
                    # Si c'est déjà un datetime, on peut l'utiliser. Sinon, parser.
                    if isinstance(date_val, datetime):
                        dt_obj = date_val
                    else: # Supposer que c'est une chaîne au format dd/mm/yyyy
                        dt_obj = datetime.strptime(date_str, '%d/%m/%Y')

                    transformed_dt = dt_obj + DATE_TRANSFORMATION_DELTA
                    return transformed_dt.strftime('%d/%m/%Y')
                except ValueError as e:
                    self.logger.warning(f"Format de date inattendu '{date_str}' dans 'Report Date' pour {source_file_path.name}. Erreur: {e}. Date non transformée.")
                    return date_str # Retourner la chaîne originale en cas d'erreur de parsing
                except TypeError as e: # Si date_val n'est pas str ou datetime
                    self.logger.warning(f"Type de date inattendu '{type(date_val)}' dans 'Report Date' pour {source_file_path.name}. Erreur: {e}. Date non transformée.")
                    return str(date_val)


            df_transformed['Report Date'] = df_transformed['Report Date'].apply(transform_report_date)
            self.logger.debug("Colonne 'Report Date' transformée (ajout d'un jour).")

            # 4. Sélectionner et réordonner les colonnes finales
            final_columns = ['Report Date', 'Name', 'Total Stakes', 'Total Paid Win']
            # Vérifier que toutes les colonnes finales existent dans le DataFrame transformé
            missing_final_cols = [col for col in final_columns if col not in df_transformed.columns]
            if missing_final_cols:
                self.logger.error(f"Colonnes finales attendues manquantes après transformation: {missing_final_cols}. Fichier: {source_file_path.name}")
                raise TransformationError(f"Colonnes finales manquantes: {missing_final_cols} dans {source_file_path.name}")

            df_transformed = df_transformed[final_columns]
            self.logger.debug(f"Colonnes sélectionnées et réorganisées: {final_columns}")

            # La classe de base Transformer gère la conversion en str au moment de la sauvegarde si c'est du CSV.
            # Si des conversions de type spécifiques sont nécessaires avant la sauvegarde, les faire ici.
            # L'ancien script convertissait tout en str à la fin, ce qui est le comportement par défaut
            # pour la sauvegarde CSV si les types ne sont pas gérés autrement.

            self.logger.info(f"Transformations appliquées avec succès pour {source_file_path.name}.")
            return df_transformed

        except TransformationError: # Erreurs spécifiques déjà logguées
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue durant l'application des transformations sur {source_file_path.name}: {e}", exc_info=True)
            return None


def run_bwinner_transformer():
    """Fonction principale pour lancer le transformateur Bwinner."""
    transformer_job = None
    try:
        transformer_job = BwinnerTransformer()
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
    run_bwinner_transformer()