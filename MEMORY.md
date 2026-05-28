# MEMORY

Last updated: 2026-05-28.

## Local Facts Checked

- `C:\Projects\embedding` was empty and was not a git repository before this
  scaffold was created.
- `C:\Projects\sps-review` is the upstream SPSD systematic-review repository.
- The stable SPS review join key is `paper_id`, which is the Covidence ID.
- `C:\Projects\sps-review\data\references\paper_artifact_registry.csv` had
  1,039 rows when checked.
- `C:\Projects\sps-review\data\pdf_original` had 1,027 local PDFs when checked.
- `C:\Projects\sps-review\data\extraction_json\text` had 1,027 text JSONs when
  checked.
- `C:\Projects\sps-review\data\extraction_json\text_proceedings_ready` had 238
  proceedings-ready JSONs when checked.
- `C:\Projects\sps-review\doc\plans\embeddings_plan.md` existed but was empty
  when checked.

## External Trigger

- The user supplied the relevant X post text after direct X page content was
  unavailable through browsing.
- The first post emphasises clustering millions of documents in embedding
  space, mass-annotating them, and visualising them quickly and cheaply.
- The second post announces FlashLib from the Flash-KMeans team as a GPU
  library for fast classical ML operators, including KMeans, KNN, HDBSCAN,
  truncated SVD, PCA, exact t-SNE, and MultinomialNB.

## Decisions So Far

- No paid API calls have been approved or run.
- No dependency installation has been attempted.
- This repo should consume SPS review artefacts read-only and keep generated
  experiment outputs local to `C:\Projects\embedding`.
- The first implementation should prioritise document-level and chunk-level
  embedding maps, clustering, mass annotation, and visualisation workflows over
  PDF-native or multimodal embedding experiments.
