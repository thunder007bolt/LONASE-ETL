from .base_inserter import ProductInserter
from product_queries import virtuel_amabel_queries
import pandas as pd
import numpy as np

class VirtuelAmabelInserter(ProductInserter):
    def get_queries(self) -> dict[str, str]:
        return virtuel_amabel_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour VirtuelAmabel.
        Surcharge la méthode de base pour l'ordre spécifique des opérations.
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée fournie pour VirtuelAmabelInserter. Le chargement sera partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            if data is not None and not data.empty:
                # 1. Truncate/delete from table temporaire (SRC_PRD_SUNUBET)
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')

                # 2. Insert into table temporaire
                self.insert_dataframe_to_temp(data)

                # 2.1 Insert into dim_terminal (basé sur la table temp)
                if 'insert_dim_terminal' in queries:
                    self._execute_query('insert_dim_terminal')

                # 2.2 Update annulations in temp table
                if 'update_temp_annulations' in queries:
                    self._execute_query('update_temp_annulations')
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, les étapes liées à la table temporaire sont sautées.")


            # 3. Delete from table principale (FAIT_VENTE et FAIT_LOTS)
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates)

            # 4. Insert into table principale from table temporaire (FAIT_VENTE et FAIT_LOTS)
            if 'insert_main_fait_vente' in queries:
                self._execute_query('insert_main_fait_vente') # Ces requêtes se basent sur la table temp et DIM_TEMPS
            if 'insert_main_fait_lots' in queries:
                self._execute_query('insert_main_fait_lots')

            # 5. Opération de MERGE pour dtm_ca_daily
            if 'merge_dtm_ca_daily' in queries:
                 self._execute_query('merge_dtm_ca_daily', params=params_dates)

            # 6. Archiver et nettoyer la table temporaire
            if data is not None and not data.empty:
                if 'delete_ar_sunubet_prd' in queries: # Supprime les enregistrements du jour de l'archive
                    self._execute_query('delete_ar_sunubet_prd') # Cette requête n'utilise pas de params, elle se base sur le contenu de la temp
                if 'insert_ar_sunubet_prd' in queries: # Insère le contenu actuel de la temp dans l'archive
                    self._execute_query('insert_ar_sunubet_prd')
                if 'truncate_temp' in queries: # Vide la table temporaire
                    self._execute_query('truncate_temp')


            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str):
        """
        Orchestre la lecture du fichier et le chargement des données pour VirtuelAmabel.
        """
        if self.logger:
            self.logger.info(f"Début du traitement VirtuelAmabel pour le fichier : {source_file_path}")
            self.logger.info(f"Période du {self.date_debut} au {self.date_fin}")

        data_df = None
        try:
            data_df = pd.read_csv(source_file_path, sep=';', index_col=False, dtype=str)
            # Colonnes attendues par insert_temp: "NOM", "Total enjeu", "Total Ticket Virtuel", "Total Paiement","Date Vente"
            # Le script original fait: data = data.replace(np.nan, '')
            data_df = data_df.replace(np.nan, '')
            if self.logger:
                self.logger.info(f"{len(data_df)} lignes lues depuis {source_file_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture du fichier {source_file_path} pour {self.__class__.__name__}: {e}")
            raise

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement VirtuelAmabel pour le fichier : {source_file_path}")
