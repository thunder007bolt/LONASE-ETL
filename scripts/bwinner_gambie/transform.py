from pathlib import Path
import numpy as np # Pour np.nan
import pandas as pd
from datetime import datetime # Pour la transformation de date si nécessaire

# Suppression des imports win32com, os, re, shutil, etc.
from base.tranformer import Transformer, TransformationError

JOB_NAME = "bwinner_gambie"

class BwinnerGambieTransformer(Transformer):
    """
    Transformateur pour les fichiers "Recette paiement Journalier" de Bwinner Gambie.
    Source: Excel (.xls), Sortie: CSV.
    Lit directement les fichiers Excel avec Pandas.
    """
    def __init__(self):
        super().__init__(job_name=JOB_NAME, log_file_path=f"logs/transform_{JOB_NAME}.log")
        # Configuration de sortie CSV (séparateur ';', encodage 'utf8')
        # Peut être défini dans config.yml du job ou ici si spécifique et non modifiable par config.
        # self.job_config["output_file_type"] = "csv" # Déjà par défaut dans Transformer
        self.job_config["csv_separator"] = ";"
        # self.job_config["output_file_encoding"] = "utf8" # Déjà par défaut

    def _read_source_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier source Excel (.xls) directement avec Pandas, en sautant les 6 premières lignes.
        """
        self.logger.info(f"Lecture du fichier Excel source (via Pandas): {file_path.name}")

        if file_path.suffix.lower() != ".xls":
            # Ce transformateur est spécifiquement pour .xls selon l'ancien code (FileFormat=51 pour .xlsx, mais ici c'est .xls)
            # Si des .xlsx sont aussi possibles, ajuster cette vérification ou la logique.
            self.logger.error(f"Type de fichier non géré: {file_path.name}. Attendu .xls pour ce transformateur.")
            raise TransformationError(f"Type de fichier non géré: {file_path.suffix}, attendu .xls")

        try:
            # Pour les fichiers .xls, pandas utilise typiquement xlrd. `pip install xlrd` peut être nécessaire.
            # skiprows=range(0,6) signifie sauter les lignes d'index 0 à 5 (les 6 premières).
            dataframe = pd.read_excel(file_path, engine='xlrd', skiprows=range(0, 6))
            self.logger.info(f"Fichier {file_path.name} lu avec succès via Pandas/xlrd. {len(dataframe)} lignes trouvées (après skip).")
            return dataframe
        except FileNotFoundError:
            self.logger.error(f"Fichier source Excel non trouvé: {file_path}", exc_info=True)
            return None
        except pd.errors.EmptyDataError:
            self.logger.warning(f"Le fichier Excel {file_path.name} est vide (après skip des premières lignes).")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture du fichier Excel {file_path.name} avec Pandas/xlrd: {e}", exc_info=True)
            self.logger.info("Vérifiez que 'xlrd' est installé (`pip install xlrd`) et que le fichier n'est pas corrompu.")
            return None

    def _process_numeric_column_value(self, value):
        """
        Nettoie et convertit une valeur individuelle en entier.
        Retourne 0 si la conversion échoue ou si la valeur est NaN.
        Logique de nettoyage (rstrip '00', suppression de ',') conservée de l'ancien script,
        mais à utiliser avec prudence car elle peut être incorrecte pour certains formats numériques.
        """
        if pd.isna(value): # Gérer les NaN en amont
            return 0

        value_str = str(value).replace(u'\xa0', '').strip() # Supprimer espaces insécables et espaces normaux

        # La logique de rstrip('00').replace(',', '') est très spécifique et potentiellement dangereuse.
        # Si les nombres sont "1,234.00" et que le but est d'avoir 1234:
        #   1. Remplacer ',' par '' -> "1234.00"
        #   2. Convertir en float -> 1234.00
        #   3. Convertir en int -> 1234
        # Si les nombres sont "1.234,00" (format européen) et le but est 1234:
        #   1. Remplacer '.' par '' -> "1234,00"
        #   2. Remplacer ',' par '.' -> "1234.00"
        #   3. Convertir en float -> 1234.00
        #   4. Convertir en int -> 1234
        # L'ancien code: `value_str.rstrip('00').replace(',', '')`
        #   "1,234.50" -> "1,234.5".replace(',', '') -> "1234.5" -> Erreur int()
        #   "1,234.00" -> "1,234.".replace(',', '') -> "1234." -> Erreur int()
        #   "1,234,000" -> "1,234,00".replace(',', '') -> "123400" -> OK
        # Cette logique est donc probablement pour des entiers formatés avec des virgules comme séparateurs de milliers
        # et potentiellement des zéros non significatifs à la fin.

        # Tentative de nettoyage plus standard pour les entiers avec séparateurs de milliers (virgule)
        cleaned_value_str = value_str.replace(',', '') # Supprimer les séparateurs de milliers

        try:
            # Tenter de convertir en float d'abord pour gérer les ".0" ou ".00" puis en int
            numeric_value = float(cleaned_value_str)
            return int(numeric_value) # Tronque la partie décimale
        except ValueError:
            # Si la conversion échoue, logguer un avertissement et retourner 0
            self.logger.debug(f"Impossible de convertir '{value_str}' (nettoyé: '{cleaned_value_str}') en entier. Retourne 0.")
            return 0


    def _apply_transformation(self, source_file_path: Path, source_dataframe: pd.DataFrame) -> pd.DataFrame | None:
        """Applique les transformations spécifiques aux données Bwinner Gambie."""
        self.logger.info(f"Application des transformations sur les données de {source_file_path.name}...")
        df = source_dataframe.copy()

        try:
            # 1. Renommer les colonnes (selon l'ancien script)
            # Il est crucial que le nombre de colonnes du fichier Excel (après skip) corresponde.
            expected_original_col_count = 10
            if len(df.columns) != expected_original_col_count:
                self.logger.error(f"Nombre de colonnes inattendu ({len(df.columns)}) dans {source_file_path.name} "
                                  f"après skip. Attendu: {expected_original_col_count}.")
                raise TransformationError(f"Nombre de colonnes incorrect pour {source_file_path.name}.")

            df.columns = ['No','Agences','Operateurs','date de vente','Recette','Annulation',
                          'Ventes Resultant','comm vente','Paiements','Resultats']
            self.logger.debug("Colonnes renommées.")

            # 2. Supprimer les 6 dernières lignes (lignes de totaux/pied de page)
            if len(df) > 6:
                df = df[:-6]
                self.logger.debug("Les 6 dernières lignes ont été supprimées.")
            else:
                self.logger.warning(f"Moins de 7 lignes dans le fichier {source_file_path.name} après skip, "
                                    "la suppression des 6 dernières lignes n'est pas appliquée ou videra le DataFrame.")


            # 3. Remplacer NaN dans 'Operateurs' par chaîne vide (avant conversion numérique)
            if 'Operateurs' in df.columns:
                df['Operateurs'] = df['Operateurs'].replace({np.nan: ''})
            else: # Devrait être impossible si le renommage a fonctionné et que le nombre de colonnes est correct
                self.logger.warning("Colonne 'Operateurs' non trouvée avant nettoyage numérique.")


            # 4. Appliquer le traitement numérique aux colonnes spécifiées
            numeric_cols = ['Operateurs', 'Recette', 'Annulation', 'Ventes Resultant',
                            'comm vente', 'Paiements', 'Resultats']
            for col_name in numeric_cols:
                if col_name in df.columns:
                    df[col_name] = df[col_name].apply(self._process_numeric_column_value)
                else:
                    self.logger.warning(f"Colonne numérique attendue '{col_name}' non trouvée. Elle sera ignorée.")
            self.logger.debug(f"Colonnes numériques traitées: {numeric_cols}")

            # 5. Transformer 'date de vente' : prendre les 10 premiers caractères
            # Si la colonne contient des objets datetime, cela les convertira en str YYYY-MM-DD.
            # Si ce sont des chaînes, cela prendra les 10 premiers caractères.
            if 'date de vente' in df.columns:
                df['date de vente'] = df['date de vente'].apply(lambda x: str(x)[:10] if pd.notna(x) else '')
                self.logger.debug("Colonne 'date de vente' transformée (prise des 10 premiers caractères).")
            else:
                 raise TransformationError(f"Colonne 'date de vente' manquante dans {source_file_path.name}.")


            # 6. Sélectionner et réordonner les colonnes (confirme l'ordre final)
            # C'est redondant si df.columns a déjà été assigné et que l'ordre est bon.
            # df = pd.DataFrame(df, columns=['No', 'Agences', 'Operateurs', 'date de vente', 'Recette',
            #                                'Annulation','Ventes Resultant', 'comm vente', 'Paiements', 'Resultats'])
            # On va supposer que l'assignation de df.columns au point 1 a fixé l'ordre.

            # 7. Remplacer les NaN restants (s'il y en a après les transformations) par chaîne vide
            df = df.replace({np.nan: ''})

            # 8. Convertir toutes les colonnes en type string pour la sortie CSV
            df = df.astype(str)
            self.logger.debug("Toutes les colonnes converties en type str pour la sortie.")

            self.logger.info(f"Transformations appliquées avec succès pour {source_file_path.name}.")
            return df

        except TransformationError: # Erreurs spécifiques déjà logguées
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue durant l'application des transformations sur {source_file_path.name}: {e}", exc_info=True)
            return None


def run_bwinner_gambie_transformer():
    """Fonction principale pour lancer le transformateur Bwinner Gambie."""
    transformer_job = None
    try:
        transformer_job = BwinnerGambieTransformer()
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
    run_bwinner_gambie_transformer()