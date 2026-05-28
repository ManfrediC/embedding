# AGENTS.md

Repo-specific instructions for `C:\Projects\embedding`.

## Purpose

This repository is an experimental workspace for embedding, retrieval, and
clustering tests over stiff person spectrum disorder (SPSD) paper artefacts
maintained in `C:\Projects\sps-review`.

It is not the canonical systematic-review pipeline. Treat it as a sandbox that
must preserve source provenance and make every retrieval result traceable back
to `paper_id`, source text path, and page or chunk location.

## Inherited Context

- Follow `C:\Users\Manfredi\.codex\AGENTS.md`.
- When reading `C:\Projects\sps-review`, follow its `AGENTS.md` and
  `doc/repo_rules.md`.
- Use `paper_id` as the stable join key across SPS review artefacts.
- Prefer the SPS review registries over ad hoc filename parsing.

## Boundaries

- Treat `C:\Projects\sps-review\data\pdf_original`,
  `C:\Projects\sps-review\data\extraction_json`, and
  `C:\Projects\sps-review\data\references` as read-only unless the user
  explicitly asks to edit the SPS review repo.
- Do not copy raw PDFs or bulk extracted paper text into tracked files here.
- Keep generated manifests, chunks, vectors, indexes, and run reports under
  this repo's `data/`, `results/`, or `qa/` directories.
- Keep local secrets in `env/*.env`; never commit keys, raw prompts containing
  secrets, or paid-service logs.
- Do not start paid API or LLM runs without explicit approval and a visible cost
  estimate or cap.

## Expected Layout

- `config/`: local experiment configuration and model/evaluation settings.
- `data/cache/`: temporary local caches.
- `data/interim/`: generated manifests, extracted chunks, and draft datasets.
- `data/processed/`: generated embeddings, indexes, and compact derived tables.
- `doc/`: design notes, plans, and decision records.
- `env/`: untracked local environment files.
- `qa/`: review sheets, sampled checks, and human evaluation packs.
- `results/`: run metrics, logs, and reports.
- `spec/`: implementation specs and clarifying questions before coding.
- `src/embedding_sps/`: reusable experiment code.
- `tests/`: focused tests and fixtures.

## Verification Defaults

- For ingestion work, verify counts against
  `C:\Projects\sps-review\data\references\paper_artifact_registry.csv`.
- For chunking work, verify every chunk has `paper_id`, source path, chunk id,
  text hash, and page or location metadata.
- For retrieval work, include a lexical baseline and a small judged query set
  before claiming one embedding model is better.
- For model/API work, validate model output as untrusted input and keep all
  artefacts traceable to source evidence.

## Reporting

Final reports should include:

- Files changed.
- Upstream SPS artefacts read.
- Commands/checks run.
- Counts verified.
- Checks skipped and why.
- Remaining risks, especially cost, provenance, OCR quality, and clinical
  over-interpretation.
