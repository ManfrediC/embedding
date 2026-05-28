# Spec 03: Local Embedding Pilots

## Goal

Generate local embeddings for two pilot sets:

- a 50-paper stratified corpus pilot;
- a 10 to 20 paper intra-paper chunk-role pilot.

No paid API calls are allowed in this step.

## Inputs

- Manifest from Spec 01.
- Paper and chunk text views from Spec 02.

## Local Outputs

- `data/processed/embeddings/<run_id>/paper_embeddings.*`
- `data/processed/embeddings/<run_id>/chunk_embeddings.*`
- `results/embedding_runs/<run_id>/run_manifest.json`
- `results/embedding_runs/<run_id>/summary.md`

## Pilot Sampling

The corpus pilot should be stratified across:

- source category;
- proceedings-ready vs full-text sources;
- count manual-review status;
- case-series split status;
- text-quality/OCR flags where available.

The intra-paper pilot should include:

- reviewed split-auto case series;
- manual-review case series;
- single-case reports;
- observational/group papers;
- at least one lab-heavy/translational paper if available.

## Verification

- Embedding rows match selected paper/chunk rows.
- Model id, dimension, runtime, device, and package versions are logged.
- No full-corpus run occurs unless this spec is explicitly revised.

## Clarifying Questions For Manfredi

1. Which local embedding model should be the first baseline?
   - Default assumption: choose a maintained local sentence/document embedding
     model with no paid API dependency, after checking installed packages.
2. Should the first pilot run on CPU only, or may it use a local GPU if already
   available?
   - Default assumption: CPU/local environment first; no new GPU dependencies.
3. Should the 50-paper pilot include the highest-risk manual-review rows, or
   hold those back for evaluation?
   - Default assumption: include some high-risk rows but keep a few held out.
4. Should embeddings be normalised for cosine similarity?
   - Default assumption: yes, store normalised vectors plus metadata.
5. Preferred storage format for vectors: NumPy, Parquet, SQLite, or another
   local format?
   - Default assumption: NumPy for vectors and CSV/JSON metadata for the pilot.
6. Should Gemini/OpenAI embeddings be considered in this spec?
   - Default assumption: no; they require a separate approved paid/API spec.

## Acceptance Evidence

- Pilot embeddings are generated locally.
- Every embedding links back to paper/chunk metadata.
- Run manifest makes the pilot reproducible.
