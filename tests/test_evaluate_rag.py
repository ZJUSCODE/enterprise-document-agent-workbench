from scripts.evaluate_rag import build_markdown_report, evidence_recall, summarize


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


def test_summarize_scores_positive_retrieval_and_negative_abstention_separately() -> None:
    summary = summarize(
        [
            {
                "expected_hit": True,
                "hit": True,
                "reciprocal_rank": 1.0,
                "evidence_recall": 1.0,
            },
            {
                "expected_hit": False,
                "hit": True,
                "reciprocal_rank": 0.0,
                "evidence_recall": 0.0,
            },
        ],
        top_k=3,
    )

    assert summary["hit_rate"] == 1.0
    assert summary["negative_abstention_rate"] == 1.0


def test_negative_case_report_has_no_trailing_whitespace() -> None:
    report = build_markdown_report(
        {
            "case_count": 1,
            "positive_cases": 0,
            "negative_cases": 1,
            "top_k": 3,
            "hit_rate": 0.0,
            "mrr": 0.0,
            "evidence_recall": 0.0,
            "negative_abstention_rate": 1.0,
            "results": [
                {
                    "id": "negative",
                    "question": "irrelevant question",
                    "expected_terms": [],
                    "expected_hit": False,
                    "hit": True,
                    "rank": None,
                    "evidence_recall": 0.0,
                    "top_hits": [],
                }
            ],
        }
    )

    assert not any(line.endswith(" ") for line in report.splitlines())
