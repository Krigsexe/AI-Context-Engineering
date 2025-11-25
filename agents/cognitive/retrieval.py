# =============================================================================
# ODIN v7.0 - Retrieval Agent
# =============================================================================
# Context retrieval and knowledge gathering
# =============================================================================

from __future__ import annotations
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
    semantic_hash_file,
)


@agent
class RetrievalAgent(BaseAgent):
    """
    Retrieval Agent - Context and knowledge gathering.

    Responsibilities:
    1. Find relevant files for a task
    2. Extract code context
    3. Search codebase for patterns
    4. Gather documentation
    5. Build knowledge context for other agents
    """

    @property
    def name(self) -> str:
        return "retrieval"

    @property
    def description(self) -> str:
        return "Retrieves relevant context and knowledge for tasks"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="find_files",
                description="Find files relevant to a task",
                input_schema={"query": "string", "extensions": "list"},
                output_schema={"files": "list", "relevance_scores": "list"},
            ),
            AgentCapability(
                name="search_code",
                description="Search codebase for patterns",
                input_schema={"pattern": "string", "file_type": "string"},
                output_schema={"matches": "list"},
            ),
            AgentCapability(
                name="get_context",
                description="Get code context around a location",
                input_schema={"file_path": "string", "line": "int"},
                output_schema={"context": "string", "related": "list"},
            ),
            AgentCapability(
                name="build_task_context",
                description="Build full context for a task",
                input_schema={"task_description": "string"},
                output_schema={"context": "object"},
            ),
        ]

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute retrieval task."""

        handlers = {
            "find_files": self._find_files,
            "search_code": self._search_code,
            "get_context": self._get_context,
            "build_task_context": self._build_task_context,
            "read_file": self._read_file,
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

    async def _find_files(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Find files relevant to a query."""

        query = input_data.get("query", "")
        extensions = input_data.get("extensions", [])
        root_path = input_data.get("root_path", os.getcwd())
        max_results = input_data.get("max_results", 20)

        # Convert extensions to set for faster lookup
        ext_set = set(extensions) if extensions else None

        # Walk directory tree
        matches = []
        root = Path(root_path)

        ignore_dirs = {
            ".git", ".odin", "__pycache__", "node_modules",
            ".venv", "venv", "dist", "build", ".next",
        }

        try:
            for path in root.rglob("*"):
                # Skip ignored directories
                if any(ignored in path.parts for ignored in ignore_dirs):
                    continue

                if not path.is_file():
                    continue

                # Filter by extension if specified
                if ext_set and path.suffix not in ext_set:
                    continue

                # Simple relevance scoring based on path and name
                score = self._calculate_relevance(path, query)
                if score > 0:
                    matches.append({
                        "path": str(path.relative_to(root)),
                        "score": score,
                        "size": path.stat().st_size,
                    })

            # Sort by relevance and limit results
            matches.sort(key=lambda x: x["score"], reverse=True)
            matches = matches[:max_results]

            return AgentResult(
                success=True,
                data={
                    "files": matches,
                    "total_found": len(matches),
                    "query": query,
                },
                confidence=ConfidenceLevel.HIGH if matches else ConfidenceLevel.MODERATE,
                reasoning=f"Found {len(matches)} relevant files",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"File search failed: {e}",
            )

    def _calculate_relevance(self, path: Path, query: str) -> float:
        """Calculate relevance score for a file."""
        score = 0.0
        query_lower = query.lower()
        path_str = str(path).lower()
        name = path.name.lower()

        # Exact name match
        if query_lower in name:
            score += 1.0

        # Path contains query
        if query_lower in path_str:
            score += 0.5

        # Query words in path
        words = query_lower.split()
        for word in words:
            if len(word) > 2 and word in path_str:
                score += 0.3

        return score

    async def _search_code(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Search codebase for patterns."""

        pattern = input_data.get("pattern", "")
        file_type = input_data.get("file_type", "")
        root_path = input_data.get("root_path", os.getcwd())
        max_results = input_data.get("max_results", 50)

        if not pattern:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No search pattern provided",
            )

        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Invalid regex pattern: {e}",
            )

        matches = []
        root = Path(root_path)

        ignore_dirs = {
            ".git", ".odin", "__pycache__", "node_modules",
            ".venv", "venv", "dist", "build",
        }

        ext_map = {
            "python": {".py"},
            "javascript": {".js", ".jsx", ".ts", ".tsx"},
            "go": {".go"},
            "rust": {".rs"},
            "java": {".java"},
        }
        allowed_extensions = ext_map.get(file_type.lower()) if file_type else None

        try:
            for path in root.rglob("*"):
                if any(ignored in path.parts for ignored in ignore_dirs):
                    continue

                if not path.is_file():
                    continue

                if allowed_extensions and path.suffix not in allowed_extensions:
                    continue

                # Try to read and search file
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        if regex.search(line):
                            matches.append({
                                "file": str(path.relative_to(root)),
                                "line": i,
                                "content": line.strip()[:200],
                            })

                            if len(matches) >= max_results:
                                break
                except Exception:
                    continue

                if len(matches) >= max_results:
                    break

            return AgentResult(
                success=True,
                data={
                    "matches": matches,
                    "pattern": pattern,
                    "total_matches": len(matches),
                },
                confidence=ConfidenceLevel.HIGH,
                reasoning=f"Found {len(matches)} matches for pattern",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Code search failed: {e}",
            )

    async def _get_context(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Get code context around a location."""

        file_path = input_data.get("file_path", "")
        line_number = input_data.get("line", 1)
        context_lines = input_data.get("context_lines", 10)

        if not file_path:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No file path provided",
            )

        try:
            path = Path(file_path)
            if not path.exists():
                return AgentResult(
                    success=False,
                    data=None,
                    confidence=ConfidenceLevel.AXIOM,
                    reasoning=f"File not found: {file_path}",
                )

            content = path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Get context window
            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)

            context_content = "\n".join(
                f"{i+1}: {line}"
                for i, line in enumerate(lines[start:end], start)
            )

            return AgentResult(
                success=True,
                data={
                    "context": context_content,
                    "file_path": file_path,
                    "start_line": start + 1,
                    "end_line": end,
                    "target_line": line_number,
                },
                confidence=ConfidenceLevel.HIGH,
                reasoning="Context retrieved successfully",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Context retrieval failed: {e}",
            )

    async def _read_file(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Read a file's content."""

        file_path = input_data.get("file_path", "")

        if not file_path:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No file path provided",
            )

        try:
            path = Path(file_path)
            if not path.exists():
                return AgentResult(
                    success=False,
                    data=None,
                    confidence=ConfidenceLevel.AXIOM,
                    reasoning=f"File not found: {file_path}",
                )

            content = path.read_text(encoding="utf-8")
            file_hash = semantic_hash_file(path)

            return AgentResult(
                success=True,
                data={
                    "content": content,
                    "file_path": file_path,
                    "size": len(content),
                    "lines": len(content.split("\n")),
                    "hash": file_hash,
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning="File read successfully",
            )

        except UnicodeDecodeError:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="File is not text/readable",
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"File read failed: {e}",
            )

    async def _build_task_context(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Build comprehensive context for a task."""

        task_description = input_data.get("task_description", "")
        root_path = input_data.get("root_path", os.getcwd())

        if not task_description:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No task description provided",
            )

        # Use LLM to identify relevant files and context needs
        system_prompt = """You are a context analysis agent. Given a task description, identify:

1. file_patterns: Glob patterns for potentially relevant files
2. search_terms: Code patterns to search for
3. key_concepts: Important concepts/functions/classes to find
4. documentation_needs: What documentation might be relevant

Respond in JSON format only."""

        prompt = f"""Analyze this task and identify what context is needed:

Task: {task_description}

Project root: {root_path}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            # Parse analysis
            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                analysis = json.loads(json_match.group(1))
            else:
                analysis = json.loads(response)

            # Gather context based on analysis
            gathered_context = {
                "task": task_description,
                "files": [],
                "code_snippets": [],
                "analysis": analysis,
            }

            # Find relevant files
            file_result = await self._find_files(
                {"query": task_description, "root_path": root_path},
                None
            )
            if file_result.success:
                gathered_context["files"] = file_result.data["files"][:10]

            # Search for key terms
            for term in analysis.get("search_terms", [])[:3]:
                search_result = await self._search_code(
                    {"pattern": term, "root_path": root_path, "max_results": 5},
                    None
                )
                if search_result.success:
                    gathered_context["code_snippets"].extend(
                        search_result.data["matches"]
                    )

            return AgentResult(
                success=True,
                data=gathered_context,
                confidence=ConfidenceLevel.MODERATE,
                reasoning="Task context built from codebase analysis",
            )

        except Exception as e:
            self.log("context_build_error", {"error": str(e)}, level="error")

            # Fallback: just find files by task keywords
            return await self._find_files(
                {"query": task_description, "root_path": root_path},
                None
            )
