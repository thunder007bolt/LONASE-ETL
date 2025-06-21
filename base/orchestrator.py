import logging # Utiliser logging directement pour le type hint
from pathlib import Path
from typing import Callable, Optional, Any # Callable pour les étapes

from base.logger import Logger # Utilisation de la classe Logger refactorisée

# Optionnel: Définir une interface pour les composants si on veut être plus strict
# from abc import ABC, abstractmethod
# class IRunnableComponent(ABC):
#     @abstractmethod
#     def run(self): # Ou un nom plus spécifique comme process() ou execute()
#         pass

class Orchestrator:
    """
    Orchestre l'exécution séquentielle de différentes étapes d'un processus ETL (Extract, Transform, Load).
    """
    def __init__(self,
                 orchestrator_name: str,
                 log_file_path: Optional[str | Path] = None,
                 extractor_component: Optional[Any] = None, # Anciennement juste extractor
                 transformer_component: Optional[Any] = None, # Anciennement juste transformer
                 loader_component: Optional[Any] = None): # Anciennement juste loader
        """
        Initialise l'Orchestrator.

        Args:
            orchestrator_name (str): Nom de cet orchestrateur (utilisé pour le logging).
            log_file_path (str | Path, optional): Chemin personnalisé pour le fichier de log de l'orchestrateur.
                                                 Si None, un chemin par défaut sera utilisé.
            extractor_component (Any, optional): Composant (objet) responsable de l'extraction.
                                                 Doit avoir une méthode 'process_extraction()'.
            transformer_component (Any, optional): Composant responsable de la transformation.
                                                   Doit avoir une méthode 'process_files_transformation()'.
            loader_component (Any, optional): Composant responsable du chargement.
                                              Doit avoir une méthode 'process_loading_from_files()'.
        """
        self.name = orchestrator_name

        # Configuration du logger pour l'orchestrateur lui-même
        if log_file_path is None:
            # Chemin par défaut si non fourni, s'assurant que le dossier logs existe
            default_log_dir = Path("logs")
            default_log_dir.mkdir(parents=True, exist_ok=True)
            log_file_path = default_log_dir / f"orchestrator_{self.name}.log"

        # Utilisation de la classe Logger refactorisée
        self.logger = Logger(
            log_file_path=str(log_file_path),
            logger_name=f"Orchestrator.{self.name}" # Nom de logger plus descriptif
        ).get_logger()

        self.extractor = extractor_component
        self.transformer = transformer_component
        self.loader = loader_component

        # Définir les noms des méthodes attendues pour chaque type de composant
        # Cela permet une certaine flexibilité et une vérification d'interface implicite.
        self.component_methods = {
            "extractor": "process_extraction",
            "transformer": "process_files_transformation", # Mis à jour selon la refactorisation de Transformer
            "loader": "process_loading_from_files"      # Mis à jour selon la refactorisation de Loader
        }

    def _execute_component_step(self, component: Optional[Any], component_name: str):
        """Exécute une étape (un composant) si elle est définie et valide."""
        if component is None:
            self.logger.info(f"Étape '{component_name}' non définie, elle sera sautée.")
            return

        method_name = self.component_methods.get(component_name)
        if not method_name:
            self.logger.error(f"Nom de méthode non défini pour le type de composant '{component_name}'.")
            raise ValueError(f"Configuration interne de l'orchestrateur incorrecte pour {component_name}")

        if not hasattr(component, method_name):
            self.logger.error(f"Le composant '{component_name}' (type: {type(component).__name__}) "
                              f"ne possède pas la méthode attendue '{method_name}'.")
            raise AttributeError(f"Composant {component_name} n'a pas de méthode {method_name}")

        action: Callable = getattr(component, method_name)

        self.logger.info(f"--- Début de l'étape : {component_name.upper()} ---")
        try:
            action() # Appel de la méthode (ex: self.extractor.process_extraction())
            self.logger.info(f"--- Étape '{component_name.upper()}' terminée avec succès. ---")
        except Exception as e:
            self.logger.error(f"Erreur durant l'exécution de l'étape '{component_name.upper()}': {e}", exc_info=True)
            # Renvoyer l'exception pour arrêter l'orchestration globale si une étape échoue.
            # On pourrait ajouter une logique pour continuer si certaines erreurs sont non bloquantes.
            raise # Propage l'exception


    def run(self):
        """
        Exécute le pipeline d'orchestration (extraction, transformation, chargement) séquentiellement.
        """
        self.logger.info(f"Lancement de l'orchestrateur '{self.name}'...")
        start_time = সময়.time() # Nécessite import time

        try:
            self._execute_component_step(self.extractor, "extractor")
            self._execute_component_step(self.transformer, "transformer")
            self._execute_component_step(self.loader, "loader")

            end_time = সময়.time() # Nécessite import time
            duration = end_time - start_time
            self.logger.info(f"Orchestrateur '{self.name}' terminé avec succès en {duration:.2f} secondes.")

        except Exception as e: # Attrape les erreurs propagées par _execute_component_step
            end_time = সময়.time() # Nécessite import time
            duration = end_time - start_time
            self.logger.critical(f"L'orchestrateur '{self.name}' a échoué après {duration:.2f} secondes "
                                 f"en raison d'une erreur dans l'une de ses étapes. Voir logs précédents pour détails.", exc_info=False)
            # L'exception originale est déjà loggée avec sa traceback par _execute_component_step.
            # On ne la propage pas plus loin pour que l'application principale puisse décider quoi faire.
            # Ou, si on veut que l'échec de l'orchestrateur soit une exception, on peut la repropager:
            # raise OrchestrationError(f"Échec de l'orchestrateur {self.name}") from e
        finally:
            self.logger.info(f"Fin de l'orchestrateur '{self.name}'.")


# Classe d'exception personnalisée pour l'orchestrateur (optionnel)
class OrchestrationError(Exception):
    pass

# Pour utiliser time.time(), il faut l'importer:
import time # Placé ici pour que le bloc de code soit complet. Idéalement en haut du fichier.