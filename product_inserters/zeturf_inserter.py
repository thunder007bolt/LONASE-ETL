from .base_inserter import ProductInserter
from product_queries import zeturf_queries
import pandas as pd
import numpy as np

class ZeturfInserter(ProductInserter):
    def get_queries(self) -> dict[str, str]:
        return zeturf_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour Zeturf.
        Surcharge la méthode de base pour l'ordre spécifique des opérations Zeturf.
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée fournie pour ZeturfInserter. Le chargement sera partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()

            if data is not None and not data.empty:
                # 1. Truncate/delete from table temporaire (dans les requêtes Zeturf, c'est un delete)
                if 'truncate_temp' in queries: # Le nom de la clé est 'truncate_temp' mais la requête est un DELETE
                    self._execute_query('truncate_temp')

                # 2. Insert into table temporaire
                self.insert_dataframe_to_temp(data)
            else:
                 if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, les étapes truncate_temp et insert_temp sont sautées.")


            # 3. Delete from table principale (FAIT_VENTE et FAIT_LOTS)
            params_delete = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_delete)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_delete)

            # 4. Insert into table principale from table temporaire (FAIT_VENTE et FAIT_LOTS)
            if 'insert_main_fait_vente' in queries:
                self._execute_query('insert_main_fait_vente')
            if 'insert_main_fait_lots' in queries:
                self._execute_query('insert_main_fait_lots')

            # 5. Opération de MERGE pour dtm_ca_daily
            params_merge = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
            if 'merge_dtm_ca_daily' in queries:
                 self._execute_query('merge_dtm_ca_daily', params=params_merge)

            # 6. Truncate/delete from table temporaire (après son utilisation)
            if data is not None and not data.empty and 'truncate_temp' in queries:
                 self._execute_query('truncate_temp')

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str):
        """
        Orchestre la lecture du fichier et le chargement des données pour Zeturf.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Zeturf pour le fichier : {source_file_path}")
            self.logger.info(f"Période du {self.date_debut} au {self.date_fin}")

        data_df = None
        try:
            data_df = pd.read_csv(source_file_path, sep=';', index_col=False, dtype=str)
            # Renommer la colonne si elle contient des caractères problématiques après la lecture
            # Colonnes attendues par la requête insert_temp:
            # "HIPPODROME","COURSE", "DEPART", "PARIS", "ENJEUX", "ANNULATIONS", "MARGE","DATE_DU_DEPART"
            # Le script original fait: data = pd.DataFrame(data,columns=['Hippodrome', 'Course', 'Départ', 'Paris', 'Enjeux', 'Annulations','Marge', 'Date du dÃ©part'])
            # Cela suggère que le nom de la dernière colonne peut varier.
            # Pour la robustesse, on peut essayer de mapper les noms possibles ou de se fier à l'ordre.
            # Pour l'instant, on suppose que read_csv lit correctement les noms ou que `insert_dataframe_to_temp` est flexible.
            # Si la colonne 'Date du dÃ©part' est présente, la renommer en 'DATE_DU_DEPART' si nécessaire,
            # ou s'assurer que la requête `insert_temp` utilise le nom correct.
            # La requête utilise "DATE_DU_DEPART", donc le DataFrame doit correspondre.
            if 'Date du dÃ©part' in data_df.columns:
                data_df.rename(columns={'Date du dÃ©part': 'DATE_DU_DEPART'}, inplace=True)
            elif 'Date du départ' in data_df.columns: # Au cas où l'encodage serait correct
                 data_df.rename(columns={'Date du départ': 'DATE_DU_DEPART'}, inplace=True)

            # S'assurer que toutes les colonnes nécessaires pour `insert_temp` sont présentes
            expected_cols = ["HIPPODROME","COURSE", "DEPART", "PARIS", "ENJEUX", "ANNULATIONS", "MARGE","DATE_DU_DEPART"]
            # Pour l'instant, on fait confiance à la structure du CSV. Des vérifications pourraient être ajoutées.

            data_df = data_df.replace(np.nan, '') # Remplacer NaN par des chaînes vides comme dans le script original

            if self.logger:
                self.logger.info(f"{len(data_df)} lignes lues depuis {source_file_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture ou du prétraitement du fichier {source_file_path} pour {self.__class__.__name__}: {e}")
            raise

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Zeturf pour le fichier : {source_file_path}")
