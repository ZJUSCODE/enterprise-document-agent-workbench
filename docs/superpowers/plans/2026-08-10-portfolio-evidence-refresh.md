# Document Agent Portfolio Evidence Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing Document Agent into a more credible, quickly demonstrable AI job-search project without changing its application architecture.

**Architecture:** Keep the current FastAPI, Vue, evaluator, and Docker Compose paths. Improve only the evidence around them: larger deterministic datasets, explicit negative RAG scoring, a recruiter-first README, one Chrome-based UI smoke test, and CI delivery smoke checks.

**Tech Stack:** Python 3.12, pytest, FastAPI, Vue 3, Vite, Playwright with installed Chrome, Docker Compose, GitHub Actions.

---

### Task 1: Define credible benchmark contracts

**Files:**
- Create: `tests/test_portfolio_evidence_contract.py`
- Modify: `tests/test_evaluate_rag.py`
- Modify: `scripts/evaluate_rag.py`

- [ ] **Step 1: Add failing dataset and negative-query contracts**

Add tests that load both label files and assert:

```python
assert len(extraction_cases) == 30
assert len(rag_cases) == 20
assert Counter(case["expected_document_type"] for case in extraction_cases) == {
    "contract": 10,
    "invoice": 10,
    "report": 10,
}
assert len({case["id"] for case in extraction_cases}) == 30
assert len({case["id"] for case in rag_cases}) == 20
assert sum(case.get("expected_hit", True) is False for case in rag_cases) >= 3
assert all((ROOT / case["file_path"]).is_file() for case in extraction_cases + rag_cases)
```

Add a focused RAG unit test with one positive and one negative result:

```python
summary = summarize([
    {"expected_hit": True, "hit": True, "reciprocal_rank": 1.0, "evidence_recall": 1.0},
    {"expected_hit": False, "hit": True, "reciprocal_rank": 0.0, "evidence_recall": 0.0},
], top_k=3)
assert summary["hit_rate"] == 1.0
assert summary["negative_abstention_rate"] == 1.0
```

- [ ] **Step 2: Run RED checks**

Run:

```powershell
python -m pytest tests/test_portfolio_evidence_contract.py tests/test_evaluate_rag.py -q
```

Expected: dataset counts fail at 3 and 5, and the RAG summary lacks negative-query semantics.

- [ ] **Step 3: Implement explicit positive and negative RAG scoring**

In `score_case`, derive `expected_hit = case.get("expected_hit", True)`. Positive cases pass only when all expected evidence is retrieved; negative cases pass only when the search returns no hits. Include `expected_hit` in each result.

In `summarize`, calculate `hit_rate`, MRR, and evidence recall over positive cases, then add:

```python
"negative_abstention_rate": round(
    sum(result["hit"] for result in negative_results) / len(negative_results), 3
) if negative_results else 0.0
```

Show the new metric in the Markdown summary.

- [ ] **Step 4: Run focused GREEN checks**

Run the same pytest command. Expected: only dataset count assertions remain red until Task 2; the RAG unit tests pass.

- [ ] **Step 5: Commit evaluator behavior**

```powershell
git add scripts/evaluate_rag.py tests/test_evaluate_rag.py tests/test_portfolio_evidence_contract.py
git commit -m "test: define credible document agent evidence"
```

### Task 2: Expand privacy-safe evaluation inputs

**Files:**
- Create: `samples/benchmark/*.txt`
- Create: `samples/benchmark/*.csv`
- Modify: `samples/eval_labels.json`
- Modify: `samples/rag_eval_labels.json`
- Modify: `docs/evaluation_report.md`
- Modify: `docs/rag_evaluation_report.md`

- [ ] **Step 1: Add 15 distinct privacy-safe documents**

Create five contracts, five invoices, and five operational reports. Use invented organization names ending in `示例`, clearly fictional IDs, varied Chinese/English labels, varied date and amount formats, and content long enough for meaningful retrieval.

- [ ] **Step 2: Define 30 extraction cases**

Create ten cases for each document type. Each source document appears in two cases with different expected field subsets so classification and field behavior are scored separately without claiming 30 unique documents.

- [ ] **Step 3: Define 20 RAG cases**

Add paraphrases, multi-evidence questions, and at least three questions whose terms are absent from the selected file and therefore use `"expected_hit": false`.

- [ ] **Step 4: Run dataset contracts and both evaluations**

```powershell
python -m pytest tests/test_portfolio_evidence_contract.py tests/test_evaluate_dataset.py tests/test_evaluate_rag.py -q
python scripts/evaluate_dataset.py --labels samples/eval_labels.json --report-output docs/evaluation_report.md
python scripts/evaluate_rag.py --labels samples/rag_eval_labels.json --report-output docs/rag_evaluation_report.md
```

Expected: 30 extraction cases, 20 RAG cases, and generated reports with no hand-edited totals.

- [ ] **Step 5: Commit benchmark evidence**

```powershell
git add samples docs/evaluation_report.md docs/rag_evaluation_report.md
git commit -m "test: expand privacy-safe document benchmarks"
```

### Task 3: Make the README recruiter-first

**Files:**
- Modify: `README.md`
- Create: `docs/two-minute-demo.md`
- Test: `tests/test_portfolio_evidence_contract.py`

- [ ] **Step 1: Add a failing README contract**

Assert that README embeds `frontend-refactor-wide.png`, links the CI run page, links both generated evaluation reports, links the two-minute demo, contains `隐私安全示例数据`, and does not claim a hosted demo or production customer usage.

- [ ] **Step 2: Run RED**

```powershell
python -m pytest tests/test_portfolio_evidence_contract.py -q
```

Expected: README contract fails.

- [ ] **Step 3: Rewrite only the README opening**

Place, in order: hero screenshot, one-sentence product outcome, six-step workflow, generated evidence links, honest limitations, two-minute walkthrough, then the existing detailed setup and API reference.

- [ ] **Step 4: Add the two-minute walkthrough**

Document exact timestamps for upload, trace, extraction, approval, RAG citation, and metrics. State that it is a recording script until an actual video URL is added.

- [ ] **Step 5: Run GREEN and commit**

```powershell
python -m pytest tests/test_portfolio_evidence_contract.py -q
git add README.md docs/two-minute-demo.md tests/test_portfolio_evidence_contract.py
git commit -m "docs: make the document agent interview-ready"
```

### Task 4: Add installed-Chrome browser verification

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Create: `frontend/playwright.config.ts`
- Create: `frontend/tests/workbench.spec.ts`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Confirm dependency advisories before changing versions**

Run:

```powershell
Set-Location frontend
npm audit --json
```

Record only current production and development findings. Do not use `--force`.

- [ ] **Step 2: Add Playwright without a browser download**

Add `@playwright/test` as a dev dependency. Configure `channel: "chrome"`, start the existing Vite dev server, and do not add `playwright install` to local or CI commands.

- [ ] **Step 3: Write and run the browser RED test**

The test loads `/`, expects `企业文档流程自动化`, and verifies the upload, task, approval, RAG, and metrics headings. Run:

```powershell
npm run test:e2e
```

Expected before the package/config implementation is complete: the new script or configuration is missing.

- [ ] **Step 4: Make the smallest package and CI changes**

Add `"test:e2e": "playwright test"`. CI runs it after the production build using the runner's installed Chrome. If a current audit finding is fixed by a non-breaking lockfile update, apply that update and rerun the build; otherwise report it without forcing an upgrade.

- [ ] **Step 5: Verify and commit**

```powershell
npm run build
npm run test:e2e
npm audit --json
git add frontend .github/workflows/ci.yml
git commit -m "test: verify the document workbench in Chrome"
```

### Task 5: Add Docker delivery smoke and release evidence

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `frontend/Dockerfile`
- Test: GitHub Actions `ci`

- [ ] **Step 1: Add a deterministic Docker contract check**

Extend the Python evidence contract to assert that CI starts the Docker stack and checks `http://127.0.0.1:8000/health` plus `http://127.0.0.1:4173/`.

- [ ] **Step 2: Run RED**

```powershell
python -m pytest tests/test_portfolio_evidence_contract.py -q
```

Expected: Docker CI assertions fail.

- [ ] **Step 3: Add one Docker smoke job**

Use the existing Compose file. Start the stack, poll the API health and frontend with bounded shell loops, and always run `docker compose down -v` in an `if: always()` cleanup step. Change the frontend Docker build from `npm install` to `npm ci` so it consumes the committed lockfile exactly.

- [ ] **Step 4: Run all local checks**

```powershell
python -m pytest tests -q
python scripts/evaluate_dataset.py --labels samples/eval_labels.json --report-output docs/evaluation_report.md
python scripts/evaluate_rag.py --labels samples/rag_eval_labels.json --report-output docs/rag_evaluation_report.md
npm --prefix frontend run build
npm --prefix frontend run test:e2e
docker compose config --quiet
git diff --check
```

Expected: all commands exit 0. Docker runtime smoke is proven by GitHub Actions if the local Docker server is unavailable.

- [ ] **Step 5: Commit, push, and verify CI**

```powershell
git add .github/workflows/ci.yml frontend/Dockerfile tests/test_portfolio_evidence_contract.py
git commit -m "ci: smoke-test document agent delivery"
git push --set-upstream origin feat/document-agent-portfolio-evidence
gh run watch --exit-status
```

Expected: Python, evaluations, Vue build, installed-Chrome smoke, and Docker delivery smoke are all green for the exact commit.
