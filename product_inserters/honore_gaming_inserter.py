from .base_inserter import ProductInserter
from product_queries import honore_gaming_queries
import pandas as pd
import numpy as np
import glob
from dateutil.parser import parse # Pour parser les dates dans les fichiers
from datetime import datetime, timedelta


class HonoreGamingInserter(ProductInserter):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None, base_path: str = ""):
        super().__init__(db_config, date_debut, date_fin, logger)
        self.base_path = base_path
        # date_debut et date_fin sont DD/MM/YYYY
        # Le script original utilise end_date pour nommer le fichier daily-modified... qui correspond à la date de traitement J.
        # Et start_date pour la période de données (J-1).
        # self.date_debut correspond à start_date (J-1), self.date_fin à end_date (J) du script original.

        # Convertir self.date_fin (format DD/MM/YYYY) en YYYYMMDD pour le nom du fichier principal
        try:
            day, month, year = self.date_fin.split('/')
            self.file_date_yyyymmdd = f"{year}{month}{day}"

            # Pour la requête IPMU qui utilise :current_year
            self.current_year_for_query = year

            # Pour la condition `TO_CHAR(TO_DATE(SUBSTR(DATE_REUN,1,10)),'YYYY') = TO_CHAR(SYSDATE,'YYYY')`
            # On va utiliser l'année de self.date_fin
        except ValueError:
            if logger:
                logger.error(f"Format de date_fin incorrect ({self.date_fin}) pour HonoreGaming. Attendu DD/MM/YYYY.")
            raise

        self.honore_gaming_file_pattern = rf"HONORE_GAMING/**/daily-modified-horse-racing-tickets-detailed_{self.file_date_yyyymmdd}.csv"
        # Les fichiers IPMU ne sont pas nommés avec une date dans le script original, ils sont juste lus.
        # On supposera qu'ils sont récupérés d'une autre manière ou qu'ils ont des noms fixes si nécessaire.
        # Pour l'instant, on ne gère pas la lecture de fichiers IPMU ici, car le script original
        # ne montre pas de lecture de fichier pour SRC_PRD_IPMU_DAILY ou SRC_PRD_MCI_IPMU_AGREGE.
        # Ces tables semblent être alimentées par d'autres processus ou être des tables de référence.
        # Le script `base/journalier/insertHonoregamingOnOracle.py` lit aussi le fichier daily-modified...
        # et ne montre pas de chargement de fichier pour IPMU.

    def get_queries(self) -> dict[str, str]:
        return honore_gaming_queries.get_queries()

    def _load_honore_gaming_main_file(self):
        """Charge le fichier principal d'Honore Gaming."""
        full_pattern = self.base_path + self.honore_gaming_file_pattern
        if self.logger:
            self.logger.info(f"Recherche du fichier Honore Gaming avec pattern: {full_pattern}")

        files = glob.glob(full_pattern, recursive=True)
        if not files:
            if self.logger:
                self.logger.warning(f"Aucun fichier trouvé pour Honore Gaming (pattern: {full_pattern}).")
            return False

        file_path = files[0]
        if self.logger:
            self.logger.info(f"Lecture du fichier {file_path} pour Honore Gaming.")

        try:
            data_df = pd.read_csv(file_path, sep=';', index_col=False, dtype=str)
            # Transformer les dates comme dans le script original
            if 'ReportDateTime' in data_df.columns:
                data_df['ReportDateTime'] = [parse(str(d)).strftime("%d/%m/%Y") if pd.notna(d) else None for d in data_df['ReportDateTime']]
            if 'MeetingDate' in data_df.columns:
                data_df['MeetingDate'] = [parse(str(d)).strftime("%d/%m/%Y") if pd.notna(d) else None for d in data_df['MeetingDate']]

            data_df = data_df.replace(np.nan, '')

            # Diviser l'insertion en lots si nécessaire (comme dans base/journalier/insertHonoregamingOnOracle.py)
            # La méthode `insert_dataframe_to_temp` de la classe de base utilise `executemany` qui est efficace.
            self._execute_query('truncate_temp') # Vider SRC_PRD_ALR_HONORE_GAMING
            self.insert_dataframe_to_temp(data_df) # Utilise la requête 'insert_temp' par défaut

            if self.logger:
                self.logger.info(f"Données de {file_path} chargées dans SRC_PRD_ALR_HONORE_GAMING.")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors du chargement du fichier {file_path}: {e}")
            return False

    def load_data(self, data: pd.DataFrame = None): # data n'est pas utilisé ici
        """
        Charge les données pour HonoreGaming.
        Les opérations sur tables temporaires sont gérées par _load_honore_gaming_main_file.
        """
        # La connexion est gérée par _load_honore_gaming_main_file et ensuite ici.
        # Pour éviter les ouvertures/fermetures multiples, on pourrait la gérer plus globalement dans process.

        # Les tables SRC_PRD_IPMU_DAILY et SRC_PRD_MCI_IPMU_AGREGE ne sont pas alimentées par des fichiers
        # dans les scripts fournis (elles sont utilisées par des requêtes mais leur source n'est pas un CSV lu ici).
        # On suppose qu'elles sont déjà peuplées ou qu'un autre mécanisme s'en charge.
        # Le script ne truncate/insert pas dans ces tables.

        self._connect_db() # Assurer une connexion pour les opérations suivantes
        try:
            queries = self.get_queries()
            # Les dates pour les requêtes delete/merge sont self.date_debut et self.date_fin (format DD/MM/YYYY)
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
            params_ipmu = {'current_year': self.current_year_for_query}


            # --- Partie principale Honore Gaming (basée sur SRC_PRD_ALR_HONORE_GAMING) ---
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates)

            if 'insert_dim_terminal' in queries: # Se base sur SRC_PRD_ALR_HONORE_GAMING
                self._execute_query('insert_dim_terminal')

            if 'insert_main_fait_vente' in queries: # Se base sur SRC_PRD_ALR_HONORE_GAMING
                self._execute_query('insert_main_fait_vente')
            if 'insert_main_fait_lots' in queries: # Se base sur SRC_PRD_ALR_HONORE_GAMING
                self._execute_query('insert_main_fait_lots')

            # --- Partie IPMU (utilise SRC_PRD_IPMU_DAILY qui est supposée pré-existante/alimentée ailleurs) ---
            if 'insert_main_fait_lots_ipmu' in queries:
                 self._execute_query('insert_main_fait_lots_ipmu', params=params_ipmu)

            # --- Merge Masse Commune (utilise SRC_PRD_ALR_HONORE_GAMING et SRC_PRD_IPMU_DAILY) ---
            if 'merge_masse_commune' in queries:
                self._execute_query('merge_masse_commune', params=params_ipmu) # current_year est nécessaire

            # --- Merge DTM Masse Commune IPMU (utilise SRC_PRD_MCI_IPMU_AGREGE, supposée pré-existante) ---
            if 'insert_dtm_masse_commune_ipmu' in queries:
                self._execute_query('insert_dtm_masse_commune_ipmu')
            if 'truncate_temp_mci_ipmu_agrege' in queries: # Nettoie cette table après usage
                self._execute_query('truncate_temp_mci_ipmu_agrege')


            # --- Archivage et Nettoyage des tables temporaires Honore Gaming ---
            # (SRC_PRD_ALR_HONORE_GAMING et SRC_PRD_IPMU_DAILY)
            if 'delete_ar_honore_gaming_prd' in queries:
                self._execute_query('delete_ar_honore_gaming_prd') # Se base sur le contenu de la temp principale
            if 'insert_ar_honore_gaming_prd' in queries:
                self._execute_query('insert_ar_honore_gaming_prd')

            if 'delete_ar_ipmu_prd' in queries:
                 self._execute_query('delete_ar_ipmu_prd') # Se base sur le contenu de la temp IPMU
            if 'insert_ar_ipmu_prd' in queries:
                 self._execute_query('insert_ar_ipmu_prd')

            if 'truncate_temp_ipmu_daily' in queries: # Nettoie la table temp IPMU après usage/archivage
                 self._execute_query('truncate_temp_ipmu_daily')
            if 'cleanup_temp_honore_gaming' in queries: # Nettoie la table temp principale Honore Gaming
                 self._execute_query('cleanup_temp_honore_gaming')


            # --- Merge DTM CA Daily ---
            if 'merge_dtm_ca_daily_plr' in queries:
                self._execute_query('merge_dtm_ca_daily_plr', params=params_dates)
            if 'merge_dtm_ca_daily_alr' in queries:
                self._execute_query('merge_dtm_ca_daily_alr', params=params_dates)

            if self.logger:
                self.logger.info(f"Processus load_data (opérations BDD) complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()


    def process(self, source_file_path: str = None): # generalDirectory
        """
        Orchestre la lecture des fichiers et le chargement des données pour HonoreGaming.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Honore Gaming. Période: {self.date_debut} - {self.date_fin}")

        # Gérer la connexion BDD au niveau process pour les chargements de fichiers temporaires
        main_file_loaded = False
        self._connect_db()
        try:
            # Truncate initial de SRC_PRD_ALR_HONORE_GAMING avant de lire les fichiers
            # car le script base/journalier le fait avant la boucle de lecture.
            queries = self.get_queries()
            if 'truncate_temp' in queries:
                 self._execute_query('truncate_temp')

            # Le script base/journalier/insertHonoregamingOnOracle.py boucle sur une plage de dates
            # pour lire plusieurs fichiers daily-modified... si start_date et end_date couvrent plusieurs jours.
            # Notre modèle actuel est un fichier par jour (le fichier du jour J, contenant les données de J-1).
            # Si le besoin est de charger plusieurs jours, cette logique de boucle sur les dates de fichiers
            # devrait être ici. Pour l'instant, on charge un seul fichier basé sur self.file_date_yyyymmdd.
            main_file_loaded = self._load_honore_gaming_main_file()

        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur critique pendant le chargement du fichier principal Honore Gaming: {e}")
            self._close_db()
            raise
        finally:
            if self.conn: # Fermer la connexion après le chargement du fichier temp
                self._close_db()

        if not main_file_loaded:
            if self.logger:
                self.logger.warning(f"Fichier principal Honore Gaming non chargé. Certaines opérations BDD pourraient être affectées.")

        # Appeler la logique de base de données principale (delete, insert, merge, archive)
        # load_data() gère sa propre connexion.
        self.load_data()

        if self.logger:
            self.logger.info(f"Fin du traitement Honore Gaming.")
