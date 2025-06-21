from datetime import date # Import date pour le typage
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path # Path est utilisé implicitement par BaseScrapper pour les logs

from base.web_scrapper import BaseScrapper, ElementInteractionError # Importer l'exception personnalisée
# utils.date_utils.sleep n'est plus nécessaire ici car géré dans BaseScrapper ou non utilisé.
# utils.file_manipulation.rename_file n'est plus directement utilisé ici, BaseScrapper s'en charge.

JOB_NAME = "acajou_digital" # Définir comme constante pour éviter les chaînes magiques

class ExtractAcajouDigital(BaseScrapper):
    """
    Scraper pour extraire les données de la plateforme Acajou Digital.
    Hérite de BaseScrapper et implémente la logique spécifique à Acajou Digital.
    """
    def __init__(self, ftp_env_vars_mapping: dict): # Le nom du paramètre est générique, mais ici c'est pour les secrets de login
        """
        Initialise le scraper Acajou Digital.

        Args:
            ftp_env_vars_mapping (dict): Mapping des variables d'environnement pour les identifiants.
                                         Ex: {'ACAJOU_DIGITAL_LOGIN_USERNAME': 'ENV_VAR_FOR_USER', ...}
        """
        # Les options Chrome spécifiques peuvent être passées ici si nécessaire.
        # L'option "--unsafely-treat-insecure-origin-as-secure" est très spécifique et peut poser des risques.
        # Il serait préférable de voir si le problème de certificat/origine peut être résolu autrement.
        # Si elle est absolument nécessaire, elle doit être bien documentée.
        chrome_options_args = [
            # "--unsafely-treat-insecure-origin-as-secure=http://115.110.148.83/bwinnersmis/Administration/"
            # Commenté pour l'instant. Si besoin, la configuration du job pourrait le spécifier.
        ]

        # Le chemin du log est maintenant géré par BaseScrapper ou Orchestrator.
        # On passe le nom du job et le mapping des variables d'environnement.
        # BaseScrapper construira le chemin du log par défaut ou utilisera celui fourni par l'orchestrateur.
        super().__init__(
            name=JOB_NAME,
            env_variables_list=ftp_env_vars_mapping, # BaseScrapper attend 'env_variables_list'
            log_file_path=f"logs/extract_{JOB_NAME}.log", # Chemin de log spécifique au job
            chrome_options_arguments=chrome_options_args
        )

    def _connection_to_platform(self):
        """Gère la connexion à la plateforme Acajou Digital."""
        self.logger.info("Connexion à la plateforme Acajou Digital...")

        login_url = self.config.get('urls', {}).get('login')
        if not login_url:
            self.logger.error("URL de login non trouvée dans la configuration.")
            raise ValueError("URL de login manquante.") # Ou une exception de configuration

        self.browser.get(login_url)

        html_elements = self.config.get('html_elements', {})
        # Utiliser les clés standardisées de secret_config attendues par BaseScrapper si possible,
        # ou s'assurer que get_secret est appelé avec les bonnes clés d'environnement.
        # Ici, on suppose que self.secret_config contient déjà les valeurs mappées.
        username = self.secret_config.get("ACAJOU_DIGITAL_LOGIN_USERNAME")
        password = self.secret_config.get("ACAJOU_DIGITAL_LOGIN_PASSWORD")

        if not (username and password):
            self.logger.error("Identifiants de connexion (username/password) pour Acajou Digital non trouvés dans la configuration des secrets.")
            raise ValueError("Identifiants Acajou Digital manquants.")

        username_id = html_elements.get("username_element_id", "Input_Email")
        password_id = html_elements.get("password_element_id", "Input_Password")
        submit_xpath = html_elements.get("login_submit_button_element_xpath")
        verification_xpath = html_elements.get("verification_xpath")

        if not submit_xpath or not verification_xpath:
            self.logger.error("Configuration des éléments HTML pour le login incomplète (submit_xpath ou verification_xpath manquant).")
            raise ValueError("Configuration HTML de login incomplète.")

        try:
            self.logger.info("Saisie des identifiants...")
            self._wait_and_send_keys(locator=username_id, locator_type='id', keys_to_send=username)
            self._wait_and_send_keys(locator=password_id, locator_type='id', keys_to_send=password)

            self.logger.info("Soumission du formulaire de connexion...")
            self._wait_and_click(locator=submit_xpath, locator_type='xpath')

            self.logger.info("Vérification de la connexion...")
            # Augmenter le timeout si la page après login est lente à charger.
            # Le timeout de 10*9 (90s) est très long, s'assurer qu'il est justifié.
            # Remplacé par un timeout configurable ou un défaut raisonnable (ex: 60s).
            self._wait_for_element_presence(locator=verification_xpath, locator_type='xpath', timeout=html_elements.get("login_verification_timeout_sec", 60))
            self.logger.info("Connexion à la plateforme Acajou Digital réussie.")

        except ElementInteractionError as e: # Attraper l'exception personnalisée de BaseScrapper
            self.logger.error(f"Échec de l'interaction avec un élément lors de la connexion: {e}", exc_info=True)
            # _quit_browser() sera appelé dans le finally de process_extraction de BaseScrapper
            raise # Renvoyer l'erreur pour arrêter le processus
        except Exception as e: # Autres erreurs
            self.logger.error(f"Erreur inattendue lors de la connexion à la plateforme: {e}", exc_info=True)
            raise


    def _download_files(self):
        """Gère la navigation vers la page des rapports et initie le processus de téléchargement."""
        self.logger.info("Navigation vers la page des rapports Acajou Digital.")

        reports_url = self.config.get('urls', {}).get('report')
        if not reports_url:
            self.logger.error("URL des rapports non trouvée dans la configuration.")
            raise ValueError("URL des rapports manquante.")

        self.browser.get(reports_url)

        # Logique spécifique pour sélectionner "DIGITAIN" dans un champ "game"
        # S'assurer que cet élément est bien un champ de saisie ou un select gérable par send_keys.
        html_elements = self.config.get('html_elements', {})
        game_locator_name = html_elements.get("game_element_name", "game") # Supposons que c'est 'name'

        try:
            self.logger.info(f"Sélection du jeu/fournisseur 'DIGITAIN'...")
            # _wait_and_click puis send_keys est inhabituel pour un champ de saisie.
            # Si c'est un champ de saisie, _wait_and_send_keys est plus direct.
            # Si c'est un dropdown complexe, la logique peut être différente.
            # On suppose ici que c'est un champ input.
            self._wait_and_send_keys(locator=game_locator_name, locator_type='name', keys_to_send="DIGITAIN", timeout=30)
        except ElementInteractionError as e:
            self.logger.error(f"Échec de la sélection du jeu/fournisseur: {e}", exc_info=True)
            raise

        # La méthode _process_multiple_files a été renommée en _process_multiple_files_by_date
        # et nécessite que _process_download_for_date_range soit implémentée.
        self.logger.info("Lancement du processus de téléchargement pour la plage de dates configurée.")
        self._process_multiple_files_by_date(rename_downloaded_file=True) # True pour renommer automatiquement


    def _process_download_for_date_range(self, start_date_to_process: date, end_date_to_process: date):
        """
        Gère le téléchargement d'un rapport pour une journée spécifique (start_date_to_process).
        end_date_to_process est ignoré ici car Acajou Digital semble fonctionner jour par jour pour ce rapport.
        """
        self.logger.info(f"Préparation du téléchargement du rapport pour la date: {start_date_to_process.strftime('%Y-%m-%d')}")

        html_elements = self.config.get('html_elements', {})
        date_element_name = html_elements.get("date_element_name")
        # step_x1_element_id est utilisé pour une attente, pas un clic direct ici.
        loading_indicator_id = html_elements.get("step_x1_element_id")
        submit_report_button_xpath = html_elements.get("step_x2_element_xpath") # C'est le bouton "Download" ou "Export"

        if not (date_element_name and loading_indicator_id and submit_report_button_xpath):
            self.logger.error("Configuration des éléments HTML pour la page de rapport incomplète.")
            raise ValueError("Configuration HTML de la page de rapport incomplète.")

        # Formatage de la date pour le champ spécifique d'Acajou (YYYY/MM/DD HH:MM:SS - YYYY/MM/DD HH:MM:SS)
        # On prend la journée entière pour start_date_to_process.
        formatted_date_range = (
            f"{start_date_to_process.strftime('%Y/%m/%d')} 00:00:00"
            f" - "
            f"{start_date_to_process.strftime('%Y/%m/%d')} 23:59:59"
        )
        self.logger.info(f"Date formatée pour le rapport: {formatted_date_range}")

        try:
            # Trouver l'élément de date, le vider, et envoyer la nouvelle plage de dates
            # _wait_and_click n'est pas approprié pour un champ de saisie. Utiliser _wait_and_send_keys.
            date_input_element = self._wait_for_element_presence(locator=date_element_name, locator_type='name', timeout=30)
            if not date_input_element: # Devrait lever une erreur si non trouvé, mais double check
                 self.logger.error(f"L'élément de date '{date_element_name}' n'a pas été trouvé.")
                 raise ElementInteractionError(f"Élément de date '{date_element_name}' introuvable.")

            date_input_element.clear()
            date_input_element.send_keys(formatted_date_range)
            date_input_element.send_keys(Keys.ENTER) # Pour fermer un éventuel date picker ou valider la saisie

            # Attendre que l'indicateur de chargement (spinner/overlay) disparaisse.
            # L'ancienne logique attendait que le style de l'élément contienne "none".
            # On peut utiliser EC.invisibility_of_element_located si l'élément devient display:none
            # Ou EC.text_to_be_present_in_element_attribute si c'est un style inline.
            # Pour l'instant, on garde la logique de style, mais en utilisant une méthode de BaseScrapper.
            # WebDriverWait(self.browser, timeout=15).until(
            #     EC.text_to_be_present_in_element_attribute((By.ID, loading_indicator_id), "style", "none")
            # )
            # Alternative plus robuste si l'élément disparaît ou devient non visible:
            self._wait_for_invisibility(locator=loading_indicator_id, locator_type='id', timeout=30)
            self.logger.info("Champ de date rempli et indicateur de chargement disparu.")

            self.logger.info("Clic sur le bouton pour générer/télécharger le rapport...")
            self._wait_and_click(locator=submit_report_button_xpath, locator_type='xpath', timeout=60)
            # À ce stade, le téléchargement devrait être initié.
            # _verify_and_rename_download sera appelé par _process_multiple_files_by_date après cette méthode.

        except ElementInteractionError as e:
            self.logger.error(f"Échec de l'interaction avec un élément lors de la préparation du téléchargement: {e}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la préparation du téléchargement pour {start_date_to_process}: {e}", exc_info=True)
            raise


def run_acajou_digital_extraction():
    """Fonction principale pour lancer l'extraction Acajou Digital."""
    # Mapping des variables d'environnement pour les identifiants de ce scraper spécifique
    env_mapping = {
        "ACAJOU_DIGITAL_LOGIN_USERNAME": "ACAJOU_DIGITAL_LOGIN_USERNAME", # Clé de secret_config : Nom de la variable d'env
        "ACAJOU_DIGITAL_LOGIN_PASSWORD": "ACAJOU_DIGITAL_LOGIN_PASSWORD"
    }

    scraper_job = None # Pour le bloc finally
    try:
        scraper_job = ExtractAcajouDigital(ftp_env_vars_mapping=env_mapping)
        scraper_job.process_extraction() # Méthode principale de BaseScrapper
    except (ValueError, ElementInteractionError) as e: # Erreurs de config ou d'interaction Selenium
        if scraper_job and scraper_job.logger: # Si le logger a été initialisé
            scraper_job.logger.critical(f"Échec critique du job d'extraction {JOB_NAME}: {e}", exc_info=True)
        else: # Logger non dispo (erreur très précoce)
            print(f"ERREUR CRITIQUE (logger non disponible) pour {JOB_NAME}: {e}")
    except Exception as e: # Autres erreurs inattendues
        if scraper_job and scraper_job.logger:
             scraper_job.logger.critical(f"Erreur inattendue et non gérée dans le job {JOB_NAME}: {e}", exc_info=True)
        else:
            print(f"ERREUR INATTENDUE CRITIQUE (logger non disponible) pour {JOB_NAME}: {e}")
    finally:
        if scraper_job: # Assure que _quit_browser est appelé même si process_extraction n'est pas atteint
            scraper_job._quit_browser()


if __name__ == "__main__":
    # Pour exécuter ce script directement
    # Assurez-vous que load_env.py a été appelé si les variables d'env sont dans un .env
    # Exemple:
    # from load_env import load_env
    # load_env()
    run_acajou_digital_extraction()
