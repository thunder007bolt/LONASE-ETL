from pathlib import Path

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
    if isinstance(pattern, Path):
        file = pattern
        new_file = rename(file, rename_name)
        if file.exists():
            file.unlink()
        logger.info(f"Fichier renommé {new_file}")
        pass
    else:
        files = list(Path(source_folder).glob(pattern))  # R, echerche dans le dossier courant
        if not files:
            logger.info(f"Aucun fichier trouvé avec le pattern : {pattern}")
            return
        for file in files:
            new_file = rename(file, rename_name)
            logger.info(f"Fichier renommé {new_file}")

def rename(file, rename_name):
    new_file = file.parent / f"{rename_name}{file.suffix}"  # Conserve le dossier d'origine
    if new_file.exists():
        new_file.unlink()
    file.rename(new_file)
    return new_file

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