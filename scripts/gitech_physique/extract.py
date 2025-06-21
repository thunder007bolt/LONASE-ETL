from datetime import date, timedelta
import time
from pathlib import Path # Importé pour Path() dans _verify_single_zip_download

from selenium.webdriver.common.by import By # Nécessaire pour find_elements
from base.web_scrapper import BaseScrapper, ElementInteractionError

JOB_NAME = "gitech_physique"

class ExtractGitechPhysique(BaseScrapper):
    """
    Scraper pour extraire des fichiers ZIP quotidiens depuis la plateforme Gitech Physique (filedownload).
    """
    def __init__(self, env_vars_mapping: dict):
        super().__init__(
            name=JOB_NAME,
            env_variables_list=env_vars_mapping,
            log_file_path=f"logs/extract_{JOB_NAME}.log"
        )

    def _connection_to_platform(self):
        """Gère la connexion à la plateforme Gitech Physique."""
        self.logger.info(f"Connexion à la plateforme {self.name}...")
        login_url = self.config.get('urls', {}).get('login')
        if not login_url:
            raise ValueError(f"URL de login pour {self.name} manquante.")
        self.browser.get(login_url)

        html_elements = self.config.get('html_elements', {})
        username = self.secret_config.get("GITECH_PHYSIQUE_LOGIN_USERNAME") # Assurez-vous que cette variable d'env existe
        password = self.secret_config.get("GITECH_PHYSIQUE_LOGIN_PASSWORD") # Assurez-vous que cette variable d'env existe

        if not (username and password):
            raise ValueError(f"Identifiants (username/password) pour {self.name} manquants.")

        username_id = html_elements.get("username_element_id")
        password_id = html_elements.get("password_element_id")
        submit_id = html_elements.get("login_submit_button_element_id")
        verification_xpath = html_elements.get("verification_xpath")

        if not (username_id and password_id and submit_id and verification_xpath):
            raise ValueError(f"Configuration HTML de login incomplète pour {self.name}.")

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

        time.sleep(self.job_config.get("delay_after_login_sec", 2))

    def _verify_single_zip_download(self, date_str_for_pattern: str, zip_file_pattern_template: str) -> bool:
        """
        Vérifie le téléchargement d'un fichier ZIP spécifique basé sur un template de pattern et une date.
        Utilise une partie de la logique de _verify_and_rename_download de BaseScrapper, mais sans renommage.
        """
        # Construire le pattern de recherche spécifique pour ce fichier ZIP et cette date
        # Ex: zip_file_pattern_template = "*ALR1.zip", date_str_for_pattern = "2023_01_01"
        # -> formatted_search_pattern = "2023_01_01_ALR1.zip" (si le * est au début)
        # Ou, si le pattern est comme "prefix_*_suffix.zip" -> "prefix_2023_01_01_suffix.zip"
        # L'ancien code faisait: formatted_pattern = file_pattern.replace("*",f"{day}_") -> ex: "2023_01_01_ALR1.zip"
        specific_file_pattern = zip_file_pattern_template.replace("*", f"{date_str_for_pattern}_")

        download_dir = Path(self.config["download_path"]) # Chemin de téléchargement configuré
        timeout_seconds = self.config.get("wait_time_zip", self.config.get("wait_time", 120)) # Timeout spécifique pour ZIPs ou global
        poll_interval_seconds = 2

        self.logger.info(f"Attente du fichier ZIP '{specific_file_pattern}' dans {download_dir} (timeout: {timeout_seconds}s).")

        start_time = time.time()
        found_file = None
        while time.time() - start_time < timeout_seconds:
            # Utiliser glob pour trouver le fichier. Le pattern peut être simple (nom exact) ou avec wildcards.
            # Ici, specific_file_pattern est supposé être un nom de fichier quasi-exact.
            candidate_files = list(download_dir.glob(specific_file_pattern))

            if candidate_files:
                # S'assurer que le fichier n'est pas temporaire et a une taille > 0
                for f_path in candidate_files: # Normalement un seul si le pattern est précis
                    if not f_path.name.endswith((".tmp", ".crdownload", ".part")):
                        # Vérification de stabilité (simple)
                        try:
                            current_size = f_path.stat().st_size
                            time.sleep(0.5)
                            if current_size == f_path.stat().st_size and current_size > 0:
                                self.logger.info(f"Fichier ZIP '{f_path.name}' trouvé et stable (taille: {current_size} bytes).")
                                found_file = f_path
                                break
                        except FileNotFoundError: # Le fichier a pu être déplacé/supprimé rapidement
                            self.logger.debug(f"Fichier {f_path.name} disparu pendant la vérification de stabilité.")
                            continue
                if found_file:
                    break
            time.sleep(poll_interval_seconds)

        if not found_file:
            self.logger.warning(f"Timeout: Fichier ZIP '{specific_file_pattern}' non trouvé ou non stabilisé après {timeout_seconds}s.")
            return False
        return True


    def _download_files(self):
        """
        Navigue dans la structure de dossiers basée sur l'année, puis télécharge les fichiers ZIP
        pour chaque jour de la plage de dates configurée.
        """
        # L'appel à self._delete_old_files() est fait par BaseScrapper.process_extraction()
        # avant d'appeler cette méthode _download_files().

        current_processing_date = self.start_date
        year_str = current_processing_date.strftime("%Y") # Suppose que la plage de dates est dans la même année.
                                                        # Si ce n'est pas le cas, la navigation d'année doit être gérée.

        self.logger.info(f"Navigation vers le dossier de l'année {year_str} sur la plateforme...")
        try:
            # L'ancien XPath était `*//td/a[contains(text(), '{year}')]`.
            # Il faut s'assurer que cela fonctionne toujours et qu'il n'y a qu'un seul lien par an.
            # Utilisation de _wait_and_click pour plus de robustesse.
            year_link_xpath = f"//td/a[contains(text(), '{year_str}')]" # Enlever le '*' initial, non standard pour XPath
            self._wait_and_click(year_link_xpath, timeout=30)
            self.logger.info(f"Navigation vers le dossier de l'année {year_str} réussie.")
            time.sleep(self.job_config.get("delay_after_folder_click_sec", 3)) # Laisser la page charger
        except ElementInteractionError as e:
            self.logger.error(f"Impossible de naviguer vers le dossier de l'année {year_str}: {e}", exc_info=True)
            raise # Arrêter si on ne peut pas atteindre le dossier de l'année

        delta_one_day = timedelta(days=1)

        zip_patterns_to_check = self.config.get('zip_file_patterns', []) # Liste des motifs ZIP de config.yml
        if not zip_patterns_to_check:
            self.logger.warning("Aucun 'zip_file_patterns' défini dans la configuration. Aucun fichier ZIP ne sera activement recherché.")
            return

        while current_processing_date <= self.end_date:
            date_str_for_links = current_processing_date.strftime("%Y_%m_%d") # Format YYYY_MM_DD pour les liens
            self.logger.info(f"Recherche et téléchargement des fichiers ZIP pour la date: {date_str_for_links}")

            # Trouver tous les liens de fichiers pour la date actuelle
            # Il est important que la page soit complètement chargée ici.
            # On pourrait avoir besoin de rafraîchir la liste des éléments si la page change dynamiquement.
            file_links_xpath = f"//a[contains(text(), '{date_str_for_links}')]"
            try:
                # Utiliser find_elements pour obtenir tous les liens correspondants
                # Il faut s'assurer que self.browser est bien l'instance du navigateur
                matching_links = self.browser.find_elements(By.XPATH, file_links_xpath)
                if not matching_links:
                    self.logger.warning(f"Aucun lien de fichier trouvé pour la date {date_str_for_links}.")

                for link_element in matching_links:
                    try:
                        # Il est plus sûr de récupérer le href et de naviguer, ou de s'assurer que le clic est sans risque
                        # de StaleElementReferenceException si la page se recharge après chaque clic.
                        # Pour l'instant, on clique directement.
                        link_text = link_element.text # Pour log
                        self.logger.info(f"Clic sur le lien: {link_text}")
                        link_element.click()
                        # Une petite pause après le clic pour initier le téléchargement peut être utile.
                        time.sleep(self.job_config.get("delay_after_zip_download_click_sec", 2))
                    except Exception as e_click: # Peut être StaleElementReferenceException
                        self.logger.error(f"Erreur en cliquant sur un lien pour {date_str_for_links} (lien: {link_text if 'link_text' in locals() else 'inconnu'}): {e_click}", exc_info=False)
                        # Si un clic échoue, on pourrait vouloir recharger la page et retenter, ou juste continuer.
                        # Pour l'instant, on continue avec les autres liens/dates.

                # Après avoir cliqué sur tous les liens pour la date, vérifier les téléchargements
                if matching_links: # Seulement si on a tenté de télécharger quelque chose
                    self.logger.info(f"Vérification des téléchargements pour la date {date_str_for_links}...")
                    all_found_for_date = True
                    for zip_pattern_template in zip_patterns_to_check:
                        if not self._verify_single_zip_download(date_str_for_links, zip_pattern_template):
                            all_found_for_date = False
                            self.logger.warning(f"Le fichier ZIP correspondant à '{zip_pattern_template}' pour la date {date_str_for_links} n'a pas été vérifié.")

                    if all_found_for_date:
                        self.logger.info(f"Tous les fichiers ZIP attendus pour {date_str_for_links} semblent avoir été téléchargés.")
                    else:
                        self.logger.warning(f"Certains fichiers ZIP pour {date_str_for_links} n'ont pas pu être vérifiés. Voir logs précédents.")

            except Exception as e_date_process:
                 self.logger.error(f"Erreur majeure lors du traitement de la date {date_str_for_links}: {e_date_process}", exc_info=True)

            current_processing_date += delta_one_day
            if current_processing_date <= self.end_date: # Si on va traiter une autre date
                # Revenir à la page du dossier de l'année pour la date suivante, ou s'assurer que la page est correcte.
                # Si cliquer sur un lien de fichier change la page, il faut re-naviguer.
                # L'ancien code ne montrait pas de re-navigation explicite ici.
                # On va supposer que la page reste la même (liste de fichiers) ou que les clics n'invalident pas la session/page.
                # Si la page change, il faudrait faire self.browser.get(URL_DU_DOSSIER_ANNEE) ou self.browser.back()
                self.logger.debug("Passage à la date suivante.")
                time.sleep(self.job_config.get("delay_between_dates_in_listing_sec", 1))


    # La méthode _process_download_for_date_range n'est pas utilisée par ce scraper
    # car _download_files a une logique de boucle et de téléchargement personnalisée.
    def _process_download_for_date_range(self, start_date_to_process: date, end_date_to_process: date):
        self.logger.debug(f"_process_download_for_date_range appelée pour {JOB_NAME} mais non utilisée directement.")
        pass


def run_gitech_physique_extraction(): # Nom de fonction mis à jour
    """Fonction principale pour lancer l'extraction Gitech Physique."""
    env_mapping = {
        "GITECH_PHYSIQUE_LOGIN_USERNAME": "GITECH_PHYSIQUE_LOGIN_USERNAME",
        "GITECH_PHYSIQUE_LOGIN_PASSWORD": "GITECH_PHYSIQUE_LOGIN_PASSWORD"
    }
    scraper_job = None
    try:
        scraper_job = ExtractGitechPhysique(env_vars_mapping=env_mapping)
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
    run_gitech_physique_extraction() # Nom de fonction mis à jour
