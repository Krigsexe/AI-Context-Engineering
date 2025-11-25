# =============================================================================
# ODIN v7.0 - Audit Agent
# =============================================================================
# Activity logging, audit trails, and compliance monitoring
# =============================================================================

from __future__ import annotations
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..shared import (
    BaseAgent,
    AgentCapability,
    AgentResult,
    ConfidenceLevel,
    agent,
)


@agent
class AuditAgent(BaseAgent):
    """
    Audit Agent - Activity logging and audit trails.

    Responsibilities:
    1. Log all significant actions
    2. Track who did what and when
    3. Generate audit reports
    4. Monitor for anomalies
    5. Support compliance requirements
    """

    @property
    def name(self) -> str:
        return "audit"

    @property
    def description(self) -> str:
        return "Maintains audit trails and generates compliance reports"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="log_action",
                description="Log an auditable action",
                input_schema={
                    "actor": "string",
                    "action": "string",
                    "resource": "string",
                    "details": "object",
                },
                output_schema={
                    "audit_id": "string",
                },
            ),
            AgentCapability(
                name="generate_report",
                description="Generate audit report",
                input_schema={
                    "start_date": "string",
                    "end_date": "string",
                    "filters": "object",
                },
                output_schema={
                    "report": "object",
                },
            ),
            AgentCapability(
                name="search_logs",
                description="Search audit logs",
                input_schema={
                    "query": "string",
                    "filters": "object",
                },
                output_schema={
                    "results": "list",
                },
            ),
            AgentCapability(
                name="check_anomalies",
                description="Check for anomalous activity",
                input_schema={
                    "time_window": "int",
                },
                output_schema={
                    "anomalies": "list",
                },
            ),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audit_log_dir = Path(kwargs.get("audit_log_dir", ".odin/audit"))
        self.audit_log_dir.mkdir(parents=True, exist_ok=True)

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute audit task."""

        handlers = {
            "log_action": self._log_action,
            "generate_report": self._generate_report,
            "search_logs": self._search_logs,
            "check_anomalies": self._check_anomalies,
            "get_activity_summary": self._get_activity_summary,
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

    async def _log_action(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Log an auditable action."""

        actor = input_data.get("actor", "system")
        action = input_data.get("action", "")
        resource = input_data.get("resource", "")
        details = input_data.get("details", {})
        severity = input_data.get("severity", "info")

        if not action:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="Action is required",
            )

        try:
            timestamp = datetime.utcnow()
            audit_id = f"{timestamp.strftime('%Y%m%d%H%M%S%f')}_{actor[:8]}"

            audit_entry = {
                "id": audit_id,
                "timestamp": timestamp.isoformat(),
                "actor": actor,
                "action": action,
                "resource": resource,
                "details": details,
                "severity": severity,
                "task_id": self._current_task_id,
            }

            # Write to daily log file
            log_date = timestamp.strftime("%Y-%m-%d")
            log_file = self.audit_log_dir / f"audit_{log_date}.jsonl"

            with open(log_file, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")

            # Also store in state store if available
            if self.store:
                self.store.log_agent_action(
                    agent_id=self.agent_id,
                    action=f"audit:{action}",
                    details={
                        "audit_id": audit_id,
                        "actor": actor,
                        "resource": resource,
                        **details,
                    },
                    task_id=self._current_task_id,
                    level=severity,
                )

            return AgentResult(
                success=True,
                data={
                    "audit_id": audit_id,
                    "timestamp": timestamp.isoformat(),
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning="Action logged successfully",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Failed to log action: {e}",
            )

    async def _generate_report(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Generate audit report."""

        start_date = input_data.get("start_date")
        end_date = input_data.get("end_date")
        filters = input_data.get("filters", {})
        report_type = input_data.get("report_type", "summary")

        try:
            # Parse dates
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
            else:
                start_dt = datetime.utcnow() - timedelta(days=7)

            if end_date:
                end_dt = datetime.fromisoformat(end_date)
            else:
                end_dt = datetime.utcnow()

            # Collect entries from log files
            entries = []
            current_date = start_dt.date()
            while current_date <= end_dt.date():
                log_file = self.audit_log_dir / f"audit_{current_date}.jsonl"
                if log_file.exists():
                    with open(log_file) as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                entry_dt = datetime.fromisoformat(entry["timestamp"])
                                if start_dt <= entry_dt <= end_dt:
                                    if self._matches_filters(entry, filters):
                                        entries.append(entry)
                            except (json.JSONDecodeError, KeyError):
                                continue
                current_date += timedelta(days=1)

            # Generate report based on type
            if report_type == "summary":
                report = self._generate_summary_report(entries)
            elif report_type == "detailed":
                report = self._generate_detailed_report(entries)
            elif report_type == "compliance":
                report = self._generate_compliance_report(entries)
            else:
                report = {"entries": entries}

            return AgentResult(
                success=True,
                data={
                    "report": report,
                    "period": {
                        "start": start_dt.isoformat(),
                        "end": end_dt.isoformat(),
                    },
                    "entry_count": len(entries),
                    "report_type": report_type,
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Generated {report_type} report with {len(entries)} entries",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Report generation failed: {e}",
            )

    async def _search_logs(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Search audit logs."""

        query = input_data.get("query", "")
        filters = input_data.get("filters", {})
        limit = input_data.get("limit", 100)
        days_back = input_data.get("days_back", 30)

        try:
            results = []
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days_back)
            current_date = end_date

            while current_date >= start_date and len(results) < limit:
                log_file = self.audit_log_dir / f"audit_{current_date}.jsonl"
                if log_file.exists():
                    with open(log_file) as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                if self._matches_filters(entry, filters):
                                    if not query or self._matches_query(entry, query):
                                        results.append(entry)
                                        if len(results) >= limit:
                                            break
                            except (json.JSONDecodeError, KeyError):
                                continue
                current_date -= timedelta(days=1)

            return AgentResult(
                success=True,
                data={
                    "results": results,
                    "count": len(results),
                    "query": query,
                    "filters": filters,
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Found {len(results)} matching entries",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Search failed: {e}",
            )

    async def _check_anomalies(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Check for anomalous activity."""

        time_window_hours = input_data.get("time_window", 24)
        thresholds = input_data.get("thresholds", {
            "high_frequency_actor": 100,
            "failed_actions_ratio": 0.3,
            "unusual_hours": [0, 1, 2, 3, 4, 5],
        })

        try:
            # Collect recent entries
            entries = []
            end_dt = datetime.utcnow()
            start_dt = end_dt - timedelta(hours=time_window_hours)

            current_date = start_dt.date()
            while current_date <= end_dt.date():
                log_file = self.audit_log_dir / f"audit_{current_date}.jsonl"
                if log_file.exists():
                    with open(log_file) as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                entry_dt = datetime.fromisoformat(entry["timestamp"])
                                if start_dt <= entry_dt <= end_dt:
                                    entries.append(entry)
                            except (json.JSONDecodeError, KeyError):
                                continue
                current_date += timedelta(days=1)

            anomalies = []

            # Check for high-frequency actors
            actor_counts = {}
            for entry in entries:
                actor = entry.get("actor", "unknown")
                actor_counts[actor] = actor_counts.get(actor, 0) + 1

            for actor, count in actor_counts.items():
                if count > thresholds.get("high_frequency_actor", 100):
                    anomalies.append({
                        "type": "high_frequency_actor",
                        "severity": "medium",
                        "actor": actor,
                        "count": count,
                        "threshold": thresholds["high_frequency_actor"],
                    })

            # Check for unusual hours activity
            unusual_hours = thresholds.get("unusual_hours", [])
            for entry in entries:
                entry_dt = datetime.fromisoformat(entry["timestamp"])
                if entry_dt.hour in unusual_hours:
                    anomalies.append({
                        "type": "unusual_hour_activity",
                        "severity": "low",
                        "timestamp": entry["timestamp"],
                        "actor": entry.get("actor"),
                        "action": entry.get("action"),
                    })

            # Check for high failure rate
            failed_count = len([e for e in entries if e.get("severity") == "error"])
            total_count = len(entries)
            if total_count > 0:
                failure_ratio = failed_count / total_count
                if failure_ratio > thresholds.get("failed_actions_ratio", 0.3):
                    anomalies.append({
                        "type": "high_failure_rate",
                        "severity": "high",
                        "failure_ratio": failure_ratio,
                        "failed_count": failed_count,
                        "total_count": total_count,
                    })

            return AgentResult(
                success=True,
                data={
                    "anomalies": anomalies,
                    "anomaly_count": len(anomalies),
                    "entries_analyzed": len(entries),
                    "time_window_hours": time_window_hours,
                },
                confidence=ConfidenceLevel.HIGH,
                reasoning=f"Found {len(anomalies)} potential anomalies",
                warnings=[a["type"] for a in anomalies if a.get("severity") == "high"],
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Anomaly check failed: {e}",
            )

    async def _get_activity_summary(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Get activity summary for a time period."""

        days = input_data.get("days", 7)

        try:
            entries = []
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            current_date = end_date

            while current_date >= start_date:
                log_file = self.audit_log_dir / f"audit_{current_date}.jsonl"
                if log_file.exists():
                    with open(log_file) as f:
                        for line in f:
                            try:
                                entries.append(json.loads(line.strip()))
                            except json.JSONDecodeError:
                                continue
                current_date -= timedelta(days=1)

            # Compute summary
            actions_by_type = {}
            actors = set()
            resources = set()

            for entry in entries:
                action = entry.get("action", "unknown")
                actions_by_type[action] = actions_by_type.get(action, 0) + 1
                actors.add(entry.get("actor", "unknown"))
                if entry.get("resource"):
                    resources.add(entry["resource"])

            return AgentResult(
                success=True,
                data={
                    "total_entries": len(entries),
                    "unique_actors": len(actors),
                    "unique_resources": len(resources),
                    "actions_by_type": actions_by_type,
                    "top_actions": sorted(
                        actions_by_type.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10],
                    "period_days": days,
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Activity summary for {days} days",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Summary generation failed: {e}",
            )

    def _matches_filters(self, entry: Dict, filters: Dict) -> bool:
        """Check if entry matches filters."""
        for key, value in filters.items():
            if key in entry:
                if isinstance(value, list):
                    if entry[key] not in value:
                        return False
                elif entry[key] != value:
                    return False
        return True

    def _matches_query(self, entry: Dict, query: str) -> bool:
        """Check if entry matches search query."""
        query_lower = query.lower()
        searchable = json.dumps(entry).lower()
        return query_lower in searchable

    def _generate_summary_report(self, entries: List[Dict]) -> Dict:
        """Generate summary report."""
        actions_by_type = {}
        actors = set()
        severity_counts = {"info": 0, "warning": 0, "error": 0}

        for entry in entries:
            action = entry.get("action", "unknown")
            actions_by_type[action] = actions_by_type.get(action, 0) + 1
            actors.add(entry.get("actor", "unknown"))
            severity = entry.get("severity", "info")
            if severity in severity_counts:
                severity_counts[severity] += 1

        return {
            "total_entries": len(entries),
            "unique_actors": len(actors),
            "actions_by_type": actions_by_type,
            "severity_distribution": severity_counts,
        }

    def _generate_detailed_report(self, entries: List[Dict]) -> Dict:
        """Generate detailed report."""
        return {
            "summary": self._generate_summary_report(entries),
            "entries": entries[-1000:],  # Last 1000 entries
        }

    def _generate_compliance_report(self, entries: List[Dict]) -> Dict:
        """Generate compliance-focused report."""
        sensitive_actions = ["delete", "modify", "create", "deploy", "rollback"]
        sensitive_entries = [
            e for e in entries
            if any(sa in e.get("action", "").lower() for sa in sensitive_actions)
        ]

        return {
            "summary": self._generate_summary_report(entries),
            "sensitive_actions": sensitive_entries,
            "sensitive_action_count": len(sensitive_entries),
            "compliance_notes": [
                f"Total audited actions: {len(entries)}",
                f"Sensitive actions requiring review: {len(sensitive_entries)}",
            ],
        }
