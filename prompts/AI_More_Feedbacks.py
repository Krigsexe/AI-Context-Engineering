from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio

class FeedbackType(Enum):
    BINARY = "BINARY"           # Faux/Parfait
    SCALE = "SCALE"             # 1-5 ou 1-10
    DETAILED = "DETAILED"       # Commentaires structurés
    CONTINUOUS = "CONTINUOUS"   # Feedback temps réel
    CONTEXTUAL = "CONTEXTUAL"   # Feedback spécifique au contexte

class FeedbackCategory(Enum):
    CODE_QUALITY = "CODE_QUALITY"
    DOCUMENTATION = "DOCUMENTATION"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    USABILITY = "USABILITY"
    ACCURACY = "ACCURACY"
    COMPLETENESS = "COMPLETENESS"

@dataclass
class FeedbackItem:
    """Structure de feedback enrichie"""
    feedback_id: str
    type: FeedbackType
    category: FeedbackCategory
    value: Union[str, int, float, Dict]
    confidence: float  # 0-1
    timestamp: datetime
    context: Dict[str, Any]
    suggestions: List[str] = None
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL

class ODINFeedbackSystem:
    """
    Système de feedback avancé pour ODIN
    Support multi-modal et apprentissage adaptatif
    """
    
    def __init__(self):
        self.feedback_history = []
        self.learning_patterns = {}
        self.auto_improvement_rules = {}
        self.feedback_processors = {}
        self.setup_processors()
    
    def setup_processors(self):
        """Configuration des processeurs de feedback"""
        self.feedback_processors = {
            FeedbackType.BINARY: self._process_binary_feedback,
            FeedbackType.SCALE: self._process_scale_feedback,
            FeedbackType.DETAILED: self._process_detailed_feedback,
            FeedbackType.CONTINUOUS: self._process_continuous_feedback,
            FeedbackType.CONTEXTUAL: self._process_contextual_feedback
        }
    
    def collect_feedback(self, feedback_item: FeedbackItem) -> Dict[str, Any]:
        """Collection et traitement du feedback"""
        
        # Validation du feedback
        if not self._validate_feedback(feedback_item):
            return {"success": False, "error": "Invalid feedback format"}
        
        # Traitement spécialisé
        processor = self.feedback_processors.get(feedback_item.type)
        if processor:
            processing_result = processor(feedback_item)
        else:
            processing_result = {"processed": False, "reason": "No processor found"}
        
        # Stockage
        self.feedback_history.append(feedback_item)
        
        # Apprentissage automatique
        learning_result = self._learn_from_feedback(feedback_item)
        
        # Génération de recommandations
        recommendations = self._generate_recommendations(feedback_item)
        
        return {
            "success": True,
            "feedback_id": feedback_item.feedback_id,
            "processing_result": processing_result,
            "learning_result": learning_result,
            "recommendations": recommendations,
            "next_actions": self._determine_next_actions(feedback_item)
        }
    
    def _validate_feedback(self, feedback: FeedbackItem) -> bool:
        """Validation du feedback"""
        if not feedback.feedback_id or not feedback.type or not feedback.category:
            return False
        
        if feedback.confidence < 0 or feedback.confidence > 1:
            return False
        
        return True
    
    def _process_binary_feedback(self, feedback: FeedbackItem) -> Dict:
        """Traitement du feedback binaire (Faux/Parfait)"""
        value = feedback.value
        
        if value == "Faux":
            return {
                "action": "IMMEDIATE_CORRECTION",
                "severity": "HIGH",
                "rollback_required": True,
                "learning_opportunity": True
            }
        elif value == "Parfait":
            return {
                "action": "DOCUMENT_SUCCESS",
                "severity": "LOW",
                "continue_process": True,
                "reinforce_pattern": True
            }
        else:
            return {
                "action": "CLARIFICATION_NEEDED",
                "severity": "MEDIUM",
                "valid_values": ["Faux", "Parfait"]
            }
    
    def _process_scale_feedback(self, feedback: FeedbackItem) -> Dict:
        """Traitement du feedback sur échelle"""
        value = feedback.value
        
        if isinstance(value, (int, float)):
            if value >= 4:  # Bon (sur 5)
                return {
                    "action": "CONTINUE_WITH_MONITORING",
                    "quality_level": "GOOD",
                    "improvement_needed": False
                }
            elif value >= 2:  # Moyen
                return {
                    "action": "MINOR_ADJUSTMENTS",
                    "quality_level": "AVERAGE",
                    "improvement_needed": True
                }
            else:  # Mauvais
                return {
                    "action": "MAJOR_REVISION",
                    "quality_level": "POOR",
                    "improvement_needed": True
                }
        
        return {"error": "Invalid scale value"}
    
    def _process_detailed_feedback(self, feedback: FeedbackItem) -> Dict:
        """Traitement du feedback détaillé"""
        value = feedback.value
        
        if isinstance(value, dict):
            specific_issues = value.get("issues", [])
            positive_aspects = value.get("positive", [])
            suggestions = value.get("suggestions", [])
            
            return {
