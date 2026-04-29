from pathlib import Path


KEYWORDS = {
    "invoice": ["invoice", "tax", "amount due", "发票", "价税合计", "税额", "开票"],
    "contract": ["contract", "agreement", "party a", "party b", "合同", "甲方", "乙方", "违约"],
    "report": ["report", "summary", "analysis", "报告", "分析", "结论"],
    "spreadsheet": ["worksheet", "sheet", "table", "表格", "明细", "合计"],
}


def classify_document(text: str, filename: str) -> tuple[str, float]:
    lower_text = text.lower()
    lower_name = Path(filename).name.lower()
    scores: dict[str, int] = {}
    for document_type, keywords in KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in lower_text:
                score += 2
            if keyword.lower() in lower_name:
                score += 1
        scores[document_type] = score
    best_type, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return "general", 0.35
    return best_type, min(0.95, 0.45 + best_score * 0.1)
