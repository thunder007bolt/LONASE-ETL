"""
Gestion de la configuration via variables d'environnement.
Jenkins transmet toutes les configurations via des variables d'environnement.
"""
from os import getenv
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class JobConfig:
    """Configuration d'un job depuis les variables d'environnement"""
    job_name: str
    source_name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip_extract: bool = False
    skip_transform: bool = False
    skip_load: bool = False
    retry_count: int = 3
    retry_delay: int = 5
    batch_size: int = 1000
    dry_run: bool = False
    debug: bool = False
    extra_params: Dict[str, Any] = field(default_factory=dict)


class EnvConfigLoader:
    """Charge la configuration depuis les variables d'environnement"""
    
    # Variables d'environnement standardisées
    ENV_JOB_NAME = "ETL_JOB_NAME"
    ENV_SOURCE_NAME = "ETL_SOURCE_NAME"
    ENV_START_DATE = "ETL_START_DATE"  # Format: YYYY-MM-DD
    ENV_END_DATE = "ETL_END_DATE"      # Format: YYYY-MM-DD
    ENV_SKIP_EXTRACT = "ETL_SKIP_EXTRACT"
    ENV_SKIP_TRANSFORM = "ETL_SKIP_TRANSFORM"
    ENV_SKIP_LOAD = "ETL_SKIP_LOAD"
    ENV_RETRY_COUNT = "ETL_RETRY_COUNT"
    ENV_RETRY_DELAY = "ETL_RETRY_DELAY"
    ENV_BATCH_SIZE = "ETL_BATCH_SIZE"
    ENV_DRY_RUN = "ETL_DRY_RUN"
    ENV_DEBUG = "ETL_DEBUG"
    ENV_EXTRA_PARAMS = "ETL_EXTRA_PARAMS"  # JSON string
    
    @classmethod
    def load_job_config(cls) -> JobConfig:
        """Charge la configuration du job depuis les variables d'environnement"""
        
        # Job name et source (requis)
        job_name = getenv(cls.ENV_JOB_NAME)
        source_name = getenv(cls.ENV_SOURCE_NAME)
        
        if not job_name or not source_name:
            raise ValueError(
                f"Variables d'environnement requises manquantes: "
                f"{cls.ENV_JOB_NAME}={job_name}, {cls.ENV_SOURCE_NAME}={source_name}"
            )
        
        # Dates (optionnelles, peuvent être dans config.yml sinon)
        start_date = cls._parse_date(getenv(cls.ENV_START_DATE))
        end_date = cls._parse_date(getenv(cls.ENV_END_DATE))
        
        # Flags booléens
        skip_extract = cls._parse_bool(getenv(cls.ENV_SKIP_EXTRACT), False)
        skip_transform = cls._parse_bool(getenv(cls.ENV_SKIP_TRANSFORM), False)
        skip_load = cls._parse_bool(getenv(cls.ENV_SKIP_LOAD), False)
        dry_run = cls._parse_bool(getenv(cls.ENV_DRY_RUN), False)
        debug = cls._parse_bool(getenv(cls.ENV_DEBUG), False)
        
        # Paramètres numériques
        retry_count = int(getenv(cls.ENV_RETRY_COUNT, "3"))
        retry_delay = int(getenv(cls.ENV_RETRY_DELAY, "5"))
        batch_size = int(getenv(cls.ENV_BATCH_SIZE, "1000"))
        
        # Paramètres supplémentaires (JSON)
        extra_params_str = getenv(cls.ENV_EXTRA_PARAMS)
        extra_params = {}
        if extra_params_str:
            try:
                extra_params = json.loads(extra_params_str)
            except json.JSONDecodeError:
                pass
        
        return JobConfig(
            job_name=job_name,
            source_name=source_name,
            start_date=start_date,
            end_date=end_date,
            skip_extract=skip_extract,
            skip_transform=skip_transform,
            skip_load=skip_load,
            retry_count=retry_count,
            retry_delay=retry_delay,
            batch_size=batch_size,
            dry_run=dry_run,
            debug=debug,
            extra_params=extra_params
        )
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse une date depuis une string"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None
    
    @staticmethod
    def _parse_bool(value: Optional[str], default: bool = False) -> bool:
        """Parse un booléen depuis une string"""
        if not value:
            return default
        return value.lower() in ("true", "1", "yes", "on")
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Optional[str]]:
        """Récupère la config de base de données depuis les env vars"""
        return {
            "sql_server_host": getenv("SQL_SERVER_HOST"),
            "sql_server_database": getenv("SQL_SERVER_TEMPDB_NAME"),
            "sql_server_username": getenv("SQL_SERVER_TEMPDB_USERNAME"),
            "sql_server_password": getenv("SQL_SERVER_TEMPDB_PASSWORD"),
            "oracle_username": getenv("ORACLE_TARGET_USERNAME"),
            "oracle_password": getenv("ORACLE_TARGET_PASSWORD"),
            "oracle_host": getenv("ORACLE_TARGET_HOST"),
            "oracle_port": getenv("ORACLE_TARGET_PORT"),
            "oracle_service": getenv("ORACLE_TARGET_SERVICE"),
        }
    
    @classmethod
    def get_paths_config(cls) -> Dict[str, Optional[Path]]:
        """Récupère les chemins depuis les env vars ou config.yml"""
        data_path = getenv("ETL_DATA_PATH")
        project_path = getenv("ETL_PROJECT_PATH") or getenv("ABSOLUTE_PROJECT_PATH")
        
        return {
            "data_path": Path(data_path) if data_path else None,
            "project_path": Path(project_path) if project_path else None,
        }

