# =============================================================================
# ODIN v7.0 - Intake Agent
# =============================================================================
# Entry point for user requests
# Analyzes, classifies, and routes tasks to appropriate agents
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


class TaskClassification:
    """Task classification result."""

    # Task types
    CODE_WRITE = "code_write"           # Write new code
    CODE_MODIFY = "code_modify"         # Modify existing code
    CODE_DEBUG = "code_debug"           # Fix bugs
    CODE_REVIEW = "code_review"         # Review code
    CODE_EXPLAIN = "code_explain"       # Explain code
    REFACTOR = "refactor"               # Refactoring
    TEST = "test"                       # Testing
    DOCUMENTATION = "documentation"     # Documentation
    ARCHITECTURE = "architecture"       # Architecture decisions
    DEPLOYMENT = "deployment"           # Deployment tasks
    QUESTION = "question"               # General questions
    ANALYSIS = "analysis"               # Code analysis
    SECURITY = "security"               # Security review
    PERFORMANCE = "performance"         # Performance optimization
    UNKNOWN = "unknown"                 # Cannot classify


@agent
class IntakeAgent(BaseAgent):
    """
    Intake Agent - Entry point for all user requests.

    Responsibilities:
    1. Parse and understand user intent
    2. Classify task type
    3. Extract relevant context
    4. Route to appropriate agent(s)
    5. Handle clarification if needed
    """

    @property
    def name(self) -> str:
        return "intake"

    @property
    def description(self) -> str:
        return "Analyzes user requests, classifies tasks, and routes to appropriate agents"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="classify_task",
                description="Classify user request into task type",
                input_schema={"request": "string"},
                output_schema={"task_type": "string", "confidence": "float"},
            ),
            AgentCapability(
                name="extract_context",
                description="Extract relevant context from request",
                input_schema={"request": "string"},
                output_schema={"files": "list", "requirements": "list"},
            ),
            AgentCapability(
                name="route_task",
                description="Determine which agent(s) should handle the task",
                input_schema={"task_type": "string", "context": "object"},
                output_schema={"agents": "list", "workflow": "string"},
            ),
        ]

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute intake task."""

        if task_type == "analyze_request":
            return await self._analyze_request(input_data, context)
        elif task_type == "classify":
            return await self._classify_request(input_data)
        elif task_type == "route":
            return await self._route_task(input_data)
        else:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Unknown task type: {task_type}",
            )

    async def _analyze_request(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """
        Full analysis of user request.

        Combines classification, context extraction, and routing.
        """
        request = input_data.get("request", "")

        if not request:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="Empty request provided",
            )

        # Use LLM to analyze the request
        system_prompt = """You are a task analysis agent. Analyze the user's request and provide:

1. task_type: One of [code_write, code_modify, code_debug, code_review, code_explain,
   refactor, test, documentation, architecture, deployment, question, analysis,
   security, performance, unknown]
2. files: List of files mentioned or likely needed
3. requirements: List of specific requirements extracted
4. clarifications_needed: List of questions if request is unclear
5. complexity: One of [trivial, simple, moderate, complex, critical]
6. risk_level: One of [none, low, medium, high, critical]
7. suggested_agents: List of agents to involve

Respond in JSON format only."""

        prompt = f"""Analyze this request:

{request}

Additional context:
{context or "None provided"}

Provide your analysis in JSON format."""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            # Parse JSON response
            import json
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                analysis = json.loads(json_match.group(1))
            else:
                analysis = json.loads(response)

            # Determine confidence based on analysis
            confidence = ConfidenceLevel.MODERATE
            if analysis.get("clarifications_needed"):
                confidence = ConfidenceLevel.UNCERTAIN
            elif analysis.get("task_type") != "unknown":
                confidence = ConfidenceLevel.HIGH

            return AgentResult(
                success=True,
                data={
                    "task_type": analysis.get("task_type", "unknown"),
                    "files": analysis.get("files", []),
                    "requirements": analysis.get("requirements", []),
                    "clarifications_needed": analysis.get("clarifications_needed", []),
                    "complexity": analysis.get("complexity", "moderate"),
                    "risk_level": analysis.get("risk_level", "low"),
                    "suggested_agents": analysis.get("suggested_agents", ["dev"]),
                    "original_request": request,
                },
                confidence=confidence,
                reasoning="Request analyzed successfully",
            )

        except Exception as e:
            self.log("analysis_error", {"error": str(e)}, level="error")

            # Fallback to rule-based classification
            return await self._classify_request({"request": request})

    async def _classify_request(
        self,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """
        Rule-based task classification fallback.

        Used when LLM is unavailable or fails.
        """
        request = input_data.get("request", "").lower()

        # Keyword-based classification
        classification = TaskClassification.UNKNOWN
        confidence = ConfidenceLevel.UNCERTAIN

        # Check patterns
        patterns = {
            TaskClassification.CODE_WRITE: [
                r'\b(create|write|implement|add|build|make)\b.*\b(function|class|file|module|component)\b',
                r'\bnew\s+(feature|endpoint|api)\b',
            ],
            TaskClassification.CODE_MODIFY: [
                r'\b(change|modify|update|edit|alter)\b',
                r'\b(refactor|improve)\b',
            ],
            TaskClassification.CODE_DEBUG: [
                r'\b(fix|bug|error|issue|problem|broken|crash)\b',
                r'\b(not working|doesn\'t work|fails)\b',
            ],
            TaskClassification.CODE_REVIEW: [
                r'\b(review|check|audit|inspect)\b.*\b(code|pr|pull request)\b',
            ],
            TaskClassification.CODE_EXPLAIN: [
                r'\b(explain|understand|what does|how does|why does)\b',
            ],
            TaskClassification.TEST: [
                r'\b(test|testing|unit test|integration test|e2e)\b',
            ],
            TaskClassification.DOCUMENTATION: [
                r'\b(document|documentation|readme|docstring|comment)\b',
            ],
            TaskClassification.SECURITY: [
                r'\b(security|vulnerability|exploit|injection|xss|csrf)\b',
            ],
            TaskClassification.PERFORMANCE: [
                r'\b(performance|optimize|slow|fast|speed|memory)\b',
            ],
            TaskClassification.QUESTION: [
                r'^(what|how|why|when|where|is|can|does|should)\b',
                r'\?$',
            ],
        }

        for task_type, regex_patterns in patterns.items():
            for pattern in regex_patterns:
                if re.search(pattern, request):
                    classification = task_type
                    confidence = ConfidenceLevel.MODERATE
                    break
            if classification != TaskClassification.UNKNOWN:
                break

        return AgentResult(
            success=True,
            data={
                "task_type": classification,
                "method": "rule_based",
            },
            confidence=confidence,
            reasoning=f"Classified as {classification} using pattern matching",
            warnings=["Used rule-based fallback, LLM classification recommended"],
        )

    async def _route_task(
        self,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """
        Determine routing for classified task.
        """
        task_type = input_data.get("task_type", TaskClassification.UNKNOWN)
        complexity = input_data.get("complexity", "moderate")
        risk_level = input_data.get("risk_level", "low")

        # Routing table
        routing = {
            TaskClassification.CODE_WRITE: ["retrieval", "dev", "approbation"],
            TaskClassification.CODE_MODIFY: ["retrieval", "dev", "approbation"],
            TaskClassification.CODE_DEBUG: ["retrieval", "dev", "oracle_code"],
            TaskClassification.CODE_REVIEW: ["retrieval", "review", "security"],
            TaskClassification.CODE_EXPLAIN: ["retrieval", "explain"],
            TaskClassification.REFACTOR: ["retrieval", "architect", "dev", "approbation"],
            TaskClassification.TEST: ["retrieval", "test", "oracle_code"],
            TaskClassification.DOCUMENTATION: ["retrieval", "docs"],
            TaskClassification.ARCHITECTURE: ["retrieval", "architect", "review"],
            TaskClassification.SECURITY: ["retrieval", "security", "oracle_code"],
            TaskClassification.PERFORMANCE: ["retrieval", "performance", "oracle_code"],
            TaskClassification.QUESTION: ["retrieval", "explain"],
            TaskClassification.ANALYSIS: ["retrieval", "analysis"],
        }

        agents = routing.get(task_type, ["dev"])

        # Add oracle for high-risk tasks
        if risk_level in ["high", "critical"] and "oracle_code" not in agents:
            agents.append("oracle_code")

        # Add human approval for critical tasks
        requires_approval = risk_level == "critical" or complexity == "critical"

        return AgentResult(
            success=True,
            data={
                "agents": agents,
                "workflow": "sequential" if len(agents) <= 3 else "parallel_then_sequential",
                "requires_approval": requires_approval,
                "estimated_complexity": complexity,
            },
            confidence=ConfidenceLevel.HIGH,
            reasoning=f"Routed to {len(agents)} agents based on task type and risk",
        )
