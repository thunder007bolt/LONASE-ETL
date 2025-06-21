from datetime import date, timedelta, datetime # Ajout de date, datetime
import calendar # Non utilisé ici mais gardé de l'autre extract Afitech pour référence
import time # Pour les pauses
import pyotp

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# WebDriverWait, Select, EC ne sont plus directement utilisés ici, gérés par BaseScrapper
# from selenium.common.exceptions import StaleElementReferenceException # Non utilisé, peut être enlevé

from base.web_scrapper import BaseScrapper, ElementInteractionError
# `get_yesterday_date` est dans BaseScrapper._set_dates()
# `sleep` est dans time, importé dans BaseScrapper si besoin.
# `move_file`, `loading`, `retry_operation`, `rename_file` sont gérés par BaseScrapper ou ne sont plus nécessaires ici.
# `StaleElementReferenceException` peut être gérée par les attentes explicites ou les retries de BaseScrapper.

JOB_NAME = "afitech_daily_payment_activity"

class ExtractAfitechDailyPaymentActivity(BaseScrapper):
    """
    Scraper pour extraire les rapports "Daily Payment Activity" d'Afitech.
    Ce scraper génère des rapports pour chaque jour de la plage configurée,
    puis les télécharge depuis la page d'historique.
    """
    def __init__(self, env_vars_mapping: dict):
        super().__init__(
            name=JOB_NAME,
            env_variables_list=env_vars_mapping,
            log_file_path=f"logs/extract_{JOB_NAME}.log"
        )
        self.generated_reports_to_download: list[dict] = [] # Infos des rapports générés

    def _connection_to_platform(self):
        """Gère la connexion à la plateforme Afitech, y compris la MFA."""
        # Cette méthode est identique à celle de ExtractAfitechCommissionHistory.
        # On pourrait envisager une classe de base commune pour les scrapers Afitech si la duplication augmente.
        self.logger.info("Connexion à la plateforme Afitech...")
        login_url = self.config.get('urls', {}).get('login')
        if not login_url:
            raise ValueError("URL de login Afitech manquante.")
        self.browser.get(login_url)

        html_elements = self.config.get('html_elements', {})
        username = self.secret_config.get("AFITECH_LOGIN_USERNAME")
        password = self.secret_config.get("AFITECH_LOGIN_PASSWORD")
        otp_secret_key = self.secret_config.get("AFITECH_GET_OTP_URL") # Doit être la clé secrète TOTP

        if not (username and password and otp_secret_key):
            raise ValueError("Identifiants Afitech (username, password, OTP secret key) manquants.")

        try:
            self._wait_and_send_keys(html_elements["username_element_xpath"], keys_to_send=username)
            self._wait_and_send_keys(html_elements["password_element_xpath"], keys_to_send=password)
            self._wait_and_click(html_elements["login_submit_button_element_xpath"])

            self._wait_for_element_presence(html_elements["verification_xpath"], timeout=15) # Page MFA
            self.logger.info("Page MFA atteinte.")

            self._wait_and_click(html_elements["dropdown_element_xpath"])
            self._wait_and_click(html_elements["google_authentication_element_xpath"])

            totp = pyotp.TOTP(otp_secret_key)
            otp_code = totp.now()
            self.logger.info(f"Code OTP généré.") # Ne pas logger le code
            self._wait_and_send_keys(html_elements["code_input_element_xpath"], keys_to_send=otp_code)

            self._wait_for_element_presence(html_elements["report_verification_xpath"], timeout=60)
            self.logger.info("Connexion et authentification MFA à Afitech réussies.")
        except ElementInteractionError as e:
            self.logger.error(f"Échec de l'interaction Selenium lors de la connexion/MFA: {e}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la connexion/MFA: {e}", exc_info=True)
            raise

    def _generate_daily_reports(self):
        """Génère les rapports "Daily Payment Activity" pour chaque jour de la plage."""
        self.logger.info(f"Début de la génération des rapports quotidiens de {self.start_date.strftime('%Y-%m-%d')} à {self.end_date.strftime('%Y-%m-%d')}.")

        current_processing_date = self.start_date
        delta_one_day = timedelta(days=1)

        html_elements = self.config.get('html_elements', {})
        reports_creation_url = self.config.get('urls', {}).get('report')

        while current_processing_date <= self.end_date:
            date_str_for_report = current_processing_date.strftime('%d/%m/%Y')
            self.logger.info(f"Génération du rapport DailyPaymentActivity pour : {date_str_for_report}.")

            self.browser.get(reports_creation_url) # Recharger la page de création pour chaque rapport

            try:
                self._wait_and_click(html_elements["report_dropdown_xpath"])
                self._wait_and_click(html_elements["report_type_xpath"]) # XPath pour "Daily Payment Activity"

                self._wait_and_send_keys(html_elements["start_calendar_input_xpath"], keys_to_send=date_str_for_report)
                self.browser.find_element(By.XPATH, html_elements["start_calendar_input_xpath"]).send_keys(Keys.ENTER)

                self._wait_and_send_keys(html_elements["end_calendar_input_xpath"], keys_to_send=date_str_for_report)
                self.browser.find_element(By.XPATH, html_elements["end_calendar_input_xpath"]).send_keys(Keys.ENTER)

                self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                time.sleep(0.5)
                self._wait_and_click(html_elements["report_submit_button_xpath"])

                success_notification_xpath = "//div[contains(text(),'Report created successfully')]"
                self._wait_for_element_presence(success_notification_xpath, timeout=html_elements.get("report_creation_timeout_sec", 180))

                self.generated_reports_to_download.append({
                    "report_date_obj": current_processing_date,
                    "report_date_str": date_str_for_report, # DD/MM/YYYY pour comparaison
                    "downloaded": False
                })
                self.logger.info(f"Rapport DailyPaymentActivity pour {date_str_for_report} généré et mis en file d'attente.")
            except ElementInteractionError as e:
                self.logger.error(f"Échec lors de la génération du rapport pour {date_str_for_report}: {e}", exc_info=True)
            except Exception as e:
                 self.logger.error(f"Erreur inattendue lors de la génération pour {date_str_for_report}: {e}", exc_info=True)

            current_processing_date += delta_one_day
            # La pause de 15s de l'ancien code (_generate_files) est déplacée ici.
            time.sleep(self.job_config.get("delay_between_report_generation_sec", 15))

    def _download_generated_daily_reports_from_history(self):
        """Télécharge les rapports Daily Payment Activity générés depuis l'historique."""
        if not self.generated_reports_to_download:
            self.logger.info("Aucun rapport DailyPaymentActivity généré à télécharger.")
            return

        self.logger.info("Début du téléchargement des rapports DailyPaymentActivity depuis l'historique.")
        history_url = self.config.get('urls', {}).get('report_history')
        html_elements = self.config.get('html_elements', {})

        max_check_attempts = self.job_config.get("history_check_max_attempts", 10)
        delay_between_checks_sec = self.job_config.get("history_check_delay_sec", 60)

        for attempt in range(max_check_attempts):
            if not any(not rpt["downloaded"] for rpt in self.generated_reports_to_download):
                self.logger.info("Tous les rapports DailyPaymentActivity générés ont été téléchargés.")
                break

            self.logger.info(f"Tentative {attempt + 1}/{max_check_attempts} de vérification/téléchargement (DailyPaymentActivity).")
            self.browser.get(history_url)
            time.sleep(5) # Laisser la page charger

            try:
                load_more_button_xpath = "/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div[3]/div/p-tabview/div/div[2]/p-tabpanel[1]/div/hg-load-more/div/hg-button/button"
                for _ in range(self.job_config.get("history_load_more_clicks", 6)):
                    try:
                        self._wait_and_click(load_more_button_xpath, timeout=10)
                        time.sleep(2)
                    except ElementInteractionError:
                        self.logger.debug("'Load More' non trouvé ou plus cliquable.")
                        break

                table_rows = self.browser.find_elements(By.XPATH, html_elements["table_row_xpath"])
                if not table_rows: self.logger.warning("Aucune ligne dans l'historique des rapports.")

                for row_element in table_rows:
                    try:
                        cols = row_element.find_elements(By.TAG_NAME, "td")
                        if len(cols) < 5: continue

                        report_name_on_page = cols[1].text
                        date1_on_page = cols[2].text
                        date2_on_page = cols[3].text
                        status_on_page = cols[4].text.lower()

                        for report_info in self.generated_reports_to_download:
                            if report_info["downloaded"]: continue

                            if (report_info["report_date_str"] == date1_on_page and
                                report_info["report_date_str"] == date2_on_page and
                                "dailypaymentactivity" in report_name_on_page.lower()):

                                if "available" in status_on_page:
                                    self.logger.info(f"Rapport DailyPaymentActivity pour {date1_on_page} disponible. Téléchargement...")
                                    download_button = row_element.find_element(By.XPATH, html_elements["download_button_xpath"])
                                    download_button.click()

                                    downloaded_file = self._verify_and_rename_download(
                                        date_for_filename=report_info["report_date_obj"],
                                        file_pattern_to_wait_for=self.config['file_pattern']
                                    )
                                    if downloaded_file:
                                        self.logger.info(f"Rapport pour {date1_on_page} téléchargé et renommé: {downloaded_file.name}")
                                        report_info["downloaded"] = True
                                    else:
                                        self.logger.error(f"Échec vérification/renommage pour {date1_on_page}.")
                                    time.sleep(self.job_config.get("delay_after_download_click_sec", 10))
                                    break
                                elif status_on_page in ["incomplete", "queued", "in progress"]:
                                    self.logger.info(f"Rapport DailyPaymentActivity pour {date1_on_page} toujours en cours: '{status_on_page}'.")
                                else:
                                    self.logger.warning(f"Statut inattendu '{status_on_page}' pour rapport {date1_on_page}.")
                    except Exception as e_row:
                        self.logger.warning(f"Erreur traitement ligne historique: {e_row}.", exc_info=False)
                        break
            except Exception as e_hist:
                self.logger.error(f"Erreur page historique: {e_hist}", exc_info=True)

            if attempt < max_check_attempts - 1 and any(not rpt["downloaded"] for rpt in self.generated_reports_to_download):
                self.logger.info(f"Attente de {delay_between_checks_sec}s avant prochaine vérification (DailyPaymentActivity).")
                time.sleep(delay_between_checks_sec)

        not_downloaded = [r for r in self.generated_reports_to_download if not r["downloaded"]]
        if not_downloaded:
            self.logger.warning(f"{len(not_downloaded)} rapport(s) DailyPaymentActivity non téléchargé(s):")
            for rpt_info in not_downloaded: self.logger.warning(f"  - Date: {rpt_info['report_date_str']}")

    def _download_files(self): # Surcharge la méthode de BaseScrapper
        """Orchestre la génération puis le téléchargement des rapports DailyPaymentActivity."""
        self._generate_daily_reports() # Étape 1: Générer tous les rapports pour la plage de dates
        if self.generated_reports_to_download: # Étape 2: Télécharger ceux qui ont été générés
            self._download_generated_daily_reports_from_history()
        else:
            self.logger.info("Aucun rapport DailyPaymentActivity généré, aucun téléchargement.")

    def _process_download_for_date_range(self, start_date_to_process: date, end_date_to_process: date):
        # Non utilisé directement par le flux principal de ce scraper car _download_files est surchargé.
        self.logger.warning("_process_download_for_date_range non implémenté pour le flux principal de ExtractAfitechDailyPaymentActivity.")
        pass

def run_afitech_daily_payment_activity_extraction(): # Renommé pour clarté
    """Fonction principale pour lancer l'extraction Afitech Daily Payment Activity."""
    env_mapping = {
        "AFITECH_LOGIN_USERNAME": "AFITECH_LOGIN_USERNAME",
        "AFITECH_LOGIN_PASSWORD": "AFITECH_LOGIN_PASSWORD",
        "AFITECH_GET_OTP_URL": "AFITECH_GET_OTP_URL" # Assumer que c'est la clé secrète TOTP
    }
    scraper_job = None
    try:
        scraper_job = ExtractAfitechDailyPaymentActivity(env_vars_mapping=env_mapping)
        scraper_job.process_extraction() # Méthode de BaseScrapper qui appelle _set_dates, _open_browser, _connection_to_platform, _download_files, _quit_browser
    except (ValueError, ElementInteractionError, ConnectionError) as e: # Erreurs attendues
        log_msg = f"Échec critique du job {JOB_NAME}: {e}"
        if scraper_job and scraper_job.logger: scraper_job.logger.critical(log_msg, exc_info=True)
        else: print(f"ERREUR CRITIQUE (logger non dispo) pour {JOB_NAME}: {log_msg}")
    except Exception as e: # Autres erreurs inattendues
        log_msg = f"Erreur inattendue job {JOB_NAME}: {e}"
        if scraper_job and scraper_job.logger: scraper_job.logger.critical(log_msg, exc_info=True)
        else: print(f"ERREUR INATTENDUE CRITIQUE (logger non dispo) pour {JOB_NAME}: {log_msg}")
    # finally: # _quit_browser est déjà dans le finally de BaseScrapper.process_extraction()

if __name__ == "__main__":
    from load_env import load_env # Nécessaire si exécuté directement et .env utilisé
    load_env()
    run_afitech_daily_payment_activity_extraction() # Nom de fonction mis à jour
