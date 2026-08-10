from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_cases(relative_path: str) -> list[dict[str, object]]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_public_benchmarks_have_credible_scope_and_existing_sources() -> None:
    extraction_cases = load_cases("samples/eval_labels.json")
    rag_cases = load_cases("samples/rag_eval_labels.json")

    assert len(extraction_cases) == 30
    assert len(rag_cases) == 20
    assert Counter(case["expected_document_type"] for case in extraction_cases) == {
        "contract": 10,
        "invoice": 10,
        "report": 10,
    }
    assert len({case["id"] for case in extraction_cases}) == 30
    assert len({case["id"] for case in rag_cases}) == 20
    assert len({case["file_path"] for case in extraction_cases}) >= 15
    assert sum(case.get("expected_hit", True) is False for case in rag_cases) >= 3
    assert all((ROOT / case["file_path"]).is_file() for case in extraction_cases + rag_cases)


def test_readme_leads_with_demo_and_generated_evidence() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "![文档 Agent 工作台](frontend-refactor-wide.png)" in readme
    assert "docs/evaluation_report.md" in readme
    assert "docs/rag_evaluation_report.md" in readme
    assert "docs/two-minute-demo.md" in readme
    assert "隐私安全示例数据" in readme
    assert "当前未提供公网托管演示" in readme


def test_ci_builds_and_smoke_tests_the_container_stack() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    dockerfile = (ROOT / "frontend/Dockerfile").read_text(encoding="utf-8")
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    backend_config = (ROOT / "backend/app/core/config.py").read_text(encoding="utf-8")

    assert "docker compose up --build -d" in workflow
    assert "http://127.0.0.1:8000/health" in workflow
    assert "http://127.0.0.1:4173/" in workflow
    assert "--retry-all-errors" in workflow
    assert "npm run test:e2e:docker" in workflow
    assert "docker compose down -v" in workflow
    assert "RUN npm ci" in dockerfile
    assert "RUN npm install" not in dockerfile
    for origin in ("http://localhost:4173", "http://127.0.0.1:4173"):
        assert origin in env_example
        assert origin in backend_config
