from scripts.evaluate_rag import evidence_recall, summarize


def test_evidence_recall_counts_expected_terms_across_hits() -> None:
    hits = [
        type("Hit", (), {"text": "服务内容包括文档解析和字段抽取。"})(),
        type("Hit", (), {"text": "违约责任要求 10 个工作日内完成整改。"})(),
    ]

    assert evidence_recall(hits, ["字段抽取", "整改"]) == 1.0
    assert evidence_recall(hits, ["字段抽取", "不存在"]) == 0.5


def test_summarize_reports_hit_rate_mrr_and_evidence_recall() -> None:
    summary = summarize(
        [
            {"hit": True, "reciprocal_rank": 1.0, "evidence_recall": 1.0},
            {"hit": False, "reciprocal_rank": 0.0, "evidence_recall": 0.5},
        ],
        top_k=3,
    )

    assert summary["hit_rate"] == 0.5
    assert summary["mrr"] == 0.5
    assert summary["evidence_recall"] == 0.75
