from app.services.rag import RagSearchHit, RagService


def test_rag_chunking_and_term_scoring() -> None:
    service = RagService()
    chunks = service.chunk_text("合同编号 CT-001。付款方式为分三期支付。违约责任按日计算。" * 20)

    assert chunks
    assert service._score(chunks[0], service._terms("付款方式是什么")) > 0


def test_rag_term_weighting_prefers_specific_hits() -> None:
    service = RagService()
    corpus = [
        "合同包含付款方式、服务范围和验收流程。",
        "违约责任按日计算，逾期交付需要支付违约金。",
    ]
    weighted_terms = service._weight_terms(service._terms("违约责任怎么计算"), corpus)

    assert service._score(corpus[1], weighted_terms) > service._score(corpus[0], weighted_terms)


def test_rag_fallback_answer_uses_numbered_citations() -> None:
    service = RagService()
    answer = service.answer(
        "付款方式是什么",
        [
            RagSearchHit(
                chunk_id="chunk-1",
                file_id="file-1",
                task_id="task-1",
                document_type="contract",
                score=1.0,
                text="合同编号 CT-001。付款方式为分三期支付，验收后支付尾款。",
                metadata={},
            )
        ],
    )

    assert "[1]" in answer
    assert "付款方式" in answer
