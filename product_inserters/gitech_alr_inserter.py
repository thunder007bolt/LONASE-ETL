from .base_inserter import ProductInserter
from product_queries import gitech_alr_queries # Ce fichier contient les requêtes pour les deux
import pandas as pd

class GitechAlrInserter(ProductInserter): # Gère ALR Gitech et PMU Online (Gitech)
    def get_queries(self) -> dict[str, str]:
        return gitech_alr_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour Gitech (ALR et PMU Online).
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée fournie pour GitechAlrInserter. Le chargement sera partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            if data is not None and not data.empty:
                # 1. Truncate table temporaire (GITECH)
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')

                # 2. Insert into table temporaire
                self.insert_dataframe_to_temp(data)

                # 2.1 Insert into dim_terminal pour Gitech (principalement ALR, idsysteme 81)
                # Le script original ne semble pas avoir de logique d'insertion dim_terminal pour PMU Online (idsysteme 123) ici.
                if 'insert_dim_terminal_gitech' in queries:
                    self._execute_query('insert_dim_terminal_gitech')
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, les étapes liées à la table temporaire sont sautées.")


            # --- Traitement ALR Gitech (IDJEUX = 25, IDSYSTEME = 81) ---
            if 'delete_main_fait_vente_alr' in queries:
                self._execute_query('delete_main_fait_vente_alr', params=params_dates)
            if 'delete_main_fait_lots_alr' in queries:
                self._execute_query('delete_main_fait_lots_alr', params=params_dates)
            if 'insert_main_fait_vente_alr' in queries:
                self._execute_query('insert_main_fait_vente_alr')
            if 'insert_main_fait_lots_alr' in queries:
                self._execute_query('insert_main_fait_lots_alr')
            if 'merge_dtm_ca_daily_alr' in queries:
                 self._execute_query('merge_dtm_ca_daily_alr', params=params_dates)

            # --- Traitement PMU Online (Gitech) (IDJEUX = 223, IDSYSTEME = 123) ---
            # Les terminaux pour idsysteme 123 doivent exister. Le script original ne les insère pas ici.
            if 'delete_main_fait_vente_pmu_online' in queries:
                self._execute_query('delete_main_fait_vente_pmu_online', params=params_dates)
            if 'delete_main_fait_lots_pmu_online' in queries:
                self._execute_query('delete_main_fait_lots_pmu_online', params=params_dates)
            if 'insert_main_fait_vente_pmu_online' in queries:
                self._execute_query('insert_main_fait_vente_pmu_online')
            if 'insert_main_fait_lots_pmu_online' in queries:
                self._execute_query('insert_main_fait_lots_pmu_online')
            if 'merge_dtm_ca_daily_pmu_online' in queries:
                 self._execute_query('merge_dtm_ca_daily_pmu_online', params=params_dates)

            # Archiver et nettoyer la table temporaire (commun aux deux)
            if data is not None and not data.empty:
                if 'delete_ar_gitech_prd' in queries:
                    self._execute_query('delete_ar_gitech_prd') # Se base sur le contenu de la temp pour les dates
                if 'insert_ar_gitech_prd' in queries:
                    self._execute_query('insert_ar_gitech_prd')
                if 'truncate_temp' in queries: # Vide la table GITECH
                    self._execute_query('truncate_temp')

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str):
        """
        Orchestre la lecture du fichier et le chargement des données pour Gitech ALR et PMU Online.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Gitech ALR/PMU Online pour le fichier : {source_file_path}")
            self.logger.info(f"Période du {self.date_debut} au {self.date_fin}")

        data_df = None
        try:
            data_df = pd.read_csv(source_file_path, sep=';', index_col=False, dtype=str)
            # Colonnes du CSV: 'Agences', 'Operateur', 'Date vente', 'Vente', 'Annulation', 'Paiement'
            # Requête insert_temp: "Agences","Operateurs","date_de_vente","Recette_CFA","Annulation_CFA","Paiements_CFA"
            rename_map = {
                'Operateur': 'Operateurs',
                'Date vente': 'date_de_vente',
                'Vente': 'Recette_CFA',
                'Annulation': 'Annulation_CFA',
                'Paiement': 'Paiements_CFA'
            }
            data_df.rename(columns=rename_map, inplace=True)

            # S'assurer que les colonnes attendues sont présentes
            expected_cols = ["Agences","Operateurs","date_de_vente","Recette_CFA","Annulation_CFA","Paiements_CFA"]
            for col in expected_cols:
                if col not in data_df.columns:
                    data_df[col] = ""
            data_df = data_df[expected_cols]


            if self.logger:
                self.logger.info(f"{len(data_df)} lignes lues et préparées depuis {source_file_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture ou préparation du fichier {source_file_path} pour {self.__class__.__name__}: {e}")
            raise

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Gitech ALR/PMU Online pour le fichier : {source_file_path}")
