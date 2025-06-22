from .base_inserter import ProductInserter
from product_queries import gitech_casino_queries
import pandas as pd

class GitechCasinoInserter(ProductInserter):
    def get_queries(self) -> dict[str, str]:
        return gitech_casino_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour Gitech Casino.
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée pour GitechCasinoInserter. Le chargement sera partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            if data is not None and not data.empty:
                # 1. Truncate table temporaire (src_prd_casino_gitech)
                if 'truncate_temp' in queries: # La clé est truncate_temp, mais la requête peut être différente
                    self._execute_query('truncate_temp')

                # 2. Insert into table temporaire
                self.insert_dataframe_to_temp(data)
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
                self._execute_query('insert_main_fait_vente')
            if 'insert_main_fait_lots' in queries:
                self._execute_query('insert_main_fait_lots')

            # 5. Opération de MERGE pour dtm_ca_daily
            if 'merge_dtm_ca_daily' in queries:
                 self._execute_query('merge_dtm_ca_daily', params=params_dates)

            # 6. Nettoyage de la table temporaire
            if data is not None and not data.empty and 'cleanup_temp' in queries: # Ex: delete from optiwaretemp.src_prd_casino_gitech
                 self._execute_query('cleanup_temp')

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str):
        """
        Orchestre la lecture du fichier et le chargement des données pour Gitech Casino.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Gitech Casino pour le fichier : {source_file_path}")
            self.logger.info(f"Période du {self.date_debut} au {self.date_fin}")

        data_df = None
        try:
            data_df = pd.read_csv(source_file_path, sep=';', index_col=False, dtype=str)
            # Colonnes du CSV: Non spécifié explicitement, mais la requête insert_temp est :
            # INSERT INTO OPTIWARETEMP.src_prd_casino_gitech( "IDJEU","NOMJEU","DATEVENTE","VENTE","PAIEMENT","POURCENTAGEPAIEMENT")
            # On suppose que le CSV a ces colonnes ou des colonnes qui peuvent y être mappées.
            # Si les noms de colonnes du CSV sont différents, il faudra les renommer ici.
            # Exemple: data_df.rename(columns={'AncienNom': 'IDJEU', ...}, inplace=True)

            # Pour l'instant, on assume que les noms correspondent ou que le DataFrame est déjà préparé.
            # S'assurer que les colonnes attendues sont présentes
            expected_cols = ["IDJEU","NOMJEU","DATEVENTE","VENTE","PAIEMENT","POURCENTAGEPAIEMENT"]
            # data_df = data_df[expected_cols] # Décommenter si le CSV peut avoir plus de colonnes

            if self.logger:
                self.logger.info(f"{len(data_df)} lignes lues depuis {source_file_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture du fichier {source_file_path} pour {self.__class__.__name__}: {e}")
            raise

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Gitech Casino pour le fichier : {source_file_path}")
