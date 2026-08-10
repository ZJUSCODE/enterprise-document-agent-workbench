# Document Agent Portfolio Evidence Refresh

## Goal

Make the existing Document Agent easier to trust and demonstrate in an AI job interview without redesigning its architecture.

## Chosen approach

Use an evidence-first refresh:

1. Replace the tiny, all-perfect benchmark impression with a larger privacy-safe benchmark that includes varied wording, negative cases, and at least one documented limitation.
2. Put one existing product screenshot and a two-minute walkthrough at the top of the README.
3. Add one real browser smoke path and one Docker delivery smoke path to CI.
4. Recheck frontend dependency findings and update only packages required to remove confirmed current vulnerabilities.

Alternatives rejected:

- Presentation-only polish would leave the weak evaluation evidence unchanged.
- Architecture expansion with a new vector database, SSO, or Agent framework would add complexity without improving the current interview story.

## Scope

### Evaluation

- Keep the current evaluator and report formats as the source of truth.
- Expand the extraction benchmark to 30 clearly labeled privacy-safe cases across contract, invoice, and report documents.
- Expand the RAG benchmark to 20 questions with paraphrases, multi-evidence questions, and negative queries.
- Keep the benchmark deterministic and offline.
- Include wording and formatting variation instead of duplicating one template.
- Report case count and metrics from generated output; do not hand-maintain result totals in README prose.

### Presentation

- Reuse `frontend-refactor-wide.png` as the README hero image.
- Put the problem, workflow, evidence, limitations, and two-minute demo path before setup instructions.
- State honestly that the public benchmark is privacy-safe sample data and that no hosted demo currently exists.
- Do not publish synthetic logs or claim production usage.

### Verification

- Add a minimal Playwright smoke test that uses an installed Chrome channel and does not download a browser locally.
- The browser test proves that the workbench loads and exposes the primary upload, task, approval, and RAG surfaces.
- Retain the existing backend workflow test as the functional end-to-end proof.
- Add a CI Docker smoke job that builds the existing Compose stack and verifies backend health plus the frontend response.
- Do not add a second runtime path or new deployment platform.

### Dependency boundary

- Run the current package audit against the committed lockfile.
- Change dependency versions only when a current advisory is confirmed and the existing production build remains green.

## Files expected to change

- `README.md`
- `samples/eval_labels.json` and privacy-safe benchmark fixtures under `samples/benchmark/`
- `tests/` only where benchmark or delivery contracts need coverage
- `frontend/package.json` and `frontend/package-lock.json` only if the audit confirms an actionable issue
- `.github/workflows/ci.yml`
- Playwright configuration and one focused browser smoke specification

## Acceptance

- Both extraction and RAG evaluation commands succeed from generated inputs.
- The extraction report contains 30 cases, the RAG report contains 20 cases, and all displayed totals come from generated reports.
- Existing Python tests plus new benchmark contract tests pass.
- The frontend production build passes.
- The browser smoke test passes with installed Chrome and no browser install command.
- CI validates Python, both evaluations, frontend build, browser smoke, and Docker smoke.
- README contains no production-customer claim, hosted-demo claim, or manually asserted perfect metric.
- No new application architecture, model provider, authentication system, or deployment service is introduced.
