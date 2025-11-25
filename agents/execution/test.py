# =============================================================================
# ODIN v7.0 - Test Agent
# =============================================================================
# Test generation, execution, and coverage analysis
# =============================================================================

from __future__ import annotations
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..shared import (
    BaseAgent,
    AgentCapability,
    AgentResult,
    ConfidenceLevel,
    agent,
)


@agent
class TestAgent(BaseAgent):
    """
    Test Agent - Test generation and execution.

    Responsibilities:
    1. Generate unit tests
    2. Generate integration tests
    3. Run test suites
    4. Analyze coverage
    5. Suggest test improvements
    """

    @property
    def name(self) -> str:
        return "test"

    @property
    def description(self) -> str:
        return "Generates tests, runs test suites, and analyzes coverage"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="generate_tests",
                description="Generate tests for code",
                input_schema={
                    "code": "string",
                    "language": "string",
                    "test_framework": "string",
                },
                output_schema={
                    "tests": "string",
                    "coverage_targets": "list",
                },
            ),
            AgentCapability(
                name="run_tests",
                description="Run test suite",
                input_schema={
                    "test_command": "string",
                    "working_dir": "string",
                },
                output_schema={
                    "passed": "int",
                    "failed": "int",
                    "output": "string",
                },
                risk_level="low",
            ),
            AgentCapability(
                name="analyze_coverage",
                description="Analyze test coverage",
                input_schema={
                    "coverage_report": "string",
                },
                output_schema={
                    "coverage_percent": "float",
                    "uncovered": "list",
                },
            ),
        ]

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute test task."""

        handlers = {
            "generate_tests": self._generate_tests,
            "generate_unit_tests": self._generate_unit_tests,
            "generate_integration_tests": self._generate_integration_tests,
            "run_tests": self._run_tests,
            "analyze_coverage": self._analyze_coverage,
            "suggest_tests": self._suggest_tests,
        }

        handler = handlers.get(task_type)
        if not handler:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Unknown task type: {task_type}",
            )

        return await handler(input_data, context)

    async def _generate_tests(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Generate tests for code."""

        code = input_data.get("code", "")
        language = input_data.get("language", "python")
        test_framework = input_data.get("test_framework", self._detect_framework(language))
        test_type = input_data.get("test_type", "unit")

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided",
            )

        system_prompt = f"""You are a test engineer expert in {language} and {test_framework}.
Generate comprehensive {test_type} tests that:

1. Cover all public functions/methods
2. Test edge cases and error conditions
3. Use descriptive test names
4. Include setup/teardown when needed
5. Mock external dependencies appropriately
6. Follow {test_framework} best practices

Provide:
- Complete test code
- List of scenarios covered
- Suggested additional test cases"""

        prompt = f"""Generate {test_type} tests for this {language} code using {test_framework}:

```{language}
{code}
```"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            # Extract test code
            code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)```', response)
            test_code = code_blocks[0] if code_blocks else ""

            # Extract covered scenarios
            scenarios = []
            scenario_match = re.search(r'(?:scenarios?|cases?|covered)[\s:]*\n((?:[-*]\s+.+\n?)+)', response, re.I)
            if scenario_match:
                scenarios = [s.strip('- *').strip() for s in scenario_match.group(1).split('\n') if s.strip()]

            return AgentResult(
                success=bool(test_code),
                data={
                    "tests": test_code,
                    "language": language,
                    "framework": test_framework,
                    "test_type": test_type,
                    "scenarios_covered": scenarios,
                },
                confidence=ConfidenceLevel.HIGH if test_code else ConfidenceLevel.UNCERTAIN,
                reasoning=f"Generated {test_type} tests using {test_framework}",
                suggestions=["Review generated tests", "Add edge cases as needed"],
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Test generation failed: {e}",
            )

    async def _generate_unit_tests(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Generate unit tests specifically."""
        input_data["test_type"] = "unit"
        return await self._generate_tests(input_data, context)

    async def _generate_integration_tests(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Generate integration tests."""
        input_data["test_type"] = "integration"
        return await self._generate_tests(input_data, context)

    async def _run_tests(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Run test suite."""

        test_command = input_data.get("test_command", "")
        working_dir = input_data.get("working_dir", ".")
        timeout = input_data.get("timeout", 300)

        if not test_command:
            # Try to detect test command
            test_command = self._detect_test_command(working_dir)

        if not test_command:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No test command provided and could not auto-detect",
            )

        try:
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                timeout=timeout,
                cwd=working_dir,
            )

            stdout = result.stdout.decode("utf-8", errors="replace")
            stderr = result.stderr.decode("utf-8", errors="replace")
            output = stdout + stderr

            # Parse results
            stats = self._parse_test_output(output, test_command)

            success = result.returncode == 0

            return AgentResult(
                success=success,
                data={
                    "passed": stats.get("passed", 0),
                    "failed": stats.get("failed", 0),
                    "skipped": stats.get("skipped", 0),
                    "total": stats.get("total", 0),
                    "output": output[-10000:],  # Last 10k chars
                    "exit_code": result.returncode,
                    "command": test_command,
                },
                confidence=ConfidenceLevel.AXIOM,  # Execution results are deterministic
                reasoning=f"Tests: {stats.get('passed', 0)} passed, {stats.get('failed', 0)} failed",
            )

        except subprocess.TimeoutExpired:
            return AgentResult(
                success=False,
                data={"errors": f"Tests timed out after {timeout}s"},
                confidence=ConfidenceLevel.AXIOM,
                reasoning="Test execution timed out",
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Test execution failed: {e}",
            )

    async def _analyze_coverage(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Analyze test coverage."""

        coverage_report = input_data.get("coverage_report", "")
        coverage_file = input_data.get("coverage_file", "")

        if not coverage_report and coverage_file:
            try:
                coverage_report = Path(coverage_file).read_text()
            except Exception as e:
                return AgentResult(
                    success=False,
                    data=None,
                    confidence=ConfidenceLevel.AXIOM,
                    reasoning=f"Could not read coverage file: {e}",
                )

        if not coverage_report:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No coverage data provided",
            )

        # Parse coverage data
        coverage_percent = 0.0
        uncovered_lines = []

        # Try to extract percentage
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', coverage_report)
        if pct_match:
            coverage_percent = float(pct_match.group(1))

        # Extract uncovered files/lines
        uncovered_matches = re.findall(r'(\S+\.py)\s+\d+\s+\d+\s+(\d+)%', coverage_report)
        for file_path, pct in uncovered_matches:
            if int(pct) < 80:
                uncovered_lines.append({
                    "file": file_path,
                    "coverage": int(pct),
                })

        return AgentResult(
            success=True,
            data={
                "coverage_percent": coverage_percent,
                "uncovered": uncovered_lines,
                "meets_threshold": coverage_percent >= 80,
            },
            confidence=ConfidenceLevel.HIGH,
            reasoning=f"Coverage: {coverage_percent}%",
            warnings=["Coverage below 80%"] if coverage_percent < 80 else [],
        )

    async def _suggest_tests(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Suggest tests to improve coverage."""

        code = input_data.get("code", "")
        existing_tests = input_data.get("existing_tests", "")
        coverage_report = input_data.get("coverage_report", "")

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided",
            )

        system_prompt = """You are a test coverage expert. Analyze the code and suggest tests to improve coverage.

Provide:
1. **Missing Tests**: Functions/methods without tests
2. **Edge Cases**: Edge cases not covered
3. **Error Paths**: Error handling not tested
4. **Suggested Tests**: Specific test cases to add with descriptions

Respond in JSON format."""

        prompt = f"""Analyze test coverage and suggest improvements:

Code:
```
{code}
```

{"Existing Tests:" + existing_tests if existing_tests else "No existing tests provided."}

{"Coverage Report:" + coverage_report if coverage_report else ""}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                suggestions = json.loads(json_match.group(1))
            else:
                suggestions = json.loads(response)

            return AgentResult(
                success=True,
                data={
                    "missing_tests": suggestions.get("missing_tests", []),
                    "edge_cases": suggestions.get("edge_cases", []),
                    "error_paths": suggestions.get("error_paths", []),
                    "suggested_tests": suggestions.get("suggested_tests", []),
                },
                confidence=ConfidenceLevel.MODERATE,
                reasoning=f"Suggested {len(suggestions.get('suggested_tests', []))} new tests",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Test suggestion failed: {e}",
            )

    def _detect_framework(self, language: str) -> str:
        """Detect default test framework for language."""
        frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "go": "testing",
            "rust": "cargo test",
            "java": "junit",
        }
        return frameworks.get(language.lower(), "unittest")

    def _detect_test_command(self, working_dir: str) -> Optional[str]:
        """Detect test command from project files."""
        path = Path(working_dir)

        # Python
        if (path / "pytest.ini").exists() or (path / "pyproject.toml").exists():
            return "pytest -v"
        if (path / "setup.py").exists():
            return "python -m pytest -v"

        # Node.js
        package_json = path / "package.json"
        if package_json.exists():
            import json
            try:
                pkg = json.loads(package_json.read_text())
                if "test" in pkg.get("scripts", {}):
                    return "npm test"
            except Exception:
                pass

        # Go
        if list(path.glob("*_test.go")):
            return "go test -v ./..."

        return None

    def _parse_test_output(self, output: str, command: str) -> Dict[str, int]:
        """Parse test output to extract stats."""
        stats = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}

        # pytest
        pytest_match = re.search(r'(\d+) passed', output)
        if pytest_match:
            stats["passed"] = int(pytest_match.group(1))
        pytest_fail = re.search(r'(\d+) failed', output)
        if pytest_fail:
            stats["failed"] = int(pytest_fail.group(1))
        pytest_skip = re.search(r'(\d+) skipped', output)
        if pytest_skip:
            stats["skipped"] = int(pytest_skip.group(1))

        # Jest
        jest_match = re.search(r'Tests:\s+(\d+) passed', output)
        if jest_match:
            stats["passed"] = int(jest_match.group(1))
        jest_fail = re.search(r'(\d+) failed', output)
        if jest_fail:
            stats["failed"] = int(jest_fail.group(1))

        # Go
        go_pass = len(re.findall(r'--- PASS:', output))
        go_fail = len(re.findall(r'--- FAIL:', output))
        if go_pass or go_fail:
            stats["passed"] = go_pass
            stats["failed"] = go_fail

        stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"]
        return stats
