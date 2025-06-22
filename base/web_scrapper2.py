# System
import time
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    UnexpectedTagNameException,
    WebDriverException,
    ElementClickInterceptedException
)

# Base
from base.logger import Logger

# Utils
from utils.config_utils import get_config, get_secret
from utils.date_utils import get_yesterday_date
from utils.file_manipulation import rename_file, delete_files
from utils.config_utils import get_scrapper_configurations

# Constants
MAX_BROWSER_OPEN_RETRIES = 5
DOWNLOAD_RETRY_LIMIT = 3
INTER_DATE_SLEEP_SECONDS = 2

class BaseScrapper(ABC):
    """
    Classe de base abstraite pour les opérations de scraping web utilisant Selenium.
    Gère le cycle de vie du navigateur, la configuration, le logging, les interactions
    web courantes et le processus de téléchargement de fichiers sur une période donnée.
    """

    # Mapping des types de localisateurs Selenium
    BY_MAP = {
        'id': By.ID,
        'xpath': By.XPATH,
        'name': By.NAME,
        'tag': By.TAG_NAME,
        'css': By.CSS_SELECTOR
    }

    def __init__(self, name: str, env_variables_list: list, log_file: str, chrome_options_arguments: list = None):
        """
        Initialise le scrapper.

        Args:
            name (str): Nom du scrapper (utilisé pour la configuration).
            env_variables_list (list): Liste des variables d'environnement pour les secrets.
            log_file (str): Chemin vers le fichier de log.
            chrome_options_arguments (list, optional): Arguments additionnels pour ChromeOptions. Defaults to None.
        """
        self.name: str = name
        self.browser: webdriver.Chrome | None = None
        self.chrome_options_arguments: list = chrome_options_arguments or []
        self.start_date: datetime.date
        self.end_date: datetime.date
        (
            self.config,
            self.base_config,
            self.secret_config,
            self.logger,
            self.extraction_dest_path,
        ) = get_scrapper_configurations(name, log_file, env_variables_list)

        self.logger.info(f"Initialisation du scrapper '{self.name}'...")

    def __enter__(self):
        """Méthode pour le context manager: ouvre le navigateur."""
        self._open_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Méthode pour le context manager: ferme le navigateur et log les erreurs."""
        self.logger.info("Fermeture du navigateur...")
        if self.browser:
            try:
                self.browser.quit()
                self.logger.info("Navigateur fermé avec succès.")
            except Exception as e:
                self.logger.error(f"Erreur lors de la tentative de fermeture du navigateur: {e}")
        if exc_type:
            self.logger.error(f"Une exception non gérée a terminé le processus: {exc_val}", exc_info=(exc_type, exc_val, exc_tb))
        else:
             self.logger.info("Processus terminé sans erreur majeure.")
        self.logger.info(f"------------ Fin du scrapper '{self.name}' --------------")
        return False

    def _open_browser(self):
        """Ouvre le navigateur Chrome avec les options de téléchargement configurées."""
        self.logger.info(f"Tentative d'ouverture du navigateur Chrome. Répertoire de téléchargement : {self.extraction_dest_path}")
        self.extraction_dest_path.mkdir(parents=True, exist_ok=True) # Crée le dossier s'il n'existe pas

        chrome_options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": str(self.extraction_dest_path)}
        chrome_options.add_experimental_option("prefs", prefs)

        for argument in self.chrome_options_arguments:
            chrome_options.add_argument(argument)
            self.logger.info(f"Ajout de l'option Chrome: {argument}")

        for attempt in range(MAX_BROWSER_OPEN_RETRIES):
            try:
                self.logger.info(f"Tentative {attempt + 1}/{MAX_BROWSER_OPEN_RETRIES}...")
                self.browser = webdriver.Chrome(options=chrome_options)
                self.logger.info("Navigateur ouvert avec succès.")
                return
            except WebDriverException as e:
                self.logger.error(f"Erreur lors de l'ouverture du navigateur (tentative {attempt + 1}): {e}")
                if attempt < MAX_BROWSER_OPEN_RETRIES - 1:
                    time.sleep(5)
                else:
                    self.logger.critical("Échec de l'ouverture du navigateur après plusieurs tentatives.")
                    raise

    def process_extraction(self):
        """Orchestre le processus principal de scraping."""
        if not self.browser:
             self.logger.error("Le navigateur n'est pas ouvert. Impossible de continuer.")
             raise RuntimeError("Tentative d'extraction sans navigateur initialisé.")

        self._set_date()
        self._delete_old_files()
        self._connection_to_platform()
        self._download_files() # Cette méthode devrait implémenter la logique de boucle si nécessaire

    def _set_date(self):
        """Définit les dates de début et de fin pour l'extraction."""
        _, _, _, yesterday_date = get_yesterday_date()

        start_date_config = self.config.get("start_date")
        end_date_config = self.config.get("end_date")

        try:
            self.start_date = start_date_config or yesterday_date
            self.end_date = end_date_config or yesterday_date
        except ValueError as e:
             self.logger.error(f"Format de date invalide dans la configuration: {e}. Utilisation de la date d'hier.")
             self.start_date = yesterday_date
             self.end_date = yesterday_date

        self.logger.info(f"Période d'extraction définie du {self.start_date.strftime('%Y-%m-%d')} au {self.end_date.strftime('%Y-%m-%d')}")

    @staticmethod
    def _get_by_type(locator_type: str) -> By:
        """Retourne le type de localisateur Selenium basé sur une chaîne."""
        by_type = BaseScrapper.BY_MAP.get(locator_type.lower())
        if not by_type:
            raise ValueError(f"Type de localisateur non supporté: {locator_type}")
        return by_type

    @abstractmethod
    def _connection_to_platform(self):
        """Méthode abstraite pour la connexion à la plateforme cible."""
        pass

    @abstractmethod
    def _download_files(self):
        """
        Méthode abstraite principale pour déclencher le(s) téléchargement(s).
        Devrait contenir la logique de boucle sur les dates si nécessaire,
        en appelant _process_download_for_date ou une méthode similaire.
        """
        pass

    def _process_download(self, target_date: datetime.date):
        """
        Méthode (potentiellement abstraite ou avec implémentation par défaut)
        pour déclencher le téléchargement pour UNE date spécifique.
        Appelée par _process_multiple_files.
        """
        self.logger.warning(f"La méthode _process_download n'est pas implémentée pour la date {target_date}. Aucun téléchargement déclenché.")
        pass

    def _delete_old_files(self, pattern: str = "*"):
        """Supprime les fichiers correspondant au motif dans le dossier de téléchargement."""
        self.logger.info(f"Suppression des fichiers existants correspondant à '{pattern}' dans {self.extraction_dest_path}...")
        count = delete_files(self.extraction_dest_path, pattern)
        self.logger.info(f"{count or 'Aucun'} fichier(s) supprimé(s).")

    def _process_multiple_files(self, skip_verification_and_rename: bool = False):
        """
        Gère le téléchargement de fichiers sur une plage de dates, jour par jour.
        Appelle _process_download pour chaque date.
        """
        self.logger.info("Début du processus de téléchargement ...")
        current_date = self.start_date
        delta = timedelta(days=1)

        while current_date <= self.end_date:
            self.logger.info(f"--- Traitement pour la date : {current_date.strftime('%Y-%m-%d')} ---")
            for attempt in range(DOWNLOAD_RETRY_LIMIT):
                 self.logger.info(f"Tentative de téléchargement {attempt + 1}/{DOWNLOAD_RETRY_LIMIT} pour {current_date.strftime('%Y-%m-%d')}")
                 try:
                    # 1. Déclencher le téléchargement pour la date courante
                    self._process_download(current_date)

                    if not skip_verification_and_rename:
                        # 2. Vérifier que le fichier est bien téléchargé
                        file_pattern = self.config.get('file_pattern', '*') # Prend le pattern du config ou '*' par défaut
                        downloaded_file_path = self._verify_download(
                            file_pattern=file_pattern,
                            target_date=current_date # Pour le logging dans _verify_download
                        )

                        # 3. Renommer le fichier
                        target_name = f"{self.name}_{current_date.strftime('%Y-%m-%d')}"
                        rename_file(file_pattern, self.extraction_dest_path, target_name, self.logger)
                        self.logger.info(f"Fichier pour {current_date.strftime('%Y-%m-%d')} renommé en {target_name}{downloaded_file_path.suffix}")

                    break # Sortir de la boucle de retry si succès

                 except Exception as e:
                    self.logger.error(f"Échec de la tentative {attempt + 1} pour {current_date.strftime('%Y-%m-%d')}: {e}")
                    if attempt == DOWNLOAD_RETRY_LIMIT - 1:
                         self.logger.error(f"Échec final du téléchargement/vérification pour {current_date.strftime('%Y-%m-%d')} après {DOWNLOAD_RETRY_LIMIT} tentatives.")
                         #TODO: Décider quoi faire : continuer avec la date suivante ou arrêter ?
                         # pour l'instant, on continue avec la date suivante.
                    else:
                        time.sleep(5) # Attendre avant la prochaine tentative

            # Aller à la date suivante
            current_date += delta
            if current_date <= self.end_date:
                 # Petit délai entre les traitements de dates pour éviter de surcharger le serveur
                 self.logger.debug(f"Pause de {INTER_DATE_SLEEP_SECONDS}s avant la prochaine date.")
                 time.sleep(INTER_DATE_SLEEP_SECONDS)

        self.logger.info("Fin du processus de téléchargement.")

    def _verify_download(self, file_pattern: str = None, target_date: datetime.date = None, patterns_in_name: list = None, timeout: int = None) -> Path:
        """
        Attend et vérifie l'apparition d'un fichier téléchargé correspondant
        à un motif dans le répertoire de téléchargement.

        Args:
            file_pattern (str, optional): Motif Glob pour rechercher le fichier. Utilise config['file_pattern'] si None.
            target_date (datetime.date, optional): Date concernée (pour le logging). Utilise self.start_date si None.
            patterns_in_name (list, optional): Liste de chaînes qui doivent être présentes dans le nom du fichier trouvé.
            timeout (int, optional): Temps d'attente maximum en secondes. Utilise config['wait_time'] si None.

        Raises:
            TimeoutException: Si le fichier n'est pas trouvé dans le délai imparti.

        Returns:
            Path: Chemin d'accès au fichier téléchargé vérifié.
        """
        effective_pattern = file_pattern or self.config.get("file_pattern", "*")
        effective_timeout = timeout or self.config.get("wait_time", 120)
        log_date_str = (target_date or self.start_date).strftime('%Y-%m-%d')

        self.logger.info(f"Attente ({effective_timeout}s max) du fichier pour la date {log_date_str} correspondant à '{effective_pattern}' dans {self.extraction_dest_path}")
        if patterns_in_name:
            self.logger.info(f"Le nom du fichier doit aussi contenir: {patterns_in_name}")

        start_time = time.time()
        poll_interval = 2 # secondes

        while time.time() - start_time < effective_timeout:
            # Recherche des fichiers correspondant au motif principal
            found_files = list(self.extraction_dest_path.glob(effective_pattern))

            # Filtrage supplémentaire si patterns_in_name est fourni
            valid_files = []
            if found_files:
                 # Exclure les fichiers temporaires courants
                 potential_files = [f for f in found_files if not f.name.endswith(('.tmp', '.crdownload', '.part'))]

                 if patterns_in_name:
                    for file_path in potential_files:
                         # Vérifie si TOUS les motifs requis sont dans le nom du fichier
                         if all(p in file_path.name for p in patterns_in_name):
                             valid_files.append(file_path)
                 else:
                     valid_files = potential_files # Prend tous les fichiers non temporaires si pas de motifs spécifiques

            if valid_files:
                 # Pour l'instant, on prend le premier fichier valide trouvé.
                 #Todo:  Ajouter une logique pour choisir le plus récent si plusieurs correspondent.
                 found_file_path = valid_files[0]
                 self.logger.info(f"Fichier trouvé pour la date {log_date_str}: {found_file_path.name}")
                 return found_file_path

            # Attendre avant la prochaine vérification
            time.sleep(poll_interval)

        # Si la boucle se termine sans trouver de fichier
        self.logger.error(f"Timeout: Aucun fichier correspondant trouvé pour la date {log_date_str} et le motif '{effective_pattern}' après {effective_timeout} secondes.")
        raise TimeoutException(f"Téléchargement non détecté ou anormalement long pour la date {log_date_str} (motif: {effective_pattern})")

    # --- Méthodes d'aide Selenium ---
    def _find_element(self, locator: str, locator_type: str = 'xpath'):
        """Trouve un élément sans attendre explicitement (pour vérification ou usage interne)."""
        by_type = self._get_by_type(locator_type)
        return self.browser.find_element(by_type, locator)

    def wait_and_click(self, locator: str, locator_type: str = 'xpath', timeout: int = 60, raise_error: bool = True, is_element: bool = False):
        """Attend qu'un élément soit cliquable, puis clique dessus."""
        by_type = self._get_by_type(locator_type)
        self.logger.debug(f"Attente (max {timeout}s) et clic sur l'élément: [{by_type}: {locator}]")
        try:
            if is_element:
                locator.click()
            else:
                element = WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((by_type, locator)))
                element.click()
                self.logger.debug(f"Clic effectué sur [{by_type}: {locator}]")
                return element
        except TimeoutException:
            msg = f"Timeout: Élément non cliquable après {timeout}s: [{by_type}: {locator}]"
            self.logger.error(msg)
            if raise_error: raise TimeoutException(msg)
        except ElementClickInterceptedException:
            self.logger.warning(f"Clic intercepté sur [{by_type}: {locator}]. Tentative de clic via JavaScript.")
            try:
                # Utiliser JavaScript pour forcer le clic
                self.browser.execute_script("arguments[0].click();", element)
                self.logger.debug(f"Clic effectué via JavaScript sur [{by_type}: {locator}]")
                return element
            except Exception as js_e:
                msg = f"Échec du clic via JavaScript sur [{by_type}: {locator}]: {js_e}"
                self.logger.error(msg, exc_info=True)
                if raise_error: raise
        except ElementNotInteractableException:
            msg = f"Erreur: Élément trouvé mais non interactable (pas cliquable): [{by_type}: {locator}]"
            self.logger.error(msg)
            if raise_error: raise ElementNotInteractableException(msg)
        except NoSuchElementException:
            msg = f"Erreur: Élément introuvable: [{by_type}: {locator}]"
            self.logger.error(msg)
            if raise_error: raise NoSuchElementException(msg)
        except Exception as e:
             msg = f"Erreur inattendue lors du clic sur [{by_type}: {locator}]: {e}"
             self.logger.error(msg, exc_info=True)
             if raise_error: raise

    def wait_for_clickable(self, locator: str, locator_type: str = 'xpath', timeout: int = 60, raise_error: bool = True):
        """Attend qu'un élément soit cliquable et le retourne (sans cliquer)."""
        by_type = self._get_by_type(locator_type)
        self.logger.debug(f"Attente (max {timeout}s) de cliquabilité de l'élément: [{by_type}: {locator}]")
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.element_to_be_clickable((by_type, locator))
            )
            self.logger.debug(f"Élément [{by_type}: {locator}] est cliquable.")
            return element
        except TimeoutException:
            msg = f"Timeout: Élément non cliquable après {timeout}s: [{by_type}: {locator}]"
            self.logger.warning(msg)
            if raise_error: raise TimeoutException(msg)
            return None

    def wait_for_presence(self, locator: str, locator_type: str = 'xpath', timeout: int = 60, raise_error: bool = True):
        """Attend qu'un élément soit présent dans le DOM."""
        by_type = self._get_by_type(locator_type)
        self.logger.debug(f"Attente (max {timeout}s) de présence de l'élément: [{by_type}: {locator}]")
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((by_type, locator))
            )
            self.logger.debug(f"Élément [{by_type}: {locator}] est présent.")
            return element
        except TimeoutException:
            msg = f"Timeout: Élément non présent après {timeout}s: [{by_type}: {locator}]"
            self.logger.warning(msg)
            if raise_error: raise TimeoutException(msg)
            return None

    def wait_for_visibility(self, locator: str, locator_type: str = 'xpath', timeout: int = 60, raise_error: bool = True):
        """Attend qu'un élément soit présent et visible."""
        by_type = self._get_by_type(locator_type)
        self.logger.debug(f"Attente (max {timeout}s) de visibilité de l'élément: [{by_type}: {locator}]")
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.visibility_of_element_located((by_type, locator))
            )
            self.logger.debug(f"Élément [{by_type}: {locator}] est visible.")
            return element
        except TimeoutException:
            msg = f"Timeout: Élément non visible après {timeout}s: [{by_type}: {locator}]"
            self.logger.warning(msg)
            if raise_error: raise TimeoutException(msg)
            return None

    def wait_for_invisibility(self, locator: str, locator_type: str = 'xpath', timeout: int = 60, raise_error: bool = True):
        """Attend qu'un élément devienne invisible ou disparaisse du DOM."""
        by_type = self._get_by_type(locator_type)
        self.logger.debug(f"Attente (max {timeout}s) d'invisibilité de l'élément: [{by_type}: {locator}]")
        try:
            WebDriverWait(self.browser, timeout).until(
                EC.invisibility_of_element_located((by_type, locator))
            )
            self.logger.debug(f"Élément [{by_type}: {locator}] est devenu invisible.")
            return True
        except TimeoutException:
            msg = f"Timeout: Élément toujours visible/présent après {timeout}s: [{by_type}: {locator}]"
            self.logger.warning(msg)
            if raise_error: raise TimeoutException(msg)
            return False

    def wait_and_send_keys(self, locator: str, keys: str, locator_type: str = 'id', timeout: int = 60, clear_first: bool = True, raise_error: bool = True):
        """Attend qu'un champ soit cliquable, le vide (optionnel) et y envoie du texte."""
        by_type = self._get_by_type(locator_type)
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.element_to_be_clickable((by_type, locator))
            )
            if clear_first:
                element.clear()
                self.logger.debug(f"Champ [{by_type}: {locator}] vidé.")
            element.send_keys(keys)
            self.logger.debug(f"Texte envoyé à [{by_type}: {locator}]")
            return element
        except TimeoutException:
            msg = f"Timeout: Champ non cliquable/modifiable après {timeout}s: [{by_type}: {locator}]"
            self.logger.error(msg)
            if raise_error: raise TimeoutException(msg)
        except ElementNotInteractableException:
             msg = f"Erreur: Élément trouvé mais non interactable (pas modifiable): [{by_type}: {locator}]"
             self.logger.error(msg)
             if raise_error: raise ElementNotInteractableException(msg)
        except Exception as e:
             msg = f"Erreur inattendue lors de l'envoi de texte vers [{by_type}: {locator}]: {e}"
             self.logger.error(msg, exc_info=True)
             if raise_error: raise

    def fill_select_by_visible_text(self, locator: str, text_value: str, locator_type: str = 'id', timeout: int = 10, raise_error: bool = True):
        """Sélectionne une option dans un élément <select> par son texte visible."""
        by_type = self._get_by_type(locator_type)
        try:
            # Attend que l'élément select soit présent avant d'essayer de le trouver
            select_element = self.wait_for_presence(locator, locator_type, timeout, raise_error=True) # Leve une erreur si non trouvé
            select = Select(select_element)
            select.select_by_visible_text(str(text_value))
            self.logger.debug(f"Option '{text_value}' sélectionnée avec succès.")
            return select_element
        except TimeoutException:
             if not raise_error: self.logger.error(f"Timeout: Élément select introuvable [{by_type}: {locator}]")
        except NoSuchElementException as e_opt:
            msg = f"Erreur: Option '{text_value}' non trouvée dans le select [{by_type}: {locator}]"
            self.logger.error(msg)
            if raise_error: raise NoSuchElementException(msg) from e_opt
        except UnexpectedTagNameException:
            msg = f"Erreur: L'élément trouvé n'est pas un <select>: [{by_type}: {locator}]"
            self.logger.error(msg)
            if raise_error: raise UnexpectedTagNameException(msg)
        except Exception as e:
             msg = f"Erreur inattendue lors de la sélection dans [{by_type}: {locator}]: {e}"
             self.logger.error(msg, exc_info=True)
             if raise_error: raise