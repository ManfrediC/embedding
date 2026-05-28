# spec

Implementation specs for the agreed embedding pilot order in
`doc/sps_embedding_application_plan.md`, section 12.

Each spec contains:

- goal and non-goals;
- upstream SPS review inputs;
- local outputs;
- verification and acceptance evidence;
- clarifying questions for Manfredi before coding.

Do not treat unanswered questions as approval for paid model calls, GPU
dependency installation, upstream `sps-review` edits, or broad full-corpus runs.
When a question is unanswered but a safe default exists, the spec states the
default assumption explicitly.

## Step Specs

1. `01_manifest.md`: build a local manifest from SPS review registries.
2. `02_text_views.md`: build paper-level and chunk-level text views.
3. `03_embedding_pilots.md`: generate local embeddings for the pilot sets.
4. `04_maps_neighbours_roles.md`: produce neighbours, clusters, projections,
   and intra-paper chunk roles.
5. `05_review_packs.md`: create human review packs.
6. `06_human_judgement.md`: have the user judge whether the packs save time.
7. `07_scale_or_flashlib.md`: decide whether to scale or use FlashLib/GPU.
