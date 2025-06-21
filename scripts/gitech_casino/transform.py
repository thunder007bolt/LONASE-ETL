from pathlib import Path
import numpy as np # Pour np.nan
import pandas as pd
import re # Pour la regex d'extraction de date

from base.tranformer import Transformer, TransformationError

JOB_NAME = "gitech_casino"

class GitechCasinoTransformer(Transformer):
    """
    Transformateur pour les fichiers "Cumul CA des types de jeux" de Gitech (PMU Online).
    Source: Excel (.xls), Sortie: CSV.
    Lit directement les fichiers Excel avec Pandas et extrait la date du contenu.
    """
    def __init__(self):
        super().__init__(job_name=JOB_NAME, log_file_path=f"logs/transform_{JOB_NAME}.log")
        self.job_config["csv_separator"] = ";"
        # self.job_config["output_file_encoding"] = "utf8" # Déjà par défaut

    def _extract_date_from_excel_content(self, file_path: Path) -> str | None:
        """
        Extrait une date du fichier Excel.
        L'ancien code lisait df.iloc[2] (troisième ligne après lecture complète) pour la date.
        """
        self.logger.info(f"Tentative d'extraction de la date depuis le contenu de {file_path.name}")
        try:
            # Lire les premières lignes pour trouver la date.
            # La ligne contenant "Du: DD/MM/YYYY" est à l'index 2 (3ème ligne) du DataFrame original.
            # Si le fichier a X lignes d'en-tête à sauter pour les données tabulaires,
            # il faut lire ces lignes d'en-tête pour trouver la date.
            # L'ancien code faisait skiprows=range(0,6) pour les données, ce qui signifie que les lignes 0 à 5 sont des en-têtes.
            # La date est dans la ligne index 2 de ces lignes d'en-tête.
            df_preview = pd.read_excel(file_path, engine='xlrd', nrows=3, header=None) # Lire les 3 premières lignes

            if len(df_preview) > 2: # S'assurer que la ligne d'index 2 existe
                for cell_value in df_preview.iloc[2]: # Itérer sur les cellules de la 3ème ligne (index 2)
                    if pd.isna(cell_value):
                        continue
                    match = re.search(r"Du:\s*(\d{2}/\d{2}/\d{4})", str(cell_value))
                    if match:
                        date_str = match.group(1)
                        self.logger.info(f"Date extraite du contenu du fichier ({file_path.name}): {date_str}")
                        return date_str

            self.logger.warning(f"Motif de date 'Du: DD/MM/YYYY' non trouvé dans la 3ème ligne de {file_path.name}.")
            return None
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction de la date du contenu de {file_path.name}: {e}", exc_info=True)
            return None

    def _read_source_file_to_dataframe(self, file_path: Path) -> tuple[pd.DataFrame | None, str | None]:
        """
        Lit un fichier source Excel (.xls), extrait la date, puis lit les données tabulaires.
        Retourne un tuple: (DataFrame, date_extraite_str).
        """
        self.logger.info(f"Lecture du fichier Excel source: {file_path.name}")

        if file_path.suffix.lower() != ".xls":
            self.logger.error(f"Type de fichier non géré: {file_path.name}. Attendu .xls.")
            raise TransformationError(f"Type de fichier non géré: {file_path.suffix}, attendu .xls")

        extracted_date_str = self._extract_date_from_excel_content(file_path)
        if not extracted_date_str:
            self.logger.error(f"Date de rapport n'a pas pu être extraite de {file_path.name}.")
            return None, None

        try:
            # L'ancien code: skiprows=range(0, 6) -> saute les lignes d'index 0 à 5.
            # La ligne 6 (index 5 après skip si on commence à 0, ou ligne 7 du fichier) devient l'en-tête.
            dataframe = pd.read_excel(file_path, engine='xlrd', skiprows=6)
            self.logger.info(f"Données tabulaires de {file_path.name} lues. {len(dataframe)} lignes trouvées.")
            return dataframe, extracted_date_str
        except Exception as e: # FileNotFoundError, EmptyDataError, etc.
            self.logger.error(f"Erreur lors de la lecture des données tabulaires de {file_path.name}: {e}", exc_info=True)
            return None, extracted_date_str # Retourner la date si trouvée, mais DataFrame None

    def _process_numeric_column_value(self, value):
        """Nettoie et convertit une valeur en entier, retournant 0 en cas d'erreur."""
        # Logique identique à GitechTransformer, pourrait être dans une classe utilitaire ou BaseGitechTransformer.
        if pd.isna(value): return 0
        value_str = str(value).replace(u'\xa0', '').strip()
        cleaned_value_str = value_str.replace(',', '') # Supposé être un séparateur de milliers
        try:
            return int(float(cleaned_value_str)) # float d'abord pour gérer ex: "123.0"
        except ValueError:
            self.logger.debug(f"Impossible de convertir '{value_str}' en entier. Retourne 0.")
            return 0

    def _apply_transformation(self, source_file_path: Path, source_data: tuple) -> pd.DataFrame | None:
        """
        Applique les transformations. source_data est un tuple (DataFrame, extracted_date_str).
        """
        source_dataframe, extracted_date_str = source_data
        if source_dataframe is None or extracted_date_str is None:
            return None

        self.logger.info(f"Application des transformations sur {source_file_path.name} (Date rapport: {extracted_date_str})...")
        df = source_dataframe.copy()

        try:
            # 1. Renommer les colonnes
            expected_original_cols = ['No','IdJeu','NomJeu','Vente','Paiement','PourcentagePaiement']
            if len(df.columns) < len(expected_original_cols):
                 self.logger.error(f"Moins de colonnes que prévu ({len(df.columns)} vs {len(expected_original_cols)}) dans {source_file_path.name}.")
                 raise TransformationError(f"Nombre de colonnes insuffisant pour {source_file_path.name}.")
            df.columns = expected_original_cols[:len(df.columns)]
            self.logger.debug("Colonnes renommées.")

            # 2. Filtrer les lignes indésirables dans 'NomJeu'
            valeurs_a_filtrer = ['Total', 'montant global', 'PMU Online', 'Nom de jeu']
            if 'NomJeu' in df.columns:
                df = df[~df['NomJeu'].astype(str).isin(valeurs_a_filtrer)]
                self.logger.debug(f"Lignes filtrées sur 'NomJeu' pour les valeurs: {valeurs_a_filtrer}.")
            else:
                raise TransformationError(f"Colonne 'NomJeu' manquante pour le filtrage dans {source_file_path.name}.")

            # 3. Supprimer la colonne 'No'
            if 'No' in df.columns:
                df = df.drop('No', axis=1)
                self.logger.debug("Colonne 'No' supprimée.")

            # 4. Insérer la colonne "Date vente"
            # Colonnes après drop de 'No': ['IdJeu', 'NomJeu', 'Vente', ...]
            # Insertion à l'index 2 mettra 'Date vente' entre 'NomJeu' et 'Vente'.
            df.insert(2, "Date vente", extracted_date_str)
            self.logger.debug(f"Colonne 'Date vente' insérée avec la valeur '{extracted_date_str}'.")

            # 5. Nettoyer et convertir les colonnes numériques 'Vente', 'Paiement'
            # La colonne 'PourcentagePaiement' n'était pas traitée numériquement dans l'ancien code.
            # Elle sera donc convertie en str à la fin avec le reste.
            numeric_cols_to_process = ['Vente', 'Paiement']
            for col_name in numeric_cols_to_process:
                if col_name in df.columns:
                    df[col_name] = df[col_name].apply(self._process_numeric_column_value)
                else:
                    self.logger.warning(f"Colonne numérique attendue '{col_name}' non trouvée. Ignorée.")
            self.logger.debug(f"Colonnes numériques traitées: {numeric_cols_to_process}")

            # 6. Remplacer les NaN restants et convertir tout en str
            df = df.replace({np.nan: ''}).astype(str)
            self.logger.debug("NaN restants remplacés par '' et toutes colonnes converties en str.")

            self.logger.info(f"Transformations appliquées avec succès pour {source_file_path.name}.")
            return df

        except TransformationError:
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue durant _apply_transformation pour {source_file_path.name}: {e}", exc_info=True)
            return None


def run_gitech_casino_transformer():
    """Fonction principale pour lancer le transformateur Gitech Casino."""
    transformer_job = None
    try:
        transformer_job = GitechCasinoTransformer()
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
    run_gitech_casino_transformer()