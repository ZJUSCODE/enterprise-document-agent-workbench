import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.classifier import classify_document
from app.services.extractor import ExtractorService
from app.services.parser import DocumentParser


def divide(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 3) if denominator else 0.0


def normalize(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.strip().lower()
    text = re.sub(r"\s+", "", text)
    text = text.replace(",", "")
    return text


def score_case(case: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / case["file_path"]
    parsed = DocumentParser().parse(path, path.name)
    document_type, confidence = classify_document(parsed.text, path.name)
    extraction = ExtractorService().extract(parsed, document_type=document_type, template_id="offline_eval")

    expected_fields = case.get("expected_fields", {})
    field_results = {}
    matches = 0
    predicted = 0
    for field_name, expected_value in expected_fields.items():
        actual_value = extraction.fields.get(field_name)
        matched = normalize(actual_value) == normalize(expected_value)
        predicted += int(bool(normalize(actual_value)))
        matches += int(matched)
        field_results[field_name] = {
            "expected": expected_value,
            "actual": actual_value,
            "matched": matched,
            "predicted": bool(normalize(actual_value)),
        }

    expected_document_type = case.get("expected_document_type")
    classification_matched = expected_document_type == document_type if expected_document_type else None
    precision = divide(matches, predicted)
    recall = divide(matches, len(expected_fields))
    return {
        "id": case["id"],
        "document_type": document_type,
        "classification_confidence": confidence,
        "classification_matched": classification_matched,
        "field_accuracy": recall,
        "field_precision": precision,
        "field_recall": recall,
        "field_f1": divide(2 * matches, predicted + len(expected_fields)),
        "matched_fields": matches,
        "predicted_fields": predicted,
        "expected_fields": len(expected_fields),
        "field_results": field_results,
        "anomalies": extraction.anomalies,
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    total_fields = sum(len(result["field_results"]) for result in results)
    matched_fields = sum(
        1 for result in results for field_result in result["field_results"].values() if field_result["matched"]
    )
    predicted_fields = sum(
        1 for result in results for field_result in result["field_results"].values() if field_result["predicted"]
    )
    classification_total = sum(1 for result in results if result["classification_matched"] is not None)
    classification_matches = sum(1 for result in results if result["classification_matched"] is True)
    field_totals: dict[str, dict[str, int]] = {}
    for result in results:
        for field_name, field_result in result["field_results"].items():
            item = field_totals.setdefault(field_name, {"matched": 0, "predicted": 0, "total": 0})
            item["total"] += 1
            item["matched"] += int(field_result["matched"])
            item["predicted"] += int(field_result["predicted"])
    return {
        "case_count": len(results),
        "field_accuracy": divide(matched_fields, total_fields),
        "field_precision": divide(matched_fields, predicted_fields),
        "field_recall": divide(matched_fields, total_fields),
        "field_f1": divide(2 * matched_fields, predicted_fields + total_fields),
        "matched_fields": matched_fields,
        "predicted_fields": predicted_fields,
        "expected_fields": total_fields,
        "classification_accuracy": divide(classification_matches, classification_total),
        "field_breakdown": {
            field_name: {
                "accuracy": divide(item["matched"], item["total"]),
                "precision": divide(item["matched"], item["predicted"]),
                "recall": divide(item["matched"], item["total"]),
                "f1": divide(2 * item["matched"], item["predicted"] + item["total"]),
                **item,
            }
            for field_name, item in sorted(field_totals.items())
        },
        "results": results,
    }


def build_markdown_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Document Extraction Evaluation Report",
        "",
        "## Summary",
        "",
        f"- Case count: {summary['case_count']}",
        f"- Classification accuracy: {summary['classification_accuracy']:.3f}",
        f"- Field accuracy: {summary['field_accuracy']:.3f}",
        f"- Field precision: {summary['field_precision']:.3f}",
        f"- Field recall: {summary['field_recall']:.3f}",
        f"- Field F1: {summary['field_f1']:.3f}",
        f"- Matched / predicted / expected fields: {summary['matched_fields']} / {summary['predicted_fields']} / {summary['expected_fields']}",
        "",
        "## Field Breakdown",
        "",
        "| Field | Precision | Recall | F1 | Matched | Predicted | Expected |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for field_name, item in summary["field_breakdown"].items():
        lines.append(
            f"| {field_name} | {item['precision']:.3f} | {item['recall']:.3f} | {item['f1']:.3f} | "
            f"{item['matched']} | {item['predicted']} | {item['total']} |"
        )
    lines.extend(["", "## Case Details", ""])
    for result in summary["results"]:
        lines.extend(
            [
                f"### {result['id']}",
                "",
                f"- Predicted type: `{result['document_type']}`",
                f"- Classification matched: `{result['classification_matched']}`",
                f"- Field accuracy: `{result['field_accuracy']:.3f}`",
                f"- Field precision / recall / F1: `{result['field_precision']:.3f}` / `{result['field_recall']:.3f}` / `{result['field_f1']:.3f}`",
                "",
                "| Field | Expected | Actual | Predicted | Matched |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for field_name, field_result in result["field_results"].items():
            expected = str(field_result["expected"]).replace("|", "\\|")
            actual = str(field_result["actual"]).replace("|", "\\|")
            lines.append(
                f"| {field_name} | {expected} | {actual} | {field_result['predicted']} | {field_result['matched']} |"
            )
        if result["anomalies"]:
            lines.extend(["", "Anomalies:"])
            for anomaly in result["anomalies"]:
                lines.append(f"- `{anomaly.get('code')}`: {anomaly.get('message')}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate extraction against a labeled local dataset.")
    parser.add_argument("--labels", default="samples/eval_labels.json")
    parser.add_argument("--output", default="")
    parser.add_argument("--report-output", default="")
    args = parser.parse_args()

    labels_path = ROOT / args.labels
    cases = json.loads(labels_path.read_text(encoding="utf-8"))
    results = [score_case(case) for case in cases]
    summary = summarize(results)

    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output:
        (ROOT / args.output).write_text(payload, encoding="utf-8")
    if args.report_output:
        (ROOT / args.report_output).write_text(build_markdown_report(summary), encoding="utf-8")
    sys.stdout.buffer.write(payload.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
