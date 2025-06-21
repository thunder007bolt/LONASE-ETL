from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

from base.tranformer import Transformer, TransformationError # Importer l'exception personnalisée

# Les imports os, re, shutil, win32com.client, base.logger, utils.config_utils, utils.file_manipulation
# ne semblent plus nécessaires directement ici si la classe de base gère la configuration et le déplacement des fichiers.

JOB_NAME = "acajou_digital" # Constante pour le nom du job

class AcajouDigitalTransformer(Transformer):
    """
    Transformateur pour les fichiers de Acajou Digital.
    Hérite de la classe Transformer de base et implémente la logique de transformation spécifique.
    """
    def __init__(self):
        # Le chemin du log est maintenant géré par la classe de base Transformer ou par l'Orchestrateur.
        # On passe seulement le nom du job et le chemin du fichier de log spécifique à ce transformateur.
        super().__init__(job_name=JOB_NAME, log_file_path=f"logs/transform_{JOB_NAME}.log")

    def _read_source_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Lit un fichier source CSV et le charge dans un DataFrame pandas.
        """
        self.logger.info(f"Lecture du fichier source CSV: {file_path.name}")
        try:
            # L'ancien code lisait avec delimiter=',', on le garde.
            # Si des erreurs de parsing spécifiques surviennent (ex: mauvais encodage),
            # des options supplémentaires pour read_csv peuvent être nécessaires (ex: encoding='latin1').
            dataframe = pd.read_csv(file_path, delimiter=',')
            self.logger.info(f"Fichier {file_path.name} lu avec succès. {len(dataframe)} lignes trouvées.")
            return dataframe
        except FileNotFoundError:
            self.logger.error(f"Fichier source non trouvé: {file_path}", exc_info=True)
            return None # Provoquera le déplacement du fichier source vers le dossier d'erreur par la classe de base
        except pd.errors.EmptyDataError:
            self.logger.warning(f"Le fichier source {file_path.name} est vide.")
            return pd.DataFrame() # Retourner un DataFrame vide pour traitement standard des fichiers vides
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture du fichier CSV {file_path.name}: {e}", exc_info=True)
            return None # Provoquera le déplacement du fichier source vers le dossier d'erreur

    def _apply_transformation(self, source_file_path: Path, source_dataframe: pd.DataFrame) -> pd.DataFrame | None:
        """
        Applique les transformations spécifiques aux données d'Acajou Digital.
        L'argument source_file_path est disponible si des transformations dépendent du nom/chemin du fichier.
        """
        self.logger.info(f"Application des transformations sur les données de {source_file_path.name}...")

        # Copier le DataFrame pour éviter les SettingWithCopyWarning si on modifie directement source_dataframe
        df_transformed = source_dataframe.copy()

        try:
            # 1. Transformation de la colonne 'Date Created'
            # L'ancien format était '%Y-%m-%d' dans la chaîne, puis reformaté en '%d/%m/%Y'.
            # S'assurer que la colonne existe.
            if 'Date Created' not in df_transformed.columns:
                self.logger.error(f"Colonne 'Date Created' manquante dans le fichier {source_file_path.name}.")
                raise TransformationError(f"Colonne 'Date Created' manquante pour {source_file_path.name}")

            # La transformation de date peut échouer si le format n'est pas constant.
            # Il faut une gestion d'erreur plus fine ici si nécessaire.
            def format_date_created(date_str):
                if pd.isna(date_str) or not isinstance(date_str, str) or len(date_str) < 10:
                    return None # Ou une valeur par défaut, ou lever une erreur
                try:
                    return datetime.strptime(date_str[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
                except ValueError:
                    self.logger.warning(f"Format de date inattendu '{date_str[:10]}' dans 'Date Created' pour {source_file_path.name}. Laissé tel quel ou mis à None.")
                    return None # Ou date_str[:10] pour garder la valeur originale si le parsing échoue

            df_transformed['Date Created'] = df_transformed['Date Created'].apply(format_date_created)
            self.logger.debug("Colonne 'Date Created' transformée.")

            # 2. Ajout de la colonne 'Produit'
            df_transformed['Produit'] = "Pari Sportif" # Valeur constante
            self.logger.debug("Colonne 'Produit' ajoutée.")

            # 3. Sélection et réorganisation des colonnes
            # Définir les colonnes attendues dans l'ordre final.
            # Ces colonnes pourraient être mises dans la configuration du job si elles changent souvent.
            final_columns_ordered = [
                'Date Created', 'Ticket ID', 'Msisdn', 'Purchase Method', 'Collection',
                'Gross Payout', 'Status', 'Produit'
            ]

            # Vérifier si toutes les colonnes finales existent (sauf 'Produit' qu'on vient d'ajouter)
            missing_cols = [col for col in final_columns_ordered if col not in df_transformed.columns and col != 'Produit']
            if missing_cols:
                self.logger.error(f"Colonnes finales manquantes après transformations initiales: {missing_cols} pour {source_file_path.name}.")
                raise TransformationError(f"Colonnes finales manquantes: {missing_cols} pour {source_file_path.name}")

            df_transformed = df_transformed[final_columns_ordered]
            self.logger.debug("Colonnes sélectionnées et réorganisées.")

            # 4. Remplacement des NaN et conversion en str
            # Remplacer np.nan par une chaîne vide. Attention: cela convertit tout en chaîne.
            # Si des types numériques ou date sont attendus plus tard, ce n'est pas idéal.
            # Pour une sortie CSV, c'est souvent acceptable si les consommateurs s'y attendent.
            # Si les types doivent être préservés, utiliser df.fillna() de manière plus ciblée.
            df_transformed = df_transformed.replace({np.nan: ''})
            # Convertir toutes les colonnes en chaîne de caractères.
            df_transformed = df_transformed.astype(str)
            self.logger.debug("NaN remplacés par '' et toutes les colonnes converties en type str.")

            self.logger.info(f"Transformations appliquées avec succès pour {source_file_path.name}.")
            return df_transformed

        except TransformationError: # Erreurs spécifiques déjà logguées
            raise # Pour que la classe de base gère le déplacement du fichier
        except Exception as e:
            self.logger.error(f"Erreur inattendue durant l'application des transformations sur {source_file_path.name}: {e}", exc_info=True)
            # Renvoyer None pour indiquer l'échec à la classe de base, qui déplacera le fichier source.
            return None


def run_acajou_digital_transformer():
    """Fonction principale pour lancer le transformateur Acajou Digital."""
    transformer_job = None
    try:
        transformer_job = AcajouDigitalTransformer()
        # La méthode principale de la classe Transformer de base
        transformer_job.process_files_transformation()
    except TransformerConfigurationError as e:
        # Le logger peut ne pas être initialisé si l'erreur est dans __init__ avant l'init du logger.
        print(f"ERREUR CRITIQUE de configuration du Transformer {JOB_NAME}: {e}")
        if transformer_job and transformer_job.logger: # Au cas où le logger a été init
             transformer_job.logger.critical(f"Erreur de configuration: {e}", exc_info=True)
    except Exception as e:
        # Gérer les autres erreurs inattendues qui pourraient survenir avant ou pendant process_files_transformation.
        log_msg = f"Erreur inattendue et non gérée dans l'exécution du transformateur {JOB_NAME}: {e}"
        if transformer_job and transformer_job.logger:
            transformer_job.logger.critical(log_msg, exc_info=True)
        else:
            print(log_msg) # Fallback si logger non dispo


if __name__ == '__main__':
    # Assurez-vous que load_env.py a été appelé si les variables d'env sont dans un .env
    # from load_env import load_env
    # load_env()
    run_acajou_digital_transformer()
