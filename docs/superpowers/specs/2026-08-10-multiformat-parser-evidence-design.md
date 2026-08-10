# Multi-format Parser Evidence Design

## Goal

Turn the advertised PDF, DOCX, XLSX, image, and OCR support into repeatable CI evidence without publishing customer documents or committing generated binaries.

## Approaches considered

1. Commit binary fixtures under `samples/benchmark/`. This is easy to inspect but enlarges the repository and makes fixture provenance harder to review.
2. Generate privacy-safe files during tests. This keeps every input reproducible from readable test code and exercises the real parser libraries. **Selected.**
3. Build a separate benchmark framework and report generator. This would produce richer metrics but duplicates the existing evaluator and is unnecessary for format coverage.

## Design

`tests/test_multiformat_parsing.py` will generate four temporary inputs with dependencies already declared in `backend/requirements.txt`:

- a two-page text PDF made with ReportLab and parsed by pypdf;
- a DOCX table made with python-docx and parsed by python-docx;
- an XLSX worksheet made with openpyxl and parsed by openpyxl;
- a high-contrast PNG made with Pillow and read by the real Tesseract OCR process.

Each test will assert parser identity or metadata plus a user-visible extracted value. The OCR test may skip on developer machines where the operating-system binary is absent; GitHub Actions will install `tesseract-ocr` and run it without skipping. No production parser path changes unless a test reveals a real defect.

The README evidence table will link directly to the test file. A repository contract assertion will prevent that link and the CI Tesseract installation from being removed silently.

## Success criteria

- Four new format tests pass in GitHub Actions with zero skips.
- Existing extraction and RAG evaluations remain unchanged at their current results.
- All Python tests, the Vue production build, installed-Chrome test, and Docker smoke test pass.
- No generated PDF, DOCX, XLSX, or PNG is committed.

