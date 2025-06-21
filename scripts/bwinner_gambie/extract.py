from datetime import date, timedelta # timedelta utilisé, date pour typage
import time # Pour sleep

from base.web_scrapper import BaseScrapper, ElementInteractionError
# Imports Selenium spécifiques (By, Keys, WebDriverWait, EC, Select) plus nécessaires directement ici
# Imports utils (get_config, get_secret, get_yesterday_date, rename_file, move_file, loading) plus nécessaires ici

JOB_NAME = "bwinner_gambie"

class ExtractBwinnerGambie(BaseScrapper):
    """
    Scraper pour extraire les rapports "Recette paiement Journalier" de la plateforme Bwinner Gambie.
    """
    def __init__(self, env_vars_mapping: dict):
        # L'option Chrome pour origine non sécurisée est spécifique et potentiellement risquée.
        # À conserver si absolument nécessaire et bien documenté.
        # Elle pourrait être rendue configurable via config.yml si besoin.
        chrome_options_args = [
            "--unsafely-treat-insecure-origin-as-secure=http://115.110.148.83/bwinnersmis/Administration/"
        ]
        super().__init__(
            name=JOB_NAME,
            env_variables_list=env_vars_mapping,
            log_file_path=f"logs/extract_{JOB_NAME}.log",
            chrome_options_arguments=chrome_options_args
        )

    def _connection_to_platform(self):
        """Gère la connexion à la plateforme Bwinner Gambie."""
        self.logger.info(f"Connexion à la plateforme {self.name}...")
        login_url = self.config.get('urls', {}).get('login')
        if not login_url:
            raise ValueError(f"URL de login pour {self.name} manquante.")
        self.browser.get(login_url)

        html_elements = self.config.get('html_elements', {})
        username = self.secret_config.get("BWINNER_GAMBIE_LOGIN_USERNAME")
        password = self.secret_config.get("BWINNER_GAMBIE_LOGIN_PASSWORD")

        if not (username and password):
            raise ValueError(f"Identifiants (username/password) pour {self.name} manquants.")

        username_id = html_elements.get("username_element_id")
        password_id = html_elements.get("password_element_id")
        submit_id = html_elements.get("login_submit_button_element_id")
        verification_xpath = html_elements.get("verification_xpath")

        if not (username_id and password_id and submit_id and verification_xpath):
            raise ValueError(f"Configuration des éléments HTML de login incomplète pour {self.name}.")

        try:
            self.logger.info("Saisie des identifiants...")
            self._wait_and_send_keys(username_id, locator_type='id', keys_to_send=username, timeout=30)
            self._wait_and_send_keys(password_id, locator_type='id', keys_to_send=password, timeout=30)

            self.logger.info("Soumission du formulaire de connexion...")
            self._wait_and_click(submit_id, locator_type='id', timeout=30)

            self.logger.info("Vérification de la connexion...")
            self._wait_for_element_presence(verification_xpath, locator_type='xpath', timeout=60)
            self.logger.info(f"Connexion à la plateforme {self.name} réussie.")

        except ElementInteractionError as e:
            self.logger.error(f"Échec de l'interaction Selenium lors de la connexion à {self.name}: {e}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la connexion à {self.name}: {e}", exc_info=True)
            raise

        time.sleep(self.job_config.get("delay_after_login_sec", 2)) # Pause après login


    def _download_files(self):
        """Navigue vers la page de rapport et lance le processus de téléchargement jour par jour."""
        self.logger.info(f"Navigation vers la page des rapports pour {self.name}...")
        reports_url = self.config.get('urls', {}).get('report')
        if not reports_url:
            raise ValueError(f"URL des rapports pour {self.name} manquante.")
        self.browser.get(reports_url)
        time.sleep(self.job_config.get("delay_after_page_load_sec", 2)) # Laisser la page charger

        # Utilise la méthode de BaseScrapper pour itérer sur les dates
        self.logger.info(f"Lancement du téléchargement des rapports pour la plage de dates ({self.name}).")
        self._process_multiple_files_by_date(rename_downloaded_file=True)


    def _process_download_for_date_range(self, start_date_to_process: date, end_date_to_process: date):
        """
        Remplit les listes déroulantes de date, soumet le formulaire et télécharge le rapport pour un jour donné.
        Pour ce scraper, start_date_to_process et end_date_to_process seront identiques (traitement jour par jour).
        """
        date_obj = start_date_to_process # On traite un seul jour à la fois
        day_str = date_obj.strftime("%d").lstrip('0') # Jour sans zéro initial (ex: '1' au lieu de '01')
        month_str = date_obj.strftime("%m").lstrip('0') # Mois sans zéro initial
        year_str = date_obj.strftime("%Y")

        self.logger.info(f"Préparation du téléchargement du rapport pour la date: {date_obj.strftime('%Y-%m-%d')} ({self.name}).")

        html_elements = self.config.get('html_elements', {})
        # IDs des listes déroulantes pour la date de début
        start_day_id = html_elements.get("start_date_day_element_id")
        start_month_id = html_elements.get("start_date_month_element_id")
        start_year_id = html_elements.get("start_date_year_element_id")
        # IDs des listes déroulantes pour la date de fin
        end_day_id = html_elements.get("end_date_day_element_id")
        end_month_id = html_elements.get("end_date_month_element_id")
        end_year_id = html_elements.get("end_date_year_element_id")

        submit_button_id = html_elements.get("submit_button_element_id")
        download_button_id = html_elements.get("download_button_element_id")
        error_message_xpath = html_elements.get("error_message_element_xpath")

        if not all([start_day_id, start_month_id, start_year_id, end_day_id, end_month_id, end_year_id, submit_button_id, download_button_id, error_message_xpath]):
            raise ValueError(f"Configuration des éléments HTML pour le formulaire de date/téléchargement incomplète ({self.name}).")

        try:
            self.logger.info(f"Sélection de la date de début: {day_str}/{month_str}/{year_str}")
            self._fill_select_by_visible_text(start_day_id, text_to_select=day_str, locator_type='id')
            self._fill_select_by_visible_text(start_month_id, text_to_select=month_str, locator_type='id')
            self._fill_select_by_visible_text(start_year_id, text_to_select=year_str, locator_type='id')

            self.logger.info(f"Sélection de la date de fin: {day_str}/{month_str}/{year_str}")
            self._fill_select_by_visible_text(end_day_id, text_to_select=day_str, locator_type='id')
            self._fill_select_by_visible_text(end_month_id, text_to_select=month_str, locator_type='id')
            self._fill_select_by_visible_text(end_year_id, text_to_select=year_str, locator_type='id')
            time.sleep(1) # Pause après sélection des dates

            self.logger.info("Soumission du formulaire de date...")
            self._wait_and_click(submit_button_id, locator_type='id', timeout=15)

            # Vérifier s'il y a un message d'erreur "Aucun enregistrement trouvé"
            # Attendre un court instant pour que le message apparaisse s'il y en a un.
            # Si le message est trouvé, c'est une erreur pour cette date (pas de données).
            # La méthode _wait_for_element_presence lèvera une exception si raise_error=True (par défaut).
            # Ici, on veut vérifier sa présence SANS lever d'erreur si absent.
            time.sleep(self.job_config.get("delay_after_submit_sec", 3)) # Laisser le temps au message d'erreur de s'afficher
            error_element = self._wait_for_element_presence(error_message_xpath, locator_type='xpath', timeout=5, raise_error=False)
            if error_element and error_element.is_displayed():
                self.logger.warning(f"Aucun enregistrement trouvé pour la date {date_obj.strftime('%Y-%m-%d')} sur {self.name}. Fichier non téléchargé pour cette date.")
                return # Pas de fichier à télécharger pour cette date

            self.logger.info(f"Clic sur le bouton de téléchargement pour la date {date_obj.strftime('%Y-%m-%d')}...")
            self._wait_and_click(download_button_id, locator_type='id', timeout=30)
            # Le téléchargement est initié. _verify_and_rename_download sera appelé par _process_multiple_files_by_date.

        except ElementInteractionError as e:
            self.logger.error(f"Échec de l'interaction Selenium lors du processus de téléchargement pour {date_obj.strftime('%Y-%m-%d')} ({self.name}): {e}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors du processus de téléchargement pour {date_obj.strftime('%Y-%m-%d')} ({self.name}): {e}", exc_info=True)
            raise


def run_bwinner_gambie_extraction(): # Nom de fonction mis à jour
    """Fonction principale pour lancer l'extraction Bwinner Gambie."""
    env_mapping = {
        "BWINNER_GAMBIE_LOGIN_USERNAME": "BWINNER_GAMBIE_LOGIN_USERNAME",
        "BWINNER_GAMBIE_LOGIN_PASSWORD": "BWINNER_GAMBIE_LOGIN_PASSWORD"
    }
    scraper_job = None
    try:
        scraper_job = ExtractBwinnerGambie(env_vars_mapping=env_mapping)
        scraper_job.process_extraction()
    except (ValueError, ElementInteractionError, ConnectionError) as e:
        log_msg = f"Échec critique du job d'extraction {JOB_NAME}: {e}"
        if scraper_job and scraper_job.logger: scraper_job.logger.critical(log_msg, exc_info=True)
        else: print(f"ERREUR CRITIQUE (logger non dispo) pour {JOB_NAME}: {log_msg}")
    except Exception as e:
        log_msg = f"Erreur inattendue et non gérée dans le job {JOB_NAME}: {e}"
        if scraper_job and scraper_job.logger: scraper_job.logger.critical(log_msg, exc_info=True)
        else: print(f"ERREUR INATTENDUE CRITIQUE (logger non dispo) pour {JOB_NAME}: {log_msg}")

if __name__ == "__main__":
    from load_env import load_env
    load_env()
    run_bwinner_gambie_extraction() # Nom de fonction mis à jour
