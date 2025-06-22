from .base_inserter import ProductInserter
from product_queries import acajou_digitain_queries
import pandas as pd

class AcajouDigitainInserter(ProductInserter): # Pour Pari Sportif Acajou
    def get_queries(self) -> dict[str, str]:
        return acajou_digitain_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour Acajou Digitain (Pari Sportif).
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée fournie pour AcajouDigitainInserter. Le chargement sera partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            if data is not None and not data.empty:
                # 1. Truncate spécifique pour ne pas affecter Pick3/Grattage
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')

                # 2. Insert into table temporaire (src_prd_acacia)
                self.insert_dataframe_to_temp(data)

                # 2.1 Update produit dans la table temp
                if 'update_temp_produit' in queries:
                    self._execute_query('update_temp_produit')
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, les étapes liées à la table temporaire sont sautées.")

            # 3. Delete from table principale (FAIT_VENTE et FAIT_LOTS) - spécifique au terminal 50073
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates)

            # 4. Insert into table principale from table temporaire (FAIT_VENTE et FAIT_LOTS)
            if 'insert_main_fait_vente' in queries:
                self._execute_query('insert_main_fait_vente')
            if 'insert_main_fait_lots' in queries:
                self._execute_query('insert_main_fait_lots')

            # 5. Opération de MERGE pour dtm_ca_daily (spécifique CA_ACAJOU_PARIFOOT)
            if 'merge_dtm_ca_daily' in queries:
                 self._execute_query('merge_dtm_ca_daily', params=params_dates)

            # 6. Nettoyage final de la table temporaire pour ce produit
            if data is not None and not data.empty and 'cleanup_temp' in queries:
                 self._execute_query('cleanup_temp')


            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str):
        """
        Orchestre la lecture du fichier et le chargement des données pour Acajou Digitain.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Acajou Digitain (Pari Sportif) pour le fichier : {source_file_path}")
            self.logger.info(f"Période du {self.date_debut} au {self.date_fin}")

        data_df = None
        try:
            data_df = pd.read_csv(source_file_path, sep=';', index_col=False, dtype=str)
            # Colonnes attendues par insert_temp: "DATE_HEURE", "REFERENCE_TICKET", "TELEPHONE", "PURCHASE_METHOD", "MONTANT", "LOTS_A_PAYES","STATUS"
            # Le script original fait: data = pd.DataFrame(data,columns=['Date Created', 'Ticket ID', 'Msisdn', 'Purchase Method', 'Collection','Gross Payout', 'Status'])
            # Il faut mapper ces noms aux noms attendus par la requête.
            rename_map = {
                'Date Created': 'DATE_HEURE',
                'Ticket ID': 'REFERENCE_TICKET',
                'Msisdn': 'TELEPHONE',
                'Purchase Method': 'PURCHASE_METHOD',
                'Collection': 'MONTANT', # 'Collection' semble être le montant de la mise
                'Gross Payout': 'LOTS_A_PAYES',
                'Status': 'STATUS'
            }
            data_df.rename(columns=rename_map, inplace=True)

            # S'assurer que toutes les colonnes de la requête sont présentes, même si elles sont vides
            expected_cols_for_insert = ["DATE_HEURE", "REFERENCE_TICKET", "TELEPHONE", "PURCHASE_METHOD", "MONTANT", "LOTS_A_PAYES", "STATUS"]
            for col in expected_cols_for_insert:
                if col not in data_df.columns:
                    data_df[col] = "" # ou np.nan puis remplacer par ""

            data_df = data_df[expected_cols_for_insert] # Réordonner/sélectionner les colonnes

            if self.logger:
                self.logger.info(f"{len(data_df)} lignes lues et transformées depuis {source_file_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture ou transformation du fichier {source_file_path} pour {self.__class__.__name__}: {e}")
            raise

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Acajou Digitain (Pari Sportif) pour le fichier : {source_file_path}")
