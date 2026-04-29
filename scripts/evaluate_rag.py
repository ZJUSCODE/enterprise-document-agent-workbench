import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.db.base import Base
from app.models import RagChunk  # noqa: F401
from app.services.classifier import classify_document
from app.services.parser import DocumentParser
from app.services.rag import RagSearchHit, RagService


def normalize(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.strip().lower()
    return re.sub(r"\s+", "", text)


def evidence_contains_all(hit: RagSearchHit, expected_terms: list[str]) -> bool:
    text = normalize(hit.text)
    return all(normalize(term) in text for term in expected_terms)


def evidence_recall(hits: list[RagSearchHit], expected_terms: list[str]) -> float:
    if not expected_terms:
        return 0.0
    evidence = normalize("\n".join(hit.text for hit in hits))
    matched = sum(1 for term in expected_terms if normalize(term) in evidence)
    return round(matched / len(expected_terms), 3)


def build_session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine, tables=[RagChunk.__table__])
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


def index_cases(db: Session, cases: list[dict[str, Any]]) -> None:
    parser = DocumentParser()
    rag = RagService()
    indexed_paths: set[str] = set()
    for case in cases:
        file_path = case["file_path"]
        if file_path in indexed_paths:
            continue
        path = ROOT / file_path
        parsed = parser.parse(path, path.name)
        document_type, confidence = classify_document(parsed.text, path.name)
        rag.index_document(
            db,
            file_id=file_path,
            task_id=None,
            text=parsed.text,
            document_type=document_type,
            metadata={
                "filename": path.name,
                "classification_confidence": confidence,
                "eval_source": True,
            },
        )
        indexed_paths.add(file_path)
    db.commit()


def score_case(db: Session, case: dict[str, Any], top_k: int) -> dict[str, Any]:
    rag = RagService()
    hits = rag.search(
        db,
        question=case["question"],
        top_k=top_k,
        document_type=case.get("document_type"),
        file_id=case.get("file_path"),
    )
    expected_terms = case.get("expected_terms", [])
    found_rank = next(
        (rank for rank, hit in enumerate(hits, start=1) if evidence_contains_all(hit, expected_terms)),
        None,
    )
    return {
        "id": case["id"],
        "question": case["question"],
        "expected_terms": expected_terms,
        "hit": found_rank is not None,
        "rank": found_rank,
        "reciprocal_rank": round(1 / found_rank, 3) if found_rank else 0.0,
        "evidence_recall": evidence_recall(hits, expected_terms),
        "top_hits": [
            {
                "rank": rank,
                "file_id": hit.file_id,
                "document_type": hit.document_type,
                "score": hit.score,
                "matched_terms": hit.metadata.get("matched_terms", []),
                "preview": hit.text[:180],
            }
            for rank, hit in enumerate(hits, start=1)
        ],
    }


def summarize(results: list[dict[str, Any]], top_k: int) -> dict[str, Any]:
    case_count = len(results)
    hits = sum(1 for result in results if result["hit"])
    reciprocal_rank_sum = sum(result["reciprocal_rank"] for result in results)
    evidence_recall_sum = sum(result["evidence_recall"] for result in results)
    return {
        "case_count": case_count,
        "top_k": top_k,
        "hit_rate": round(hits / case_count, 3) if case_count else 0.0,
        "mrr": round(reciprocal_rank_sum / case_count, 3) if case_count else 0.0,
        "evidence_recall": round(evidence_recall_sum / case_count, 3) if case_count else 0.0,
        "results": results,
    }


def build_markdown_report(summary: dict[str, Any]) -> str:
    lines = [
        "# RAG Retrieval Evaluation Report",
        "",
        "## Summary",
        "",
        f"- Case count: {summary['case_count']}",
        f"- Top K: {summary['top_k']}",
        f"- Hit rate@K: {summary['hit_rate']:.3f}",
        f"- MRR: {summary['mrr']:.3f}",
        f"- Evidence recall: {summary['evidence_recall']:.3f}",
        "",
        "## Case Details",
        "",
    ]
    for result in summary["results"]:
        lines.extend(
            [
                f"### {result['id']}",
                "",
                f"- Question: {result['question']}",
                f"- Expected terms: {', '.join(result['expected_terms'])}",
                f"- Hit: `{result['hit']}`",
                f"- Rank: `{result['rank']}`",
                f"- Evidence recall: `{result['evidence_recall']:.3f}`",
                "",
                "| Rank | Score | File | Matched Query Terms | Preview |",
                "| ---: | ---: | --- | --- | --- |",
            ]
        )
        for hit in result["top_hits"]:
            preview = str(hit["preview"]).replace("|", "\\|").replace("\n", " ")
            matched = ", ".join(hit["matched_terms"])
            lines.append(f"| {hit['rank']} | {hit['score']:.3f} | {hit['file_id']} | {matched} | {preview} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate local RAG retrieval against labeled evidence terms.")
    parser.add_argument("--labels", default="samples/rag_eval_labels.json")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--output", default="")
    parser.add_argument("--report-output", default="")
    args = parser.parse_args()

    cases = json.loads((ROOT / args.labels).read_text(encoding="utf-8"))
    db = build_session()
    try:
        index_cases(db, cases)
        results = [score_case(db, case, args.top_k) for case in cases]
    finally:
        db.close()
    summary = summarize(results, args.top_k)

    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output:
        (ROOT / args.output).write_text(payload, encoding="utf-8")
    if args.report_output:
        (ROOT / args.report_output).write_text(build_markdown_report(summary), encoding="utf-8")
    sys.stdout.buffer.write(payload.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
