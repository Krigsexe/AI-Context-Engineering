# =============================================================================
# ODIN v7.0 - Architect Agent
# =============================================================================
# Architecture decisions, design patterns, and system design
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
class ArchitectAgent(BaseAgent):
    """
    Architect Agent - Architecture and design decisions.

    Responsibilities:
    1. Analyze system architecture
    2. Recommend design patterns
    3. Plan refactoring strategies
    4. Evaluate technical decisions
    5. Design APIs and interfaces
    """

    @property
    def name(self) -> str:
        return "architect"

    @property
    def description(self) -> str:
        return "Provides architecture analysis, design patterns, and technical guidance"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="analyze_architecture",
                description="Analyze existing system architecture",
                input_schema={
                    "codebase_summary": "string",
                    "file_structure": "list",
                },
                output_schema={
                    "architecture_type": "string",
                    "components": "list",
                    "recommendations": "list",
                },
            ),
            AgentCapability(
                name="recommend_pattern",
                description="Recommend design patterns for a problem",
                input_schema={
                    "problem": "string",
                    "constraints": "list",
                },
                output_schema={
                    "patterns": "list",
                    "recommendation": "string",
                },
            ),
            AgentCapability(
                name="design_api",
                description="Design API interface",
                input_schema={
                    "requirements": "string",
                    "style": "string",
                },
                output_schema={
                    "endpoints": "list",
                    "schemas": "object",
                },
            ),
            AgentCapability(
                name="plan_refactoring",
                description="Plan refactoring strategy",
                input_schema={
                    "current_state": "string",
                    "target_state": "string",
                },
                output_schema={
                    "steps": "list",
                    "risks": "list",
                },
            ),
        ]

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute architecture task."""

        handlers = {
            "analyze_architecture": self._analyze_architecture,
            "recommend_pattern": self._recommend_pattern,
            "design_api": self._design_api,
            "plan_refactoring": self._plan_refactoring,
            "evaluate_decision": self._evaluate_decision,
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

    async def _analyze_architecture(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Analyze existing system architecture."""

        codebase_summary = input_data.get("codebase_summary", "")
        file_structure = input_data.get("file_structure", [])
        technologies = input_data.get("technologies", [])

        if not codebase_summary and not file_structure:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No codebase information provided",
            )

        system_prompt = """You are a software architect. Analyze the system and provide:

1. **Architecture Type**: monolith, microservices, modular-monolith, serverless, etc.
2. **Components**: Major components/modules identified
3. **Patterns Used**: Design patterns detected
4. **Strengths**: What's done well
5. **Weaknesses**: Areas for improvement
6. **Recommendations**: Specific actionable improvements

Respond in JSON format."""

        structure_str = "\n".join(file_structure) if file_structure else "Not provided"
        tech_str = ", ".join(technologies) if technologies else "Not specified"

        prompt = f"""Analyze this system architecture:

Summary:
{codebase_summary}

File Structure:
{structure_str}

Technologies: {tech_str}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                analysis = json.loads(json_match.group(1))
            else:
                analysis = json.loads(response)

            return AgentResult(
                success=True,
                data={
                    "architecture_type": analysis.get("architecture_type", "unknown"),
                    "components": analysis.get("components", []),
                    "patterns_used": analysis.get("patterns_used", []),
                    "strengths": analysis.get("strengths", []),
                    "weaknesses": analysis.get("weaknesses", []),
                    "recommendations": analysis.get("recommendations", []),
                },
                confidence=ConfidenceLevel.MODERATE,
                reasoning=f"Identified {analysis.get('architecture_type', 'unknown')} architecture",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Architecture analysis failed: {e}",
            )

    async def _recommend_pattern(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Recommend design patterns for a problem."""

        problem = input_data.get("problem", "")
        constraints = input_data.get("constraints", [])
        language = input_data.get("language", "python")

        if not problem:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No problem description provided",
            )

        system_prompt = f"""You are a design patterns expert for {language}. Given a problem:

1. Identify applicable design patterns (GoF, architectural, etc.)
2. For each pattern provide:
   - name: Pattern name
   - category: creational/structural/behavioral/architectural
   - fit_score: 1-10 how well it fits
   - pros: advantages for this problem
   - cons: disadvantages/tradeoffs
   - example: brief code skeleton

3. Recommend the best pattern with justification

Respond in JSON format with keys: patterns, recommendation, rationale"""

        constraints_str = "\n- ".join(constraints) if constraints else "None specified"

        prompt = f"""Problem: {problem}

Constraints:
- {constraints_str}

Language: {language}

What design patterns would best solve this?"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = json.loads(response)

            return AgentResult(
                success=True,
                data={
                    "patterns": result.get("patterns", []),
                    "recommendation": result.get("recommendation", ""),
                    "rationale": result.get("rationale", ""),
                },
                confidence=ConfidenceLevel.HIGH,
                reasoning=f"Recommended: {result.get('recommendation', 'No specific recommendation')}",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Pattern recommendation failed: {e}",
            )

    async def _design_api(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Design API interface."""

        requirements = input_data.get("requirements", "")
        style = input_data.get("style", "REST")
        existing_api = input_data.get("existing_api", "")

        if not requirements:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No API requirements provided",
            )

        system_prompt = f"""You are an API designer. Design a {style} API based on requirements.

Provide:
1. **Endpoints**: List of endpoints with:
   - method: HTTP method
   - path: URL path
   - description: What it does
   - request_body: Schema if applicable
   - response: Response schema
   - status_codes: Possible status codes

2. **Schemas**: Data models/types used

3. **Authentication**: Recommended auth approach

4. **Best Practices**: API design best practices applied

Respond in JSON format."""

        prompt = f"""Design a {style} API for:

Requirements:
{requirements}

{"Existing API to extend:" + existing_api if existing_api else ""}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                design = json.loads(json_match.group(1))
            else:
                design = json.loads(response)

            return AgentResult(
                success=True,
                data={
                    "endpoints": design.get("endpoints", []),
                    "schemas": design.get("schemas", {}),
                    "authentication": design.get("authentication", {}),
                    "best_practices": design.get("best_practices", []),
                    "style": style,
                },
                confidence=ConfidenceLevel.HIGH,
                reasoning=f"Designed {len(design.get('endpoints', []))} endpoints",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"API design failed: {e}",
            )

    async def _plan_refactoring(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Plan refactoring strategy."""

        current_state = input_data.get("current_state", "")
        target_state = input_data.get("target_state", "")
        constraints = input_data.get("constraints", [])

        if not current_state or not target_state:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="Both current and target state required",
            )

        system_prompt = """You are a refactoring expert. Plan a safe refactoring strategy.

Provide:
1. **Steps**: Ordered list of refactoring steps, each with:
   - order: step number
   - action: what to do
   - files_affected: which files change
   - tests_required: what tests to run after
   - rollback_plan: how to undo if needed

2. **Risks**: Potential risks with mitigation strategies

3. **Prerequisites**: What needs to be in place before starting

4. **Estimated Impact**: high/medium/low for each area:
   - code_changes
   - test_changes
   - documentation
   - deployment

Respond in JSON format."""

        constraints_str = "\n- ".join(constraints) if constraints else "None"

        prompt = f"""Plan refactoring from current to target state:

Current State:
{current_state}

Target State:
{target_state}

Constraints:
- {constraints_str}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                plan = json.loads(json_match.group(1))
            else:
                plan = json.loads(response)

            return AgentResult(
                success=True,
                data={
                    "steps": plan.get("steps", []),
                    "risks": plan.get("risks", []),
                    "prerequisites": plan.get("prerequisites", []),
                    "estimated_impact": plan.get("estimated_impact", {}),
                },
                confidence=ConfidenceLevel.MODERATE,
                reasoning=f"Planned {len(plan.get('steps', []))} refactoring steps",
                warnings=[r["description"] for r in plan.get("risks", []) if r.get("severity") == "high"],
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Refactoring planning failed: {e}",
            )

    async def _evaluate_decision(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Evaluate a technical decision."""

        decision = input_data.get("decision", "")
        alternatives = input_data.get("alternatives", [])
        criteria = input_data.get("criteria", [])

        if not decision:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No decision to evaluate",
            )

        system_prompt = """You are a technical decision evaluator. Analyze the decision objectively.

Provide:
1. **Evaluation**: Assessment of the proposed decision
   - pros: advantages
   - cons: disadvantages
   - score: 1-10

2. **Alternatives Analysis**: For each alternative
   - pros: advantages
   - cons: disadvantages
   - score: 1-10

3. **Recommendation**: Best choice with justification

4. **Considerations**: Important factors to keep in mind

Respond in JSON format."""

        alts_str = "\n- ".join(alternatives) if alternatives else "None provided"
        criteria_str = "\n- ".join(criteria) if criteria else "General best practices"

        prompt = f"""Evaluate this technical decision:

Decision: {decision}

Alternatives:
- {alts_str}

Evaluation Criteria:
- {criteria_str}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                evaluation = json.loads(json_match.group(1))
            else:
                evaluation = json.loads(response)

            return AgentResult(
                success=True,
                data={
                    "evaluation": evaluation.get("evaluation", {}),
                    "alternatives_analysis": evaluation.get("alternatives_analysis", []),
                    "recommendation": evaluation.get("recommendation", ""),
                    "considerations": evaluation.get("considerations", []),
                },
                confidence=ConfidenceLevel.MODERATE,
                reasoning=evaluation.get("recommendation", "Evaluation complete"),
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Decision evaluation failed: {e}",
            )
