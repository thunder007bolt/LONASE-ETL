### system ###
from datetime import timedelta

### selenium ###
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

### base ###
from base.web_scrapper import BaseScrapper
### utils ###
from utils.date_utils import sleep


def clean_value(text_value, is_currency=False, is_numeric=False):
    if text_value is None:
        # Pour les nombres/devises, retourner 0. Pour les dates/textes, retourner chaîne vide ou None.
        return 0 if is_numeric or is_currency else ""

    cleaned = str(text_value).replace('\u202f', '').replace(' ', '')  # Espace insécable et espace normal
    if is_currency:
        cleaned = cleaned.replace('FCFA', '')

    if is_numeric or is_currency:
        try:
            return int(cleaned)
        except ValueError:
            return 0  # Valeur par défaut si la conversion échoue
    return cleaned


class ExtractSunubetPaiement(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('sunubet_paiement', env_variables_list,
                         'logs/extract_sunubet_paiement.log')
        self.file_path = None
        self.files = []

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        username_xpath = html_elements["username_element_xpath"]
        password_xpath = html_elements["password_element_xpath"]
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]
        username = secret_config["SUNUBET_CASINO_LOGIN_USERNAME"]
        password = secret_config["SUNUBET_CASINO_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(username_xpath, keys=username, locator_type="xpath", raise_error=True)
        self.wait_and_send_keys(password_xpath, keys=password, locator_type="xpath", raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click_v2(submit_button_xpath, locator_type="xpath")
        sleep(2)

        try:
            self.logger.info("Vérification de la connexion...")
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath)
            sleep(1)
            self.logger.info("Connexion à la plateforme réussie.")
        except Exception as error:
            self.logger.info("Connexion à la plateforme n'a pas pu être établie.")
            self._quit(error)

    def _generate_files(self):
        browser = self.browser
        html_elements = self.config['html_elements']
        logger = self.logger

        logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)

        logger.info("Remplissage des champs de date...")

        start_date = self.start_date
        delta = timedelta(days=1)
        end_date = self.start_date + delta

        while end_date <= (self.end_date + delta):
            try:
                data = []
                calendar_xpath = html_elements["calendar_xpath"]
                calendar_year_button_xpath = html_elements["calendar_year_button_xpath"]
                calendar_year_xpath = html_elements["calendar_year_xpath"]
                calendar_month_xpath = html_elements["calendar_month_xpath"]
                calendar_day_xpath = html_elements["calendar_day_xpath"]
                search_button_xpath = html_elements["search_button_xpath"]

                self.wait_and_click_v2(calendar_xpath, locator_type="xpath")
                self.wait_and_click_v2(calendar_year_button_xpath, locator_type="xpath")

                # Sélection de la date de début
                for i in browser.find_elements(By.XPATH, calendar_year_xpath):
                    if start_date.strftime('%Y') in i.text:
                        i.click()
                        break
                sleep(0.5)
                for i in browser.find_elements(By.XPATH, calendar_month_xpath):
                    if start_date.strftime('%b').lower() in i.text.lower():
                        i.click()
                        break
                sleep(0.5)
                for i in browser.find_elements(By.XPATH, calendar_day_xpath):
                    if i.text.strip() == start_date.strftime('%d').lstrip('0'):
                        i.click()
                        break
                sleep(0.5)

                # Sélection de la date de fin
                for i in browser.find_elements(By.XPATH, calendar_year_xpath):
                    if start_date.strftime('%Y') in i.text:
                        i.click()
                        break
                sleep(0.5)
                for i in browser.find_elements(By.XPATH, calendar_month_xpath):
                    if start_date.strftime('%b').lower() in i.text.lower():
                        i.click()
                        break
                sleep(0.5)
                for i in browser.find_elements(By.XPATH, calendar_day_xpath):
                    if i.text.strip() == start_date.strftime('%d').lstrip('0'):
                        i.click()
                        break
                sleep(0.5)

                fournisseur_dropdown_xpath = html_elements["fournisseur_dropdown_xpath"]
                fournisseur_dropdown_ng_select_xpath = html_elements["fournisseur_dropdown_ng_select_xpath"]
                fournisseur_element_xpath = html_elements["fournisseur_element_xpath"]

                def manage_dropdown_state(desired_state: str):
                    """
                    Ouvre ou ferme le dropdown ng-select de manière fiable et uniquement si nécessaire,
                    en utilisant un clic JavaScript pour une meilleure robustesse.

                    Args:
                        desired_state (str): L'état souhaité pour le dropdown. Accepte 'open' ou 'close'.
                    """

                    try:
                        wait = WebDriverWait(self.browser, 10)  # Augmentation du timeout à 10s par sécurité

                        # Attendre que l'élément existe dans le DOM
                        dropdown_element = wait.until(EC.presence_of_element_located((By.XPATH, fournisseur_dropdown_ng_select_xpath)))

                        current_classes = dropdown_element.get_attribute('class')
                        is_currently_open = 'ng-select-opened' in current_classes

                        action_needed = (desired_state == 'open' and not is_currently_open) or \
                                        (desired_state == 'close' and is_currently_open)

                        if action_needed:
                            self.wait_and_click_v2(fournisseur_dropdown_xpath, locator_type="xpath")

                            # Attendre la confirmation du changement d'état
                            if desired_state == 'open':
                                wait.until(lambda d: 'ng-select-opened' in d.find_element(By.XPATH,
                                                                                          fournisseur_dropdown_ng_select_xpath).get_attribute(
                                    'class'))
                            else:
                                wait.until_not(lambda d: 'ng-select-opened' in d.find_element(By.XPATH,
                                                                                              fournisseur_dropdown_ng_select_xpath).get_attribute(
                                    'class'))
                        else:
                            pass
                            #self.logger.info("Le dropdown est déjà dans l'état souhaité, aucune action n'est nécessaire.")

                    except TimeoutException:
                        # Si le timeout se produit, on log l'état final des classes pour le débogage
                        final_classes = self.browser.find_element(By.XPATH, fournisseur_dropdown_ng_select_xpath).get_attribute(
                            'class')
                        self.logger.error(
                            f"Timeout: L'état du dropdown n'a pas changé comme attendu. Classes finales: '{final_classes}'")
                        raise
                    except Exception as e:
                        self.logger.error(f"Une erreur imprévue est survenue lors de la gestion du dropdown: {e}")
                        raise
                manage_dropdown_state('open')

                initial_supplier_web_elements = browser.find_elements(By.XPATH, fournisseur_element_xpath)
                supplier_names_to_process = []
                for el in initial_supplier_web_elements:
                    name = el.text.strip()
                    if name:  # S'assurer que le nom n'est pas vide
                        supplier_names_to_process.append(name)

                self.logger.info(f"Nombre de fournisseurs détectés initialement: {len(supplier_names_to_process)}")
                self.logger.info(f"Fournisseurs à traiter: {supplier_names_to_process}")

                for fournisseur_nom_cible in supplier_names_to_process:
                    self.logger.info(f"--- Début du traitement pour le fournisseur : {fournisseur_nom_cible} ---")

                    try:
                        manage_dropdown_state( 'open')

                        found_element_for_selection = None
                        current_elements_in_dropdown = browser.find_elements(By.XPATH, fournisseur_element_xpath)
                        for el_sel in current_elements_in_dropdown:
                            if el_sel.text.strip() == fournisseur_nom_cible:
                                found_element_for_selection = el_sel
                                break

                        if not found_element_for_selection:
                            self.logger.info(f"ERREUR: Impossible de trouver '{fournisseur_nom_cible}' pour la SÉLECTION.")
                            continue

                        self.logger.info(f"Sélection de : {fournisseur_nom_cible}")
                        found_element_for_selection.click()
                    except Exception as e_select:
                        self.logger.info(f"ERREUR Exception lors de la SÉLECTION de '{fournisseur_nom_cible}': {e_select}")
                        continue

                    manage_dropdown_state( 'close')

                    self.wait_and_click_v2(search_button_xpath, locator_type="xpath")
                    sleep(5)

                    kpi_data = {
                        "fournisseur": fournisseur_nom_cible,
                        "jour": start_date.strftime('%d/%m/%Y'),
                        "annee": start_date.strftime('%Y'),
                        "mois": start_date.strftime('%m')
                    }

                    try:
                        nombre_depots_text_xpath = html_elements["nombre_depots_text_xpath"]
                        montant_depots_text_xpath = html_elements["montant_depots_text_xpath"]
                        nombre_retraits_text_xpath = html_elements["nombre_retraits_text_xpath"]
                        montant_retraits_text_xpath = html_elements["montant_retraits_text_xpath"]

                        nombre_depots_text = self._get_text_from_xpath(nombre_depots_text_xpath)
                        montant_depots_text = self._get_text_from_xpath(montant_depots_text_xpath)
                        nombre_retraits_text = self._get_text_from_xpath(nombre_retraits_text_xpath)
                        montant_retraits_text = self._get_text_from_xpath(montant_retraits_text_xpath)

                        kpi_data["nombre_depots"] = clean_value(nombre_depots_text, is_numeric=True)
                        kpi_data["montant_depots"] = clean_value(montant_depots_text, is_currency=True)
                        kpi_data["nombre_retraits"] = clean_value(nombre_retraits_text, is_numeric=True)
                        kpi_data["montant_retraits"] = clean_value(montant_retraits_text, is_currency=True)

                        data.append(kpi_data)
                        self.logger.info(f"Données extraites pour {fournisseur_nom_cible}: OK")

                    except Exception as e_kpi:
                        self.logger.info(f"ERREUR Exception lors de l'EXTRACTION des KPI pour '{fournisseur_nom_cible}': {e_kpi}")
                        raise (e_kpi)
                        kpi_data.update({
                            "nombre_depots": 0, "montant_depots": 0, "nombre_retraits": 0, "montant_retraits": 0,
                        })
                        data.append(kpi_data)

                    try:
                        self.logger.info(f"Début de la déselection pour : {fournisseur_nom_cible}")

                        # --- DÉBUT DE LA MODIFICATION ---
                        manage_dropdown_state( 'open')
                        # --- FIN DE LA MODIFICATION ---

                        # Le code ci-dessous s'exécute maintenant avec la certitude que le dropdown est ouvert
                        found_element_for_deselection = None
                        # Il est conseillé de relancer la recherche des éléments pour éviter les "StaleElementReferenceException"
                        current_elements_in_dropdown_desel = browser.find_elements(By.XPATH, fournisseur_element_xpath)
                        for el_desel in current_elements_in_dropdown_desel:
                            if el_desel.text.strip() == fournisseur_nom_cible:
                                found_element_for_deselection = el_desel
                                break

                        if not found_element_for_deselection:
                            self.logger.info(
                                f"AVERTISSEMENT: Impossible de trouver '{fournisseur_nom_cible}' pour la DÉSÉLECTION.")

                        else:
                            found_element_for_deselection.click()
                            self.logger.info(f"Fournisseur '{fournisseur_nom_cible}' déselectionné (par clic).")
                            sleep(0.5)

                    except Exception as e_deselect:
                        self.logger.info(
                            f"ERREUR Exception lors de la DÉSÉLECTION de '{fournisseur_nom_cible}': {e_deselect}")


                    self.logger.info(f"--- Fin du traitement pour le fournisseur : {fournisseur_nom_cible} ---")
                    manage_dropdown_state( 'close')
                import pandas as pd
                df = pd.DataFrame(data)
                self.logger.info(f"DataFrame final : {start_date}")
                filename = f"sunubet_paiement_transformed_{start_date}.xlsx"
                full_path = self.transformation_dest_path / filename
                df.to_excel(full_path, index=False)

            except:
                continue

            start_date += delta
            end_date += delta

    def _download_files(self):
        pass

    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._generate_files()
        self._download_files()


def run_sunubet_paiement():
    env_variables_list = ["SUNUBET_CASINO_LOGIN_USERNAME", "SUNUBET_CASINO_LOGIN_PASSWORD"]
    job = ExtractSunubetPaiement(env_variables_list)
    job.process_extraction()


if __name__ == "__main__":
    run_sunubet_paiement()
