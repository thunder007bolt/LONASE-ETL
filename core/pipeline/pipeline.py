"""
Pipeline ETL flexible avec retry et gestion d'erreurs.
"""
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
from core.config.env_config import JobConfig


class StepStatus(Enum):
    """Statut d'une étape du pipeline"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """Résultat d'exécution d'une étape"""
    status: StepStatus
    output: Any = None
    error: Optional[Exception] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PipelineStep:
    """Étape du pipeline"""
    
    def __init__(self, name: str, executor_func: Callable, config: JobConfig):
        self.name = name
        self.executor_func = executor_func
        self.config = config
    
    async def execute(self, context: Dict[str, Any]) -> StepResult:
        """Exécute l'étape"""
        start_time = time.time()
        
        try:
            if self.config.dry_run:
                return StepResult(
                    status=StepStatus.SKIPPED,
                    duration=0.0,
                    metadata={"dry_run": True, "step": self.name}
                )
            
            # Exécuter la fonction (peut être sync ou async)
            if asyncio.iscoroutinefunction(self.executor_func):
                output = await self.executor_func(context, self.config)
            else:
                output = self.executor_func(context, self.config)
            
            return StepResult(
                status=StepStatus.SUCCESS,
                output=output,
                duration=time.time() - start_time,
                metadata={"step": self.name}
            )
        except Exception as e:
            return StepResult(
                status=StepStatus.FAILED,
                error=e,
                duration=time.time() - start_time,
                metadata={"step": self.name, "error_type": type(e).__name__}
            )


class Pipeline:
    """Pipeline ETL flexible avec retry"""
    
    def __init__(self, name: str, config: JobConfig):
        self.name = name
        self.config = config
        self.steps: List[PipelineStep] = []
        self.context: Dict[str, Any] = {}
    
    def add_step(self, step: PipelineStep):
        """Ajoute une étape au pipeline"""
        self.steps.append(step)
    
    async def execute_with_retry(self, step: PipelineStep) -> StepResult:
        """Exécute une étape avec retry"""
        last_result = None
        
        for attempt in range(self.config.retry_count + 1):
            if attempt > 0:
                await asyncio.sleep(self.config.retry_delay * attempt)
            
            result = await step.execute(self.context)
            last_result = result
            
            if result.status == StepStatus.SUCCESS:
                return result
            elif result.status == StepStatus.SKIPPED:
                return result
        
        return last_result
    
    async def execute(self) -> Dict[str, StepResult]:
        """Exécute le pipeline complet"""
        results = {}
        
        for step in self.steps:
            # Vérifier si l'étape doit être skippée
            if step.name == "extract" and self.config.skip_extract:
                results[step.name] = StepResult(
                    status=StepStatus.SKIPPED,
                    metadata={"reason": "skip_extract flag"}
                )
                continue
            elif step.name == "transform" and self.config.skip_transform:
                results[step.name] = StepResult(
                    status=StepStatus.SKIPPED,
                    metadata={"reason": "skip_transform flag"}
                )
                continue
            elif step.name == "load" and self.config.skip_load:
                results[step.name] = StepResult(
                    status=StepStatus.SKIPPED,
                    metadata={"reason": "skip_load flag"}
                )
                continue
            
            # Exécuter avec retry
            result = await self.execute_with_retry(step)
            results[step.name] = result
            
            # En cas d'échec, arrêter le pipeline
            if result.status == StepStatus.FAILED:
                break
            
            # Ajouter le résultat au contexte pour les étapes suivantes
            if result.output is not None:
                self.context[step.name] = result.output
        
        return results

