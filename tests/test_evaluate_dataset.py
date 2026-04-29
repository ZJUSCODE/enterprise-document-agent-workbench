from scripts.evaluate_dataset import summarize


def test_summarize_reports_precision_recall_and_f1() -> None:
    summary = summarize(
        [
            {
                "classification_matched": True,
                "field_results": {
                    "document_no": {"matched": True, "predicted": True},
                    "amount": {"matched": False, "predicted": True},
                    "date": {"matched": False, "predicted": False},
                },
            }
        ]
    )

    assert summary["classification_accuracy"] == 1.0
    assert summary["field_precision"] == 0.5
    assert summary["field_recall"] == 0.333
    assert summary["field_f1"] == 0.4
    assert summary["field_breakdown"]["amount"]["precision"] == 0.0
    assert summary["field_breakdown"]["date"]["recall"] == 0.0
