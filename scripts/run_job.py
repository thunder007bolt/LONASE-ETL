"""
Point d'entrée unique pour Jenkins.
Jenkins appelle ce script avec des variables d'environnement.
"""
import sys
import asyncio
from pathlib import Path

# Setup des paths
from utils.path_utils import setup_project_paths
setup_project_paths()

from load_env import load_env
load_env()

from core.config.env_config import EnvConfigLoader, JobConfig
from core.pipeline.pipeline import Pipeline, PipelineStep, StepStatus
from infrastructure.logging.logger import get_logger
from adapters import get_adapter_factory


async def main():
    """Point d'entrée principal"""
    logger = get_logger("run_job", "logs/run_job.log")
    
    try:
        # Charger la configuration depuis les variables d'environnement
        config = EnvConfigLoader.load_job_config()
        logger.info("=" * 60)
        logger.info(f"Démarrage du job: {config.job_name}")
        logger.info(f"Source: {config.source_name}")
        logger.info(f"Dates: {config.start_date or 'Non définie'} -> {config.end_date or 'Non définie'}")
        logger.info(f"Configuration:")
        logger.info(f"  - Skip Extract: {config.skip_extract}")
        logger.info(f"  - Skip Transform: {config.skip_transform}")
        logger.info(f"  - Skip Load: {config.skip_load}")
        logger.info(f"  - Retry Count: {config.retry_count}")
        logger.info(f"  - Retry Delay: {config.retry_delay}s")
        logger.info(f"  - Dry Run: {config.dry_run}")
        logger.info(f"  - Debug: {config.debug}")
        logger.info("=" * 60)
        
        if config.debug:
            import logging
            logger.setLevel(logging.DEBUG)
            logger.debug(f"Mode debug activé. Config complète: {config}")
        
        # Créer le pipeline
        pipeline = Pipeline(name=config.job_name, config=config)
        
        # Récupérer l'adapter factory pour la source
        adapter_factory = get_adapter_factory(config.source_name)
        
        # Ajouter les étapes selon la configuration
        if not config.skip_extract:
            extract_func = adapter_factory.create_extractor(config)
            pipeline.add_step(PipelineStep("extract", extract_func, config))
            logger.info("Étape Extract ajoutée au pipeline")
        
        if not config.skip_transform:
            transform_func = adapter_factory.create_transformer(config)
            pipeline.add_step(PipelineStep("transform", transform_func, config))
            logger.info("Étape Transform ajoutée au pipeline")
        
        if not config.skip_load:
            load_func = adapter_factory.create_loader(config)
            pipeline.add_step(PipelineStep("load", load_func, config))
            logger.info("Étape Load ajoutée au pipeline")
        
        if not pipeline.steps:
            logger.warning("Aucune étape à exécuter (toutes skippées)")
            sys.exit(0)
        
        # Exécuter le pipeline
        logger.info(f"Exécution du pipeline avec {len(pipeline.steps)} étape(s)")
        results = await pipeline.execute()
        
        # Vérifier les résultats
        logger.info("=" * 60)
        logger.info("Résultats de l'exécution:")
        logger.info("=" * 60)
        
        failed_steps = [
            name for name, result in results.items()
            if result.status == StepStatus.FAILED
        ]
        
        skipped_steps = [
            name for name, result in results.items()
            if result.status == StepStatus.SKIPPED
        ]
        
        success_steps = [
            name for name, result in results.items()
            if result.status == StepStatus.SUCCESS
        ]
        
        # Afficher les résultats par étape
        for step_name, result in results.items():
            if result.status == StepStatus.SUCCESS:
                logger.info(f"✅ {step_name}: SUCCÈS ({result.duration:.2f}s)")
            elif result.status == StepStatus.SKIPPED:
                reason = result.metadata.get("reason", "Non spécifié") if result.metadata else "Non spécifié"
                logger.info(f"⏭️  {step_name}: IGNORÉ ({reason})")
            elif result.status == StepStatus.FAILED:
                logger.error(f"❌ {step_name}: ÉCHEC")
                if result.error:
                    logger.error(f"   Erreur: {result.error}")
        
        logger.info("=" * 60)
        
        if failed_steps:
            logger.error(f"❌ Job {config.job_name} terminé avec des erreurs")
            logger.error(f"Étapes en échec: {', '.join(failed_steps)}")
            for step_name in failed_steps:
                result = results[step_name]
                if result.error:
                    logger.error(f"Détails de l'erreur dans {step_name}:", exc_info=result.error)
            sys.exit(1)
        
        if success_steps:
            logger.info(f"✅ Job {config.job_name} terminé avec succès")
            logger.info(f"Étapes réussies: {', '.join(success_steps)}")
        
        if skipped_steps:
            logger.info(f"Étapes ignorées: {', '.join(skipped_steps)}")
        
        sys.exit(0)
        
    except ValueError as e:
        logger.error(f"Erreur de configuration: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur fatale: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import logging
    asyncio.run(main())

