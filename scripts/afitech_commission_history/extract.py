from datetime import date, timedelta, datetime # datetime importé pour calendar.monthrange et strptime
import calendar # Pour obtenir le dernier jour du mois
import time # Pour les pauses
import pyotp # Pour la génération de code OTP

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# WebDriverWait, Select, EC ne sont plus directement utilisés ici, gérés par BaseScrapper
# from selenium.common.exceptions import StaleElementReferenceException # Non utilisé, peut être enlevé

from base.web_scrapper import BaseScrapper, ElementInteractionError # Importer l'exception
# Les utilitaires (config, date, file_manipulation, other_utils) sont utilisés via BaseScrapper ou ne sont plus nécessaires ici.

JOB_NAME = "afitech_commission_history"

class ExtractAfitechCommissionHistory(BaseScrapper):
    """
    Scraper pour extraire les rapports "Commission History" de la plateforme Afitech.
    Ce scraper a une logique complexe :
    1. Il génère des rapports pour chaque mois dans la plage de dates configurée.
    2. Ensuite, il va sur la page d'historique des rapports pour télécharger ceux qui sont prêts.
    """
    def __init__(self, env_vars_mapping: dict):
        super().__init__(
            name=JOB_NAME,
            env_variables_list=env_vars_mapping,
            log_file_path=f"logs/extract_{JOB_NAME}.log"
            # Pas d'options Chrome spécifiques ici, peuvent être ajoutées si besoin.
        )
        # self.range = False # Cet attribut n'est plus nécessaire avec la nouvelle gestion des dates de BaseScrapper
        self.generated_reports_to_download: list[dict] = [] # Pour stocker les infos des rapports générés

    # La méthode _set_dates de BaseScrapper est utilisée.
    # L'ancienne _set_date personnalisée n'est plus nécessaire.

    def _connection_to_platform(self):
        """Gère la connexion à la plateforme Afitech, y compris la MFA."""
        self.logger.info("Connexion à la plateforme Afitech...")
        login_url = self.config.get('urls', {}).get('login')
        if not login_url:
            raise ValueError("URL de login Afitech manquante dans la configuration.")
        self.browser.get(login_url)

        html_elements = self.config.get('html_elements', {})
        username = self.secret_config.get("AFITECH_LOGIN_USERNAME")
        password = self.secret_config.get("AFITECH_LOGIN_PASSWORD")
        otp_secret_url = self.secret_config.get("AFITECH_GET_OTP_URL")

        if not (username and password and otp_secret_url):
            raise ValueError("Identifiants Afitech (username, password, OTP URL) manquants.")

        try:
            # Saisie des identifiants
            self._wait_and_send_keys(html_elements["username_element_xpath"], keys_to_send=username)
            self._wait_and_send_keys(html_elements["password_element_xpath"], keys_to_send=password)
            self._wait_and_click(html_elements["login_submit_button_element_xpath"])

            # Vérification de la page MFA
            self._wait_for_element_presence(html_elements["verification_xpath"], timeout=15) # Page MFA
            self.logger.info("Page MFA atteinte. Tentative d'authentification Google.")

            # Choix de Google Authenticator et saisie du code OTP
            self._wait_and_click(html_elements["dropdown_element_xpath"])
            self._wait_and_click(html_elements["google_authentication_element_xpath"])

            totp = pyotp.TOTP(otp_secret_url) # pyotp.parse_uri(otp_secret_url).now() est pour les URI otpauth://
                                            # Si otp_secret_url est juste la clé secrète, alors pyotp.TOTP(otp_secret_url).now()
                                            # Il faut clarifier ce que contient AFITECH_GET_OTP_URL.
                                            # On suppose que c'est la clé secrète Base32 pour TOTP.
            otp_code = totp.now()
            self.logger.info(f"Code OTP généré: {otp_code[:3]}...") # Ne pas logger le code complet
            self._wait_and_send_keys(html_elements["code_input_element_xpath"], keys_to_send=otp_code)
            # Le site soumet souvent automatiquement après la saisie du code OTP. Sinon, ajouter un clic.

            # Vérification de la connexion réussie (arrivée sur la page des rapports ou tableau de bord)
            self._wait_for_element_presence(html_elements["report_verification_xpath"], timeout=60)
            self.logger.info("Connexion et authentification MFA à Afitech réussies.")

        except ElementInteractionError as e:
            self.logger.error(f"Échec de l'interaction Selenium lors de la connexion/MFA: {e}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la connexion/MFA: {e}", exc_info=True)
            raise

    def _generate_reports_for_date_range(self):
        """
        Génère les rapports "Commission History" pour chaque mois inclus dans la plage
        self.start_date à self.end_date.
        """
        self.logger.info(f"Début de la génération des rapports de {self.start_date.strftime('%Y-%m-%d')} à {self.end_date.strftime('%Y-%m-%d')}.")

        current_month_start = date(self.start_date.year, self.start_date.month, 1)

        while current_month_start <= self.end_date:
            # Déterminer le premier et le dernier jour du mois actuel
            _, last_day_of_month = calendar.monthrange(current_month_start.year, current_month_start.month)
            month_end_date = date(current_month_start.year, current_month_start.month, last_day_of_month)

            # S'assurer qu'on ne dépasse pas self.end_date pour le dernier mois
            actual_end_for_report = min(month_end_date, self.end_date)
            # S'assurer que start_for_report n'est pas avant self.start_date pour le premier mois
            actual_start_for_report = max(current_month_start, self.start_date)

            # Si le début calculé est après la fin calculée (cas où self.start_date est après la fin du mois partiel)
            if actual_start_for_report > actual_end_for_report:
                self.logger.info(f"Saut du mois {current_month_start.strftime('%Y-%m')} car la plage de dates effective est invalide.")
                # Passer au mois suivant
                if current_month_start.month == 12:
                    current_month_start = date(current_month_start.year + 1, 1, 1)
                else:
                    current_month_start = date(current_month_start.year, current_month_start.month + 1, 1)
                continue

            self.logger.info(f"Génération du rapport pour la période : {actual_start_for_report.strftime('%d/%m/%Y')} au {actual_end_for_report.strftime('%d/%m/%Y')}.")

            html_elements = self.config.get('html_elements', {})
            reports_url = self.config.get('urls', {}).get('report')
            self.browser.get(reports_url)

            try:
                # Sélectionner le type de rapport "Commission History"
                self._wait_and_click(html_elements["report_dropdown_xpath"])
                self._wait_and_click(html_elements["report_type_xpath"]) # XPath pour "Commission History"

                # Remplir les dates
                start_date_str = actual_start_for_report.strftime('%d/%m/%Y')
                end_date_str = actual_end_for_report.strftime('%d/%m/%Y')

                # Utiliser _wait_and_send_keys pour plus de robustesse
                self._wait_and_send_keys(html_elements["start_calendar_input_xpath"], keys_to_send=start_date_str)
                # Peut nécessiter d'envoyer Keys.ENTER ou de cliquer ailleurs pour fermer le calendrier
                self.browser.find_element(By.XPATH, html_elements["start_calendar_input_xpath"]).send_keys(Keys.ENTER)

                self._wait_and_send_keys(html_elements["end_calendar_input_xpath"], keys_to_send=end_date_str)
                self.browser.find_element(By.XPATH, html_elements["end_calendar_input_xpath"]).send_keys(Keys.ENTER)

                # Soumettre la demande de rapport
                # Scroll peut être nécessaire si le bouton n'est pas visible
                self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                time.sleep(0.5) # Petite pause après scroll
                self._wait_and_click(html_elements["report_submit_button_xpath"])

                # Vérifier la notification de succès de création du rapport
                success_notification_xpath = "//div[contains(text(),'Report created successfully')]" # Ajuster si besoin
                self._wait_for_element_presence(success_notification_xpath, timeout=html_elements.get("report_creation_timeout_sec", 180))

                self.generated_reports_to_download.append({
                    "start_date_obj": actual_start_for_report,
                    "end_date_obj": actual_end_for_report,
                    "start_date_str": start_date_str, # Garder pour comparaison avec le texte de la table
                    "end_date_str": end_date_str,
                    "downloaded": False
                })
                self.logger.info(f"Rapport pour {start_date_str} - {end_date_str} généré avec succès et mis en file d'attente pour téléchargement.")

            except ElementInteractionError as e:
                self.logger.error(f"Échec de l'interaction Selenium lors de la génération du rapport pour {start_date_str} - {end_date_str}: {e}", exc_info=True)
                # Continuer avec le mois suivant, mais marquer cette période comme échouée potentiellement.
            except Exception as e:
                 self.logger.error(f"Erreur inattendue lors de la génération du rapport pour {start_date_str} - {end_date_str}: {e}", exc_info=True)

            # Passer au mois suivant
            if current_month_start.month == 12:
                current_month_start = date(current_month_start.year + 1, 1, 1)
            else:
                current_month_start = date(current_month_start.year, current_month_start.month + 1, 1)

            time.sleep(self.job_config.get("delay_between_report_generation_sec", 5)) # Pause entre les générations


    def _download_generated_reports_from_history(self):
        """
        Navigue vers la page d'historique des rapports et télécharge les rapports générés
        qui sont maintenant disponibles.
        """
        if not self.generated_reports_to_download:
            self.logger.info("Aucun rapport n'a été généré ou mis en file d'attente pour téléchargement.")
            return

        self.logger.info("Début du téléchargement des rapports depuis la page d'historique.")
        history_url = self.config.get('urls', {}).get('report_history')
        html_elements = self.config.get('html_elements', {})

        # Nombre de tentatives pour trouver tous les rapports
        max_check_attempts = self.job_config.get("history_check_max_attempts", 5)
        delay_between_checks_sec = self.job_config.get("history_check_delay_sec", 60)

        for attempt in range(max_check_attempts):
            if not any(not rpt["downloaded"] for rpt in self.generated_reports_to_download):
                self.logger.info("Tous les rapports générés ont été téléchargés.")
                break # Sortir si tout est téléchargé

            self.logger.info(f"Tentative {attempt + 1}/{max_check_attempts} de vérification/téléchargement depuis l'historique.")
            self.browser.get(history_url)
            time.sleep(5) # Laisser la page charger

            try:
                # Logique pour cliquer sur "Load More" plusieurs fois si nécessaire.
                # Ceci est fragile. Une meilleure approche serait de vérifier si le bouton "Load More" est présent et cliquable.
                load_more_button_xpath = "/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div[3]/div/p-tabview/div/div[2]/p-tabpanel[1]/div/hg-load-more/div/hg-button/button"
                for _ in range(self.job_config.get("history_load_more_clicks", 4)): # Configurable
                    try:
                        self._wait_and_click(load_more_button_xpath, timeout=10) # Timeout court pour chaque clic
                        time.sleep(2) # Pause pour le chargement
                    except ElementInteractionError:
                        self.logger.debug("Bouton 'Load More' non trouvé ou plus cliquable.")
                        break # Sortir si le bouton n'est plus là

                table_rows = self.browser.find_elements(By.XPATH, html_elements["table_row_xpath"])
                if not table_rows:
                    self.logger.warning("Aucune ligne de rapport trouvée dans la table d'historique.")

                for row_element in table_rows:
                    try:
                        cols = row_element.find_elements(By.TAG_NAME, "td")
                        if len(cols) < 5: continue # Ligne invalide

                        report_name_on_page = cols[1].text
                        date1_on_page = cols[2].text # Format DD/MM/YYYY
                        date2_on_page = cols[3].text # Format DD/MM/YYYY
                        status_on_page = cols[4].text.lower() # Mettre en minuscule pour comparaison

                        for report_info in self.generated_reports_to_download:
                            if report_info["downloaded"]: continue # Déjà traité

                            # Comparer les dates (format DD/MM/YYYY)
                            if (report_info["start_date_str"] == date1_on_page and
                                report_info["end_date_str"] == date2_on_page and
                                "commissionhistory" in report_name_on_page.lower()): # Nom du rapport

                                if "available" in status_on_page:
                                    self.logger.info(f"Rapport pour {date1_on_page} - {date2_on_page} est disponible. Tentative de téléchargement.")
                                    download_button = row_element.find_element(By.XPATH, html_elements["download_button_xpath"])
                                    download_button.click()

                                    # Utiliser la méthode de vérification et renommage de BaseScrapper
                                    # Le nom du fichier sera basé sur la date de fin du rapport pour unicité.
                                    # Le file_pattern est défini dans config.yml (ex: "*CommissionHistory*.xls*")
                                    downloaded_file = self._verify_and_rename_download(
                                        date_for_filename=report_info["end_date_obj"], # Utilise la date de fin du rapport
                                        file_pattern_to_wait_for=self.config['file_pattern']
                                    )
                                    if downloaded_file:
                                        self.logger.info(f"Rapport pour {date1_on_page} - {date2_on_page} téléchargé et renommé: {downloaded_file.name}")
                                        report_info["downloaded"] = True
                                    else:
                                        self.logger.error(f"Échec de la vérification/renommage du téléchargement pour {date1_on_page} - {date2_on_page}.")
                                    time.sleep(self.job_config.get("delay_after_download_click_sec", 5)) # Pause après clic
                                    break # Sortir de la boucle des rapports générés, passer à la ligne suivante de la table
                                elif status_on_page in ["incomplete", "queued", "in progress"]:
                                    self.logger.info(f"Rapport pour {date1_on_page} - {date2_on_page} est toujours en cours: '{status_on_page}'.")
                                else:
                                    self.logger.warning(f"Statut inattendu '{status_on_page}' pour le rapport {date1_on_page} - {date2_on_page}.")
                    except Exception as e_row: # StaleElementReferenceException ou autre
                        self.logger.warning(f"Erreur lors du traitement d'une ligne de l'historique: {e_row}. La page a peut-être changé.", exc_info=False)
                        break # Sortir de la boucle des lignes et retenter après une pause

            except ElementInteractionError as e_page:
                 self.logger.error(f"Erreur d'interaction sur la page d'historique: {e_page}", exc_info=True)
            except Exception as e_hist:
                self.logger.error(f"Erreur inattendue sur la page d'historique: {e_hist}", exc_info=True)

            if attempt < max_check_attempts - 1 and any(not rpt["downloaded"] for rpt in self.generated_reports_to_download):
                self.logger.info(f"Certains rapports ne sont pas encore téléchargés. Attente de {delay_between_checks_sec}s avant la prochaine vérification.")
                time.sleep(delay_between_checks_sec)

        # Après toutes les tentatives, logger les rapports non téléchargés
        not_downloaded = [r for r in self.generated_reports_to_download if not r["downloaded"]]
        if not_downloaded:
            self.logger.warning(f"{len(not_downloaded)} rapport(s) généré(s) n'ont pas pu être téléchargé(s) après {max_check_attempts} tentatives:")
            for rpt_info in not_downloaded:
                self.logger.warning(f"  - Période: {rpt_info['start_date_str']} à {rpt_info['end_date_str']}")


    def _download_files(self): # Surcharge la méthode de BaseScrapper
        """
        Orchestre la génération puis le téléchargement des rapports.
        """
        # 1. Générer tous les rapports nécessaires pour la plage de dates.
        self._generate_reports_for_date_range()

        # 2. Télécharger les rapports générés depuis la page d'historique.
        if self.generated_reports_to_download:
            self._download_generated_reports_from_history()
        else:
            self.logger.info("Aucun rapport n'a été généré, donc aucun téléchargement à effectuer depuis l'historique.")

    # La méthode _process_download_for_date_range de BaseScrapper n'est pas directement utilisée ici
    # car la logique de ce scraper est : 1. générer tout, 2. télécharger tout.
    # Si on voulait un flux où chaque rapport est téléchargé immédiatement après sa génération,
    # il faudrait adapter _generate_reports_for_date_range pour qu'elle utilise
    # _process_download_for_date_range et _verify_and_rename_download pour chaque rapport.

    # Pour satisfaire l'interface de BaseScrapper si _process_multiple_files_by_date est appelée:
    def _process_download_for_date_range(self, start_date_to_process: date, end_date_to_process: date):
        # Cette méthode ne sera pas appelée directement par le flux actuel de ce scraper.
        # Le flux est géré par _download_files() qui appelle _generate_reports et _download_generated_reports.
        self.logger.warning("_process_download_for_date_range appelée mais non implémentée pour le flux principal de ce scraper.")
        pass


def run_afitech_commission_history_extraction():
    """Fonction principale pour lancer l'extraction Afitech Commission History."""
    env_mapping = {
        "AFITECH_LOGIN_USERNAME": "AFITECH_LOGIN_USERNAME",
        "AFITECH_LOGIN_PASSWORD": "AFITECH_LOGIN_PASSWORD",
        "AFITECH_GET_OTP_URL": "AFITECH_GET_OTP_URL" # Assumer que c'est la clé secrète TOTP
    }
    scraper_job = None
    try:
        scraper_job = ExtractAfitechCommissionHistory(env_vars_mapping=env_mapping)
        scraper_job.process_extraction() # Déclenche le _set_dates, _open_browser, _connection, _download_files, _quit_browser
    except (ValueError, ElementInteractionError, ConnectionError) as e:
        # Erreurs attendues de configuration, Selenium, ou connexion
        log_msg = f"Échec critique du job d'extraction {JOB_NAME}: {e}"
        if scraper_job and scraper_job.logger: scraper_job.logger.critical(log_msg, exc_info=True)
        else: print(f"ERREUR CRITIQUE (logger non dispo) pour {JOB_NAME}: {log_msg}")
    except Exception as e:
        log_msg = f"Erreur inattendue et non gérée dans le job {JOB_NAME}: {e}"
        if scraper_job and scraper_job.logger: scraper_job.logger.critical(log_msg, exc_info=True)
        else: print(f"ERREUR INATTENDUE CRITIQUE (logger non dispo) pour {JOB_NAME}: {log_msg}")
    # finally:
        # _quit_browser est déjà dans le finally de BaseScrapper.process_extraction()
        # if scraper_job: scraper_job._quit_browser()


if __name__ == "__main__":
    from load_env import load_env # Nécessaire si exécuté directement et .env utilisé
    load_env()
    run_afitech_commission_history_extraction()
