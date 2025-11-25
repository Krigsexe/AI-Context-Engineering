# =============================================================================
# ODIN v7.0 - Security Agent
# =============================================================================
# Security scanning, vulnerability detection, and secure code review
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
class SecurityAgent(BaseAgent):
    """
    Security Agent - Security analysis and vulnerability detection.

    Responsibilities:
    1. Scan code for vulnerabilities (OWASP Top 10)
    2. Review code for security issues
    3. Check for secrets/credentials exposure
    4. Analyze dependencies for vulnerabilities
    5. Suggest security improvements
    """

    @property
    def name(self) -> str:
        return "security"

    @property
    def description(self) -> str:
        return "Scans code for security vulnerabilities and provides secure coding guidance"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="scan_vulnerabilities",
                description="Scan code for security vulnerabilities",
                input_schema={
                    "code": "string",
                    "language": "string",
                },
                output_schema={
                    "vulnerabilities": "list",
                    "risk_level": "string",
                },
            ),
            AgentCapability(
                name="check_secrets",
                description="Check for exposed secrets/credentials",
                input_schema={"code": "string"},
                output_schema={
                    "secrets_found": "list",
                    "safe": "bool",
                },
            ),
            AgentCapability(
                name="security_review",
                description="Comprehensive security code review",
                input_schema={
                    "code": "string",
                    "context": "object",
                },
                output_schema={
                    "issues": "list",
                    "recommendations": "list",
                },
            ),
        ]

    # Common patterns for secret detection
    SECRET_PATTERNS = [
        (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', "API Key"),
        (r'(?i)(secret[_-]?key|secretkey)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', "Secret Key"),
        (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{8,})["\']', "Password"),
        (r'(?i)(token)\s*[=:]\s*["\']?([a-zA-Z0-9_\-\.]{20,})["\']?', "Token"),
        (r'(?i)bearer\s+([a-zA-Z0-9_\-\.]{20,})', "Bearer Token"),
        (r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[=:]\s*["\']?([A-Z0-9]{20})["\']?', "AWS Access Key"),
        (r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[=:]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?', "AWS Secret Key"),
        (r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----', "Private Key"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
        (r'sk-[a-zA-Z0-9]{48}', "OpenAI API Key"),
    ]

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute security task."""

        handlers = {
            "scan_vulnerabilities": self._scan_vulnerabilities,
            "check_secrets": self._check_secrets,
            "security_review": self._security_review,
            "check_dependencies": self._check_dependencies,
            "suggest_fixes": self._suggest_fixes,
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

    async def _scan_vulnerabilities(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Scan code for security vulnerabilities."""

        code = input_data.get("code", "")
        language = input_data.get("language", "python")

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided",
            )

        system_prompt = f"""You are a security expert specializing in {language}. Analyze code for OWASP Top 10 and common vulnerabilities:

1. Injection (SQL, Command, XSS, etc.)
2. Broken Authentication
3. Sensitive Data Exposure
4. XML External Entities (XXE)
5. Broken Access Control
6. Security Misconfiguration
7. Cross-Site Scripting (XSS)
8. Insecure Deserialization
9. Using Components with Known Vulnerabilities
10. Insufficient Logging & Monitoring

For each vulnerability found, provide:
- type: OWASP category or specific type
- severity: critical, high, medium, low
- line: approximate line number
- description: what's wrong
- exploit_scenario: how it could be exploited
- fix: how to remediate

Respond in JSON format with keys: vulnerabilities, risk_level (critical/high/medium/low), summary"""

        prompt = f"""Scan this {language} code for security vulnerabilities:

```{language}
{code}
```"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                scan_result = json.loads(json_match.group(1))
            else:
                scan_result = json.loads(response)

            vulnerabilities = scan_result.get("vulnerabilities", [])
            risk_level = scan_result.get("risk_level", "low")

            # Determine confidence based on scan quality
            confidence = ConfidenceLevel.HIGH
            if len(code.split('\n')) > 500:
                confidence = ConfidenceLevel.MODERATE

            return AgentResult(
                success=True,
                data={
                    "vulnerabilities": vulnerabilities,
                    "risk_level": risk_level,
                    "summary": scan_result.get("summary", ""),
                    "vulnerability_count": len(vulnerabilities),
                },
                confidence=confidence,
                reasoning=f"Found {len(vulnerabilities)} potential vulnerabilities, risk: {risk_level}",
                warnings=[v["description"] for v in vulnerabilities if v.get("severity") == "critical"],
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Vulnerability scan failed: {e}",
            )

    async def _check_secrets(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Check for exposed secrets/credentials."""

        code = input_data.get("code", "")
        file_path = input_data.get("file_path", "")

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided",
            )

        secrets_found = []

        for pattern, secret_type in self.SECRET_PATTERNS:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                secrets_found.append({
                    "type": secret_type,
                    "line": line_num,
                    "matched": match.group(0)[:30] + "..." if len(match.group(0)) > 30 else match.group(0),
                    "file": file_path,
                })

        safe = len(secrets_found) == 0

        return AgentResult(
            success=True,
            data={
                "secrets_found": secrets_found,
                "safe": safe,
                "count": len(secrets_found),
            },
            confidence=ConfidenceLevel.HIGH,  # Pattern matching is reliable
            reasoning=f"{'No secrets found' if safe else f'Found {len(secrets_found)} potential secrets'}",
            warnings=["CRITICAL: Secrets detected in code!"] if not safe else [],
        )

    async def _security_review(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Comprehensive security code review."""

        code = input_data.get("code", "")
        language = input_data.get("language", "python")
        # Reserved for future use with custom security requirement checks
        _security_requirements = input_data.get("security_requirements", [])

        if not code:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No code provided",
            )

        # First check for secrets
        secrets_result = await self._check_secrets({"code": code}, context)

        # Then scan for vulnerabilities
        vuln_result = await self._scan_vulnerabilities(
            {"code": code, "language": language},
            context
        )

        # Combine results
        all_issues = []

        if secrets_result.success and secrets_result.data:
            for secret in secrets_result.data.get("secrets_found", []):
                all_issues.append({
                    "category": "secrets",
                    "severity": "critical",
                    "type": secret["type"],
                    "line": secret["line"],
                    "description": f"Exposed {secret['type']} in code",
                })

        if vuln_result.success and vuln_result.data:
            for vuln in vuln_result.data.get("vulnerabilities", []):
                all_issues.append({
                    "category": "vulnerability",
                    "severity": vuln.get("severity", "medium"),
                    "type": vuln.get("type", "unknown"),
                    "line": vuln.get("line", 0),
                    "description": vuln.get("description", ""),
                    "fix": vuln.get("fix", ""),
                })

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_issues.sort(key=lambda x: severity_order.get(x["severity"], 4))

        # Determine overall risk
        if any(i["severity"] == "critical" for i in all_issues):
            risk_level = "critical"
        elif any(i["severity"] == "high" for i in all_issues):
            risk_level = "high"
        elif any(i["severity"] == "medium" for i in all_issues):
            risk_level = "medium"
        else:
            risk_level = "low"

        return AgentResult(
            success=True,
            data={
                "issues": all_issues,
                "risk_level": risk_level,
                "secrets_detected": not secrets_result.data.get("safe", True) if secrets_result.data else False,
                "vulnerability_count": len(vuln_result.data.get("vulnerabilities", [])) if vuln_result.data else 0,
                "recommendations": [
                    "Fix all critical and high severity issues before deployment",
                    "Remove any exposed secrets and rotate credentials",
                    "Add input validation for user-supplied data",
                    "Implement proper error handling without exposing internals",
                ],
            },
            confidence=ConfidenceLevel.HIGH,
            reasoning=f"Security review complete: {len(all_issues)} issues found, risk level: {risk_level}",
            warnings=[i["description"] for i in all_issues if i["severity"] == "critical"],
        )

    async def _check_dependencies(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Check dependencies for known vulnerabilities."""

        dependencies = input_data.get("dependencies", [])
        lockfile_content = input_data.get("lockfile", "")
        package_type = input_data.get("package_type", "pip")

        if not dependencies and not lockfile_content:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No dependencies provided",
            )

        system_prompt = """You are a dependency security expert. Analyze dependencies for:

1. Known CVEs (Common Vulnerabilities and Exposures)
2. Outdated versions with security patches
3. Deprecated packages
4. Packages with known security issues

For each issue found, provide:
- package: package name
- current_version: installed version
- issue: what's wrong
- severity: critical, high, medium, low
- recommendation: what to do (upgrade to version X, replace with Y, etc.)

Respond in JSON format with keys: vulnerable_deps, safe_deps, recommendations"""

        deps_str = "\n".join(dependencies) if dependencies else lockfile_content

        prompt = f"""Check these {package_type} dependencies for security issues:

{deps_str}"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            import json
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = json.loads(response)

            vulnerable = result.get("vulnerable_deps", [])

            return AgentResult(
                success=True,
                data={
                    "vulnerable_deps": vulnerable,
                    "safe_deps": result.get("safe_deps", []),
                    "recommendations": result.get("recommendations", []),
                    "vulnerable_count": len(vulnerable),
                },
                confidence=ConfidenceLevel.MODERATE,  # Depends on LLM knowledge freshness
                reasoning=f"Found {len(vulnerable)} potentially vulnerable dependencies",
                warnings=[f"{d['package']}: {d['issue']}" for d in vulnerable if d.get("severity") == "critical"],
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Dependency check failed: {e}",
            )

    async def _suggest_fixes(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Suggest fixes for security issues."""

        code = input_data.get("code", "")
        vulnerabilities = input_data.get("vulnerabilities", [])
        language = input_data.get("language", "python")

        if not code or not vulnerabilities:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="Code and vulnerabilities list required",
            )

        system_prompt = f"""You are a security remediation expert for {language}. For each vulnerability:

1. Provide the exact fix with code
2. Explain why the fix works
3. Note any trade-offs or considerations

Format your response with clear sections for each fix."""

        vuln_str = "\n".join([
            f"- {v.get('type', 'Unknown')}: {v.get('description', '')}"
            for v in vulnerabilities
        ])

        prompt = f"""Fix these security vulnerabilities in the code:

Vulnerabilities:
{vuln_str}

Code:
```{language}
{code}
```"""

        try:
            response = await self.ask_llm(prompt, system_prompt=system_prompt)

            # Extract fixed code blocks
            code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)```', response)
            fixed_code = code_blocks[0] if code_blocks else ""

            return AgentResult(
                success=bool(fixed_code),
                data={
                    "fixed_code": fixed_code,
                    "explanation": response,
                    "original_vulnerabilities": vulnerabilities,
                },
                confidence=ConfidenceLevel.MODERATE,
                reasoning="Security fixes suggested",
                suggestions=["Review fixes carefully before applying", "Run security scan on fixed code"],
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Fix suggestion failed: {e}",
            )
