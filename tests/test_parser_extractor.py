from pathlib import Path

from app.services.classifier import classify_document
from app.services.extractor import ExtractorService
from app.services.parser import DocumentParser


def test_text_contract_parse_and_extract(tmp_path: Path) -> None:
    sample = tmp_path / "contract.txt"
    sample.write_text(
        "合同编号: CT-2026-0417\n甲方: 上海示例科技有限公司\n乙方: 北京流程自动化服务有限公司\n"
        "生效日期: 2026年4月17日\n总金额: ¥128,000.00",
        encoding="utf-8",
    )
    parsed = DocumentParser().parse(sample, sample.name)
    document_type, confidence = classify_document(parsed.text, sample.name)
    result = ExtractorService().extract(parsed, document_type=document_type, template_id="contract_review")

    assert document_type == "contract"
    assert confidence > 0.4
    assert result.fields["document_no"] == "CT-2026-0417"
    assert result.fields["party_a"] == "上海示例科技有限公司"
    assert result.quality_score >= 0.75


def test_report_title_stops_before_owner_and_date(tmp_path: Path) -> None:
    sample = tmp_path / "report.txt"
    sample.write_text(
        "标题: 企业文档流程自动化月度运行报告\n负责人: ops.demo\n日期: 2026-04-18\n"
        "主要结论: Agent 工作流稳定完成解析、检索、抽取和审批。",
        encoding="utf-8",
    )
    parsed = DocumentParser().parse(sample, sample.name)
    document_type, _ = classify_document(parsed.text, sample.name)
    result = ExtractorService().extract(parsed, document_type=document_type, template_id="report_summary")

    assert document_type == "report"
    assert result.fields["title"] == "企业文档流程自动化月度运行报告"
    assert result.fields["owner"] == "ops.demo"
    assert result.fields["date"] == "2026-04-18"


def test_english_invoice_csv_uses_structured_table_fields() -> None:
    sample = Path(__file__).resolve().parents[1] / "samples" / "benchmark" / "invoice_03.csv"
    parsed = DocumentParser().parse(sample, sample.name)
    document_type, _ = classify_document(parsed.text, sample.name)
    result = ExtractorService().extract(parsed, document_type=document_type, template_id="invoice_review")

    assert document_type == "invoice"
    assert result.fields["document_no"] == "DEMO-INV-003"
    assert result.fields["issuer"] == "River Example Systems Ltd."
