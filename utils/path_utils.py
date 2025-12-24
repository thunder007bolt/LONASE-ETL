"""
Utility module for managing project paths.
Centralizes path management to avoid hardcoded paths throughout the codebase.
"""
import sys
from pathlib import Path


def setup_project_paths():
    """
    Add project root to Python path if not already present.
    Uses relative paths based on file location for portability.
    """
    # Get the project root (parent of utils directory)
    project_root = Path(__file__).parent.parent.resolve()
    
    # Convert to string for sys.path
    project_root_str = str(project_root)
    
    # Add to path if not already present
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    return project_root


def get_project_root():
    """
    Get the absolute path to the project root directory.
    
    Returns:
        Path: Path object pointing to project root
    """
    return Path(__file__).parent.parent.resolve()

