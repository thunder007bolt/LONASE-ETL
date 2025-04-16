### system ###
### base ###
from asyncio import timeout
from pathlib import Path

import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.keys import Keys

from base.web_scrapper import BaseScrapper
### utils ###
from utils.date_utils import sleep
from utils.file_manipulation import move_file
import pandas as pd
from time import sleep
from pathlib import Path
from selenium.webdriver.common.by import By
# Nouveaux imports nécessaires pour l'attente explicite
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

def content_has_changed(self, element_hash, previous_hash):
    """Vérifie si le contenu HTML de l'élément a changé"""

    return element_hash != previous_hash

class ExtractPmuLots(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('pmu_lots', env_variables_list, 'logs/extract_pmu_lots.log')
        self.file_path = None

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']

        attempts = 3
        for attempt in range(0,attempts):
            self.logger.info(f"Tentative n {attempt}")
            try:
                browser.get(login_url)
                break
            except Exception as e:
                if attempt == 3:
                    self.logger.info(f"Toutes les tentatives de connexions ont échoué")
                    self._quit()


        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        login_step1_xpath = html_elements["login_step1_xpath"]
        login_step2_xpath = html_elements["login_step2_xpath"]
        username_xpath = html_elements["username_element_xpath"]
        password_xpath = html_elements["password_element_xpath"]
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]
        username = secret_config["PMU_LOGIN_USERNAME"]
        password = secret_config["PMU_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_click(login_step1_xpath, locator_type='xpath', timeout=60*10)
        self.wait_and_click(login_step2_xpath, locator_type='xpath', timeout=60*3)
        self.wait_and_send_keys(username_xpath, locator_type='xpath', keys=username, raise_error=True)
        self.wait_and_send_keys(password_xpath, locator_type='xpath', keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type='xpath')

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_element_visible(verification_xpath)
            self.logger.info("Connexion à la plateforme réussie.")
        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()
        sleep(10)
        pass

    def _download_files(self):
       self._process_multiple_files()

    def _process_download2(self, start_date, end_date):
        browser = self.browser
        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        products = self.config['produits']

        datas = []
        for product in products:
            browser.get(reports_url)
            self.logger.info("Remplissage des champs de date...")
            html_elements = self.config['html_elements']

            date_element_xpath = html_elements["date_element_xpath"]
            product_element_xpath = html_elements["product_element_xpath"]
            submit_button_element_xpath = html_elements["submit_button_element_xpath"]
            step1_element_xpath = html_elements["step1_element_xpath"]
            step2_element_xpath = html_elements["step2_element_xpath"]
            step_element_xpath = html_elements["step_element_xpath"]

            date_element = self.wait_for_click(date_element_xpath, locator_type="xpath")
            date_element.clear()
            date_element.send_keys(str(start_date))

            self.fill_select(product_element_xpath, "xpath", value=product)

            self.logger.info("Soumission du formulaire...")
            self.wait_and_click(submit_button_element_xpath, locator_type="xpath")
            sleep(3)

            self.wait_for_invisibility(step_element_xpath, locator_type="xpath", timeout=60*20)
            sleep(5)

            while True:
                try:
                    table = self.wait_for_click(step1_element_xpath, locator_type="xpath", raise_error=True)
                    sleep(5)
                except:
                    break

                df = pd.read_html(table.get_attribute('outerHTML'))
                df = df[0].dropna(axis=0, thresh=4)

                for index, row in df.iterrows():
                    for column in df.columns:
                        df.at[index, column] = str(row[column]).strip().replace('\u202f', ' ')
                    if len(str(df.at[index, 'Joueur'])) < 9:
                        df = df.drop(index=(index))

                df['produit'] = str(product)
                datas.append(df)

                step2_element = browser.find_elements(by=By.XPATH, value=step2_element_xpath)[-2]
                if 'disabled' in str(step2_element.get_attribute('class')):
                    break
                step2_element.click()

                try:
                    self.wait_for_invisibility(step_element_xpath, locator_type="xpath", raise_error=True, timeout=60*50)
                    sleep(5)
                except:
                    continue

        df = pd.concat(datas, ignore_index=True)
        try:
            df = df.drop(['Unnamed: 6'], axis=1)
        except:
            pass
        try:
            df = df.drop(['Unnamed: 7'], axis=1)
        except:
            pass
        try:
            df = df.drop(['Unnamed: 8'], axis=1)
        except:
            pass

        df['JOUR'] = str(start_date.strftime('%d/%m/%Y'))
        df['ANNEE'] = str(start_date.strftime('%Y'))
        df['MOIS'] = str(start_date.strftime('%m'))

        try:
            self.logger.info(f"Enregistrement du fichier PMU Senegal du {start_date} ...")
            filename = "Pmu_Senegal_lots_" + str(start_date) + ".csv"
            # todo: update path
            destination = Path(self.config["download_path"])
            final_file = destination / filename
            df.to_csv(final_file, index=False, sep=';', encoding='latin1')

        except Exception as e:
            self.logger.error(f"Erreur lors de la telechargement du fichier PMU Senegal : {e}")
            raise e

    def _process_download(self, start_date, end_date):
        browser = self.browser
        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        products = self.config['produits']
        html_elements = self.config['html_elements']

        # Récupération des XPaths une seule fois
        date_element_xpath = html_elements["date_element_xpath"]
        product_element_xpath = html_elements["product_element_xpath"]
        submit_button_element_xpath = html_elements["submit_button_element_xpath"]
        step1_element_xpath = html_elements["step1_element_xpath"]  # Table
        step2_element_xpath = html_elements["step2_element_xpath"]  # Bouton Suivant
        step_element_xpath = html_elements["step_element_xpath"]  # Loader
        step1_tbody_xpath = "/html/body/jhi-main/div[2]/div/jhi-winner/div/div[2]/table/tbody"  # Tbody

        datas = []
        for product in products:
            self.logger.info(f"Traitement du produit : {product}")
            browser.get(reports_url)

            # Remplissage et soumission du formulaire
            self.logger.info("Remplissage des champs de date et produit...")
            try:
                date_element = self.wait_for_click(date_element_xpath, locator_type="xpath")
                date_element.clear()
                date_element.send_keys(str(start_date))

                self.fill_select(product_element_xpath, "xpath", value=product)

                self.logger.info("Soumission du formulaire...")
                self.wait_and_click(submit_button_element_xpath, locator_type="xpath")

                self.logger.info("Attente de la fin du chargement initial...")
                self.wait_for_presence(step_element_xpath, locator_type="xpath", timeout=60*5, exit_on_error=True)
                self.wait_for_invisibility(step_element_xpath, locator_type="xpath", timeout=120, exit_on_error=True)
                sleep(2)  # Délai pour stabiliser le DOM

            except Exception as e:
                self.logger.error(f"Erreur lors de la configuration initiale pour {product} : {e}")
                continue

            # Boucle de pagination
            page_num = 1
            while True:
                self.logger.info(f"Traitement de la page {page_num} pour {product}...")
                try:
                    # Attendre la table
                    self.logger.info("Attente de l'apparition de la table...")
                    self.wait_for_presence(step1_element_xpath, locator_type="xpath", timeout=120, exit_on_error=True)
                    current_table_element = WebDriverWait(browser, 10 ).until(
                        EC.presence_of_element_located((By.XPATH, step1_element_xpath))
                    )

                    # Extraire les données initiales pour comparaison
                    current_tbody_element = browser.find_element(By.XPATH, step1_tbody_xpath)
                    DONNEES_INITIALES = tuple(
                        row.text for row in current_tbody_element.find_elements(By.TAG_NAME, "tr"))

                    # Lire et nettoyer la table
                    self.logger.info("Lecture de la table HTML...")
                    df = pd.read_html(current_table_element.get_attribute('outerHTML'))[0]
                    df = df.dropna(axis=0, thresh=4)

                    rows_to_drop = []
                    for index, row in df.iterrows():
                        try:
                            for column in df.columns:
                                cell_value = row[column]
                                df.at[index, column] = '' if pd.isna(cell_value) else str(cell_value).strip().replace(
                                    '\u202f', ' ')
                            if 'Joueur' in df.columns and len(str(df.at[index, 'Joueur'])) < 9:
                                rows_to_drop.append(index)
                        except Exception as clean_err:
                            self.logger.warning(f"Erreur lors du nettoyage de la ligne {index} : {clean_err}")
                    df = df.drop(index=rows_to_drop)

                    if not df.empty:
                        df['produit'] = str(product)
                        datas.append(df)
                        self.logger.info(f"{len(df)} lignes ajoutées depuis la page {page_num}.")

                except Exception as e:
                    self.logger.error(f"Erreur lors de la lecture de la table page {page_num} : {e}")
                    raise RuntimeError("Échec de l'extraction")


                # Gestion du bouton "suivant"
                try:
                    next_buttons = browser.find_elements(By.XPATH, step2_element_xpath)
                    if len(next_buttons) < 2:
                        self.logger.info("Bouton 'suivant' introuvable ou insuffisant, fin de la pagination.")
                        break

                    step2_element = next_buttons[-2]  # Avant-dernier élément
                    if 'disabled' in (step2_element.get_attribute('class') or ''):
                        self.logger.info("Bouton 'suivant' désactivé, fin de la pagination.")
                        break

                    self.logger.info("Clic sur le bouton 'suivant'...")
                    step2_element.click()

                    # Attendre la mise à jour
                    self.logger.info("Attente de la disparition du loader...")
                    self.wait_for_presence(step_element_xpath, locator_type="xpath", exit_on_error=True)
                    self.wait_for_invisibility(step_element_xpath, locator_type="xpath", timeout=180*2, exit_on_error=True)

                    self.logger.info("Vérification du changement de contenu...")
                    attempts = 20
                    for attempt in range(attempts):
                        self.logger.info(f"Tentative {attempt}")
                        new_tbody_element = browser.find_element(By.XPATH, step1_tbody_xpath)
                        new_donnees = tuple(row.text for row in new_tbody_element.find_elements(By.TAG_NAME, "tr"))
                        if new_donnees != DONNEES_INITIALES:
                            self.logger.info("Contenu mis à jour avec succès.")
                            break
                        else:
                            if attempt == attempts - 1:
                                self.logger.warning("Contenu inchangé après plusieurs tentatives. Annulation du script")
                                #todo: mieux gérer
                                raise RuntimeError("Échec de la mise à jour du contenu")
                        sleep(10)
                    page_num += 1

                except NoSuchElementException:
                    self.logger.info("Bouton 'suivant' non trouvé, fin de la pagination.")
                    break
                except RuntimeError as e:
                    self.logger.error(f"Erreur lors de la pagination : {e}")
                    raise RuntimeError("Échec de l'extraction")
                except Exception as e:
                    self.logger.error(f"Erreur lors de la pagination : {e}")
                    break

        # Finalisation
        if not datas:
            self.logger.warning("Aucune donnée collectée.")
            return

        self.logger.info(f"Concaténation de {len(datas)} DataFrames...")
        df_final = pd.concat(datas, ignore_index=True)
        df_final['JOUR'] = start_date.strftime('%d/%m/%Y')
        df_final['ANNEE'] = start_date.strftime('%Y')
        df_final['MOIS'] = start_date.strftime('%m')

        try:
            self.logger.info(f"Enregistrement du fichier PMU Senegal du {start_date} ...")
            filename = "Pmu_Senegal_lots_" + str(start_date) + ".csv"
            # todo: update path
            destination = Path(self.config["download_path"])
            final_file = destination / filename
            df_final.to_csv(final_file, index=False, sep=';', encoding='latin1')

        except Exception as e:
            self.logger.error(f"Erreur lors de la telechargement du fichier PMU Senegal : {e}")
            raise e

    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._download_files()


def run_pmu_lots():
    env_variables_list = ["PMU_LOGIN_USERNAME", "PMU_LOGIN_PASSWORD"]
    job = ExtractPmuLots(env_variables_list)
    job.process_extraction()


if __name__ == "__main__":
    run_pmu_lots()
