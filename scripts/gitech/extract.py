from datetime import date, timedelta # Pour le typage et timedelta
import time # Pour sleep

from base.web_scrapper import BaseScrapper, ElementInteractionError
# Imports Selenium spécifiques (By, Keys, WebDriverWait, EC, Select) et utils non nécessaires directement ici

JOB_NAME = "gitech"

class ExtractGitech(BaseScrapper):
    """
    Scraper pour extraire les rapports "Etat de la course" de la plateforme Gitech (PMU Online).
    """
    def __init__(self, env_vars_mapping: dict):
        # Pas d'options Chrome spécifiques pour ce scraper a priori.
        super().__init__(
            name=JOB_NAME,
            env_variables_list=env_vars_mapping,
            log_file_path=f"logs/extract_{JOB_NAME}.log"
        )

    def _connection_to_platform(self):
        """Gère la connexion à la plateforme Gitech."""
        self.logger.info(f"Connexion à la plateforme {self.name}...")
        login_url = self.config.get('urls', {}).get('login')
        if not login_url:
            raise ValueError(f"URL de login pour {self.name} manquante.")
        self.browser.get(login_url)

        html_elements = self.config.get('html_elements', {})
        username = self.secret_config.get("GITECH_LOGIN_USERNAME")
        password = self.secret_config.get("GITECH_LOGIN_PASSWORD")

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
            # Les WebDriverWait directs sont remplacés par les méthodes de BaseScrapper.
            # Les timeouts excessifs sont réduits.
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

        # L'ancien sleep(10) est long, réduit et rendu configurable si besoin.
        time.sleep(self.job_config.get("delay_after_login_sec", 5))


    def _download_files(self):
        """Navigue vers la page de rapport et lance le processus de téléchargement jour par jour."""
        self.logger.info(f"Navigation vers la page des rapports pour {self.name}...")
        reports_url = self.config.get('urls', {}).get('report')
        if not reports_url:
            raise ValueError(f"URL des rapports pour {self.name} manquante.")
        self.browser.get(reports_url)
        time.sleep(self.job_config.get("delay_after_page_load_sec", 2))

        self.logger.info(f"Lancement du téléchargement des rapports pour la plage de dates ({self.name}).")
        self._process_multiple_files_by_date(rename_downloaded_file=True)


    def _process_download_for_date_range(self, start_date_to_process: date, end_date_to_process: date):
        """
        Remplit les listes déroulantes de date, soumet et télécharge pour un jour donné.
        start_date_to_process et end_date_to_process seront identiques.
        """
        date_obj = start_date_to_process
        day_str = date_obj.strftime("%d").lstrip('0')
        month_str = date_obj.strftime("%m").lstrip('0')
        year_str = date_obj.strftime("%Y")

        self.logger.info(f"Préparation du téléchargement pour la date: {date_obj.strftime('%Y-%m-%d')} ({self.name}).")

        html_elements = self.config.get('html_elements', {})
        start_day_id = html_elements.get("start_date_day_element_id")
        start_month_id = html_elements.get("start_date_month_element_id")
        start_year_id = html_elements.get("start_date_year_element_id")
        end_day_id = html_elements.get("end_date_day_element_id")
        end_month_id = html_elements.get("end_date_month_element_id")
        end_year_id = html_elements.get("end_date_year_element_id")
        submit_button_id = html_elements.get("submit_button_element_id")
        download_button_id = html_elements.get("download_button_element_id")
        error_message_xpath = html_elements.get("error_message_element_xpath")

        if not all([start_day_id, start_month_id, start_year_id, end_day_id, end_month_id, end_year_id,
                    submit_button_id, download_button_id, error_message_xpath]):
            raise ValueError(f"Configuration HTML incomplète pour le formulaire de date/téléchargement ({self.name}).")

        try:
            time.sleep(self.job_config.get("delay_before_date_fill_sec", 2)) # Pause avant de remplir

            self.logger.info(f"Sélection de la date de début: {day_str}/{month_str}/{year_str}")
            self._fill_select_by_visible_text(start_day_id, text_to_select=day_str, locator_type='id')
            self._fill_select_by_visible_text(start_month_id, text_to_select=month_str, locator_type='id')
            self._fill_select_by_visible_text(start_year_id, text_to_select=year_str, locator_type='id')

            self.logger.info(f"Sélection de la date de fin: {day_str}/{month_str}/{year_str}")
            self._fill_select_by_visible_text(end_day_id, text_to_select=day_str, locator_type='id')
            self._fill_select_by_visible_text(end_month_id, text_to_select=month_str, locator_type='id')
            self._fill_select_by_visible_text(end_year_id, text_to_select=year_str, locator_type='id')
            time.sleep(1)

            self.logger.info("Soumission du formulaire de date...")
            self._wait_and_click(submit_button_id, locator_type='id', timeout=15)

            time.sleep(self.job_config.get("delay_after_submit_sec", 5)) # Laisser le temps au message d'erreur/résultat de s'afficher
            error_element = self._wait_for_element_presence(error_message_xpath, locator_type='xpath', timeout=5, raise_error=False)

            if error_element and error_element.is_displayed():
                self.logger.warning(f"Aucun enregistrement trouvé pour la date {date_obj.strftime('%Y-%m-%d')} sur {self.name}. Fichier non téléchargé.")
                # L'ancien code appelait self._quit(). Ici, on retourne pour que _process_multiple_files_by_date continue.
                # Si c'est une erreur fatale pour tout le processus, il faudrait lever une exception.
                return

            self.logger.info(f"Clic sur le bouton de téléchargement pour la date {date_obj.strftime('%Y-%m-%d')}...")
            self._wait_and_click(download_button_id, locator_type='id', timeout=30)

        except ElementInteractionError as e:
            self.logger.error(f"Échec interaction Selenium pour {date_obj.strftime('%Y-%m-%d')} ({self.name}): {e}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue pour {date_obj.strftime('%Y-%m-%d')} ({self.name}): {e}", exc_info=True)
            raise


def run_gitech_extraction(): # Nom de fonction mis à jour
    """Fonction principale pour lancer l'extraction Gitech."""
    env_mapping = {
        "GITECH_LOGIN_USERNAME": "GITECH_LOGIN_USERNAME",
        "GITECH_LOGIN_PASSWORD": "GITECH_LOGIN_PASSWORD"
    }
    scraper_job = None
    try:
        scraper_job = ExtractGitech(env_vars_mapping=env_mapping)
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
    run_gitech_extraction() # Nom de fonction mis à jour
