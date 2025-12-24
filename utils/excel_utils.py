"""
Utilitaires pour la manipulation de fichiers Excel.
"""
import shutil
import tempfile
from pathlib import Path
from typing import Optional
import logging

try:
    import xlwings as xw
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False


def convert_xls_to_xlsx(xls_file: Path, logger: Optional[logging.Logger] = None) -> Path:
    """
    Convertit un fichier XLS en XLSX via l'automatisation COM d'Excel.
    
    Args:
        xls_file: Chemin vers le fichier XLS à convertir
        logger: Logger optionnel pour les messages de log
    
    Returns:
        Path: Chemin vers le fichier XLSX créé
    
    Raises:
        ImportError: Si xlwings n'est pas disponible
        Exception: Si la conversion échoue
    """
    if not XLWINGS_AVAILABLE:
        raise ImportError("xlwings n'est pas installé. Installez-le avec: pip install xlwings")
    
    log = logger.info if logger else print
    
    # Utiliser le répertoire temporaire système au lieu d'un chemin hardcodé
    temp_dir = Path(tempfile.gettempdir()) / "gen_py"
    
    def clear_temp():
        """Nettoie le répertoire temporaire si nécessaire."""
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except OSError as e:
            if logger:
                logger.warning(f"Impossible de nettoyer le répertoire temporaire: {e}")
    
    clear_temp()
    
    log(f"Conversion du fichier XLS {xls_file.name} en XLSX...")
    
    # Lancement d'Excel (en arrière-plan)
    app = xw.App(visible=False)
    
    try:
        wb = app.books.open(str(xls_file.resolve()))
        xlsx_file = xls_file.with_suffix(".xlsx")
        
        if xlsx_file.exists():
            xlsx_file.unlink()
        
        wb.save(str(xlsx_file.resolve()))
        wb.close()
        
        log(f"Conversion réussie: {xlsx_file.name}")
        return xlsx_file
        
    except Exception as e:
        if logger:
            logger.error(f"Erreur lors de la conversion de {xls_file.name}: {e}")
        raise
    finally:
        app.quit()

