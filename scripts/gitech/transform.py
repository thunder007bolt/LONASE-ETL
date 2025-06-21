from pathlib import Path
import numpy as np # Pour np.nan
import pandas as pd
import re # Pour la regex d'extraction de date
from datetime import datetime # Non utilisé directement, mais pd.to_datetime pourrait l'être

from base.tranformer import Transformer, TransformationError

JOB_NAME = "gitech"

class GitechTransformer(Transformer):
    """
    Transformateur pour les fichiers "Etat de la course" de Gitech (PMU Online).
    Source: Excel (.xls), Sortie: CSV.
    Lit directement les fichiers Excel avec Pandas et extrait la date du contenu.
    """
    def __init__(self):
        super().__init__(job_name=JOB_NAME, log_file_path=f"logs/transform_{JOB_NAME}.log")
        self.job_config["csv_separator"] = ";" # Spécifique à ce job

    def _extract_date_from_excel_content(self, file_path: Path) -> str | None:
        """
        Extrait une date d'une cellule spécifique (ou ligne) du fichier Excel.
        Lit seulement les premières lignes pour trouver la date.
        """
        self.logger.info(f"Tentative d'extraction de la date depuis le contenu de {file_path.name}")
        try:
            # Lire seulement les premières lignes pour trouver la date (ex: les 10 premières)
            # sans essayer de parser tout le fichier comme des données tabulaires immédiatement.
            df_preview = pd.read_excel(file_path, engine='xlrd', nrows=5, header=None) # Lire sans en-tête

            # Chercher la date dans les cellules lues. L'ancien code cherchait dans df.iloc[1] (deuxième ligne lue).
            # On suppose que la date est dans la deuxième ligne (index 1) de ce preview.
            if len(df_preview) > 1:
                # Concaténer les valeurs de la ligne en une seule chaîne si la date est répartie
                # ou chercher dans une colonne spécifique si la position est fixe.
                # L'ancien code faisait str(df.iloc[1]), ce qui convertit toute la Series en str.
                # On va itérer sur les cellules de la ligne 1 pour trouver le motif.
                for cell_value in df_preview.iloc[1]:
                    if pd.isna(cell_value):
                        continue
                    match = re.search(r"Du:\s*(\d{2}/\d{2}/\d{4})", str(cell_value))
                    if match:
                        date_str = match.group(1)
                        self.logger.info(f"Date extraite du contenu du fichier: {date_str}")
                        return date_str

            self.logger.warning(f"Motif de date 'Du: DD/MM/YYYY' non trouvé dans les premières lignes de {file_path.name}.")
            return None # Retourner None si non trouvé, pour que _apply_transformation puisse gérer.

        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction de la date du contenu de {file_path.name}: {e}", exc_info=True)
            return None


    def _read_source_file_to_dataframe(self, file_path: Path) -> tuple[pd.DataFrame | None, str | None]:
        """
        Lit un fichier source Excel (.xls), extrait la date du contenu,
        puis lit les données tabulaires en sautant les en-têtes.
        Retourne un tuple: (DataFrame, date_extraite_str) ou (None, None) en cas d'erreur.
        """
        self.logger.info(f"Lecture du fichier Excel source: {file_path.name}")

        if file_path.suffix.lower() != ".xls":
            self.logger.error(f"Type de fichier non géré: {file_path.name}. Attendu .xls.")
            raise TransformationError(f"Type de fichier non géré: {file_path.suffix}, attendu .xls")

        # Étape 1: Extraire la date du contenu du fichier
        extracted_date_str = self._extract_date_from_excel_content(file_path)
        if not extracted_date_str:
            # Si la date ne peut pas être extraite, c'est une erreur pour ce transformateur.
            self.logger.error(f"Date de rapport n'a pas pu être extraite de {file_path.name}. Transformation annulée pour ce fichier.")
            return None, None
            # La classe de base déplacera le fichier source vers error/ si _apply_transformation retourne None.

        # Étape 2: Lire les données tabulaires en sautant les lignes d'en-tête.
        # L'ancien code utilisait skiprows=range(1, 6), signifiant sauter les lignes d'index 1 à 5.
        # Cela implique que la ligne 0 est lue, puis les lignes 1-5 sont sautées, et la ligne 6 devient l'en-tête.
        # Si la ligne 0 contient des en-têtes non désirés et la ligne 6 les vrais en-têtes:
        # skiprows=list(range(1,6)) + [0] # sauter 0, et 1-5. La ligne 6 est lue comme en-tête.
        # Ou, si la ligne 6 est la première ligne de données et qu'il n'y a pas d'en-tête à lire:
        # skiprows=range(0,6), header=None
        # L'ancien code faisait: data = pd.read_excel(xlsx_file, skiprows=range(1, 6))
        # Cela signifie que la ligne 0 est lue, les lignes 1 à 5 sont ignorées, et la ligne 6 (index 5 après skip)
        # est interprétée comme l'en-tête par défaut.
        # On va supposer que la ligne 6 (index 5 après skip, ou ligne 7 du fichier si index 0) est l'en-tête.
        # Donc, on saute les lignes 0, 1, 2, 3, 4, 5. La ligne 6 devient l'en-tête.
        # skiprows = 6 (si la 7ème ligne est l'en-tête) ou skiprows=range(0,6) et header=0 sur la ligne suivante.
        # L'ancien code: skiprows=range(1,6) -> skip lignes index 1,2,3,4,5. Ligne 0 est lue, ligne 6 (index 5) devient header.
        # Cela semble un peu étrange. On va supposer que les données commencent après 6 lignes d'en-tête/méta.
        # Et que la 7ème ligne (index 6) contient les vrais en-têtes.
        try:
            dataframe = pd.read_excel(file_path, engine='xlrd', skiprows=6)
            self.logger.info(f"Données tabulaires de {file_path.name} lues. {len(dataframe)} lignes trouvées.")
            return dataframe, extracted_date_str
        except FileNotFoundError: # Déjà géré mais par sécurité
            self.logger.error(f"Fichier source Excel non trouvé (deuxième tentative): {file_path}", exc_info=True)
            return None, extracted_date_str # On a la date, mais pas les données.
        except pd.errors.EmptyDataError:
            self.logger.warning(f"Le fichier Excel {file_path.name} est vide après skip des en-têtes.")
            return pd.DataFrame(), extracted_date_str # Retourner DF vide mais avec la date.
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture des données tabulaires de {file_path.name}: {e}", exc_info=True)
            return None, extracted_date_str

    def _process_numeric_column_value(self, value):
        """Nettoie et convertit une valeur en entier, retournant 0 en cas d'erreur."""
        if pd.isna(value): return 0
        value_str = str(value).replace(u'\xa0', '').strip()
        cleaned_value_str = value_str.replace(',', '')
        try:
            return int(float(cleaned_value_str))
        except ValueError:
            self.logger.debug(f"Impossible de convertir '{value_str}' en entier. Retourne 0.")
            return 0

    def _apply_transformation(self, source_file_path: Path, source_data: tuple) -> pd.DataFrame | None:
        """
        Applique les transformations. source_data est un tuple (DataFrame, extracted_date_str).
        """
        source_dataframe, extracted_date_str = source_data
        if source_dataframe is None or extracted_date_str is None:
            # Erreur déjà loggée par _read_source_file_to_dataframe ou _extract_date_from_excel_content
            return None

        self.logger.info(f"Application des transformations sur les données de {source_file_path.name} (Date rapport: {extracted_date_str})...")
        df = source_dataframe.copy()

        try:
            # 1. Renommer les colonnes (selon l'ancien script)
            expected_original_cols = ['No', 'Agences', 'Operateur', 'Vente', 'Annulation',
                                      'Remboursement', 'Paiement', 'Resultat']
            if len(df.columns) < len(expected_original_cols):
                 self.logger.error(f"Moins de colonnes que prévu ({len(df.columns)} vs {len(expected_original_cols)}) dans {source_file_path.name}.")
                 raise TransformationError(f"Nombre de colonnes insuffisant pour {source_file_path.name}.")
            # Utiliser seulement le nombre de colonnes attendues pour le renommage
            df.columns = expected_original_cols[:len(df.columns)] # Prend les N premières colonnes
            self.logger.debug("Colonnes renommées.")

            # 2. Filtrer les lignes où 'Operateur' est 'Total' ou 'montant global'
            if 'Operateur' in df.columns:
                df = df[~df['Operateur'].astype(str).isin(['Total', 'montant global'])]
                self.logger.debug("Lignes de totaux filtrées sur 'Operateur'.")
            else:
                raise TransformationError(f"Colonne 'Operateur' manquante pour le filtrage dans {source_file_path.name}.")

            # 3. Supprimer la colonne 'No' si elle existe
            if 'No' in df.columns:
                df = df.drop('No', axis=1)
                self.logger.debug("Colonne 'No' supprimée.")

            # 4. Insérer la colonne "Date vente" avec la date extraite
            # L'ancien code l'insérait à l'index 2. Ajuster si l'ordre des colonnes a changé.
            # Colonnes après drop de 'No': ['Agences', 'Operateur', 'Vente', ...]
            # Insertion à l'index 2 mettra 'Date vente' entre 'Operateur' et 'Vente'.
            df.insert(2, "Date vente", extracted_date_str)
            self.logger.debug(f"Colonne 'Date vente' insérée avec la valeur '{extracted_date_str}'.")

            # 5. Remplir les NaN dans 'Agences' par propagation vers l'avant
            if 'Agences' in df.columns:
                df['Agences'] = df['Agences'].ffill()
                self.logger.debug("Valeurs NaN dans 'Agences' remplies (ffill).")
            else:
                 raise TransformationError(f"Colonne 'Agences' manquante pour ffill dans {source_file_path.name}.")


            # 6. Nettoyer et convertir les colonnes numériques
            numeric_cols = ['Vente', 'Annulation', 'Remboursement', 'Paiement', 'Resultat']
            for col_name in numeric_cols:
                if col_name in df.columns:
                    df[col_name] = df[col_name].apply(self._process_numeric_column_value)
                else:
                    self.logger.warning(f"Colonne numérique attendue '{col_name}' non trouvée. Ignorée.")
            self.logger.debug(f"Colonnes numériques traitées: {numeric_cols}")

            # 7. Remplacer les NaN restants (s'il y en a) par chaîne vide et convertir tout en str
            df = df.replace({np.nan: ''}).astype(str)
            self.logger.debug("NaN restants remplacés par '' et toutes colonnes converties en str.")

            self.logger.info(f"Transformations appliquées avec succès pour {source_file_path.name}.")
            return df

        except TransformationError:
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue durant _apply_transformation pour {source_file_path.name}: {e}", exc_info=True)
            return None


def run_gitech_transformer():
    """Fonction principale pour lancer le transformateur Gitech."""
    transformer_job = None
    try:
        transformer_job = GitechTransformer()
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
    run_gitech_transformer()