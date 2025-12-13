import pandas as pd
import numpy as np

from base.loader import Loader
from utils.file_manipulation import move_file  # For moving files in the overridden process_loading


class LonasebetGlobalLoad(Loader):
    def __init__(self):
        name = 'lonasebet_global'
        log_file = 'logs/loader_lonasebet_global.log'
        columns = [
            "Nombre_de_paris",
            "Nombre_de_tickets",
            "Mises"
            # , "Produit_brut_des_jeux"
            # , "Rentabilite"
            , "Mises_en_cours"
            , "Gains_Joueurs"
            , "Montant_total_a_payer"
            , "Montant_total_paye"
            , "Montant_a_payer_expire"
            , "Produit_bruts_des_jeux_Cashed_Out"
            , "JOUR"
            , "ANNEE"
            , "MOIS"
            , "CANAL"
            , "CATEGORIE"]
        table_name = '[DWHPR_TEMP].[OPTIWARETEMP].[src_prd_globalLonasebet]'
        super().__init__(name, log_file, columns, table_name)
        self.db_archive_table_name = '[DWHPR_TEMP].[OPTIWARETEMP].[ar_globalLonasebet]'

    def _convert_file_to_dataframe(self, file_path):
        self.logger.info(f"Lecture du fichier transformé : {file_path}")
        try:
            df = pd.read_csv(file_path, sep=';', dtype=str, encoding='latin1')
            columns = ['Nombre de paris', 'Nombre de tickets', 'Mises', 'Mises en cours',
                       'Gains Joueurs', 'Montant total à payer', 'Montant total payé', 'Montant à payer expiré',
                       'Produit bruts des jeux Cashed Out', 'JOUR', 'ANNEE', 'MOIS', 'CANAL',
                       'CATEGORIE']
            df= df [columns]
            if len(df.columns) < 16:
                self.logger.info(file_path)
            df.replace(np.nan, '', inplace=True)
            df = df.astype(str)
            return df
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture ou de la conversion du fichier {file_path}: {e}")
            raise

    def _archive_data(self):

        if not self.cursor:
            self.logger.error("Aucun curseur de base de données disponible pour archiver les données.")
            raise Exception("Cursor not initialized for _archive_data")

        try:
            delete_query = f"""
                DELETE FROM {self.db_archive_table_name}
                WHERE CAST(jour AS DATE) IN (
                    SELECT DISTINCT CAST(jour AS DATE) FROM {self.table_name}
                )
            """
            self.logger.info(
                f"Suppression des données existantes dans {self.db_archive_table_name} pour les jours concernés...")
            self.cursor.execute(delete_query)
            self.connexion.commit()
            self.logger.info("Données existantes supprimées avec succès de la table d'archive.")

            insert_archive_query = f"""
                INSERT INTO {self.db_archive_table_name} ({', '.join([f'[{col}]' for col in self.columns])})
                SELECT {', '.join([f'[{col}]' for col in self.columns])} FROM {self.table_name}
            """
            self.logger.info(f"Archivage des données de {self.table_name} vers {self.db_archive_table_name}...")
            self.cursor.execute(insert_archive_query)
            self.connexion.commit()
            self.logger.info("Données archivées avec succès.")

        except Exception as e:
            self.logger.error(f"Erreur lors de l'archivage des données: {e}")
            raise

    def process_loading(self):

        self.logger.info(f"Démarrage du chargement")

        self._connection_to_db()

        try:
            self._delete_table_datas()

            all_data_to_load_tuples = []
            files_processed_successfully_paths = []

            for file_path in self.source_path.glob(self.file_pattern):
                try:
                    self.logger.info(f"Traitement du fichier pour consolidation : {file_path.name}")
                    df = self._convert_file_to_dataframe(file_path)
                    tuples_data = self._dataframe_to_tuples(df)
                    all_data_to_load_tuples.extend(tuples_data)
                    files_processed_successfully_paths.append(file_path)
                    self.logger.info(f"Fichier {file_path.name} consolidé pour chargement.")
                except Exception as e:
                    self.logger.error(f"Impossible de traiter le fichier {file_path.name} pour consolidation: {e}")
                    self.set_error(file_path.name)
                    move_file(file_path, self.error_path)

            if all_data_to_load_tuples:
                self.logger.info(f"Total de {len(all_data_to_load_tuples)} lignes à charger.")
                self._load_datas(all_data_to_load_tuples)

                self._archive_data()

                for file_path in files_processed_successfully_paths:
                    move_file(file_path, self.loaded_path)
                self.logger.info("Tous les fichiers traités et consolidés ont été déplacés vers le dossier 'loaded'.")
            else:
                self.logger.info("Aucune donnée à charger après consolidation des fichiers.")

            self.check_error()

        except Exception as e:
            self.logger.error(f"Erreur majeure lors du processus de chargement pour {e}")
            raise
        finally:
            if self.cursor:
                self.cursor.close()
            if self.connexion:
                self.connexion.close()
            self.logger.info("Connexion à la base de données fermée.")


def run_lonasebet_global_loader():
    loader = LonasebetGlobalLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_lonasebet_global_loader()
