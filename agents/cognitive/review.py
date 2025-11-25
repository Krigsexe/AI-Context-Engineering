# =============================================================================
# ODIN v7.0 - Review Agent
# =============================================================================
# Code review, quality analysis, and improvement suggestions
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
class ReviewAgent(BaseAgent):
    """
    Review Agent - Code review and quality analysis.

    Responsibilities:
    1. Review code for quality issues
    2. Check coding standards compliance
    3. Identify potential bugs and issues
    4. Suggest improvements
    5. Assess maintainability
    """

    @property
    def name(self) -> str:
        return "review"

    @property
    def description(self) -> str:
        return "Reviews code for quality, standards compliance, and potential issues"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="review_code",
                description="Perform comprehensive code review",
                input_schema={
                    "code": "string",
                    "language": "string",
                    "context": "object",
                },
                output_schema={
                    "issues": "list",
                    "suggestions": "list",
                    "score": "float",
                },
            ),
            AgentCapability(
                name="check_standards",
                description="Check coding standards compliance",
                input_schema={
                    "code": "string",
                    "standards": "list",
                },
                output_schema={
                    "compliant": "bool",
                    "violations": "list",
                },
            ),
            AgentCapability(
                name="assess_maintainability",
                description="Assess code maintainability",
                input_schema={"code": "string"},
                output_schema={
                    "score": "float",
                    "factors": "object",
                },
            ),
        ]

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute review task."""

        handlers = {
            "review_code": self._review_code,
            "check_standards": self._check_standards,
            "assess_maintainability": self._assess_maintainability,
            "review_changes": self._review_changes,
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

    async def _review_code(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Perform comprehensive code review."""

        code = input_data.get("code", "")
        language = input_data.get("language", "python")
        focus_areas = input_data.get("focus_areas", [])

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided for review",
            )

        system_prompt = f"""You are an expert code reviewer for {language}. Analyze the code and provide:

1. **Issues**: Problems that should be fixed (bugs, security issues, performance problems)
   - severity: critical, high, medium, low
   - line: approximate line number
   - description: clear explanation
   - suggestion: how to fix

2. **Suggestions**: Improvements that would enhance the code
   - type: readability, performance, maintainability, best-practice
   - description: what to improve
   - example: code example if applicable

3. **Quality Score**: 0-100 based on:
   - Correctness (40%)
   - Readability (20%)
   - Maintainability (20%)
   - Best practices (20%)

Respond in JSON format with keys: issues, suggestions, score, summary"""

        focus_str = f"\n\nFocus especially on: {', '.join(focus_areas)}" if focus_areas else ""

        prompt = f"""Review this {language} code:{focus_str}

```{language}
{code}
```

Provide a thorough review in JSON format."""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            # Parse JSON response
            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                review = json.loads(json_match.group(1))
            else:
                review = json.loads(response)

            issues = review.get("issues", [])
            score = review.get("score", 70)

            # Determine confidence based on analysis depth
            confidence = ConfidenceLevel.HIGH
            if len(code.split('\n')) > 500:
                confidence = ConfidenceLevel.MODERATE  # Large files harder to review

            return AgentResult(
                success=True,
                data={
                    "issues": issues,
                    "suggestions": review.get("suggestions", []),
                    "score": score,
                    "summary": review.get("summary", ""),
                    "language": language,
                },
                confidence=confidence,
                reasoning=f"Found {len(issues)} issues, quality score: {score}/100",
                warnings=[i["description"] for i in issues if i.get("severity") == "critical"],
            )

        except Exception as e:
            self.log("review_error", {"error": str(e)}, level="error")
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Review failed: {e}",
            )

    async def _check_standards(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Check coding standards compliance."""

        code = input_data.get("code", "")
        standards = input_data.get("standards", ["pep8", "clean-code"])
        language = input_data.get("language", "python")

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided",
            )

        standards_str = ", ".join(standards)

        system_prompt = f"""You are a coding standards checker. Check the code against these standards: {standards_str}

For each violation found, provide:
- standard: which standard is violated
- rule: specific rule name
- line: approximate line number
- description: what's wrong
- fix: how to fix it

Respond in JSON format with keys: compliant (bool), violations (list), summary"""

        prompt = f"""Check this {language} code for standards compliance:

```{language}
{code}
```

Standards to check: {standards_str}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = json.loads(response)

            violations = result.get("violations", [])
            compliant = result.get("compliant", len(violations) == 0)

            return AgentResult(
                success=True,
                data={
                    "compliant": compliant,
                    "violations": violations,
                    "standards_checked": standards,
                    "summary": result.get("summary", ""),
                },
                confidence=ConfidenceLevel.HIGH,
                reasoning=f"{'Compliant' if compliant else f'Found {len(violations)} violations'}",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Standards check failed: {e}",
            )

    async def _assess_maintainability(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Assess code maintainability."""

        code = input_data.get("code", "")

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided",
            )

        # Calculate basic metrics
        lines = code.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])

        # Function/class count (basic)
        function_count = len(re.findall(r'\bdef\s+\w+', code))
        class_count = len(re.findall(r'\bclass\s+\w+', code))

        system_prompt = """You are a code maintainability assessor. Evaluate the code and provide:

1. **Maintainability Score**: 0-100
2. **Factors**:
   - complexity: cyclomatic complexity estimate (low/medium/high)
   - readability: how easy to read (low/medium/high)
   - modularity: how well organized (low/medium/high)
   - documentation: comment quality (low/medium/high)
   - testability: how easy to test (low/medium/high)
3. **Recommendations**: Top 3 improvements for maintainability

Respond in JSON format."""

        prompt = f"""Assess maintainability of this code:

```
{code}
```

Metrics:
- Total lines: {total_lines}
- Code lines: {code_lines}
- Comment lines: {comment_lines}
- Functions: {function_count}
- Classes: {class_count}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                assessment = json.loads(json_match.group(1))
            else:
                assessment = json.loads(response)

            return AgentResult(
                success=True,
                data={
                    "score": assessment.get("score", 70),
                    "factors": assessment.get("factors", {}),
                    "recommendations": assessment.get("recommendations", []),
                    "metrics": {
                        "total_lines": total_lines,
                        "code_lines": code_lines,
                        "comment_lines": comment_lines,
                        "function_count": function_count,
                        "class_count": class_count,
                        "comment_ratio": comment_lines / max(code_lines, 1),
                    },
                },
                confidence=ConfidenceLevel.MODERATE,
                reasoning=f"Maintainability score: {assessment.get('score', 70)}/100",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Assessment failed: {e}",
            )

    async def _review_changes(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Review code changes (diff)."""

        diff = input_data.get("diff", "")
        original = input_data.get("original", "")
        modified = input_data.get("modified", "")

        if not diff and not (original and modified):
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No diff or original/modified code provided",
            )

        system_prompt = """You are a code change reviewer. Analyze the changes and provide:

1. **Summary**: Brief description of what changed
2. **Risk Assessment**: low/medium/high with explanation
3. **Issues**: Any problems introduced by the changes
4. **Approval**: approve/request-changes/comment-only
5. **Comments**: Specific feedback on the changes

Respond in JSON format."""

        if diff:
            prompt = f"""Review these code changes:

```diff
{diff}
```"""
        else:
            prompt = f"""Review these code changes:

Original:
```
{original}
```

Modified:
```
{modified}
```"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                review = json.loads(json_match.group(1))
            else:
                review = json.loads(response)

            approval = review.get("approval", "comment-only")
            risk = review.get("risk_assessment", {}).get("level", "medium")

            return AgentResult(
                success=True,
                data={
                    "summary": review.get("summary", ""),
                    "risk_assessment": review.get("risk_assessment", {}),
                    "issues": review.get("issues", []),
                    "approval": approval,
                    "comments": review.get("comments", []),
                },
                confidence=ConfidenceLevel.HIGH if risk == "low" else ConfidenceLevel.MODERATE,
                reasoning=f"Review complete: {approval}, risk: {risk}",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Change review failed: {e}",
            )
