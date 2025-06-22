from .base_inserter import ProductInserter
from product_queries import acajou_pick3_grattage_queries
import pandas as pd
import glob
import numpy as np

class AcajouPick3GrattageInserter(ProductInserter):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None, base_path: str = ""):
        super().__init__(db_config, date_debut, date_fin, logger)
        self.base_path = base_path # K:\DATA_FICHIERS\
        self.pick3_file_pattern = r"ACAJOU/PICK3/**/Listing_Tickets_Pick3 {date_str}_{date_str}.csv"
        self.grattage_file_pattern = r"ACAJOU/GRATTAGE/**/Listing_Tickets_Grattage {date_str}_{date_str}.csv"

    def get_queries(self) -> dict[str, str]:
        return acajou_pick3_grattage_queries.get_queries()

    def _load_single_acajou_type_to_temp(self, file_pattern_template: str, product_name_in_file: str, query_truncate_key: str, query_insert_key: str):
        """Charge un type de fichier Acajou (Pick3 ou Grattage) dans la table temporaire SRC_PRD_ACACIA."""

        # La date pour les fichiers Acajou est au format YYYYMMDD
        try:
            day, month, year = self.date_debut.split('/')
            date_for_file = f"{year}{month}{day}"
        except ValueError:
            if self.logger:
                self.logger.error(f"Format de date_debut incorrect ({self.date_debut}) pour Acajou. Attendu DD/MM/YYYY.")
            raise ValueError(f"Format de date_debut incorrect ({self.date_debut}) pour Acajou.")

        full_file_pattern = self.base_path + file_pattern_template.format(date_str=date_for_file)
        if self.logger:
            self.logger.info(f"Recherche du fichier Acajou ({product_name_in_file}) avec pattern: {full_file_pattern}")

        files = glob.glob(full_file_pattern, recursive=True)
        if not files:
            if self.logger:
                self.logger.warning(f"Aucun fichier trouvé pour Acajou {product_name_in_file} (pattern: {full_file_pattern}).")
            return False

        file_path = files[0]
        if self.logger:
            self.logger.info(f"Lecture du fichier {file_path} pour Acajou {product_name_in_file}")

        try:
            data_df = pd.read_csv(file_path, sep=';', index_col=False, dtype=str)
            # Colonnes du CSV: 'Date Created', 'Msisdn', 'Ticket ID', 'Purchase Method','Collection', 'Status', 'Gross Payout', 'Produit'
            # Requête INSERT: "DATE_HEURE","TELEPHONE","REFERENCE_TICKET","PURCHASE_METHOD","MONTANT","STATUS","LOTS_A_PAYES","PRODUIT"
            rename_map = {
                'Date Created': 'DATE_HEURE',
                'Msisdn': 'TELEPHONE',
                'Ticket ID': 'REFERENCE_TICKET',
                'Purchase Method': 'PURCHASE_METHOD',
                'Collection': 'MONTANT',
                'Status': 'STATUS',
                'Gross Payout': 'LOTS_A_PAYES',
                'Produit': 'PRODUIT' # La colonne PRODUIT existe déjà dans le CSV
            }
            data_df.rename(columns=rename_map, inplace=True)

            # S'assurer que le nom du produit est correct (parfois il peut manquer ou être différent)
            # data_df['PRODUIT'] = product_name_in_file # Forcer le nom du produit si nécessaire

            # S'assurer que toutes les colonnes de la requête sont présentes
            expected_cols_for_insert = ["DATE_HEURE","TELEPHONE","REFERENCE_TICKET","PURCHASE_METHOD","MONTANT","STATUS","LOTS_A_PAYES","PRODUIT"]
            for col in expected_cols_for_insert:
                if col not in data_df.columns:
                    data_df[col] = ""
            data_df = data_df[expected_cols_for_insert]
            data_df = data_df.replace(np.nan, '')

            # Exécuter la suppression spécifique pour ce type avant d'insérer
            self._execute_query(query_truncate_key)
            self.insert_dataframe_to_temp(data_df, query_key=query_insert_key)
            if self.logger:
                self.logger.info(f"Données de {file_path} (Acajou {product_name_in_file}) chargées dans SRC_PRD_ACACIA.")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors du chargement du fichier {file_path} (Acajou {product_name_in_file}): {e}")
            return False

    def load_data(self, data: pd.DataFrame = None): # data n'est pas utilisé ici
        """
        Charge les données pour Acajou Pick3 et Grattage.
        Les chargements des fichiers Pick3 et Grattage dans la table temporaire sont gérés par la méthode `process`.
        Cette méthode se concentre sur les opérations BDD après le remplissage de la table temporaire.
        """
        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            # Les suppressions et insertions se basent sur le contenu de SRC_PRD_ACACIA
            # qui a été rempli par _load_single_acajou_type_to_temp dans process()

            # 3. Delete from table principale (FAIT_VENTE et FAIT_LOTS) - exclut le terminal de Pari Sportif
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates)

            # 4. Insert into table principale from table temporaire (FAIT_VENTE et FAIT_LOTS)
            if 'insert_main_fait_vente' in queries:
                self._execute_query('insert_main_fait_vente')
            if 'insert_main_fait_lots' in queries:
                self._execute_query('insert_main_fait_lots')

            # 5. Archive et Nettoyage
            if 'insert_ar_acacia_prd' in queries: # Archive ce qui est dans la temp (Pick3 et Grattage)
                 self._execute_query('insert_ar_acacia_prd')
            # La requête AR_ACACIA_PRD_2 est complexe et omise pour l'instant comme dans le script original.

            if 'cleanup_temp' in queries: # Vide SRC_PRD_ACACIA des données Pick3/Grattage
                 self._execute_query('cleanup_temp')

            # 6. Opérations de MERGE pour dtm_ca_daily (spécifiques à Pick3 et Grattage par IDTERMINAL)
            if 'merge_dtm_ca_daily_pick3' in queries:
                 self._execute_query('merge_dtm_ca_daily_pick3', params=params_dates)
            if 'merge_dtm_ca_daily_grattage' in queries:
                 self._execute_query('merge_dtm_ca_daily_grattage', params=params_dates)

            if self.logger:
                self.logger.info(f"Processus load_data (opérations BDD) complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str = None): # source_file_path (generalDirectory) est utilisé via self.base_path
        """
        Orchestre la lecture des fichiers Pick3 et Grattage et le chargement des données.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Acajou Pick3 & Grattage. Période: {self.date_debut} - {self.date_fin}")

        pick3_loaded = False
        grattage_loaded = False

        # Connexion BDD pour les opérations sur les tables temporaires
        self._connect_db()
        try:
            # Charger Pick3
            pick3_loaded = self._load_single_acajou_type_to_temp(
                file_pattern_template=self.pick3_file_pattern,
                product_name_in_file="Pick3", # Ce nom est utilisé pour le log, le fichier CSV a déjà une colonne 'Produit'
                query_truncate_key='truncate_temp_pick3', # Supprime seulement les Pick3 de la temp
                query_insert_key='insert_temp_pick3'
            )
            # Charger Grattage
            grattage_loaded = self._load_single_acajou_type_to_temp(
                file_pattern_template=self.grattage_file_pattern,
                product_name_in_file="Grattage",
                query_truncate_key='truncate_temp_grattage', # Supprime seulement les Grattage de la temp
                query_insert_key='insert_temp_grattage'
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur critique pendant le chargement des fichiers Pick3/Grattage: {e}")
            self._close_db() # S'assurer de fermer la connexion en cas d'erreur ici
            raise
        finally:
            # Fermer la connexion utilisée pour les tables temporaires si elle n'est pas déjà fermée.
            if self.conn:
                self._close_db()

        if not (pick3_loaded or grattage_loaded):
            if self.logger:
                self.logger.warning(f"Aucun fichier Pick3 ou Grattage trouvé pour la date {self.date_debut}. "
                                 "Les opérations sur la base de données principale seront exécutées mais pourraient ne rien traiter.")

        # Appeler la logique de base de données principale (delete, insert, merge, archive)
        # load_data() gère sa propre connexion.
        self.load_data()

        if self.logger:
            self.logger.info(f"Fin du traitement Acajou Pick3 & Grattage.")
