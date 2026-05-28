# CONTINUITY

Last updated: 2026-05-28.

## Current State

- Basic repository layout has been created.
- Top-level operating files are present: `AGENTS.md`, `MEMORY.md`,
  `CONTINUITY.md`, and `GOALS.md`.
- The first application plan is in `doc/sps_embedding_application_plan.md`.
- No code, environment, vector index, or embedding run exists yet.

## Next Small Steps

1. Choose the first pilot scope: recommended default is 25 to 50 papers
   stratified across source categories, including proceedings abstracts and a
   few split case-series rows.
2. Create an ingestion script that reads the SPS `paper_artifact_registry.csv`
   and writes a local manifest under `data/interim/`.
3. Create a chunking script that reads preferred text JSONs, preserves page
   provenance, and writes JSONL chunks under `data/interim/`.
4. Add tests for manifest counts, missing-file handling, and chunk provenance.
5. Run a local text embedding map with paper-level clustering, nearest
   neighbours, and projection outputs before any paid, GPU-specific, or
   PDF-native API test.

## Known Boundaries

- Do not modify `C:\Projects\sps-review` unless the user explicitly changes the
  task.
- Do not run Gemini, OpenAI, or any other paid API without explicit approval.
- Do not commit raw PDFs, bulk extracted text, vector stores, or local secrets.
- Treat cluster labels as navigation aids until manually reviewed against source
  evidence.
