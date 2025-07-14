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
            return {
                "action": "TARGETED_IMPROVEMENTS",
                "specific_issues": specific_issues,
                "positive_aspects": positive_aspects,
                "suggestions": suggestions,
                "priority_fixes": self._prioritize_issues(specific_issues),
                "improvement_plan": self._create_improvement_plan(specific_issues, suggestions)
            }
        
        return {"error": "Invalid detailed feedback format"}
    
    def _process_continuous_feedback(self, feedback: FeedbackItem) -> Dict:
        """Traitement du feedback continu (temps réel)"""
        value = feedback.value
        
        if isinstance(value, dict):
            metrics = value.get("metrics", {})
            trends = value.get("trends", {})
            alerts = value.get("alerts", [])
            
            return {
                "action": "REAL_TIME_ADJUSTMENT",
                "current_metrics": metrics,
                "trend_analysis": self._analyze_trends(trends),
                "immediate_alerts": alerts,
                "auto_corrections": self._suggest_auto_corrections(metrics, trends)
            }
        
        return {"error": "Invalid continuous feedback format"}
    
    def _process_contextual_feedback(self, feedback: FeedbackItem) -> Dict:
        """Traitement du feedback contextuel"""
        value = feedback.value
        context = feedback.context
        
        if isinstance(value, dict) and context:
            context_type = context.get("type", "unknown")
            context_data = context.get("data", {})
            
            return {
                "action": "CONTEXT_AWARE_ADJUSTMENT",
                "context_type": context_type,
                "context_specific_actions": self._get_context_actions(context_type, value),
                "adaptation_required": self._needs_adaptation(context_data),
                "learning_weight": self._calculate_learning_weight(context)
            }
        
        return {"error": "Invalid contextual feedback format"}
    
    def _learn_from_feedback(self, feedback: FeedbackItem) -> Dict:
        """Apprentissage automatique à partir du feedback"""
        
        # Extraction des patterns
        pattern_key = f"{feedback.category.value}_{feedback.type.value}"
        
        if pattern_key not in self.learning_patterns:
            self.learning_patterns[pattern_key] = {
                "occurrences": 0,
                "success_rate": 0.0,
                "common_issues": [],
                "effective_solutions": []
            }
        
        pattern = self.learning_patterns[pattern_key]
        pattern["occurrences"] += 1
        
        # Mise à jour du taux de succès
        if feedback.type == FeedbackType.BINARY:
            if feedback.value == "Parfait":
                pattern["success_rate"] = (pattern["success_rate"] * (pattern["occurrences"] - 1) + 1) / pattern["occurrences"]
            else:
                pattern["success_rate"] = (pattern["success_rate"] * (pattern["occurrences"] - 1)) / pattern["occurrences"]
        
        # Extraction des problèmes communs
        if hasattr(feedback, 'suggestions') and feedback.suggestions:
            for suggestion in feedback.suggestions:
                if suggestion not in pattern["effective_solutions"]:
                    pattern["effective_solutions"].append(suggestion)
        
        return {
            "pattern_updated": pattern_key,
            "new_success_rate": pattern["success_rate"],
            "total_occurrences": pattern["occurrences"],
            "learning_confidence": min(pattern["occurrences"] / 10, 1.0)
        }
    
    def _generate_recommendations(self, feedback: FeedbackItem) -> List[str]:
        """Génération de recommandations basées sur l'apprentissage"""
        
        recommendations = []
        pattern_key = f"{feedback.category.value}_{feedback.type.value}"
        
        if pattern_key in self.learning_patterns:
            pattern = self.learning_patterns[pattern_key]
            
            # Recommandations basées sur l'historique
            if pattern["success_rate"] < 0.7:
                recommendations.append(f"Success rate for {feedback.category.value} is low ({pattern['success_rate']:.2f}). Consider reviewing approach.")
            
            # Recommandations basées sur les solutions efficaces
            for solution in pattern["effective_solutions"][:3]:  # Top 3
                recommendations.append(f"Consider: {solution}")
        
        # Recommandations spécifiques au contexte
        if feedback.context:
            context_recommendations = self._get_context_recommendations(feedback.context)
            recommendations.extend(context_recommendations)
        
        return recommendations
    
    def _determine_next_actions(self, feedback: FeedbackItem) -> List[str]:
        """Détermination des actions suivantes"""
        
        actions = []
        
        if feedback.type == FeedbackType.BINARY:
            if feedback.value == "Faux":
                actions.extend([
                    "ROLLBACK_LAST_CHANGE",
                    "ANALYZE_ERROR_PATTERN",
                    "IMPLEMENT_CORRECTION",
                    "VALIDATE_CORRECTION",
                    "RETRY_OPERATION"
                ])
            else:  # Parfait
                actions.extend([
                    "DOCUMENT_SUCCESS",
                    "UPDATE_LEARNING_PATTERNS",
                    "PROCEED_TO_NEXT_STEP",
                    "CLEAN_TEMPORARY_FILES"
                ])
        
        elif feedback.type == FeedbackType.SCALE:
            score = feedback.value
            if score < 3:
                actions.extend([
                    "MAJOR_REVISION_REQUIRED",
                    "IDENTIFY_ROOT_CAUSES",
                    "IMPLEMENT_IMPROVEMENTS"
                ])
            elif score < 4:
                actions.extend([
                    "MINOR_ADJUSTMENTS",
                    "OPTIMIZE_PERFORMANCE",
                    "ENHANCE_QUALITY"
                ])
            else:
                actions.extend([
                    "MAINTAIN_CURRENT_APPROACH",
                    "DOCUMENT_BEST_PRACTICES"
                ])
        
        # Actions basées sur la priorité
        if feedback.priority == "CRITICAL":
            actions.insert(0, "IMMEDIATE_ATTENTION_REQUIRED")
        elif feedback.priority == "HIGH":
            actions.insert(0, "PRIORITIZE_RESOLUTION")
        
        return actions
    
    def _prioritize_issues(self, issues: List[str]) -> List[Dict]:
        """Priorisation des problèmes"""
        
        priority_keywords = {
            "CRITICAL": ["security", "crash", "data loss", "corruption"],
            "HIGH": ["error", "bug", "failure", "broken"],
            "MEDIUM": ["warning", "performance", "optimization"],
            "LOW": ["style", "formatting", "suggestion"]
        }
        
        prioritized = []
        for issue in issues:
            priority = "LOW"
            for level, keywords in priority_keywords.items():
                if any(keyword in issue.lower() for keyword in keywords):
                    priority = level
                    break
            
            prioritized.append({
                "issue": issue,
                "priority": priority,
                "estimated_effort": self._estimate_effort(issue),
                "impact": self._estimate_impact(issue)
            })
        
        return sorted(prioritized, key=lambda x: ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(x["priority"]), reverse=True)
    
    def _create_improvement_plan(self, issues: List[str], suggestions: List[str]) -> Dict:
        """Création d'un plan d'amélioration"""
        
        prioritized_issues = self._prioritize_issues(issues)
        
        plan = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_improvements": [],
            "estimated_timeline": {}
        }
        
        for item in prioritized_issues:
            if item["priority"] == "CRITICAL":
                plan["immediate_actions"].append(item)
            elif item["priority"] == "HIGH":
                plan["short_term_goals"].append(item)
            else:
                plan["long_term_improvements"].append(item)
        
        # Estimation des délais
        plan["estimated_timeline"] = {
            "immediate": f"{len(plan['immediate_actions'])} * 0.5 hours",
            "short_term": f"{len(plan['short_term_goals'])} * 2 hours",
            "long_term": f"{len(plan['long_term_improvements'])} * 4 hours"
        }
        
        return plan
    
    def _analyze_trends(self, trends: Dict) -> Dict:
        """Analyse des tendances"""
        analysis = {
            "improving_areas": [],
            "declining_areas": [],
            "stable_areas": [],
            "recommendations": []
        }
        
        for metric, values in trends.items():
            if len(values) < 2:
                continue
            
            recent_trend = values[-1] - values[-2]
            
            if recent_trend > 0.1:
                analysis["improving_areas"].append(metric)
            elif recent_trend < -0.1:
                analysis["declining_areas"].append(metric)
                analysis["recommendations"].append(f"Monitor {metric} - showing decline")
            else:
                analysis["stable_areas"].append(metric)
        
        return analysis
    
    def _suggest_auto_corrections(self, metrics: Dict, trends: Dict) -> List[str]:
        """Suggestions de corrections automatiques"""
        
        corrections = []
        
        for metric, value in metrics.items():
            if metric == "performance" and value < 0.5:
                corrections.append("AUTO_OPTIMIZE_PERFORMANCE")
            elif metric == "memory_usage" and value > 0.8:
                corrections.append("AUTO_CLEANUP_MEMORY")
            elif metric == "error_rate" and value > 0.1:
                corrections.append("AUTO_ERROR_MITIGATION")
        
        return corrections
    
    def _get_context_actions(self, context_type: str, value: Dict) -> List[str]:
        """Actions spécifiques au contexte"""
        
        context_actions = {
            "code_review": [
                "ANALYZE_CODE_QUALITY",
                "CHECK_SECURITY_PATTERNS",
                "VALIDATE_PERFORMANCE"
            ],
            "documentation": [
                "SYNC_WITH_CODE",
                "UPDATE_EXAMPLES",
                "VALIDATE_ACCURACY"
            ],
            "testing": [
                "EXPAND_TEST_COVERAGE",
                "VALIDATE_EDGE_CASES",
                "PERFORMANCE_TESTING"
            ]
        }
        
        return context_actions.get(context_type, ["GENERIC_IMPROVEMENT"])
    
    def _needs_adaptation(self, context_data: Dict) -> bool:
        """Détermine si une adaptation est nécessaire"""
        
        adaptation_triggers = [
            "new_technology",
            "changed_requirements",
            "performance_degradation",
            "security_update"
        ]
        
        return any(trigger in str(context_data).lower() for trigger in adaptation_triggers)
    
    def _calculate_learning_weight(self, context: Dict) -> float:
        """Calcule le poids d'apprentissage du feedback"""
        
        base_weight = 1.0
        
        # Ajustement selon la fiabilité de la source
        source_reliability = context.get("source_reliability", 0.5)
        base_weight *= source_reliability
        
        # Ajustement selon la fraîcheur
        recency_factor = context.get("recency_factor", 1.0)
        base_weight *= recency_factor
        
        # Ajustement selon la complexité
        complexity = context.get("complexity", "medium")
        complexity_weights = {"low": 1.2, "medium": 1.0, "high": 0.8}
        base_weight *= complexity_weights.get(complexity, 1.0)
        
        return min(base_weight, 2.0)  # Limite maximale
    
    def _get_context_recommendations(self, context: Dict) -> List[str]:
        """Recommandations basées sur le contexte"""
        
        recommendations = []
        
        if context.get("project_type") == "web":
            recommendations.append("Consider web-specific best practices")
        
        if context.get("team_size", 1) > 5:
            recommendations.append("Implement team collaboration guidelines")
        
        if context.get("deployment_frequency") == "high":
            recommendations.append("Focus on automation and reliability")
        
        return recommendations
    
    def _estimate_effort(self, issue: str) -> str:
        """Estimation de l'effort requis"""
        
        effort_keywords = {
            "LOW": ["typo", "formatting", "comment"],
            "MEDIUM": ["refactor", "optimize", "enhance"],
            "HIGH": ["rewrite", "redesign", "architecture"]
        }
        
        for level, keywords in effort_keywords.items():
            if any(keyword in issue.lower() for keyword in keywords):
                return level
        
        return "MEDIUM"
    
    def _estimate_impact(self, issue: str) -> str:
        """Estimation de l'impact"""
        
        impact_keywords = {
            "HIGH": ["security", "performance", "reliability"],
            "MEDIUM": ["usability", "maintainability"],
            "LOW": ["cosmetic", "style", "documentation"]
        }
        
        for level, keywords in impact_keywords.items():
            if any(keyword in issue.lower() for keyword in keywords):
                return level
        
        return "MEDIUM"
    
    def get_feedback_analytics(self) -> Dict:
        """Analyse des données de feedback"""
        
        if not self.feedback_history:
            return {"total_feedback": 0}
        
        analytics = {
            "total_feedback": len(self.feedback_history),
            "by_type": {},
            "by_category": {},
            "success_rate": 0.0,
            "recent_trends": {},
            "learning_progress": {}
        }
        
        # Analyse par type et catégorie
        for feedback in self.feedback_history:
            # Par type
            type_key = feedback.type.value
            analytics["by_type"][type_key] = analytics["by_type"].get(type_key, 0) + 1
            
            # Par catégorie
            cat_key = feedback.category.value
            analytics["by_category"][cat_key] = analytics["by_category"].get(cat_key, 0) + 1
        
        # Taux de succès global
        binary_feedback = [f for f in self.feedback_history if f.type == FeedbackType.BINARY]
        if binary_feedback:
            successful = len([f for f in binary_feedback if f.value == "Parfait"])
            analytics["success_rate"] = successful / len(binary_feedback)
        
        # Progrès d'apprentissage
        for pattern_key, pattern in self.learning_patterns.items():
            analytics["learning_progress"][pattern_key] = {
                "success_rate": pattern["success_rate"],
                "confidence": min(pattern["occurrences"] / 10, 1.0)
            }
        
        return analytics
    
    def export_feedback_data(self, file_path: str):
        """Export des données de feedback"""
        
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_feedback": len(self.feedback_history),
                "version": "1.0"
            },
            "feedback_history": [
                {
                    "feedback_id": f.feedback_id,
                    "type": f.type.value,
                    "category": f.category.value,
                    "value": f.value,
                    "confidence": f.confidence,
                    "timestamp": f.timestamp.isoformat(),
                    "priority": f.priority
                }
                for f in self.feedback_history
            ],
            "learning_patterns": self.learning_patterns,
            "analytics": self.get_feedback_analytics()
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)

# Exemple d'utilisation avancée
if __name__ == "__main__":
    feedback_system = ODINFeedbackSystem()
    
    # Exemple de feedback binaire
    binary_feedback = FeedbackItem(
        feedback_id="BIN_001",
        type=FeedbackType.BINARY,
        category=FeedbackCategory.CODE_QUALITY,
        value="Parfait",
        confidence=0.9,
        timestamp=datetime.now(),
        context={"operation": "code_generation", "complexity": "medium"}
    )
    
    result = feedback_system.collect_feedback(binary_feedback)
    print("Binary feedback result:", result)
    
    # Exemple de feedback détaillé
    detailed_feedback = FeedbackItem(
        feedback_id="DET_001",
        type=FeedbackType.DETAILED,
        category=FeedbackCategory.CODE_QUALITY,
        value={
            "issues": ["Performance could be improved", "Missing error handling"],
            "positive": ["Good code structure", "Clear naming"],
            "suggestions": ["Add try-catch blocks", "Implement caching"]
        },
        confidence=0.8,
        timestamp=datetime.now(),
        context={"project_type": "web", "team_size": 3},
        priority="HIGH"
    )
    
    result = feedback_system.collect_feedback(detailed_feedback)
    print("Detailed feedback result:", result)
    
    # Analytics
    analytics = feedback_system.get_feedback_analytics()
    print("Analytics:", analytics)"success": False, "error": "Invalid feedback format"}
        
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
