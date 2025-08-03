"""
Edge Case Generator Module for TestGen

Provides functionality to determine edge cases for given function inputs.
"""

class EdgeCaseGenerator:
    def detect_edge_cases(self, inputs):
        """
        Generate edge cases from given function input specifications.
        """
        # Example heuristic logic
        edge_cases = []
        for input_type in inputs:
            if input_type == "int":
                edge_cases.extend([-1, 0, 1, 100, -100])
            elif input_type == "str":
                edge_cases.extend(["", " ", "!@#$$%^", "longstring" * 10])
            # Extend more heuristics as needed
        return edge_cases

