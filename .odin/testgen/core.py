"""
Core Test Generation Logic for TestGen

Exposes the main interface to generate tests for given functions in various languages and frameworks.
"""

from .parser import FunctionParser
from .heuristics import EdgeCaseGenerator
from .renderers import TestRenderer


def generate_tests_for_function(code, language="python", framework="pytest"):
    """
    Generate tests for a given function code in the specified language and framework.

    :param code: The source code of the function
    :param language: The programming language of the code ('python', 'javascript', or 'typescript')
    :param framework: The test framework to use ('pytest', 'jest', 'luassert')
    :return: Rendered test code as a string
    """
    parser = FunctionParser()
    generator = EdgeCaseGenerator()
    renderer = TestRenderer()

    if language == "python":
        functions = parser.parse_python(code)
    else:
        functions = parser.parse_js_ts(code)

    if not functions:
        return "No functions found in the code."

    function = functions[0]  # Assuming single function for simplicity
    inputs = []  # Extract input types here based on language
    edge_cases = generator.detect_edge_cases(inputs)
    test_cases = []  # Construct test cases here based on detected edge cases

    if framework == "pytest":
        return renderer.render_pytest(function.name, test_cases)
    elif framework == "jest":
        return renderer.render_jest(function.name, test_cases)
    elif framework == "luassert":
        return renderer.render_luassert(function.name, test_cases)
    else:
        return "Unsupported test framework."

