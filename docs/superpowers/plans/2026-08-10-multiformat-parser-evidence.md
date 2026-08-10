# Multi-format Parser Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reproducible CI evidence for real PDF, DOCX, XLSX, image, and OCR parsing.

**Architecture:** Generate privacy-safe documents inside pytest temporary directories and pass them through the existing `DocumentParser` and `ExtractorService`. Keep OCR deterministic by using a high-contrast English image and installing the same Tesseract package already used by the backend Docker image.

**Tech Stack:** pytest, ReportLab, pypdf, python-docx, openpyxl, Pillow, pytesseract, GitHub Actions

---

### Task 1: Lock the public evidence contract

**Files:**
- Modify: `tests/test_portfolio_evidence_contract.py`
- Modify: `README.md`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Add failing assertions**

Assert that README links to `tests/test_multiformat_parsing.py` and CI installs `tesseract-ocr` before backend tests.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `D:\ANACONDA\python.exe -m pytest tests/test_portfolio_evidence_contract.py -q`

Expected: failure because the new evidence link and CI package step are absent.

- [ ] **Step 3: Add the minimum documentation and CI lines**

Add one README evidence-table row and one Ubuntu package-install step using `sudo apt-get update && sudo apt-get install -y tesseract-ocr`.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run the same focused pytest command and expect all tests in the file to pass.

### Task 2: Add real multi-format characterization tests

**Files:**
- Create: `tests/test_multiformat_parsing.py`

- [ ] **Step 1: Add four focused tests**

Generate a two-page PDF report, DOCX contract table, XLSX invoice table, and high-contrast PNG. Parse each through `DocumentParser`; for the first three, also run `ExtractorService` and assert core fields. For PNG, assert OCR text contains a stable English identifier.

- [ ] **Step 2: Run the tests**

Run: `D:\ANACONDA\python.exe -m pytest tests/test_multiformat_parsing.py -q`

Expected locally: three passes and one OCR skip when no Tesseract binary is installed. Expected in CI: four passes and zero skips.

### Task 3: Full verification and publication

**Files:**
- Verify all modified files
- Update local handoff: `work/portfolio-release-handoff/document.json`

- [ ] **Step 1: Run all Python tests and both evaluators**

Expect all tests to pass apart from the documented local OCR skip; extraction metrics stay at 1.000 and the RAG report remains reproducible.

- [ ] **Step 2: Run frontend production build**

Run `npm run build` in `frontend/` and expect exit code 0.

- [ ] **Step 3: Commit, publish a pull request, and wait for CI**

Require `test-and-build` and `docker-smoke` success. Confirm the OCR test ran without skipping from the CI pytest output.

- [ ] **Step 4: Merge and update the handoff**

Record the exact merged main SHA, test count, evaluation case count, and successful main CI URL.

