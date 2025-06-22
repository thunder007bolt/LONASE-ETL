from .base_inserter import ProductInserter
from product_queries import bwinner_queries
import pandas as pd

class BwinnerInserter(ProductInserter):
    def get_queries(self) -> dict[str, str]:
        return bwinner_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour Bwinner.
        Surcharge la méthode de base pour inclure la mise à jour du statut dans la table temporaire
        et pour s'assurer que les requêtes delete/insert utilisent les bonnes clés.
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée fournie pour BwinnerInserter. Le chargement sera partiel.")
            # On pourrait choisir de s'arrêter ici si les données sont essentielles pour toutes les étapes.
            # Pour l'instant, on continue pour permettre l'exécution des MERGEs qui ne dépendent pas de nouvelles données.

        self._connect_db()
        try:
            queries = self.get_queries()

            if data is not None and not data.empty:
                # 1. Truncate table temporaire
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')

                # 2. Insert into table temporaire
                # La méthode `insert_dataframe_to_temp` utilisera la requête 'insert_temp'
                self.insert_dataframe_to_temp(data) # S'assure que la requête 'insert_temp' est définie

                # 2.1 Mise à jour spécifique du statut pour Bwinner
                if 'update_status_temp' in queries:
                    self._execute_query('update_status_temp')
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, les étapes truncate_temp, insert_temp et update_status_temp sont sautées.")


            # 3. Delete from table principale (FAIT_VENTE et FAIT_LOTS)
            # Les dates doivent être formatées correctement pour Oracle si elles sont passées en tant que chaînes.
            # Le format 'DD/MM/YYYY' est utilisé dans les requêtes originales.
            params_delete = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_delete)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_delete)

            # 4. Insert into table principale from table temporaire (FAIT_VENTE et FAIT_LOTS)
            # Ces requêtes n'utilisent pas de paramètres de date dans leur forme actuelle car elles sélectionnent depuis la table temporaire.
            if 'insert_main_fait_vente' in queries:
                self._execute_query('insert_main_fait_vente')
            if 'insert_main_fait_lots' in queries:
                self._execute_query('insert_main_fait_lots')

            # 5. Truncate table temporaire (après son utilisation)
            if data is not None and not data.empty and 'truncate_temp' in queries: # On re-truncate seulement si on l'a utilisée
                 self._execute_query('truncate_temp') # Identique à la première truncate_temp

            # 6. Opérations de MERGE pour les agrégations
            params_merge = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
            if 'merge_dtm_ca_daily_online' in queries:
                 self._execute_query('merge_dtm_ca_daily_online', params=params_merge)
            if 'merge_dtm_ca_daily_physique' in queries:
                 self._execute_query('merge_dtm_ca_daily_physique', params=params_merge)
            if 'merge_dtm_mise_bwinner' in queries:
                 self._execute_query('merge_dtm_mise_bwinner', params=params_merge)

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str):
        """
        Orchestre la lecture du fichier et le chargement des données pour Bwinner.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Bwinner pour le fichier : {source_file_path}")
            self.logger.info(f"Période du {self.date_debut} au {self.date_fin}")

        data_df = None
        try:
            data_df = pd.read_csv(source_file_path, sep=';', index_col=False, dtype=str)
            # S'assurer que les colonnes attendues par insert_temp sont présentes.
            # La requête est: INSERT INTO optiwaretemp.SRC_PRD_BWINNERS(CREATE_TIME,PRODUCT,STAKE,"MAX PAYOUT") VALUES(:1,:2,:3,:4)
            # Le DataFrame doit avoir ces colonnes dans cet ordre pour to_records(index=False) ou être adapté pour executemany.
            # Pour l'instant, on suppose que insert_dataframe_to_temp gère la correspondance.
            if self.logger:
                self.logger.info(f"{len(data_df)} lignes lues depuis {source_file_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture du fichier {source_file_path} pour {self.__class__.__name__}: {e}")
            # Selon la politique, on pourrait vouloir s'arrêter ici ou continuer sans données.
            # Pour l'instant, on propage l'erreur si la lecture échoue car les données sont essentielles.
            raise

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Bwinner pour le fichier : {source_file_path}")
