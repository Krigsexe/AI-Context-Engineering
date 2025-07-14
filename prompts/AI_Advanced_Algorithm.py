import hashlib
import json
import difflib
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re

class ODINValidationEngine:
    """
    Moteur de validation avancé pour ODIN
    Intégration de contrôles d'intégrité, détection de drift, et validation contextuelle
    """
    
    def __init__(self):
        self.hash_algorithm = hashlib.sha256
        self.similarity_threshold = 0.85
        self.validation_rules = self._load_validation_rules()
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calcul hash sécurisé d'un fichier"""
        try:
            with open(file_path, 'rb') as f:
                return self.hash_algorithm(f.read()).hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def validate_file_integrity(self, file_path: str, expected_hash: str) -> Dict:
        """Validation d'intégrité avec diagnostic détaillé"""
        current_hash = self.calculate_file_hash(file_path)
        
        result = {
            "file": file_path,
            "expected_hash": expected_hash,
            "current_hash": current_hash,
            "is_valid": current_hash == expected_hash,
            "timestamp": datetime.now().isoformat(),
            "error": None
        }
        
        if not result["is_valid"]:
            result["error"] = "Hash mismatch - file may have been modified"
            result["severity"] = "CRITICAL"
        
        return result
    
    def detect_documentation_drift(self, code_content: str, doc_content: str) -> Dict:
        """Détection de drift entre code et documentation"""
        
        # Extraction des éléments clés du code
        code_elements = self._extract_code_elements(code_content)
        doc_elements = self._extract_doc_elements(doc_content)
        
        # Calcul de similarité
        similarity = self._calculate_similarity(code_elements, doc_elements)
        
        return {
            "similarity_score": similarity,
            "drift_detected": similarity < self.similarity_threshold,
            "missing_in_doc": code_elements - doc_elements,
            "extra_in_doc": doc_elements - code_elements,
            "recommendations": self._generate_sync_recommendations(code_elements, doc_elements)
        }
    
    def validate_user_input(self, user_input: str) -> Dict:
        """Validation sécurisée des entrées utilisateur"""
        
        validation_result = {
            "input": user_input,
            "is_valid": True,
            "issues": [],
            "sanitized_input": user_input,
            "risk_level": "LOW"
        }
        
        # Détection d'injections potentielles
        injection_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'eval\s*\(',
            r'exec\s*\(',
            r'import\s+os',
            r'__import__',
            r'subprocess',
            r'system\s*\('
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                validation_result["is_valid"] = False
                validation_result["issues"].append(f"Potential injection detected: {pattern}")
                validation_result["risk_level"] = "HIGH"
        
        # Validation de longueur
        if len(user_input) > 10000:
            validation_result["issues"].append("Input too long")
            validation_result["risk_level"] = "MEDIUM"
        
        # Sanitisation
        if validation_result["is_valid"]:
            validation_result["sanitized_input"] = self._sanitize_input(user_input)
        
        return validation_result
    
    def _extract_code_elements(self, code: str) -> set:
        """Extraction des éléments significatifs du code"""
        elements = set()
        
        # Fonctions
        functions = re.findall(r'def\s+(\w+)', code)
        elements.update(f"function:{func}" for func in functions)
        
        # Classes
        classes = re.findall(r'class\s+(\w+)', code)
        elements.update(f"class:{cls}" for cls in classes)
        
        # Variables globales
        variables = re.findall(r'^(\w+)\s*=', code, re.MULTILINE)
        elements.update(f"variable:{var}" for var in variables)
        
        return elements
    
    def _extract_doc_elements(self, doc: str) -> set:
        """Extraction des éléments mentionnés dans la documentation"""
        elements = set()
        
        # Recherche de références de fonctions
        functions = re.findall(r'(\w+)\(\)', doc)
        elements.update(f"function:{func}" for func in functions)
        
        # Recherche de classes
        classes = re.findall(r'(\w+)\s*class', doc)
        elements.update(f"class:{cls}" for cls in classes)
        
        return elements
    
    def _calculate_similarity(self, set1: set, set2: set) -> float:
        """Calcul de similarité entre deux ensembles"""
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_sync_recommendations(self, code_elements: set, doc_elements: set) -> List[str]:
        """Génération de recommandations pour synchroniser code et doc"""
        recommendations = []
        
        missing_in_doc = code_elements - doc_elements
        extra_in_doc = doc_elements - code_elements
        
        for element in missing_in_doc:
            recommendations.append(f"Add documentation for {element}")
        
        for element in extra_in_doc:
            recommendations.append(f"Remove or update documentation for {element}")
        
        return recommendations
    
    def _sanitize_input(self, input_str: str) -> str:
        """Sanitisation des entrées utilisateur"""
        # Suppression des caractères dangereux
        sanitized = re.sub(r'[<>"\']', '', input_str)
        
        # Limitation de longueur
        sanitized = sanitized[:5000]
        
        return sanitized.strip()
    
    def _load_validation_rules(self) -> Dict:
        """Chargement des règles de validation personnalisées"""
        return {
            "max_input_length": 10000,
            "allowed_file_extensions": [".py", ".js", ".ts", ".md", ".json", ".yml", ".yaml"],
            "forbidden_patterns": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"__import__",
                r"subprocess\.call",
                r"os\.system"
            ]
        }

# Exemple d'utilisation
if __name__ == "__main__":
    validator = ODINValidationEngine()
    
    # Test de validation d'intégrité
    result = validator.validate_file_integrity("example.py", "abcd1234...")
    print("Validation intégrité:", result)
    
    # Test de détection de drift
    code = "def hello(): pass\nclass World: pass"
    doc = "Documentation mentionnant hello() mais pas World"
    drift = validator.detect_documentation_drift(code, doc)
    print("Drift détecté:", drift)
    
    # Test de validation d'entrée
    user_input = "print('Hello World')"
    validation = validator.validate_user_input(user_input)
    print("Validation entrée:", validation)
