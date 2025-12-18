from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import datetime
import pandas as pd
import os
import sys

# === CONFIGURATION DU NAVIGATEUR ===
def openBrowser():
    for i in range(5):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--allow-insecure-localhost")
            chrome_options.add_argument("--disable-features=SafeBrowsingEnhancedProtection")

            # Dossier de téléchargement personnalisé
            download_path = r"K:\DATA_FICHIERS\USSD"
            chrome_options.add_experimental_option("prefs", {
                "download.default_directory": download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })

            chromedriver_path = r"C:\Users\optiware\Documents\jupyterNotebook\chromedriver.exe"
            service = Service(executable_path=chromedriver_path)

            browser = webdriver.Chrome(options=chrome_options)

            # Appliquer le comportement de téléchargement
            browser.execute_cdp_cmd("Page.setDownloadBehavior", {
                "behavior": "allow",
                "downloadPath": download_path
            })

            return browser
        except Exception as e:
            print(f"Tentative {i+1} échouée : {e}")
    sys.exit("Impossible de lancer Chrome avec le WebDriver fourni")

driver = openBrowser()

def clear_cookies():
    driver.delete_all_cookies()

def connectGitech():
    url = "http://dvs2.dyndns.biz:16800/backendcdr/"
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "identifiantInput"))).send_keys("lonase")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "mdpInput"))).send_keys("mdpL0n@Se")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "connexion"))).click()
        print("Connecté.")
    except Exception as e:
        print(f"Échec de connexion : {e}")

def nettoyer_valeur(val):
    val = val.replace("FCFA", "").replace(" ", "").replace(",", ".")
    try:
        float_val = float(val)
        return int(float_val) if float_val.is_integer() else float_val
    except ValueError:
        return 0

def telecharger_donnees_par_date(date_a_tester):
    try:
        driver.get("http://dvs2.dyndns.biz:16800/backendcdr/")
        date_str = date_a_tester.strftime("%Y-%m-%d")

        driver.execute_script(f"document.getElementsByName('dateDeb')[0].value = '{date_str}';")
        driver.execute_script(f"document.getElementsByName('dateFin')[0].value = '{date_str}';")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'].chercher"))
        ).click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.tab_suivi")))

        try:
            paragraphe_info = driver.find_element(By.XPATH, "//p[following-sibling::table[@class='tab_suivi']]")
            elements_b = paragraphe_info.find_elements(By.TAG_NAME, "b")
            infos_dict = dict(zip(["Total Appels", "Total Minutes", "Total CA"],
                                  [b.text.strip() for b in elements_b[:3]]))
        except Exception:
            infos_dict = {"Total Appels": "", "Total Minutes": "", "Total CA": ""}

        donnees = []

        # Gestion de la pagination
        try:
            select_elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "selectPage")))
            total_pages = len(select_elem.find_elements(By.TAG_NAME, "option"))
        except:
            total_pages = 1

        for page in range(1, total_pages + 1):
            if page > 1:
                select_elem = driver.find_element(By.ID, "selectPage")
                Select(select_elem).select_by_value(str(page))
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.tab_suivi")))

            table = driver.find_element(By.CSS_SELECTOR, "table.tab_suivi")
            lignes = table.find_elements(By.TAG_NAME, "tr")

            for ligne in lignes:
                colonnes = ligne.find_elements(By.TAG_NAME, "td")
                if len(colonnes) >= 5:
                    date_appel = colonnes[1].text.strip()
                    donnees.append({
                        "Date Appel": date_appel,
                        "Jour": date_appel.split(" ")[0],
                        "Numéro Serveur": colonnes[2].text.strip(),
                        "Numéro Appelant": colonnes[3].text.strip(),
                        "Durée Appel": colonnes[4].text.strip(),
                        "Total Appels": "",
                        "Total CA": ""
                    })

        if donnees:
            donnees[0]["Total Appels"] = infos_dict.get("Total Appels", "")
            donnees[0]["Total CA"] = infos_dict.get("Total CA", "")

        df = pd.DataFrame(donnees)

        # Nettoyage de la colonne Total Appels
        df["Total Appels"] = pd.to_numeric(df["Total Appels"].astype(str).str.replace(" ", "").str.replace(",", ""),
                                           errors='coerce').astype("Int64")
       # Nettoyage de la colonne Total CA
        df["Total CA"] = pd.to_numeric(
            df["Total CA"].astype(str).str.replace("FCFA", "").str.replace(" ", "").str.replace(",", ""),
            errors='coerce').apply(lambda x: int(x) if pd.notna(x) and x == int(x) else x).astype("Int64")
       # Repertoire cible
        chemin_fichier = os.path.join(r"K:\DATA_FICHIERS\USSD", f"GFM_CDR_DETAILS_{date_str}.csv")
        df.to_csv(chemin_fichier, index=False, sep=';', encoding='utf-8-sig')
        print(f"Données sauvegardées : {chemin_fichier}")

    except Exception as e:
        print(f"Erreur traitement {date_str} : {e}")

def supprimer_fichiers_temp(dossier):
    for fichier in os.listdir(dossier):
        if fichier.endswith(".crdownload"):
            try:
                os.remove(os.path.join(dossier, fichier))
                print(f"Fichier temporaire supprimé : {fichier}")
            except Exception as e:
                print(f"Erreur suppression fichier : {fichier} | {e}")

def boucle_sur_dates(start_date=None, end_date=None):
    if start_date and end_date:
        try:
            d_start = datetime.datetime.strptime(start_date, "%d/%m/%Y").dat()
            d_end = datetime.datetime.strptime(end_date, "%d/%m/%Y").date()
            current = d_start
            while current <= d_end:
                telecharger_donnees_par_date(current)
                current += datetime.timedelta(days=1)
        except Exception as e:
            print(f"Erreur dans les dates : {e}")
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        telecharger_donnees_par_date(yesterday)

# === EXÉCUTION ===
clear_cookies()
connectGitech()
boucle_sur_dates('01/03/2025', '31/03/2025') # mettre la plage de date à extraire ici Exemple:  boucle_sur_dates('01/04/2025', '30/04/2025') ou laisser à defaut Exemple : boucle_sur_dates(None , None)
driver.quit()
supprimer_fichiers_temp(r"K:\DATA_FICHIERS\USSD")
