import json
import logging
import traceback
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
from contextlib import contextmanager

class ErrorSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ErrorCategory(Enum):
    VALIDATION = "VALIDATION"
    INTEGRITY = "INTEGRITY"
    EXECUTION = "EXECUTION"
    ROLLBACK = "ROLLBACK"
    SYSTEM = "SYSTEM"
    USER_INPUT = "USER_INPUT"

@dataclass
class ODINError:
    """Structure standardisée pour les erreurs ODIN"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    stack_trace: Optional[str] = None
    suggested_actions: List[str] = None
    auto_recovery: bool = False

class ODINErrorManager:
    """
    Gestionnaire d'erreurs centralisé pour ODIN
    Gestion des échecs, rollbacks, et récupération automatique
    """
    
    def __init__(self):
        self.error_log = []
        self.recovery_strategies = {}
        self.rollback_stack = []
        self.max_retry_attempts = 3
        self.setup_logging()
        self.register_default_strategies()
    
    def setup_logging(self):
        """Configuration du logging structuré"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - ODIN - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('odin_errors.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ODIN')
    
    def register_recovery_strategy(self, error_category: ErrorCategory, strategy: Callable):
        """Enregistrement d'une stratégie de récupération"""
        self.recovery_strategies[error_category] = strategy
    
    def handle_error(self, error: ODINError) -> Dict[str, Any]:
        """Gestion centralisée des erreurs"""
        
        # Logging de l'erreur
        self.error_log.append(error)
        self.logger.error(f"[{error.category.value}] {error.message}")
        
        # Évaluation de la sévérité
        response = self._evaluate_severity(error)
        
        # Tentative de récupération automatique
        if error.auto_recovery and error.category in self.recovery_strategies:
            try:
                recovery_result = self.recovery_strategies[error.category](error)
                response.update(recovery_result)
            except Exception as e:
                self.logger.error(f"Recovery failed: {str(e)}")
                response["recovery_failed"] = True
        
        return response
    
    def _evaluate_severity(self, error: ODINError) -> Dict[str, Any]:
        """Évaluation et actions selon la sévérité"""
        
        response = {
            "error_id": error.error_id,
            "timestamp": error.timestamp.isoformat(),
            "action_taken": None,
            "requires_human_intervention": False
        }
        
        if error.severity == ErrorSeverity.CRITICAL:
            response["action_taken"] = "IMMEDIATE_STOP"
            response["requires_human_intervention"] = True
            self._emergency_stop()
            
        elif error.severity == ErrorSeverity.HIGH:
            response["action_taken"] = "ROLLBACK_INITIATED"
            self._initiate_rollback()
            
        elif error.severity == ErrorSeverity.MEDIUM:
            response["action_taken"] = "RETRY_WITH_FALLBACK"
            
        else:  # LOW
            response["action_taken"] = "LOGGED_CONTINUE"
        
        return response
    
    def _emergency_stop(self):
        """Arrêt d'urgence du système"""
        self.logger.critical("EMERGENCY STOP - Critical error detected")
        # Sauvegarde d'urgence
        self._emergency_checkpoint()
        # Notification
        self._notify_emergency()
    
    def _initiate_rollback(self):
        """Initiation du rollback"""
        if not self.rollback_stack:
            self.logger.error("No rollback points available")
            return False
        
        latest_checkpoint = self.rollback_stack[-1]
        return self._execute_rollback(latest_checkpoint)
    
    def _execute_rollback(self, checkpoint: Dict) -> bool:
        """Exécution du rollback"""
        try:
            # Restauration des fichiers
            for file_path, file_state in checkpoint.get("file_states", {}).items():
                self._restore_file(file_path, file_state)
            
            # Restauration de l'état
            self._restore_state(checkpoint["state"])
            
            self.logger.info(f"Rollback successful to checkpoint: {checkpoint['id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            return False
    
    def _restore_file(self, file_path: str, file_state: Dict):
        """Restauration d'un fichier"""
        # Implémentation de la restauration
        pass
    
    def _restore_state(self, state: Dict):
        """Restauration de l'état système"""
        # Implémentation de la restauration d'état
        pass
    
    def _emergency_checkpoint(self):
        """Point de contrôle d'urgence"""
        emergency_data = {
            "timestamp": datetime.now().isoformat(),
            "error_log": [
                {
                    "error_id": err.error_id,
                    "category": err.category.value,
                    "severity": err.severity.value,
                    "message": err.message,
                    "timestamp": err.timestamp.isoformat()
                }
                for err in self.error_log[-10:]  # Dernières 10 erreurs
            ],
            "system_state": self._capture_system_state()
        }
        
        with open("emergency_checkpoint.json", "w") as f:
            json.dump(emergency_data, f, indent=2)
    
    def _capture_system_state(self) -> Dict:
        """Capture de l'état système actuel"""
        return {
            "active_processes": [],
            "file_locks": [],
            "memory_usage": 0,
            "disk_usage": 0
        }
    
    def _notify_emergency(self):
        """Notification d'urgence"""
        # Implémentation des notifications
        pass
    
    def register_default_strategies(self):
        """Enregistrement des stratégies de récupération par défaut"""
        
        def validation_recovery(error: ODINError) -> Dict:
            """Stratégie de récupération pour erreurs de validation"""
            return {
                "strategy": "validation_recovery",
                "actions": ["re_validate", "sanitize_input", "retry"],
                "success": True
            }
        
        def integrity_recovery(error: ODINError) -> Dict:
            """Stratégie de récupération pour erreurs d'intégrité"""
            return {
                "strategy": "integrity_recovery",
                "actions": ["restore_from_backup", "recalculate_hash"],
                "success": True
            }
        
        def execution_recovery(error: ODINError) -> Dict:
            """Stratégie de récupération pour erreurs d'exécution"""
            return {
                "strategy": "execution_recovery",
                "actions": ["rollback_transaction", "retry_with_fallback"],
                "success": True
            }
        
        self.register_recovery_strategy(ErrorCategory.VALIDATION, validation_recovery)
        self.register_recovery_strategy(ErrorCategory.INTEGRITY, integrity_recovery)
        self.register_recovery_strategy(ErrorCategory.EXECUTION, execution_recovery)
    
    @contextmanager
    def error_context(self, operation_name: str):
        """Context manager pour capture automatique d'erreurs"""
        try:
            yield
        except Exception as e:
            error = ODINError(
                error_id=f"AUTO_{operation_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category=ErrorCategory.EXECUTION,
                severity=ErrorSeverity.HIGH,
                message=f"Unhandled exception in {operation_name}: {str(e)}",
                details={"operation": operation_name, "exception_type": type(e).__name__},
                timestamp=datetime.now(),
                stack_trace=traceback.format_exc(),
                auto_recovery=True
            )
            
            self.handle_error(error)
            raise
    
    def create_rollback_point(self, description: str) -> str:
        """Création d'un point de rollback"""
        checkpoint_id = f"ROLLBACK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        checkpoint = {
            "id": checkpoint_id,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "file_states": self._capture_file_states(),
            "state": self._capture_system_state()
        }
        
        self.rollback_stack.append(checkpoint)
        
        # Limiter la taille de la pile
        if len(self.rollback_stack) > 10:
            self.rollback_stack.pop(0)
        
        return checkpoint_id
    
    def _capture_file_states(self) -> Dict:
        """Capture des états des fichiers"""
        # Implémentation de la capture d'états
        return {}
    
    def get_error_statistics(self) -> Dict:
        """Statistiques des erreurs"""
        if not self.error_log:
            return {"total_errors": 0}
        
        stats = {
            "total_errors": len(self.error_log),
            "by_category": {},
            "by_severity": {},
            "recent_errors": len([e for e in self.error_log if 
                                (datetime.now() - e.timestamp).seconds < 3600])
        }
        
        for error in self.error_log:
            # Par catégorie
            cat = error.category.value
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            
            # Par sévérité
            sev = error.severity.value
            stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
        
        return stats

# Exemple d'utilisation
if __name__ == "__main__":
    error_manager = ODINErrorManager()
    
    # Création d'un point de rollback
    rollback_id = error_manager.create_rollback_point("Before critical operation")
    
    # Simulation d'une erreur
    error = ODINError(
        error_id="TEST_001",
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.HIGH,
        message="Test error for demonstration",
        details={"test": True},
        timestamp=datetime.now(),
        auto_recovery=True
    )
    
    # Gestion de l'erreur
    result = error_manager.handle_error(error)
    print("Error handling result:", result)
    
    # Statistiques
    stats = error_manager.get_error_statistics()
    print("Error statistics:", stats)
