from .base_inserter import ProductInserter
from product_queries import mini_shop_queries
import subprocess
import os
from datetime import datetime

class MiniShopInserter(ProductInserter):
    def get_queries(self) -> dict[str, str]:
        # Les requêtes SQL sont dans le script externe.
        return mini_shop_queries.get_queries()

    def load_data(self, data=None): # data n'est pas utilisé
        """
        Exécute le script externe pour MiniShop.
        """
        script_path = mini_shop_queries.get_external_script_path()
        if not script_path:
            if self.logger:
                self.logger.error(f"Chemin du script externe non défini pour MiniShopInserter.")
            raise ValueError("Chemin du script externe non défini pour MiniShopInserter.")

        if self.logger:
            self.logger.info(f"Exécution du script externe pour MiniShop: {script_path}")
            self.logger.info(f"Période (pour information, non passé au script): {self.date_debut} - {self.date_fin}")
            self.logger.info(f"DB Config (pour information, non passé au script): {self.db_config.get('host')}")

        try:
            if not os.path.exists(script_path):
                msg = f"Le script externe {script_path} n'a pas été trouvé."
                if self.logger: self.logger.error(msg)
                raise FileNotFoundError(msg)

            # Comme pour PmuSenegal, le script original utilise exec.
            # Nous allons simuler cela en passant les dates si le script externe les attend globalement.
            # Le script insertMiniShopOracle_bis.py semble définir ses propres dates (start_date = yesterday, end_date = today)
            # et ne pas dépendre de dates globales passées.
            # Il gère également sa propre connexion.

            script_globals = globals().copy()
            # Si le script externe s'attend à ce que start_date et end_date soient définis globalement:
            # script_globals['start_date'] = datetime.strptime(self.date_debut, '%d/%m/%Y').date()
            # script_globals['end_date'] = datetime.strptime(self.date_fin, '%d/%m/%Y').date()
            # Cependant, en analysant insertMiniShopOracle_bis.py (si possible), il semble qu'il calcule ses propres dates.

            with open(script_path, 'r') as f:
                script_content = f.read()

            if self.logger: self.logger.info(f"Contenu du script {script_path} va être exécuté.")

            exec(script_content, script_globals)

            if self.logger:
                self.logger.info(f"Script externe {script_path} exécuté avec succès pour MiniShop.")

        except FileNotFoundError:
            raise
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de l'exécution du script externe {script_path} pour MiniShop: {e}")
            raise

    def process(self, source_file_path: str = None): # source_file_path n'est pas utilisé
        """
        Orchestre le traitement pour MiniShop.
        """
        if self.logger:
            self.logger.info(f"Début du traitement MiniShop (via script externe).")

        self.load_data()

        if self.logger:
            self.logger.info(f"Fin du traitement MiniShop.")
