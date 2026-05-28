# Spec 04: Maps, Neighbours, Clusters, And Chunk Roles

## Goal

Use pilot embeddings to produce:

- KNN neighbours;
- simple clusters;
- 2D projection coordinates;
- advisory intra-paper chunk roles.

## Inputs

- Embedding outputs from Spec 03.
- Manifest metadata from Spec 01.
- Chunk metadata from Spec 02.

## Local Outputs

- `results/maps/<run_id>/paper_neighbours.csv`
- `results/maps/<run_id>/chunk_neighbours.csv`
- `results/maps/<run_id>/paper_clusters.csv`
- `results/maps/<run_id>/paper_projection.csv`
- `results/maps/<run_id>/chunk_role_candidates.csv`
- `results/maps/<run_id>/summary.md`

## Candidate Methods

- KNN over paper and chunk vectors.
- KMeans for simple genre/source-type structure.
- HDBSCAN only if dependencies are already available or explicitly approved.
- PCA or truncated SVD for first projection.
- UMAP/t-SNE only after the simple projection is useful.
- Intra-paper chunk role scoring that combines embeddings, document order,
  lexical anchors, headings, and patient labels.

## Verification

- Every neighbour result links to source and target `paper_id`.
- Cluster rows include deterministic annotations from existing metadata.
- Projection rows have stable IDs and no missing coordinates.
- Chunk-role rows are advisory and include ambiguity flags.

## Clarifying Questions For Manfredi

1. Which neighbour depth should be default: top 5, top 10, or top 20?
   - Default assumption: top 10.
2. Which first clustering method should be used?
   - Default assumption: KMeans with several candidate `k` values, plus
     metadata enrichment rather than claiming a true taxonomy.
3. Should source category be used only for evaluation/annotation, or also as a
   supervised signal?
   - Default assumption: annotation/evaluation first; no supervised training
     until the unsupervised baseline is inspected.
4. Which chunk-role taxonomy should the first version use?
   - Default assumption: `background`, `shared_context`,
     `unit_candidate`, `aggregate_context`, `table_or_case_summary`,
     `methods_quality`, `ignore_reference`, `uncertain`.
5. Should projections be optimised for interpretability or speed?
   - Default assumption: speed and determinism first.
6. Do you want FlashLib considered in this step?
   - Default assumption: not yet; use ordinary local CPU tooling for the pilot.

## Acceptance Evidence

- Outputs can be joined back to manifest and chunk views.
- A small sample of neighbours/clusters/roles is reviewable in plain CSV.
- No advisory label is presented as a reviewed fact.
