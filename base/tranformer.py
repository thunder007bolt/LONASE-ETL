from pathlib import Path
from abc import ABC, abstractmethod
import re
from datetime import datetime, date # S'assurer que date est importé
import pandas as pd # Importer pour type hints

from utils.config_utils import get_transformation_configurations # Fonction utilitaire existante
from utils.file_manipulation import move_file # Fonction utilitaire existante
# Logger est fourni par get_transformation_configurations

# Exceptions personnalisées
class TransformerConfigurationError(Exception):
    pass

class TransformationError(Exception):
    pass


class Transformer(ABC):
    """
    Classe de base abstraite pour transformer des fichiers de données.
    Gère la configuration des chemins, l'itération sur les fichiers sources,
    l'application d'une transformation spécifique (définie par la classe fille),
    et la sauvegarde du fichier transformé.
    """
    DEFAULT_OUTPUT_FILE_TYPE = "csv"
    DEFAULT_OUTPUT_ENCODING = "utf-8"
    DEFAULT_CSV_SEPARATOR = ","

    def __init__(self, job_name: str, log_file_path: str):
        """
        Initialise le Transformer.

        Args:
            job_name (str): Nom du job, utilisé pour la configuration.
            log_file_path (str): Chemin vers le fichier de log.
        """
        self.name = job_name
        self.log_file_path = log_file_path
        self.logger = None # Sera initialisé par get_transformation_configurations

        # Attributs pour le suivi des erreurs
        self.files_with_errors_count = 0
        self.files_with_errors_list: list[Path] = [] # Stocke les noms de fichiers en erreur

        try:
            (
                self.job_config,       # Configuration spécifique au job (anciennement self.config)
                self.base_config,      # Configuration de base (si utilisée directement)
                self.logger,           # Initialisé ici
                self.local_transformation_dest_path, # Dossier de destination pour les fichiers transformés
                self.local_processed_source_path, # Dossier où déplacer les sources après succès
                self.local_source_path, # Dossier source des fichiers à transformer
                self.source_file_pattern, # Motif des fichiers à chercher dans source_path
                self.local_error_dest_path # Dossier pour les sources en cas d'erreur de transfo/sauvegarde
            ) = get_transformation_configurations(
                name=self.name,
                log_file=self.log_file_path
            )
            # S'assurer que les chemins essentiels sont des Path et existent
            for path_attr_name in [
                'local_transformation_dest_path', 'local_processed_source_path',
                'local_source_path', 'local_error_dest_path'
            ]:
                path_val = getattr(self, path_attr_name)
                if not isinstance(path_val, Path):
                    raise TransformerConfigurationError(f"Chemin mal configuré: {path_attr_name} n'est pas un Path.")
                path_val.mkdir(parents=True, exist_ok=True)

        except KeyError as e:
            msg = f"Clé manquante lors de la configuration du Transformer pour {self.name}: {e}."
            if self.logger: self.logger.critical(msg, exc_info=True)
            raise TransformerConfigurationError(msg) from e
        except Exception as e:
            msg = f"Erreur inattendue lors de la configuration du Transformer pour {self.name}: {e}."
            if self.logger: self.logger.critical(msg, exc_info=True)
            raise TransformerConfigurationError(msg) from e


    @abstractmethod
    def _apply_transformation(self, source_file_path: Path, source_dataframe: pd.DataFrame) -> pd.DataFrame | None:
        """
        Méthode abstraite pour appliquer la logique de transformation spécifique.
        Cette méthode est appelée pour chaque fichier source.

        Args:
            source_file_path (Path): Chemin du fichier source en cours de traitement.
                                     Peut être utile pour des transformations dépendant du nom/chemin.
            source_dataframe (pd.DataFrame): DataFrame Pandas contenant les données lues depuis le fichier source.

        Returns:
            pd.DataFrame | None: DataFrame Pandas contenant les données transformées.
                                 Si None est retourné, cela indique une erreur durant la transformation,
                                 et le fichier source sera déplacé vers le dossier d'erreurs.
        """
        pass

    @abstractmethod
    def _read_source_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Méthode abstraite pour lire un fichier source et le convertir en DataFrame.
        Similaire à celle de la classe Loader, mais spécifique au contexte de transformation.
        """
        pass


    def _extract_date_from_filename(self, filename: str, regex_pattern: str = r"(\d{4}-\d{2}-\d{2})", date_format_str: str = "%Y-%m-%d") -> date | None:
        """
        Tente d'extraire une date d'un nom de fichier en utilisant une expression régulière.

        Args:
            filename (str): Le nom du fichier.
            regex_pattern (str): Expression régulière pour capturer la date. Le groupe 1 doit être la date.
            date_format_str (str): Format de la date à parser (pour strptime).

        Returns:
            date | None: Objet date si l'extraction et le parsing réussissent, None sinon.
        """
        match = re.search(regex_pattern, filename)
        if match:
            try:
                date_str = match.group(1)
                return datetime.strptime(date_str, date_format_str).date()
            except (IndexError, ValueError) as e:
                self.logger.warning(f"Impossible d'extraire ou parser la date depuis '{filename}' avec le pattern '{regex_pattern}' et format '{date_format_str}': {e}")
                return None
        self.logger.debug(f"Aucune date trouvée dans '{filename}' avec le pattern '{regex_pattern}'.")
        return None

    def _build_transformed_filename(self, source_file_path: Path, transformed_file_type: str) -> str:
        """
        Construit le nom du fichier transformé.
        Par défaut: {job_name}_transformed_{date_extraite_du_nom_source_ou_date_actuelle}.{type}
        Peut être surchargée par les classes filles pour une logique de nommage plus complexe.
        """
        # Tenter d'extraire une date du nom de fichier source
        # Les patterns regex et formats peuvent être mis dans la config du job si besoin
        date_in_filename = self._extract_date_from_filename(source_file_path.name)

        date_to_use_str: str
        if date_in_filename:
            date_to_use_str = date_in_filename.strftime("%Y-%m-%d")
        else:
            # Fallback à la date actuelle si aucune date n'est trouvée dans le nom de fichier
            # ou si la configuration l'indique.
            use_current_date_fallback = self.job_config.get("use_current_date_for_transformed_filename_fallback", True)
            if use_current_date_fallback:
                date_to_use_str = datetime.now().strftime("%Y-%m-%d")
                self.logger.debug(f"Aucune date extraite de {source_file_path.name}, utilisation de la date actuelle ({date_to_use_str}) pour le nom du fichier transformé.")
            else: # Utiliser le nom original du fichier source comme base si pas de date et pas de fallback
                 date_to_use_str = source_file_path.stem # Nom sans extension
                 self.logger.debug(f"Utilisation du radical du nom de fichier source '{date_to_use_str}' pour le nom du fichier transformé.")


        filename_prefix = self.job_config.get("transformed_filename_prefix", f"{self.name}_transformed")
        return f"{filename_prefix}_{date_to_use_str}.{transformed_file_type.lower()}"


    def _save_transformed_dataframe(self, transformed_df: pd.DataFrame, source_file_path: Path, **kwargs) -> Path | None:
        """
        Sauvegarde le DataFrame transformé dans un fichier.
        Déplace le fichier source original vers le dossier 'processed' en cas de succès.

        Args:
            transformed_df (pd.DataFrame): Le DataFrame transformé à sauvegarder.
            source_file_path (Path): Chemin du fichier source original (pour le déplacer).
            **kwargs: Arguments supplémentaires pour les fonctions to_csv/to_excel de pandas.

        Returns:
            Path | None: Chemin du fichier sauvegardé si succès, None sinon.
        """
        output_file_type = self.job_config.get("output_file_type", self.DEFAULT_OUTPUT_FILE_TYPE)
        transformed_filename = self._build_transformed_filename(source_file_path, output_file_type)
        output_file_path = self.local_transformation_dest_path / transformed_filename

        self.logger.info(f"Sauvegarde des données transformées de '{source_file_path.name}' vers '{output_file_path}'")
        try:
            # Écraser si le fichier de destination existe (comportement par défaut de to_csv/to_excel)
            if output_file_type == "csv":
                csv_params = {
                    'index': False,
                    'encoding': self.job_config.get('output_file_encoding', self.DEFAULT_OUTPUT_ENCODING),
                    'sep': self.job_config.get('csv_separator', self.DEFAULT_CSV_SEPARATOR)
                }
                csv_params.update(kwargs)
                transformed_df.to_csv(output_file_path, **csv_params)
            elif output_file_type == "excel":
                excel_params = {'index': False, 'engine': 'openpyxl'}
                excel_params.update(kwargs)
                transformed_df.to_excel(output_file_path, **excel_params)
            else:
                self.logger.error(f"Type de fichier de sortie non supporté: '{output_file_type}'.")
                raise ValueError(f"Type de fichier de sortie non supporté: {output_file_type}")

            self.logger.info(f"Fichier transformé '{transformed_filename}' sauvegardé avec succès.")

            # Déplacer le fichier source original vers le dossier 'processed'
            try:
                move_file(source_file_path, self.local_processed_source_path)
                self.logger.info(f"Fichier source '{source_file_path.name}' déplacé vers {self.local_processed_source_path}.")
            except Exception as move_e:
                self.logger.error(f"Erreur lors du déplacement du fichier source '{source_file_path.name}' "
                                  f"vers {self.local_processed_source_path}: {move_e}", exc_info=True)
                # Le fichier transformé est sauvegardé, mais le source n'a pas pu être déplacé.
                # C'est un état potentiellement problématique pour les exécutions futures.
                # On pourrait vouloir lever une exception ici ou ajouter une logique de compensation.
            return output_file_path

        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du fichier transformé '{transformed_filename}': {e}", exc_info=True)
            # Ne pas déplacer le fichier source si la sauvegarde du transformé échoue.
            return None


    def process_files_transformation(self):
        """
        Orchestre le processus de transformation pour tous les fichiers trouvés.
        """
        self.logger.info(f"Démarrage du processus de transformation pour le job: {self.name}")
        self.logger.info(f"Recherche des fichiers sources dans: {self.local_source_path} (motif: {self.source_file_pattern})")

        self.files_with_errors_count = 0
        self.files_with_errors_list = []
        files_processed_successfully = 0

        source_files = list(self.local_source_path.glob(self.source_file_pattern))
        if not source_files:
            self.logger.info("Aucun fichier source trouvé correspondant au motif. Fin du traitement.")
            return

        self.logger.info(f"{len(source_files)} fichier(s) source(s) trouvé(s) pour transformation.")

        for source_file_path in source_files:
            self.logger.info(f"Traitement du fichier source: {source_file_path.name}")
            transformed_df = None # Pour s'assurer qu'il est défini avant le bloc try de sauvegarde
            try:
                source_dataframe = self._read_source_file_to_dataframe(source_file_path)
                if source_dataframe is None: # Erreur de lecture déjà loggée
                    raise TransformationError(f"Échec de la lecture du fichier source {source_file_path.name}.")

                if source_dataframe.empty:
                    self.logger.info(f"Le fichier source {source_file_path.name} est vide ou n'a produit aucune donnée. "
                                     "Il sera déplacé vers le dossier 'processed' sans transformation.")
                    try:
                        move_file(source_file_path, self.local_processed_source_path)
                        self.logger.info(f"Fichier source vide '{source_file_path.name}' déplacé vers {self.local_processed_source_path}.")
                        files_processed_successfully +=1
                    except Exception as move_e:
                        self.logger.error(f"Impossible de déplacer le fichier source vide '{source_file_path.name}' vers {self.local_processed_source_path}: {move_e}", exc_info=True)
                        self.files_with_errors_count += 1
                        self.files_with_errors_list.append(source_file_path.name)
                    continue # Passer au fichier suivant

                transformed_df = self._apply_transformation(source_file_path, source_dataframe)
                if transformed_df is None: # Erreur de transformation déjà loggée
                    raise TransformationError(f"Échec de la transformation du fichier {source_file_path.name}.")

                if transformed_df.empty:
                    self.logger.info(f"La transformation de {source_file_path.name} a produit un DataFrame vide. "
                                     "Aucun fichier transformé ne sera sauvegardé. Le fichier source sera déplacé vers 'processed'.")
                    try:
                        move_file(source_file_path, self.local_processed_source_path)
                        self.logger.info(f"Fichier source (transformation vide) '{source_file_path.name}' déplacé vers {self.local_processed_source_path}.")
                        files_processed_successfully +=1
                    except Exception as move_e:
                        self.logger.error(f"Impossible de déplacer le fichier source (transformation vide) '{source_file_path.name}' vers {self.local_processed_source_path}: {move_e}", exc_info=True)
                        self.files_with_errors_count += 1
                        self.files_with_errors_list.append(source_file_path.name)
                    continue


                saved_path = self._save_transformed_dataframe(transformed_df, source_file_path)
                if saved_path:
                    files_processed_successfully += 1
                else: # Erreur de sauvegarde déjà loggée
                    raise TransformationError(f"Échec de la sauvegarde du fichier transformé pour {source_file_path.name}.")

            except TransformationError as te: # Erreurs spécifiques à la transformation/sauvegarde
                self.logger.error(f"Erreur de transformation pour {source_file_path.name}: {te}", exc_info=False) # exc_info=False car déjà loggué potentiellement
                self.files_with_errors_count += 1
                self.files_with_errors_list.append(source_file_path.name)
                try:
                    move_file(source_file_path, self.local_error_dest_path)
                    self.logger.info(f"Fichier source {source_file_path.name} déplacé vers le dossier d'erreurs: {self.local_error_dest_path}.")
                except Exception as move_e:
                    self.logger.error(f"Impossible de déplacer le fichier source {source_file_path.name} (après erreur) vers {self.local_error_dest_path}: {move_e}", exc_info=True)
            except Exception as e: # Autres erreurs inattendues
                self.logger.error(f"Erreur inattendue lors du traitement de {source_file_path.name}: {e}", exc_info=True)
                self.files_with_errors_count += 1
                self.files_with_errors_list.append(source_file_path.name)
                try:
                    move_file(source_file_path, self.local_error_dest_path) # Tenter de déplacer même en cas d'erreur inconnue
                except Exception as move_e_unk:
                     self.logger.error(f"Impossible de déplacer le fichier source {source_file_path.name} (après erreur inconnue) vers {self.local_error_dest_path}: {move_e_unk}", exc_info=True)

        self._report_transformation_summary(len(source_files), files_processed_successfully)
        self.logger.info(f"Processus de transformation pour {self.name} terminé.")


    def _report_transformation_summary(self, total_files_found: int, success_count: int):
        """Affiche un résumé du processus de transformation."""
        self.logger.info("--- Résumé de la Transformation ---")
        self.logger.info(f"Nombre total de fichiers sources trouvés: {total_files_found}")
        self.logger.info(f"Nombre de fichiers traités avec succès (transformés et/ou déplacés vers 'processed'): {success_count}")

        if self.files_with_errors_count > 0:
            self.logger.warning(f"Nombre de fichiers ayant rencontré des erreurs: {self.files_with_errors_count}")
            self.logger.warning("Liste des fichiers sources en erreur (déplacés vers le dossier d'erreurs):")
            for filename_path in self.files_with_errors_list: # C'est une liste de Path maintenant
                self.logger.warning(f"  - {filename_path.name}") # Afficher juste le nom
        else:
            if total_files_found > 0 : # Seulement si des fichiers ont été trouvés
                 self.logger.info("Tous les fichiers sources trouvés ont été traités sans erreur critique.")
            # else: déjà loggué qu'aucun fichier n'a été trouvé.
        self.logger.info("------------------------------------")

    def __del__(self):
        if self.logger: # Le logger peut être None si l'init a échoué très tôt
            self.logger.info(f"Transformer {self.name} terminé.")
        # else:
        #     print(f"Transformer {self.name} terminé (logger non disponible).")