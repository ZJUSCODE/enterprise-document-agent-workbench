import math
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import DocumentFile, RagChunk, WorkflowTask


@dataclass
class RagSearchHit:
    chunk_id: str
    file_id: str
    task_id: str | None
    document_type: str | None
    score: float
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class QueryTerm:
    value: str
    weight: float


class RagService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def index_document(
        self,
        db: Session,
        *,
        file_id: str,
        task_id: str | None,
        text: str,
        document_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        db.execute(delete(RagChunk).where(RagChunk.task_id == task_id) if task_id else delete(RagChunk).where(RagChunk.file_id == file_id))
        chunks = self.chunk_text(text)
        for index, chunk_text in enumerate(chunks):
            db.add(
                RagChunk(
                    file_id=file_id,
                    task_id=task_id,
                    chunk_index=index,
                    document_type=document_type,
                    text=chunk_text,
                    metadata_json={**(metadata or {}), "chunk_length": len(chunk_text)},
                )
            )
        db.flush()
        return len(chunks)

    def chunk_text(self, text: str) -> list[str]:
        cleaned = re.sub(r"\n{3,}", "\n\n", text.strip())
        if not cleaned:
            return []
        size = max(200, self.settings.rag_chunk_size)
        overlap = min(max(0, self.settings.rag_chunk_overlap), size // 2)
        chunks = []
        start = 0
        while start < len(cleaned):
            end = min(len(cleaned), start + size)
            chunk = cleaned[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(cleaned):
                break
            start = end - overlap
        return chunks

    def search(
        self,
        db: Session,
        *,
        question: str,
        top_k: int | None = None,
        document_type: str | None = None,
        file_id: str | None = None,
    ) -> list[RagSearchHit]:
        limit = min(max(top_k or self.settings.rag_default_top_k, 1), 20)
        statement = select(RagChunk)
        if document_type:
            statement = statement.where(RagChunk.document_type == document_type)
        if file_id:
            statement = statement.where(RagChunk.file_id == file_id)
        chunks = list(db.scalars(statement).all())
        terms = self._terms(question)
        weighted_terms = self._weight_terms(terms, [chunk.text for chunk in chunks])
        scored = []
        for chunk in chunks:
            score = self._score(chunk.text, weighted_terms)
            if score > 0:
                matched_terms = self._matched_terms(chunk.text, terms)
                scored.append(
                    RagSearchHit(
                        chunk_id=chunk.id,
                        file_id=chunk.file_id,
                        task_id=chunk.task_id,
                        document_type=chunk.document_type,
                        score=score,
                        text=chunk.text,
                        metadata={**(chunk.metadata_json or {}), "matched_terms": matched_terms[:12]},
                    )
                )
        return sorted(scored, key=lambda hit: hit.score, reverse=True)[:limit]

    def answer(self, question: str, hits: list[RagSearchHit]) -> str:
        if not hits:
            return "没有检索到足够相关的文档片段。"
        settings = get_settings()
        if settings.llm.api_key:
            try:
                return self._llm_answer(question, hits)
            except Exception:
                pass
        evidence = "\n".join(
            f"[{index + 1}] {self._snippet(hit.text, question)}" for index, hit in enumerate(hits[:3])
        )
        return f"基于当前检索结果，最相关的信息如下：\n{evidence}"

    def _llm_answer(self, question: str, hits: list[RagSearchHit]) -> str:
        from openai import OpenAI

        settings = get_settings()
        llm = settings.llm
        client_kwargs: dict[str, Any] = {"api_key": llm.api_key, "timeout": settings.openai_timeout_seconds}
        if llm.base_url:
            client_kwargs["base_url"] = llm.base_url
        client = OpenAI(**client_kwargs)
        context = "\n\n".join(
            f"[{index + 1}] file_id={hit.file_id} task_id={hit.task_id}\n{hit.text}" for index, hit in enumerate(hits)
        )
        response = client.chat.completions.create(
            model=llm.model,
            messages=[
                {"role": "system", "content": "Answer using only the provided enterprise document context. Cite chunk numbers."},
                {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
            ],
        )
        return response.choices[0].message.content or ""

    def _terms(self, question: str) -> list[str]:
        ascii_terms = re.findall(r"[A-Za-z0-9_.-]{2,}", question.lower())
        chinese = re.findall(r"[\u4e00-\u9fff]", question)
        bigrams = ["".join(chinese[index : index + 2]) for index in range(len(chinese) - 1)]
        # Preserve order while removing duplicates so repeated question words do not over-amplify a chunk.
        return list(dict.fromkeys([*ascii_terms, *bigrams, *chinese]))

    def _weight_terms(self, terms: list[str], corpus: list[str]) -> list[QueryTerm]:
        if not terms:
            return []
        corpus_size = max(len(corpus), 1)
        weighted = []
        for term in terms:
            document_frequency = sum(1 for text in corpus if term.lower() in text.lower())
            idf = math.log((corpus_size + 1) / (document_frequency + 1)) + 1.0
            weighted.append(QueryTerm(value=term, weight=idf))
        return weighted

    def _score(self, text: str, terms: list[str] | list[QueryTerm]) -> float:
        if not terms:
            return 0.0
        lower = text.lower()
        score = 0.0
        for term in terms:
            value = term.value if isinstance(term, QueryTerm) else term
            weight = term.weight if isinstance(term, QueryTerm) else 1.0
            occurrences = lower.count(value.lower())
            if occurrences:
                score += (1.0 + math.log(occurrences + 1)) * min(len(value), 8) * weight
        return round(score / math.sqrt(max(len(text), 1)), 4)

    def _matched_terms(self, text: str, terms: list[str]) -> list[str]:
        lower = text.lower()
        matched = [term for term in terms if term.lower() in lower]
        informative = [term for term in matched if len(term) > 1]
        return informative or matched

    def _snippet(self, text: str, question: str, window: int = 260) -> str:
        terms = self._terms(question)
        lower = text.lower()
        first_match = min((lower.find(term.lower()) for term in terms if term.lower() in lower), default=0)
        start = max(first_match - window // 4, 0)
        snippet = text[start : start + window].strip()
        if start > 0:
            snippet = f"...{snippet}"
        if start + window < len(text):
            snippet = f"{snippet}..."
        return snippet
