from .base_inserter import ProductInserter
from product_queries import pmu_senegal_queries
import subprocess
import os

class PmuSenegalInserter(ProductInserter):
    def get_queries(self) -> dict[str, str]:
        # Les requêtes SQL sont dans le script externe.
        # Cette méthode pourrait retourner des requêtes pour des opérations post-exec si nécessaire.
        return pmu_senegal_queries.get_queries()

    def load_data(self, data=None): # data n'est pas utilisé
        """
        Exécute le script externe pour PmuSenegal.
        Les détails de connexion et les dates sont supposés être gérés par le script externe
        ou configurés dans son environnement.
        """
        script_path = pmu_senegal_queries.get_external_script_path()
        if not script_path:
            if self.logger:
                self.logger.error(f"Chemin du script externe non défini pour PmuSenegalInserter.")
            raise ValueError("Chemin du script externe non défini pour PmuSenegalInserter.")

        if self.logger:
            self.logger.info(f"Exécution du script externe pour PmuSenegal: {script_path}")
            self.logger.info(f"Période (pour information, non passé au script): {self.date_debut} - {self.date_fin}")
            self.logger.info(f"DB Config (pour information, non passé au script): {self.db_config.get('host')}")


        try:
            # Vérifier si le script existe
            if not os.path.exists(script_path):
                msg = f"Le script externe {script_path} n'a pas été trouvé."
                if self.logger: self.logger.error(msg)
                raise FileNotFoundError(msg)

            # L'exécution de scripts externes peut être risquée et dépend de l'environnement.
            # `exec(open(script_path).read())` est utilisé dans le script original.
            # Pour une meilleure isolation, subprocess pourrait être envisagé, mais `exec` est plus direct
            # pour répliquer le comportement original si le script modifie l'état global ou utilise des variables partagées.
            # Cependant, `exec` dans un long processus agent n'est pas idéal.
            # On va utiliser subprocess pour une exécution plus sûre, en supposant que le script est autonome.

            # Il faut s'assurer que l'interpréteur Python utilisé par subprocess est le même ou compatible
            # et qu'il a accès aux mêmes bibliothèques (cx_Oracle, etc.) et variables d'environnement (pour le client Oracle).

            # Le script original utilise `exec(open(...).read())` ce qui signifie qu'il s'exécute dans le même processus.
            # Pour simuler cela au plus proche tout en ayant un minimum de log:

            script_globals = globals().copy() # Copier les globaux actuels
            script_globals['start_date'] = datetime.strptime(self.date_debut, '%d/%m/%Y').date()
            script_globals['end_date'] = datetime.strptime(self.date_fin, '%d/%m/%Y').date()
            # Le script original définit aussi debut, fin, generalDirectory, conn, cur globalement.
            # Ces variables pourraient être nécessaires au script externe s'il ne les redéfinit pas.
            # C'est une limitation de l'approche `exec`.

            # Connexion à la base de données pour le script externe si nécessaire
            # Le script externe semble gérer sa propre connexion.

            with open(script_path, 'r') as f:
                script_content = f.read()

            # Pour capturer la sortie du script externe, on pourrait rediriger sys.stdout,
            # mais c'est complexe avec `exec`. On va se contenter de logguer l'exécution.
            if self.logger: self.logger.info(f"Contenu du script {script_path} va être exécuté.")

            # ATTENTION: `exec` est puissant et peut avoir des effets de bord.
            # Le script externe doit être fiable.
            exec(script_content, script_globals) # Exécuter dans un scope modifié

            if self.logger:
                self.logger.info(f"Script externe {script_path} exécuté avec succès.")

        except FileNotFoundError:
             # Déjà loggué
            raise
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de l'exécution du script externe {script_path}: {e}")
            # Il est important de remonter l'erreur pour que l'orchestrateur sache qu'il y a eu un problème.
            raise

    def process(self, source_file_path: str = None): # source_file_path n'est pas utilisé
        """
        Orchestre le traitement pour PmuSenegal.
        """
        if self.logger:
            self.logger.info(f"Début du traitement PmuSenegal (via script externe).")

        self.load_data() # Appelle l'exécution du script externe

        if self.logger:
            self.logger.info(f"Fin du traitement PmuSenegal.")

from datetime import datetime
