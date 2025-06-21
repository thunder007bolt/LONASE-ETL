from selenium import webdriver
from pathlib import Path
from abc import ABC, abstractmethod
import time
import os
import glob
from datetime import datetime, timedelta, date
from time import sleep
import logging # Utiliser le module logging standard

from base.logger import Logger # Gardé pour l'instant, mais pourrait être remplacé par logging standard
from utils.config_utils import get_config, get_secret
from utils.date_utils import get_yesterday_date
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.file_manipulation import rename_file, delete_file
# from utils.other_utils import retry_operation # Décommenter si utilisé


class BaseScrapper(ABC):
    """
    Classe de base abstraite pour le web scraping.
    Fournit des fonctionnalités communes pour l'ouverture du navigateur, la gestion des dates,
    l'interaction avec les éléments web, et le téléchargement de fichiers.
    """
    DEFAULT_RETRY_ATTEMPTS = 3
    DEFAULT_RETRY_DELAY = 5 # secondes

    def __init__(self, name: str, env_variables_list: list, log_file_path: str, chrome_options_arguments: list = None):
        self.name = name
        self.logger = Logger(log_file=log_file_path).get_logger() # Ou configurer un logger standard
        self.logger.info(f"Initialisation du Scrapper: {self.name}")

        try:
            configs = get_config(name) # Peut lever une exception si la config n'est pas trouvée
            self.base_config = configs["base"]
            # S'assurer que la config spécifique au job existe
            if name not in configs:
                self.logger.error(f"Configuration pour le job '{name}' non trouvée dans la configuration globale.")
                raise KeyError(f"Configuration pour '{name}' absente.")
            self.config = configs[name]
        except KeyError as e:
            self.logger.error(f"Clé de configuration manquante lors de l'initialisation de {self.name}: {e}")
            raise  # Renvoyer l'exception pour arrêter si la config est cruciale
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors du chargement de la configuration pour {self.name}: {e}")
            raise


        self.chrome_options_arguments = chrome_options_arguments if chrome_options_arguments is not None else []
        self.secret_config = get_secret(env_variables_list)
        self.browser = None

        # Initialisation des dates, sera configuré dans _set_dates
        self.start_date: date = None
        self.end_date: date = None

        # Attributs pour la gestion des nouvelles tentatives (non utilisé globalement pour l'instant)
        # self.max_retry_attempts = self.config.get("max_retry_attempts", self.DEFAULT_RETRY_ATTEMPTS)
        # self.retry_delay = self.config.get("retry_delay", self.DEFAULT_RETRY_DELAY)


    def _retry_operation(self, operation, max_attempts=DEFAULT_RETRY_ATTEMPTS, delay=DEFAULT_RETRY_DELAY, description="opération"):
        """Tente d'exécuter une opération plusieurs fois avec un délai entre les tentatives."""
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"Tentative {attempt + 1}/{max_attempts} pour {description}...")
                return operation()
            except Exception as e:
                self.logger.warning(f"Tentative {attempt + 1} pour {description} échouée: {e}")
                if attempt == max_attempts - 1:
                    self.logger.error(f"Toutes les {max_attempts} tentatives pour {description} ont échoué.")
                    raise # Renvoyer la dernière exception
                time.sleep(delay)

    def process_extraction(self):
        """Orchestre le processus d'extraction complet."""
        try:
            self.logger.info(f"Démarrage du processus d'extraction pour {self.name}")
            self._set_dates()
            self._delete_old_files() # S'assurer que le chemin de téléchargement est valide

            # Utilisation de _retry_operation pour l'ouverture du navigateur
            self._retry_operation(self._open_browser, description="ouvrir le navigateur")

            if not self.browser:
                self.logger.error("Le navigateur n'a pas pu être initialisé. Arrêt du processus.")
                return

            self._connection_to_platform() # Peut aussi nécessiter des retries
            self._download_files() # Peut aussi nécessiter des retries
            self.logger.info(f"Processus d'extraction pour {self.name} terminé avec succès.")

        except Exception as e:
            self.logger.error(f"Erreur majeure dans process_extraction pour {self.name}: {e}", exc_info=True)
            # exc_info=True ajoute le traceback au log
        finally:
            self._quit_browser()


    def _open_browser(self):
        """Ouvre le navigateur Chrome avec les options de téléchargement configurées."""
        self.logger.info("Tentative d'ouverture du navigateur Chrome.")

        download_path_str = self.config.get("download_path")
        if not download_path_str:
            self.logger.error("Le chemin de téléchargement 'download_path' n'est pas configuré.")
            raise ValueError("download_path non configuré.")

        # S'assurer que le chemin est absolu et correctement formaté pour Selenium
        download_path = Path(download_path_str).resolve()
        # Selenium sous Windows peut préférer les backslashes, mais os.path.normpath ou str(Path) devrait suffire.
        # fr"{str(download_path)}" est plus sûr si des caractères spéciaux sont possibles, mais str() suffit généralement.

        chrome_options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": str(download_path)}
        chrome_options.add_experimental_option("prefs", prefs)

        for argument in self.chrome_options_arguments:
            chrome_options.add_argument(argument)

        # Ajouter des options courantes pour la stabilité en mode headless (si utilisé)
        # chrome_options.add_argument("--headless") # Si besoin
        # chrome_options.add_argument("--disable-gpu") # Souvent nécessaire avec headless
        # chrome_options.add_argument("--window-size=1920,1080") # Taille de fenêtre pour headless
        # chrome_options.add_argument("--no-sandbox") # Peut être nécessaire dans certains environnements CI/Docker
        # chrome_options.add_argument("--disable-dev-shm-usage") # Peut être nécessaire dans certains environnements CI/Docker

        try:
            self.browser = webdriver.Chrome(options=chrome_options)
            self.logger.info("Navigateur Chrome ouvert avec succès.")
        except Exception as e:
            self.logger.error(f"Erreur détaillée lors de l'ouverture du navigateur : {e}", exc_info=True)
            raise # Renvoyer l'exception pour que _retry_operation puisse la gérer


    def _set_dates(self):
        """
        Définit les dates de début et de fin pour l'extraction.
        Priorité :
        1. Variables d'environnement (ex: JENKINS_START_DATE, JENKINS_END_DATE)
        2. Configuration du job (config.yml)
        3. Date d'hier (par défaut)
        """
        self.logger.info("Configuration des dates de début et de fin pour l'extraction.")
        _, _, _, yesterday = get_yesterday_date() # Objet date

        # Noms des variables d'environnement potentielles (à adapter si nécessaire)
        env_start_date_var = self.config.get("env_start_date_variable", "JENKINS_START_DATE")
        env_end_date_var = self.config.get("env_end_date_variable", "JENKINS_END_DATE")

        # Lire depuis les variables d'environnement
        env_start_date_str = os.getenv(env_start_date_var)
        env_end_date_str = os.getenv(env_end_date_var)

        parsed_start_date = None
        if env_start_date_str:
            try:
                parsed_start_date = datetime.strptime(env_start_date_str, "%Y-%m-%d").date()
                self.logger.info(f"Date de début récupérée depuis la variable d'environnement {env_start_date_var}: {parsed_start_date.strftime('%Y-%m-%d')}")
            except ValueError:
                self.logger.error(f"Format de date invalide pour {env_start_date_var} ('{env_start_date_str}'). Attendu YYYY-MM-DD.")

        parsed_end_date = None
        if env_end_date_str:
            try:
                parsed_end_date = datetime.strptime(env_end_date_str, "%Y-%m-%d").date()
                self.logger.info(f"Date de fin récupérée depuis la variable d'environnement {env_end_date_var}: {parsed_end_date.strftime('%Y-%m-%d')}")
            except ValueError:
                self.logger.error(f"Format de date invalide pour {env_end_date_var} ('{env_end_date_str}'). Attendu YYYY-MM-DD.")

        # Utiliser les dates des variables d'environnement si valides, sinon regarder la config du job
        if parsed_start_date:
            self.start_date = parsed_start_date
        else:
            start_date_config = self.config.get("start_date")
            if start_date_config is not None:
                if isinstance(start_date_config, str):
                    try:
                        self.start_date = datetime.strptime(start_date_config, "%Y-%m-%d").date()
                    except ValueError:
                        self.logger.error(f"Format de start_date invalide ('{start_date_config}') dans config.yml. Utilisation de la date d'hier.")
                        self.start_date = yesterday
                elif isinstance(start_date_config, date):
                    self.start_date = start_date_config
                else:
                    self.logger.warning(f"Type de start_date non géré ('{type(start_date_config)}') dans config.yml. Utilisation de la date d'hier.")
                    self.start_date = yesterday
            else:
                self.start_date = yesterday
            self.logger.info(f"Date de début (après fallback config/défaut) : {self.start_date.strftime('%Y-%m-%d')}")

        if parsed_end_date:
            self.end_date = parsed_end_date
        else:
            end_date_config = self.config.get("end_date")
            if end_date_config is not None:
                if isinstance(end_date_config, str):
                    try:
                        self.end_date = datetime.strptime(end_date_config, "%Y-%m-%d").date()
                    except ValueError:
                        self.logger.error(f"Format de end_date invalide ('{end_date_config}') dans config.yml. Utilisation de la date d'hier.")
                        self.end_date = yesterday
                elif isinstance(end_date_config, date):
                    self.end_date = end_date_config
                else:
                    self.logger.warning(f"Type de end_date non géré ('{type(end_date_config)}') dans config.yml. Utilisation de la date d'hier.")
                    self.end_date = yesterday
            else:
                self.end_date = yesterday
            self.logger.info(f"Date de fin (après fallback config/défaut) : {self.end_date.strftime('%Y-%m-%d')}")

        if self.start_date > self.end_date:
            self.logger.error(f"La date de début ({self.start_date.strftime('%Y-%m-%d')}) est postérieure à la date de fin ({self.end_date.strftime('%Y-%m-%d')}). "
                              "Ajustement: end_date = start_date.")
            self.end_date = self.start_date


    @staticmethod
    def _get_by_type(locator_type: str) -> str:
        """Retourne le type de localisateur Selenium correspondant."""
        if locator_type == 'id':
            return By.ID
        elif locator_type == 'xpath':
            return By.XPATH
        elif locator_type == 'name':
            return By.NAME
        elif locator_type == 'tag':
            return By.TAG_NAME
        # Ajouter d'autres types si nécessaire (e.g., By.CLASS_NAME, By.CSS_SELECTOR)
        else:
            raise ValueError(f"Type de localisateur non supporté : {locator_type}")

    @abstractmethod
    def _connection_to_platform(self):
        """Méthode abstraite pour la connexion à la plateforme spécifique."""
        pass

    @abstractmethod
    def _download_files(self):
        """Méthode abstraite pour le processus de téléchargement des fichiers."""
        pass

    @abstractmethod
    def _process_download_for_date_range(self, start_date_to_process: date, end_date_to_process: date):
        """
        Méthode abstraite pour traiter le téléchargement pour une plage de dates spécifique.
        Cette méthode sera appelée par _process_multiple_files_by_date.
        Elle doit gérer la logique de sélection de date sur la plateforme et le déclenchement du téléchargement.
        """
        pass

    def _delete_old_files(self):
        """Supprime les anciens fichiers dans le répertoire de téléchargement configuré."""
        download_path_str = self.config.get("download_path")
        if not download_path_str:
            self.logger.error("Suppression des anciens fichiers impossible: 'download_path' non configuré.")
            return # Ou lever une exception si c'est critique

        download_path = Path(download_path_str)
        if not download_path.is_dir():
            self.logger.warning(f"Le répertoire de téléchargement '{download_path}' n'existe pas. Aucun fichier à supprimer.")
            return

        self.logger.info(f"Suppression des fichiers existants dans {download_path} correspondant au motif '*'...")
        try:
            # delete_file attend un Path et un motif.
            # Pour supprimer tous les fichiers, le motif est habituellement "*"
            # Si delete_file gère la non-existence du chemin, c'est bon. Sinon, vérifier ici.
            delete_file(Path(download_path), "*") # Assurez-vous que delete_file peut prendre un Path
            self.logger.info("Anciens fichiers supprimés avec succès.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression des anciens fichiers dans {download_path}: {e}", exc_info=True)
            # Décider si c'est une erreur bloquante.


    def _process_multiple_files_by_date(self, rename_downloaded_file=True):
        """
        Traite les téléchargements pour une plage de dates définie par self.start_date et self.end_date.
        Itère jour par jour, appelle _process_download_for_date_range, vérifie le téléchargement, et renomme le fichier.
        """
        if not (self.start_date and self.end_date):
            self.logger.error("Les dates de début et/ou de fin ne sont pas définies. Impossible de traiter plusieurs fichiers.")
            return

        current_date = self.start_date
        delta = timedelta(days=1)

        self.logger.info(f"Début du traitement des fichiers multiples de {self.start_date.strftime('%Y-%m-%d')} à {self.end_date.strftime('%Y-%m-%d')}.")

        while current_date <= self.end_date:
            self.logger.info(f"Traitement pour la date : {current_date.strftime('%Y-%m-%d')}")
            try:
                # La méthode spécifique au scraper doit gérer la sélection de cette date et le téléchargement.
                # On passe current_date comme début et fin pour traiter un seul jour à la fois.
                self._process_download_for_date_range(current_date, current_date)

                # Vérification et renommage du fichier
                # Le file_pattern peut être spécifique au jour ou plus générique
                file_pattern_config = self.config.get('file_pattern', '*.csv') # Valeur par défaut si non spécifié

                # _verify_and_rename_download s'occupe de l'attente, vérification et renommage
                if rename_downloaded_file:
                    downloaded_file_path = self._verify_and_rename_download(
                        date_for_filename=current_date,
                        file_pattern_to_wait_for=file_pattern_config
                    )
                    if downloaded_file_path:
                        self.logger.info(f"Fichier pour {current_date.strftime('%Y-%m-%d')} traité et renommé : {downloaded_file_path.name}")
                    else:
                        self.logger.warning(f"Aucun fichier n'a été vérifié ou renommé pour {current_date.strftime('%Y-%m-%d')}.")
                        # Gérer l'échec: nouvelle tentative pour cette date, ou passer à la suivante?
                        # Pour l'instant, on logue et on continue.
                else:
                    # Si on ne renomme pas, on peut quand même vouloir vérifier que quelque chose a été téléchargé
                    # Ceci nécessiterait une version de _verify_download qui ne renomme pas.
                    # Pour l'instant, on suppose que si rename_downloaded_file est False, la vérification est gérée ailleurs ou n'est pas nécessaire ici.
                    self.logger.info(f"Téléchargement pour {current_date.strftime('%Y-%m-%d')} effectué (sans renommage automatique ici).")

            except Exception as e:
                self.logger.error(f"Erreur lors du traitement pour la date {current_date.strftime('%Y-%m-%d')}: {e}", exc_info=True)
                # Optionnel: implémenter une logique de retry pour la date spécifique ici
                # ou simplement continuer avec la date suivante.

            current_date += delta
            sleep(self.config.get("delay_between_dates_sec", 2)) # Petit délai configurable entre les dates

        self.logger.info("Traitement des fichiers multiples terminé.")


    def _verify_and_rename_download(self, date_for_filename: date, file_pattern_to_wait_for: str, sub_patterns_in_filename: list = None) -> Path | None:
        """
        Attend qu'un fichier correspondant au motif apparaisse dans le répertoire de téléchargement,
        le vérifie, puis le renomme en utilisant le nom du scraper et la date fournie.

        Args:
            date_for_filename: La date à utiliser pour nommer le fichier (objet date).
            file_pattern_to_wait_for: Motif glob pour le fichier attendu (ex: "*.csv", "report_*.zip").
            sub_patterns_in_filename: Liste optionnelle de chaînes qui doivent être présentes dans le nom du fichier trouvé.

        Returns:
            Le chemin (Path) du fichier renommé en cas de succès, None sinon.
        """
        download_path_str = self.config.get("download_path")
        if not download_path_str:
            self.logger.error("Chemin de téléchargement 'download_path' non configuré. Impossible de vérifier/renommer.")
            return None

        download_dir = Path(download_path_str)
        timeout_seconds = self.config.get("wait_time", 120) # Temps d'attente en secondes
        poll_interval_seconds = 2 # Interroge toutes les 2 secondes

        self.logger.info(f"Attente du fichier '{file_pattern_to_wait_for}' dans {download_dir} (timeout: {timeout_seconds}s).")

        start_time = time.time()
        found_file_path = None
        while time.time() - start_time < timeout_seconds:
            candidate_files = list(download_dir.glob(file_pattern_to_wait_for))
            if not candidate_files:
                time.sleep(poll_interval_seconds)
                continue

            # Filtrer par sous-motifs si spécifié
            if sub_patterns_in_filename:
                for f_path in candidate_files:
                    if all(sub_pattern in f_path.name for sub_pattern in sub_patterns_in_filename):
                        # S'assurer que le fichier n'est pas temporaire (par exemple, .crdownload pour Chrome)
                        if not f_path.name.endswith((".tmp", ".crdownload", ".part")):
                            found_file_path = f_path
                            break
            elif candidate_files:
                 # Prendre le premier fichier qui n'est pas temporaire
                for f_path in candidate_files:
                    if not f_path.name.endswith((".tmp", ".crdownload", ".part")):
                        found_file_path = f_path
                        break

            if found_file_path:
                # Vérifier si le fichier est stable (sa taille ne change plus)
                # C'est une heuristique simple, peut nécessiter d'être plus robuste
                last_size = -1
                current_size = found_file_path.stat().st_size
                time.sleep(0.5) # Attendre un peu pour voir si la taille change
                if current_size == found_file_path.stat().st_size and current_size > 0: # Fichier stable et non vide
                     self.logger.info(f"Fichier trouvé et semble stable: {found_file_path.name} (taille: {current_size} bytes).")
                     break # Sortir de la boucle while
                else:
                    self.logger.info(f"Fichier {found_file_path.name} trouvé mais semble encore en cours de téléchargement ou vide. Attente...")
                    found_file_path = None # Réinitialiser pour continuer à chercher/attendre

            time.sleep(poll_interval_seconds)

        if not found_file_path:
            self.logger.error(f"Timeout: Aucun fichier correspondant à '{file_pattern_to_wait_for}' (et aux sous-motifs optionnels) n'a été trouvé ou stabilisé dans {download_dir} après {timeout_seconds} secondes.")
            raise TimeoutError(f"Téléchargement non complété ou fichier non trouvé pour le motif '{file_pattern_to_wait_for}'")

        # Renommage du fichier
        try:
            new_filename_stem = f"{self.name}_{date_for_filename.strftime('%Y-%m-%d')}"
            # rename_file de file_manipulation.py prend (pattern, source_folder, rename_name, logger)
            # Ici, nous avons déjà le chemin complet du fichier source (found_file_path)
            # Nous devons adapter l'appel ou modifier rename_file pour qu'il accepte un Path direct.

            # Supposons que rename_file peut être adapté ou qu'on utilise une logique ici :
            # new_file_path = found_file_path.parent / f"{new_filename_stem}{found_file_path.suffix}"
            # if new_file_path.exists():
            #     self.logger.warning(f"Le fichier de destination {new_file_path} existe déjà et sera écrasé.")
            #     new_file_path.unlink()
            # found_file_path.rename(new_file_path)

            # Utilisation de la fonction rename_file existante (qui prend un pattern et un dossier source)
            # Cela semble moins direct car nous avons déjà le fichier exact.
            # Alternative: modifier rename_file pour accepter un Path de fichier source.
            # Pour l'instant, on adapte pour utiliser la signature actuelle si possible, ou on le fait manuellement.

            # Logique de renommage manuelle pour plus de clarté ici :
            target_path = found_file_path.parent / f"{new_filename_stem}{found_file_path.suffix}"
            if target_path.exists():
                self.logger.warning(f"Le fichier cible '{target_path}' existe déjà. Il sera écrasé.")
                target_path.unlink()
            found_file_path.rename(target_path)
            self.logger.info(f"Fichier '{found_file_path.name}' renommé en '{target_path.name}' dans {target_path.parent}.")
            return target_path
        except Exception as e:
            self.logger.error(f"Erreur lors du renommage du fichier {found_file_path.name}: {e}", exc_info=True)
            return None # Ou renvoyer found_file_path si le renommage échoue mais que le fichier existe


    # --- Méthodes d'interaction Selenium ---
    def _wait_and_click(self, locator: str, locator_type: str = 'xpath', timeout: int = 30, raise_error: bool = True):
        """Attend qu'un élément soit cliquable et clique dessus."""
        by = self._get_by_type(locator_type)
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            element.click()
            self.logger.debug(f"Cliqué sur l'élément : {locator_type}='{locator}'")
            return element
        except Exception as e:
            self.logger.error(f"Erreur en cliquant sur l'élément {locator_type}='{locator}': {e}", exc_info=not raise_error)
            if raise_error:
                raise ElementInteractionError(f"Impossible de cliquer sur {locator_type}='{locator}'") from e
            return None

    def _wait_for_element_presence(self, locator: str, locator_type: str = 'xpath', timeout: int = 30, raise_error: bool = True):
        """Attend qu'un élément soit présent dans le DOM."""
        by = self._get_by_type(locator_type)
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            self.logger.debug(f"Élément trouvé (présent) : {locator_type}='{locator}'")
            return element
        except Exception as e:
            self.logger.error(f"Erreur lors de l'attente de la présence de {locator_type}='{locator}': {e}", exc_info=not raise_error)
            if raise_error:
                raise ElementInteractionError(f"Élément non trouvé (présence) {locator_type}='{locator}'") from e
            return None

    def _wait_and_send_keys(self, locator: str, keys_to_send: str, locator_type: str = 'xpath', timeout: int = 30, clear_first: bool = True, raise_error: bool = True):
        """Attend qu'un élément soit présent/visible, (optionnellement) le vide, et y envoie des touches."""
        element = self._wait_for_element_presence(locator, locator_type, timeout, raise_error)
        if element:
            try:
                if clear_first:
                    element.clear()
                    self.logger.debug(f"Champ vidé : {locator_type}='{locator}'")
                element.send_keys(keys_to_send)
                self.logger.debug(f"Texte '{keys_to_send}' envoyé à : {locator_type}='{locator}'")
            except Exception as e:
                self.logger.error(f"Erreur en envoyant du texte à {locator_type}='{locator}': {e}", exc_info=not raise_error)
                if raise_error:
                    raise ElementInteractionError(f"Impossible d'envoyer du texte à {locator_type}='{locator}'") from e
                return None
        return element

    def _fill_select_by_visible_text(self, locator: str, text_to_select: str, locator_type: str = 'xpath', timeout: int = 30, raise_error: bool = True):
        """Remplit un élément <select> en sélectionnant une option par son texte visible."""
        element = self._wait_for_element_presence(locator, locator_type, timeout, raise_error)
        if element:
            try:
                Select(element).select_by_visible_text(str(text_to_select))
                self.logger.debug(f"Option '{text_to_select}' sélectionnée dans le select : {locator_type}='{locator}'")
            except Exception as e:
                self.logger.error(f"Erreur en sélectionnant dans le select {locator_type}='{locator}': {e}", exc_info=not raise_error)
                if raise_error:
                    raise ElementInteractionError(f"Impossible de sélectionner '{text_to_select}' dans {locator_type}='{locator}'") from e
                return None
        return element

    def _wait_for_invisibility(self, locator: str, locator_type: str='xpath', timeout: int=30, raise_error: bool = True) -> bool:
        """Attend qu'un élément devienne invisible."""
        by = self._get_by_type(locator_type)
        try:
            WebDriverWait(self.browser, timeout).until(
                EC.invisibility_of_element_located((by, locator))
            )
            self.logger.debug(f"Élément devenu invisible : {locator_type}='{locator}'")
            return True
        except Exception as e:
            self.logger.warning(f"Élément {locator_type}='{locator}' n'est pas devenu invisible dans le délai imparti ou erreur: {e}", exc_info=not raise_error)
            if raise_error:
                 raise ElementInteractionError(f"Élément {locator_type}='{locator}' toujours visible ou erreur.") from e
            return False


    def _quit_browser(self, error_message: str = None):
        """Ferme le navigateur de manière sécurisée."""
        if self.browser:
            try:
                if error_message:
                    self.logger.error(f"Erreur avant de quitter le navigateur: {error_message}")
                self.logger.info("Fermeture du navigateur...")
                self.browser.quit()
                self.browser = None # Important pour éviter les appels multiples ou sur un navigateur fermé
                self.logger.info("Navigateur fermé avec succès.")
            except Exception as e:
                self.logger.error(f"Erreur lors de la fermeture du navigateur: {e}", exc_info=True)
        else:
            self.logger.info("Aucun navigateur à fermer ou déjà fermé.")

    def __del__(self):
        """Destructeur pour s'assurer que le navigateur est fermé."""
        self.logger.debug(f"Destructeur appelé pour {self.name}. Tentative de fermeture du navigateur si ouvert.")
        self._quit_browser()
        self.logger.info(f"Scrapper {self.name} terminé et nettoyé.")


# Classe d'exception personnalisée pour les erreurs d'interaction Selenium
class ElementInteractionError(Exception):
    pass
