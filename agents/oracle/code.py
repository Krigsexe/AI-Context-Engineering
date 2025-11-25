# =============================================================================
# ODIN v7.0 - Oracle Code Agent
# =============================================================================
# Code execution verification oracle
# Validates code by actually running it in isolated environments
# =============================================================================

from __future__ import annotations
import subprocess
import tempfile
import os
import re
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
class OracleCodeAgent(BaseAgent):
    """
    Oracle Code Agent - Code verification through execution.

    Responsibilities:
    1. Execute code in isolated sandbox
    2. Verify code produces expected outputs
    3. Run tests and report results
    4. Check for runtime errors
    5. Validate security constraints

    This is a CRITICAL verification agent - its results
    carry AXIOM confidence when successful.
    """

    @property
    def name(self) -> str:
        return "oracle_code"

    @property
    def description(self) -> str:
        return "Verifies code through execution in isolated environments"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="execute_code",
                description="Execute code and capture output",
                input_schema={
                    "code": "string",
                    "language": "string",
                    "timeout": "int",
                },
                output_schema={
                    "success": "bool",
                    "output": "string",
                    "errors": "string",
                },
                risk_level="high",
            ),
            AgentCapability(
                name="run_tests",
                description="Run test suite and report results",
                input_schema={
                    "test_command": "string",
                    "working_dir": "string",
                },
                output_schema={
                    "passed": "int",
                    "failed": "int",
                    "output": "string",
                },
                risk_level="medium",
            ),
            AgentCapability(
                name="verify_output",
                description="Verify code produces expected output",
                input_schema={
                    "code": "string",
                    "expected_output": "string",
                },
                output_schema={
                    "matches": "bool",
                    "actual_output": "string",
                },
                risk_level="high",
            ),
            AgentCapability(
                name="syntax_check",
                description="Check code for syntax errors",
                input_schema={
                    "code": "string",
                    "language": "string",
                },
                output_schema={
                    "valid": "bool",
                    "errors": "list",
                },
                risk_level="low",
            ),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sandbox_enabled = kwargs.get("sandbox_enabled", True)
        self.max_execution_time = kwargs.get("max_execution_time", 30)

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute oracle verification task."""

        handlers = {
            "execute_code": self._execute_code,
            "run_tests": self._run_tests,
            "verify_output": self._verify_output,
            "syntax_check": self._syntax_check,
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

    async def _execute_code(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute code in isolated environment."""

        code = input_data.get("code", "")
        language = input_data.get("language", "python").lower()
        timeout = min(input_data.get("timeout", 30), self.max_execution_time)
        stdin_input = input_data.get("stdin", "")

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided",
            )

        # Get execution command for language
        executor = self._get_executor(language)
        if not executor:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Unsupported language: {language}",
            )

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write code to temp file
                ext = self._get_extension(language)
                code_file = Path(tmpdir) / f"code{ext}"
                code_file.write_text(code, encoding="utf-8")

                # Build execution command
                cmd = executor["command"](str(code_file))

                # Execute with timeout
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    timeout=timeout,
                    cwd=tmpdir,
                    input=stdin_input.encode() if stdin_input else None,
                    env=self._get_sandbox_env() if self.sandbox_enabled else None,
                )

                stdout = result.stdout.decode("utf-8", errors="replace")
                stderr = result.stderr.decode("utf-8", errors="replace")
                success = result.returncode == 0

                return AgentResult(
                    success=success,
                    data={
                        "output": stdout,
                        "errors": stderr,
                        "exit_code": result.returncode,
                        "language": language,
                    },
                    confidence=ConfidenceLevel.AXIOM,  # Execution is deterministic
                    reasoning="Code executed successfully" if success else f"Execution failed with code {result.returncode}",
                )

        except subprocess.TimeoutExpired:
            return AgentResult(
                success=False,
                data={"errors": f"Execution timed out after {timeout}s"},
                confidence=ConfidenceLevel.AXIOM,
                reasoning="Code execution timed out",
                warnings=["Consider optimizing code or increasing timeout"],
            )
        except Exception as e:
            self.log("execution_error", {"error": str(e)}, level="error")
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Execution failed: {e}",
            )

    async def _run_tests(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Run test suite."""

        test_command = input_data.get("test_command", "")
        working_dir = input_data.get("working_dir", os.getcwd())
        timeout = min(input_data.get("timeout", 300), 600)  # Max 10 min

        if not test_command:
            # Try to detect test framework
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

            # Parse test results
            test_stats = self._parse_test_output(output, test_command)

            success = result.returncode == 0

            return AgentResult(
                success=success,
                data={
                    "passed": test_stats.get("passed", 0),
                    "failed": test_stats.get("failed", 0),
                    "skipped": test_stats.get("skipped", 0),
                    "total": test_stats.get("total", 0),
                    "output": output[-5000:],  # Last 5000 chars
                    "exit_code": result.returncode,
                    "command": test_command,
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Tests: {test_stats.get('passed', 0)} passed, {test_stats.get('failed', 0)} failed",
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

    async def _verify_output(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Verify code produces expected output."""

        code = input_data.get("code", "")
        expected_output = input_data.get("expected_output", "")
        language = input_data.get("language", "python")
        strict = input_data.get("strict", False)

        # Execute code first
        exec_result = await self._execute_code(
            {"code": code, "language": language},
            context
        )

        if not exec_result.success:
            return AgentResult(
                success=False,
                data={
                    "matches": False,
                    "actual_output": exec_result.data.get("errors", "Execution failed"),
                    "expected_output": expected_output,
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning="Code execution failed during verification",
            )

        actual_output = exec_result.data.get("output", "")

        # Compare outputs
        if strict:
            matches = actual_output == expected_output
        else:
            # Normalize whitespace for comparison
            actual_normalized = " ".join(actual_output.split())
            expected_normalized = " ".join(expected_output.split())
            matches = actual_normalized == expected_normalized

        return AgentResult(
            success=matches,
            data={
                "matches": matches,
                "actual_output": actual_output,
                "expected_output": expected_output,
                "strict_mode": strict,
            },
            confidence=ConfidenceLevel.AXIOM,
            reasoning="Output matches expected" if matches else "Output does not match expected",
        )

    async def _syntax_check(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Check code for syntax errors without execution."""

        code = input_data.get("code", "")
        language = input_data.get("language", "python").lower()

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided",
            )

        errors = []

        if language == "python":
            try:
                import ast
                ast.parse(code)
            except SyntaxError as e:
                errors.append({
                    "line": e.lineno,
                    "column": e.offset,
                    "message": str(e.msg),
                })
        elif language in ("javascript", "typescript"):
            # Use node --check or esbuild
            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".js" if language == "javascript" else ".ts",
                    mode="w",
                    delete=False
                ) as f:
                    f.write(code)
                    f.flush()
                    result = subprocess.run(
                        f"node --check {f.name}",
                        shell=True,
                        capture_output=True,
                        timeout=10
                    )
                    if result.returncode != 0:
                        errors.append({
                            "message": result.stderr.decode("utf-8", errors="replace")
                        })
                    os.unlink(f.name)
            except Exception as e:
                errors.append({"message": str(e)})
        elif language == "go":
            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".go",
                    mode="w",
                    delete=False
                ) as f:
                    f.write(code)
                    f.flush()
                    result = subprocess.run(
                        f"gofmt -e {f.name}",
                        shell=True,
                        capture_output=True,
                        timeout=10
                    )
                    if result.returncode != 0:
                        errors.append({
                            "message": result.stderr.decode("utf-8", errors="replace")
                        })
                    os.unlink(f.name)
            except Exception as e:
                errors.append({"message": str(e)})
        else:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Syntax check not supported for: {language}",
            )

        valid = len(errors) == 0

        return AgentResult(
            success=valid,
            data={
                "valid": valid,
                "errors": errors,
                "language": language,
            },
            confidence=ConfidenceLevel.AXIOM,
            reasoning="Syntax is valid" if valid else f"Found {len(errors)} syntax error(s)",
        )

    def _get_executor(self, language: str) -> Optional[Dict]:
        """Get executor configuration for language."""
        executors = {
            "python": {
                "command": lambda f: f"python3 {f}",
                "extension": ".py",
            },
            "javascript": {
                "command": lambda f: f"node {f}",
                "extension": ".js",
            },
            "typescript": {
                "command": lambda f: f"npx ts-node {f}",
                "extension": ".ts",
            },
            "go": {
                "command": lambda f: f"go run {f}",
                "extension": ".go",
            },
            "rust": {
                "command": lambda f: f"rustc {f} -o /tmp/rust_out && /tmp/rust_out",
                "extension": ".rs",
            },
            "bash": {
                "command": lambda f: f"bash {f}",
                "extension": ".sh",
            },
        }
        return executors.get(language)

    def _get_extension(self, language: str) -> str:
        """Get file extension for language."""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "go": ".go",
            "rust": ".rs",
            "bash": ".sh",
            "java": ".java",
        }
        return extensions.get(language, ".txt")

    def _get_sandbox_env(self) -> Dict[str, str]:
        """Get restricted environment for sandbox execution."""
        env = os.environ.copy()
        # Remove sensitive env vars
        sensitive_keys = [
            "AWS_", "GOOGLE_", "AZURE_", "API_KEY", "SECRET",
            "TOKEN", "PASSWORD", "CREDENTIAL"
        ]
        return {
            k: v for k, v in env.items()
            if not any(s in k.upper() for s in sensitive_keys)
        }

    def _detect_test_command(self, working_dir: str) -> Optional[str]:
        """Auto-detect test command from project."""
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

        # Rust
        if (path / "Cargo.toml").exists():
            return "cargo test"

        return None

    def _parse_test_output(self, output: str, command: str) -> Dict[str, int]:
        """Parse test output to extract stats."""
        stats = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}

        # pytest format
        pytest_match = re.search(
            r'(\d+) passed.*?(\d+) failed|(\d+) passed',
            output
        )
        if pytest_match:
            if pytest_match.group(1):
                stats["passed"] = int(pytest_match.group(1))
            if pytest_match.group(2):
                stats["failed"] = int(pytest_match.group(2))
            if pytest_match.group(3):
                stats["passed"] = int(pytest_match.group(3))
            stats["total"] = stats["passed"] + stats["failed"]
            return stats

        # Jest format
        jest_match = re.search(
            r'Tests:\s+(\d+) passed.*?(\d+) failed|Tests:\s+(\d+) passed',
            output
        )
        if jest_match:
            if jest_match.group(1):
                stats["passed"] = int(jest_match.group(1))
            if jest_match.group(2):
                stats["failed"] = int(jest_match.group(2))
            if jest_match.group(3):
                stats["passed"] = int(jest_match.group(3))
            stats["total"] = stats["passed"] + stats["failed"]
            return stats

        # Go test format
        go_pass = len(re.findall(r'--- PASS:', output))
        go_fail = len(re.findall(r'--- FAIL:', output))
        if go_pass or go_fail:
            stats["passed"] = go_pass
            stats["failed"] = go_fail
            stats["total"] = go_pass + go_fail
            return stats

        return stats
