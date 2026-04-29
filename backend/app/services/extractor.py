import json
import re
from dataclasses import dataclass, field
from typing import Any

from app.core.config import get_settings
from app.services.parser import ParsedDocument


@dataclass
class ExtractionResult:
    fields: dict[str, Any]
    summary: dict[str, Any]
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    quality_score: float = 0.0


REQUIRED_FIELDS = {
    "invoice": ["document_no", "issuer", "amount", "date"],
    "contract": ["document_no", "party_a", "party_b", "effective_date"],
    "report": ["title", "date", "owner"],
    "spreadsheet": ["title", "amount", "date"],
    "general": ["title", "date"],
}


class ExtractorService:
    def extract(self, parsed: ParsedDocument, document_type: str, template_id: str) -> ExtractionResult:
        settings = get_settings()
        if settings.llm.api_key:
            try:
                return self._extract_with_openai(parsed, document_type, template_id)
            except Exception as exc:
                fallback = self._extract_with_rules(parsed, document_type)
                fallback.anomalies.append(
                    {"code": "llm_fallback", "severity": "warning", "message": f"LLM extraction failed: {exc}"}
                )
                return fallback
        return self._extract_with_rules(parsed, document_type)

    def _extract_with_openai(self, parsed: ParsedDocument, document_type: str, template_id: str) -> ExtractionResult:
        from openai import OpenAI

        settings = get_settings()
        llm = settings.llm
        client_kwargs: dict[str, Any] = {"api_key": llm.api_key, "timeout": settings.openai_timeout_seconds}
        if llm.base_url:
            client_kwargs["base_url"] = llm.base_url
        client = OpenAI(**client_kwargs)
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "fields": {"type": "object"},
                "summary": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "brief": {"type": "string"},
                        "key_points": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["title", "brief", "key_points"],
                    "additionalProperties": True,
                },
                "anomalies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": True,
                        "properties": {
                            "code": {"type": "string"},
                            "severity": {"type": "string"},
                            "message": {"type": "string"},
                        },
                        "required": ["code", "severity", "message"],
                    },
                },
                "quality_score": {"type": "number"},
            },
            "required": ["fields", "summary", "anomalies", "quality_score"],
        }
        prompt = (
            "Extract enterprise workflow fields from the document. "
            f"Document type: {document_type}. Template: {template_id}. "
            "Return only valid JSON that follows the requested structure. Mark missing or risky fields as anomalies.\n\n"
            f"Document text:\n{parsed.text[:16000]}"
        )
        messages = [
            {"role": "system", "content": "You are a precise enterprise document extraction engine that returns JSON."},
            {"role": "user", "content": prompt},
        ]
        try:
            response = client.chat.completions.create(
                model=llm.model,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": "document_extraction", "strict": True, "schema": schema},
                },
            )
        except Exception:
            response = client.chat.completions.create(
                model=llm.model,
                messages=messages,
                response_format={"type": "json_object"},
            )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
        return ExtractionResult(
            fields=payload.get("fields", {}),
            summary=payload.get("summary", {}),
            anomalies=payload.get("anomalies", []),
            quality_score=float(payload.get("quality_score", 0.0)),
        )

    def _extract_with_rules(self, parsed: ParsedDocument, document_type: str) -> ExtractionResult:
        text = parsed.text
        compact = re.sub(r"\s+", " ", text)
        fields = {
            "title": self._first_match(
                compact,
                [
                    r"(?:标题|title)[:：\s]*(.*?)(?=\s*(?:负责人|owner|日期|date|主要结论|summary|$))",
                    r"标题[:：]\s*([^。;]+)",
                    r"^(.{6,80})",
                ],
            ),
            "document_no": self._first_match(
                compact,
                [
                    r"(?:合同编号|发票号码|单据编号|编号|No\.?|Number)[:：\s#-]*([A-Z0-9][A-Z0-9._/-]{3,})",
                    r"\b([A-Z]{2,}-?\d{4,}[A-Z0-9-]*)\b",
                ],
            ),
            "date": self._first_match(
                compact,
                [r"(\d{4}[/-]\d{1,2}[/-]\d{1,2})", r"(\d{4}年\d{1,2}月\d{1,2}日)"],
            ),
            "effective_date": self._first_match(
                compact,
                [r"(?:生效日期|effective date)[:：\s]*([0-9年月日/-]+)", r"(\d{4}[/-]\d{1,2}[/-]\d{1,2})"],
            ),
            "amount": self._first_match(
                compact,
                [
                    r"(?:总金额|价税合计|金额|amount|total)[:：\s]*([¥$]?\s?\d[\d,]*(?:\.\d{1,2})?)",
                    r"([¥$]\s?\d[\d,]*(?:\.\d{1,2})?)",
                ],
            ),
            "issuer": self._first_match(
                compact,
                [r"(?:开票方|供应商|issuer|vendor)[:：\s]*(.*?)(?=\s*(?:购买方|开票日期|价税合计|amount|total|$))"],
            ),
            "owner": self._first_match(
                compact,
                [r"(?:负责人|owner|prepared by)[:：\s]*(.*?)(?=\s*(?:日期|date|结论|summary|$))"],
            ),
            "party_a": self._first_match(
                compact,
                [r"(?:甲方|Party A)[:：\s]*(.*?)(?=\s*(?:乙方|Party B|生效日期|effective date|总金额|amount|$))"],
            ),
            "party_b": self._first_match(
                compact,
                [r"(?:乙方|Party B)[:：\s]*(.*?)(?=\s*(?:生效日期|effective date|总金额|amount|服务周期|$))"],
            ),
        }
        table_fields = self._extract_from_tables(parsed.tables)
        fields = {
            **fields,
            **{
                key: value
                for key, value in table_fields.items()
                if self._should_replace_field(fields.get(key), value)
            },
        }
        fields = {key: value for key, value in fields.items() if value}
        if parsed.tables:
            fields["table_count"] = len(parsed.tables)
            fields["first_table_rows"] = len(parsed.tables[0].get("rows", []))

        required = REQUIRED_FIELDS.get(document_type, REQUIRED_FIELDS["general"])
        anomalies = []
        for field_name in required:
            if not fields.get(field_name):
                anomalies.append(
                    {
                        "code": "missing_required_field",
                        "severity": "warning",
                        "field": field_name,
                        "message": f"Required field '{field_name}' was not confidently extracted",
                    }
                )
        for warning in parsed.warnings:
            anomalies.append({"code": warning.get("code", "parse_warning"), "severity": "info", "message": warning.get("message", "")})

        present = sum(1 for field_name in required if fields.get(field_name))
        quality_score = round(present / max(len(required), 1), 3)
        key_points = self._key_points(compact)
        summary = {
            "title": fields.get("title") or f"{document_type.title()} document",
            "brief": key_points[0] if key_points else "Document parsed and prepared for human review.",
            "key_points": key_points[:5],
            "quality_score": quality_score,
        }
        return ExtractionResult(fields=fields, summary=summary, anomalies=anomalies, quality_score=quality_score)

    def _first_match(self, text: str, patterns: list[str]) -> str | None:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _key_points(self, text: str) -> list[str]:
        candidates = re.split(r"[。.!?\n]", text)
        points = [candidate.strip() for candidate in candidates if 24 <= len(candidate.strip()) <= 180]
        return points or [text[:160].strip()] if text.strip() else []

    def _extract_from_tables(self, tables: list[dict[str, Any]]) -> dict[str, Any]:
        header_map = {
            "发票号码": "document_no",
            "合同编号": "document_no",
            "单据编号": "document_no",
            "编号": "document_no",
            "no": "document_no",
            "number": "document_no",
            "开票方": "issuer",
            "供应商": "issuer",
            "issuer": "issuer",
            "vendor": "issuer",
            "购买方": "buyer",
            "甲方": "party_a",
            "party a": "party_a",
            "乙方": "party_b",
            "party b": "party_b",
            "开票日期": "date",
            "日期": "date",
            "date": "date",
            "生效日期": "effective_date",
            "effective date": "effective_date",
            "价税合计": "amount",
            "总金额": "amount",
            "金额": "amount",
            "amount": "amount",
            "total": "amount",
            "标题": "title",
            "title": "title",
            "负责人": "owner",
            "owner": "owner",
        }
        extracted: dict[str, Any] = {}
        for table in tables:
            rows = table.get("rows") or []
            if len(rows) < 2:
                continue
            headers = [self._normalize_header(cell) for cell in rows[0]]
            for row in rows[1:]:
                for index, raw_value in enumerate(row):
                    if index >= len(headers):
                        continue
                    field_name = header_map.get(headers[index])
                    value = str(raw_value).strip() if raw_value is not None else ""
                    if field_name and value and not extracted.get(field_name):
                        extracted[field_name] = value
        return extracted

    def _normalize_header(self, value: Any) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip().lower())

    def _should_replace_field(self, current: Any, candidate: Any) -> bool:
        if candidate is None or str(candidate).strip() == "":
            return False
        if current is None:
            return True
        stripped = str(current).strip()
        return stripped in {"", "|", "-", "n/a", "N/A"}
