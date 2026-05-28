# embedding

Experimental embedding and retrieval workspace for the SPSD paper library in
`C:\Projects\sps-review`.

The first goal is to build a small, reproducible pilot that reads the SPS review
registries and extracted text JSONs, creates provenance-preserving chunks, tests
one or more embedding models, clusters and visualises the embedding space,
mass-annotates clusters with existing metadata, and evaluates retrieval quality
against a small judged query set.

## Layout

- `AGENTS.md`: repo-specific operating rules.
- `GOALS.md`: project goals and acceptance evidence.
- `MEMORY.md`: durable facts discovered so far.
- `CONTINUITY.md`: current state and next steps.
- `doc/`: plans and design notes.
- `src/embedding_sps/`: future reusable experiment code.
- `tests/`: future tests and fixtures.
- `data/`: generated local manifests, chunks, embeddings, and indexes.
- `results/`: run outputs and metrics.
- `spec/`: step-by-step implementation specs and clarifying questions.
- `qa/`: sampled review material.
- `env/`: local untracked environment files.

## Upstream Data

Use `C:\Projects\sps-review\data\references\paper_artifact_registry.csv` as the
first source of truth. The SPS review repo owns the canonical PDFs, extracted
text, proceedings-ready text, source categorisation, case counts, and split
registries.

## Current Plan

See `doc/sps_embedding_application_plan.md`.
