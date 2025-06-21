from datetime import date # Pour le typage de start_date_to_process, end_date_to_process
import time # Pour sleep

from base.web_scrapper import BaseScrapper, ElementInteractionError
# Imports Selenium spécifiques (By, Keys, WebDriverWait, EC, Select) plus nécessaires directement ici
# Imports utils (get_config, get_secret, get_yesterday_date, move_file, loading) plus nécessaires ici

JOB_NAME = "bwinner"

class ExtractBwinner(BaseScrapper):
    """
    Scraper pour extraire les rapports "Total Tax Report" de la plateforme Bwinner.
    """
    def __init__(self, env_vars_mapping: dict):
        super().__init__(
            name=JOB_NAME,
            env_variables_list=env_vars_mapping,
            log_file_path=f"logs/extract_{JOB_NAME}.log"
            # Pas d'options Chrome spécifiques ici.
        )
        # self.file_path = None # Non utilisé dans la version refactorisée de BaseScrapper

    def _connection_to_platform(self):
        """Gère la connexion à la plateforme Bwinner."""
        self.logger.info(f"Connexion à la plateforme {self.name}...")
        login_url = self.config.get('urls', {}).get('login')
        if not login_url:
            raise ValueError(f"URL de login pour {self.name} manquante.")
        self.browser.get(login_url)

        html_elements = self.config.get('html_elements', {})
        username = self.secret_config.get("BWINNER_LOGIN_USERNAME")
        password = self.secret_config.get("BWINNER_LOGIN_PASSWORD")

        if not (username and password):
            raise ValueError(f"Identifiants (username/password) pour {self.name} manquants.")

        username_xpath = html_elements.get("username_element_xpath")
        password_xpath = html_elements.get("password_element_xpath")
        submit_id = html_elements.get("login_submit_button_element_id")
        verification_xpath = html_elements.get("verification_xpath") # Crucial pour confirmer le login

        if not (username_xpath and password_xpath and submit_id and verification_xpath):
            raise ValueError(f"Configuration des éléments HTML de login incomplète pour {self.name}.")

        try:
            self.logger.info("Saisie des identifiants...")
            # Les timeouts de 10*9 (90s) sont excessifs pour des interactions simples. Réduits.
            self._wait_and_send_keys(username_xpath, keys_to_send=username, timeout=30)
            self._wait_and_send_keys(password_xpath, keys_to_send=password, timeout=30)

            self.logger.info("Soumission du formulaire de connexion...")
            self._wait_and_click(submit_id, locator_type='id', timeout=30)

            self.logger.info("Vérification de la connexion (attente de l'élément de vérification)...")
            self._wait_for_element_presence(verification_xpath, timeout=60) # Timeout plus long pour la page après login
            self.logger.info(f"Connexion à la plateforme {self.name} réussie.")

        except ElementInteractionError as e:
            self.logger.error(f"Échec de l'interaction Selenium lors de la connexion à {self.name}: {e}", exc_info=True)
            raise # Propage pour que BaseScrapper.process_extraction gère la fermeture du navigateur
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la connexion à {self.name}: {e}", exc_info=True)
            raise

        time.sleep(self.job_config.get("delay_after_login_sec", 5)) # Pause configurable après login


    def _download_files(self):
        """Prépare la page de rapport et lance le processus de téléchargement pour la plage de dates."""
        self.logger.info(f"Préparation de la page des rapports pour {self.name}...")
        reports_url = self.config.get('urls', {}).get('report')
        if not reports_url:
            raise ValueError(f"URL des rapports pour {self.name} manquante.")

        html_elements = self.config.get('html_elements', {})
        self.browser.get(reports_url)

        # Séquence d'actions pour configurer le type de rapport sur la page
        # Ces XPaths sont très spécifiques et fragiles.
        actions_xpaths = [
            html_elements.get('actionone_element_xpath'),
            html_elements.get('actiontwo_element_xpath'),
            html_elements.get('actionthree_element_xpath'),
            html_elements.get('actionfour_element_xpath')
        ]

        if not all(actions_xpaths):
            raise ValueError(f"Configuration des XPaths pour les actions sur la page de rapport incomplète pour {self.name}.")

        try:
            self.logger.info("Exécution de la séquence d'actions de configuration du rapport...")
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)") # Scroll en bas
            self._wait_and_click(actions_xpaths[0], timeout=30)
            time.sleep(1)
            self._wait_and_click(actions_xpaths[1], timeout=10)
            time.sleep(1)
            self.browser.execute_script("window.scrollTo(document.body.scrollHeight,0)") # Scroll en haut
            self._wait_and_click(actions_xpaths[2], timeout=10)
            time.sleep(1)
            self._wait_and_click(actions_xpaths[3], timeout=10)
            time.sleep(1)
            self.logger.info("Configuration du rapport terminée.")
        except ElementInteractionError as e:
            self.logger.error(f"Échec lors de la configuration du rapport (clics d'action): {e}", exc_info=True)
            raise

        # Utilise la méthode de BaseScrapper pour itérer sur les dates et appeler _process_download_for_date_range
        self.logger.info(f"Lancement du téléchargement des rapports pour la plage de dates configurée ({self.name}).")
        self._process_multiple_files_by_date(rename_downloaded_file=True)


    def _process_download_for_date_range(self, start_date_to_process: date, end_date_to_process: date):
        """
        Remplit les dates, filtre et télécharge le rapport pour la journée spécifiée.
        Pour Bwinner, start_date_to_process et end_date_to_process seront les mêmes (traitement jour par jour).
        """
        date_str = start_date_to_process.strftime('%d/%m/%Y') # Format attendu par Bwinner
        self.logger.info(f"Préparation du téléchargement du rapport pour la date: {date_str} ({self.name}).")

        html_elements = self.config.get('html_elements', {})
        from_date_id = html_elements.get("from_date_element_id")
        to_date_id = html_elements.get("to_date_element_id")
        filter_button_id = html_elements.get("filter_button_element_id")
        download_button_xpath = html_elements.get("download_button_element_xpath")

        if not (from_date_id and to_date_id and filter_button_id and download_button_xpath):
            raise ValueError(f"Configuration des éléments HTML pour le formulaire de date/téléchargement incomplète ({self.name}).")

        try:
            # Remplir les champs de date
            # Utiliser _wait_and_send_keys pour plus de robustesse
            self._wait_and_send_keys(from_date_id, locator_type='id', keys_to_send=date_str, clear_first=True, timeout=15)
            time.sleep(0.5) # Petite pause si interaction rapide
            self._wait_and_send_keys(to_date_id, locator_type='id', keys_to_send=date_str, clear_first=True, timeout=15)
            time.sleep(0.5)

            self.logger.info("Application du filtre de date...")
            self._wait_and_click(filter_button_id, locator_type='id', timeout=15)
            # Une pause est importante ici pour laisser le tableau/lien de téléchargement se mettre à jour.
            time.sleep(self.job_config.get("delay_after_filter_sec", 5)) # Configurable

            self.logger.info("Clic sur le bouton de téléchargement...")
            self._wait_and_click(download_button_xpath, timeout=15)
            # Le téléchargement est initié. _verify_and_rename_download sera appelé par _process_multiple_files_by_date.

        except ElementInteractionError as e:
            self.logger.error(f"Échec de l'interaction Selenium lors du processus de téléchargement pour {date_str} ({self.name}): {e}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors du processus de téléchargement pour {date_str} ({self.name}): {e}", exc_info=True)
            raise


def run_bwinner_extraction(): # Nom de fonction mis à jour
    """Fonction principale pour lancer l'extraction Bwinner."""
    env_mapping = {
        "BWINNER_LOGIN_USERNAME": "BWINNER_LOGIN_USERNAME",
        "BWINNER_LOGIN_PASSWORD": "BWINNER_LOGIN_PASSWORD"
    }
    scraper_job = None
    try:
        scraper_job = ExtractBwinner(env_vars_mapping=env_mapping)
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
    run_bwinner_extraction() # Nom de fonction mis à jour
