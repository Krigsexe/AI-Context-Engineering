# =============================================================================
# ODIN v7.0 - Development Agent
# =============================================================================
# Code generation, modification, and debugging
# =============================================================================

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional

from ..shared import (
    BaseAgent,
    AgentCapability,
    AgentResult,
    ConfidenceLevel,
    agent,
)


@agent
class DevAgent(BaseAgent):
    """
    Development Agent - Code generation and modification.

    Responsibilities:
    1. Generate new code based on requirements
    2. Modify existing code
    3. Debug and fix issues
    4. Suggest improvements
    5. Follow project conventions
    """

    @property
    def name(self) -> str:
        return "dev"

    @property
    def description(self) -> str:
        return "Generates and modifies code based on requirements and context"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="generate_code",
                description="Generate new code from requirements",
                input_schema={
                    "requirements": "string",
                    "language": "string",
                    "context": "object",
                },
                output_schema={
                    "code": "string",
                    "explanation": "string",
                    "files": "list",
                },
                requires_approval=True,
                risk_level="medium",
            ),
            AgentCapability(
                name="modify_code",
                description="Modify existing code",
                input_schema={
                    "file_path": "string",
                    "current_code": "string",
                    "changes": "string",
                },
                output_schema={
                    "modified_code": "string",
                    "diff": "string",
                },
                requires_approval=True,
                risk_level="medium",
            ),
            AgentCapability(
                name="debug_code",
                description="Debug and fix code issues",
                input_schema={
                    "code": "string",
                    "error": "string",
                    "context": "object",
                },
                output_schema={
                    "fixed_code": "string",
                    "explanation": "string",
                    "root_cause": "string",
                },
                requires_approval=True,
                risk_level="medium",
            ),
        ]

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute development task."""

        handlers = {
            "generate_code": self._generate_code,
            "modify_code": self._modify_code,
            "debug_code": self._debug_code,
            "explain_code": self._explain_code,
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

    async def _generate_code(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Generate new code from requirements."""

        requirements = input_data.get("requirements", "")
        language = input_data.get("language", "python")
        file_path = input_data.get("file_path", "")

        # Build context string
        context_str = ""
        if context:
            if context.get("existing_code"):
                context_str += f"\n\nExisting code to extend:\n```\n{context['existing_code']}\n```"
            if context.get("related_files"):
                context_str += f"\n\nRelated files:\n{context['related_files']}"
            if context.get("project_conventions"):
                context_str += f"\n\nProject conventions:\n{context['project_conventions']}"

        system_prompt = f"""You are an expert {language} developer. Generate high-quality, production-ready code.

Guidelines:
1. Follow best practices and idioms for {language}
2. Include appropriate error handling
3. Add clear comments for complex logic
4. Follow SOLID principles
5. Make code testable
6. Avoid security vulnerabilities (OWASP Top 10)
7. Use meaningful variable and function names

Respond with:
1. The generated code in a code block
2. A brief explanation of your implementation choices
3. Any assumptions you made
4. Suggestions for testing"""

        prompt = f"""Generate {language} code for the following requirements:

{requirements}
{context_str}

Target file: {file_path or 'Not specified'}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            # Extract code blocks from response
            code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)```', response)
            code = code_blocks[0] if code_blocks else ""

            # Extract explanation (text outside code blocks)
            explanation = re.sub(r'```[\s\S]*?```', '', response).strip()

            # Assess confidence based on response quality
            confidence = ConfidenceLevel.MODERATE
            if code and len(code) > 50:
                confidence = ConfidenceLevel.HIGH

            warnings = []
            if not code:
                warnings.append("No code block found in response")

            return AgentResult(
                success=bool(code),
                data={
                    "code": code,
                    "explanation": explanation,
                    "language": language,
                    "file_path": file_path,
                },
                confidence=confidence,
                reasoning="Code generated based on requirements",
                warnings=warnings,
                suggestions=[
                    "Review generated code before applying",
                    "Run tests to verify functionality",
                    "Consider edge cases",
                ],
            )

        except Exception as e:
            self.log("generation_error", {"error": str(e)}, level="error")
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Code generation failed: {e}",
            )

    async def _modify_code(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Modify existing code."""

        file_path = input_data.get("file_path", "")
        current_code = input_data.get("current_code", "")
        changes = input_data.get("changes", "")

        if not current_code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No current code provided",
            )

        system_prompt = """You are an expert code modifier. Make precise, minimal changes to existing code.

Guidelines:
1. Make only the requested changes
2. Preserve existing style and conventions
3. Don't introduce unrelated changes
4. Maintain backward compatibility when possible
5. Add comments for non-obvious changes
6. Consider side effects

Respond with:
1. The modified code in a code block
2. A summary of changes made
3. Any potential impacts or side effects"""

        prompt = f"""Modify this code:

File: {file_path}

Current code:
```
{current_code}
```

Requested changes:
{changes}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            # Extract modified code
            code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)```', response)
            modified_code = code_blocks[0] if code_blocks else ""

            # Generate diff-like summary
            explanation = re.sub(r'```[\s\S]*?```', '', response).strip()

            return AgentResult(
                success=bool(modified_code),
                data={
                    "modified_code": modified_code,
                    "original_code": current_code,
                    "file_path": file_path,
                    "changes_summary": explanation,
                },
                confidence=ConfidenceLevel.MODERATE,
                reasoning="Code modified as requested",
                suggestions=[
                    "Review changes carefully",
                    "Run existing tests",
                    "Check for regressions",
                ],
            )

        except Exception as e:
            self.log("modification_error", {"error": str(e)}, level="error")
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Code modification failed: {e}",
            )

    async def _debug_code(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Debug and fix code issues."""

        code = input_data.get("code", "")
        error = input_data.get("error", "")
        stack_trace = input_data.get("stack_trace", "")

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided for debugging",
            )

        system_prompt = """You are an expert debugger. Analyze code and errors to find and fix root causes.

Guidelines:
1. Identify the root cause, not just symptoms
2. Explain why the error occurs
3. Provide a minimal fix
4. Suggest preventive measures
5. Consider edge cases that might cause similar issues

Respond with:
1. Root cause analysis
2. The fixed code in a code block
3. Explanation of the fix
4. Prevention suggestions"""

        prompt = f"""Debug this code:

```
{code}
```

Error message:
{error}

Stack trace:
{stack_trace or 'Not provided'}

Additional context:
{context or 'None'}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            # Extract fixed code
            code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)```', response)
            fixed_code = code_blocks[0] if code_blocks else ""

            explanation = re.sub(r'```[\s\S]*?```', '', response).strip()

            # Higher confidence if we found specific fix
            confidence = ConfidenceLevel.MODERATE
            if fixed_code and fixed_code != code:
                confidence = ConfidenceLevel.HIGH

            return AgentResult(
                success=bool(fixed_code),
                data={
                    "fixed_code": fixed_code,
                    "original_code": code,
                    "root_cause": explanation,
                    "error": error,
                },
                confidence=confidence,
                reasoning="Bug analyzed and fix proposed",
                suggestions=[
                    "Test the fix thoroughly",
                    "Add regression test for this bug",
                    "Review similar code for same issue",
                ],
            )

        except Exception as e:
            self.log("debug_error", {"error": str(e)}, level="error")
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Debugging failed: {e}",
            )

    async def _explain_code(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Explain what code does."""

        code = input_data.get("code", "")
        question = input_data.get("question", "What does this code do?")

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided to explain",
            )

        system_prompt = """You are an expert code explainer. Provide clear, educational explanations.

Guidelines:
1. Start with a high-level overview
2. Explain key components and their purpose
3. Describe the flow of execution
4. Highlight important patterns or techniques
5. Note any potential issues or improvements
6. Adjust explanation depth based on the question"""

        prompt = f"""Explain this code:

```
{code}
```

Question: {question}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            return AgentResult(
                success=True,
                data={
                    "explanation": response,
                    "code": code,
                    "question": question,
                },
                confidence=ConfidenceLevel.HIGH,
                reasoning="Code explained",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Explanation failed: {e}",
            )
