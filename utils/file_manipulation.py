from pathlib import Path
import shutil
import os

def move_file(file_path: Path, destination_folder: Path) -> Path:
    """
    Déplace le fichier spécifié vers le dossier de destination sans le renommer.

    Args:
        file_path (Path): Chemin complet du fichier à déplacer.
        destination_folder (Path): Répertoire de destination où le fichier sera déplacé.

    Returns:
        Path: Le nouveau chemin complet du fichier déplacé.
    """
    # S'assurer que le dossier de destination existe, sinon le créer
    destination_folder.mkdir(parents=True, exist_ok=True)

    # Construire le chemin complet de destination en conservant le même nom de fichier
    destination = destination_folder / file_path.name
    if destination.exists():
        destination.unlink()
    # Déplacer le fichier vers le répertoire de destination

    file_path.rename(destination)

    return destination


def rename_file(pattern, source_folder, rename_name, logger):
    """Renomme un fichier ou un ensemble de fichiers selon un motif."""
    if isinstance(pattern, Path):
        file = pattern
        try:
            new_file = _rename_file(file, rename_name, logger)
            logger.info(f"Fichier renommé {new_file}")
        except Exception as e:
            logger.error(f"Erreur lors du renommage de {file}: {e}")
    else:
        files = list(Path(source_folder).glob(pattern))
        if not files:
            logger.info(f"Aucun fichier trouvé avec le pattern : {pattern}")
            return
        for file in files:
            try:
                new_file = _rename_file(file, rename_name, logger)
                logger.info(f"Fichier renommé {new_file}")
            except Exception as e:
                logger.error(f"Erreur lors du renommage de {file}: {e}")

def _rename_file(file, rename_name, logger):
    """Renomme un fichier en conservant son dossier et son extension."""
    new_file = file.parent / f"{rename_name}{file.suffix}"
    if new_file.exists():
        logger.warning(f"Le fichier {new_file} existe déjà et sera remplacé.")
        new_file.unlink()
    file.rename(new_file)
    return new_file

def _rename_file2(file: Path, rename_name: str, logger) -> Path:
    """Effectue le renommage d'un fichier."""
    try:
        new_file = file.parent / f"{rename_name}{file.suffix}"
        file.rename(new_file)
        return new_file
    except Exception as e:
        logger.error(f"Échec du renommage de {file} en {rename_name}: {e}")
        raise
from pathlib import Path
import time

def rename_file2(pattern, source_folder, rename_name, logger):
    """Renomme un fichier et vérifie que le renommage est effectif."""
    if isinstance(pattern, Path):
        file = pattern
        try:
            new_file = _rename_file(file, rename_name, logger)
            # Vérifier que le fichier original n'existe plus
            if file.exists():
                logger.error(f"Le fichier original {file} existe toujours après le renommage.")
                raise FileExistsError(f"Échec du renommage : {file} n'a pas été supprimé.")
            # Vérifier que le nouveau fichier existe
            if not new_file.exists():
                logger.error(f"Le nouveau fichier {new_file} n'a pas été créé.")
                raise FileNotFoundError(f"Échec du renommage : {new_file} n'existe pas.")
            logger.info(f"Fichier renommé avec succès : {new_file}")
            return new_file
        except Exception as e:
            logger.error(f"Erreur lors du renommage de {file}: {e}")
            raise
    else:
        files = list(Path(source_folder).glob(pattern))
        if not files:
            logger.info(f"Aucun fichier trouvé avec le pattern : {pattern}")
            return
        for file in files:
            try:
                new_file = _rename_file(file, rename_name, logger)
                if file.exists():
                    logger.error(f"Le fichier original {file} existe toujours après le renommage.")
                    raise FileExistsError(f"Échec du renommage : {file} n'a pas été supprimé.")
                if not new_file.exists():
                    logger.error(f"Le nouveau fichier {new_file} n'a pas été créé.")
                    raise FileNotFoundError(f"Échec du renommage : {new_file} n'existe pas.")
                logger.info(f"Fichier renommé avec succès : {new_file}")
                return new_file
            except Exception as e:
                logger.error(f"Erreur lors du renommage de {file}: {e}")
                raise

def delete_file(path: Path, file_pattern: str):
    """
    Supprime les fichiers correspondant au pattern spécifié dans le dossier spécifié.

    Args:
        path (Path): Chemin complet du dossier où les fichiers doivent être supprimés.
        file_pattern (str): Pattern à utiliser pour la recherche des fichiers à supprimer.
    """
    files = list(Path(path).glob(file_pattern))
    if not files:
        return
    for file in files:
        file.unlink()

def files_list(path, pattern="*"):
    return list(Path(path).glob(pattern))

def check_file_not_empty(path):
    """
    Vérifie si le fichier existe ET qu'il n'est pas vide.
    Retourne True si tout est OK, sinon False.
    Affiche aussi un message explicite.
    """
    if not os.path.isfile(path):
        print(f"Le fichier n'existe pas : {path}")
        return False

    size = os.path.getsize(path)

    if size == 0:
        print(f"Le fichier est vide : {path}")
        return False

    return True
def copy_files(pattern, source_folder, destination_folder, logger):
    """
    Copie un fichier ou un ensemble de fichiers correspondant à un motif
    depuis un dossier source vers un dossier de destination.

    Args:
        pattern (str): Motif pour identifier les fichiers à copier (par exemple, "*.txt").
        source_folder (str): Chemin du dossier source contenant les fichiers.
        destination_folder (str): Chemin du dossier de destination où copier les fichiers.
        logger: Logger pour enregistrer les événements et les erreurs.
    """
    # Convertir les dossiers en objets Path
    source_path = Path(source_folder)
    destination_path = Path(destination_folder)

    # Vérifier si le dossier de destination existe, sinon le créer
    if not destination_path.exists():
        try:
            destination_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Dossier de destination créé : {destination_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la création du dossier de destination : {e}")
            return

    # Rechercher les fichiers correspondant au motif
    files = list(source_path.glob(pattern))
    if not files:
        logger.info(f"Aucun fichier trouvé avec le pattern : {pattern} dans {source_folder}")
        return

    # Copier chaque fichier vers le dossier de destination
    for file in files:
        try:
            # Construire le chemin de destination
            destination_file = destination_path / file.name

            # Vérifier si le fichier existe déjà dans le dossier de destination
            if destination_file.exists():
                logger.warning(f"Le fichier {file.name} existe déjà dans {destination_folder}")
                continue

            # Copier le fichier
            shutil.copy2(file, destination_file)  # copy2 préserve les métadonnées
            logger.info(f"Fichier copié : {file} -> {destination_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la copie de {file}: {e}")