from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from sqlalchemy.orm.attributes import flag_modified

from app.models import WorkflowTask


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentStepTrace:
    agent: str
    tool: str
    input_summary: str
    output_summary: str
    status: str = "completed"
    started_at: str = field(default_factory=utc_iso)
    ended_at: str | None = None
    duration_ms: int = 0


class AgentTraceRecorder:
    def record(
        self,
        task: WorkflowTask,
        *,
        agent: str,
        tool: str,
        input_summary: str,
        output_summary: str,
        started_at: str,
        duration_ms: int,
        status: str = "completed",
    ) -> None:
        summary = {**(task.summary or {})}
        trace = summary.get("agent_trace") or {"mode": "agentic_workflow", "steps": []}
        step = AgentStepTrace(
            agent=agent,
            tool=tool,
            input_summary=input_summary,
            output_summary=output_summary,
            status=status,
            started_at=started_at,
            ended_at=utc_iso(),
            duration_ms=duration_ms,
        )
        trace["steps"] = [*trace.get("steps", []), asdict(step)]
        summary["agent_trace"] = trace
        task.summary = summary
        flag_modified(task, "summary")

    def time_step(
        self,
        task: WorkflowTask,
        *,
        agent: str,
        tool: str,
        input_summary: str,
        output_summary: str,
        status: str = "completed",
        started_at: str | None = None,
        start_tick: float | None = None,
    ) -> None:
        started = started_at or utc_iso()
        tick = start_tick if start_tick is not None else perf_counter()
        self.record(
            task,
            agent=agent,
            tool=tool,
            input_summary=input_summary,
            output_summary=output_summary,
            status=status,
            started_at=started,
            duration_ms=int((perf_counter() - tick) * 1000),
        )


class RiskReviewAgent:
    CONTRACT_RISK_RULES = [
        ("late_delivery_penalty", "warning", "合同包含逾期交付或违约金条款，需要确认比例是否合理", ["逾期", "违约金"]),
        ("confidentiality", "info", "合同包含保密义务，审批时应确认保密范围和期限", ["保密"]),
        ("manual_review_required", "warning", "合同明确 AI 结果需人工审批，正式使用前需要人工复核", ["人工审批", "人工复核"]),
        ("litigation", "info", "合同包含诉讼管辖条款，需要确认管辖地是否符合公司政策", ["法院", "诉讼"]),
        ("payment_schedule", "info", "合同包含分期付款节点，需要和财务计划核对", ["付款", "支付"]),
    ]

    def review(self, *, document_type: str, text: str, anomalies: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        if document_type == "contract":
            for code, severity, message, keywords in self.CONTRACT_RISK_RULES:
                if all(keyword in text for keyword in keywords):
                    findings.append({"code": code, "severity": severity, "message": message, "agent": "risk_review_agent"})

        merged = [*anomalies]
        existing_codes = {item.get("code") for item in merged}
        for finding in findings:
            if finding["code"] not in existing_codes:
                merged.append(finding)
        risk_summary = {
            "risk_count": len(findings),
            "risk_codes": [finding["code"] for finding in findings],
            "risk_level": "medium" if any(finding["severity"] == "warning" for finding in findings) else "low",
        }
        return merged, risk_summary
