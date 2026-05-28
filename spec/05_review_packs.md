# Spec 05: Review Packs

## Goal

Create human-review packs from the pilot outputs so Manfredi can judge whether
the embedding workflow saves review time.

## Review Packs

1. `qa/source_category_embedding_audit.csv`
   - source-category/genre disagreement candidates.
2. `qa/proceedings_qc_embedding_audit.csv`
   - proceedings QC neighbours and suspicious trim candidates.
3. `qa/case_count_embedding_audit.csv`
   - case-count manual-review neighbours and evidence-window suggestions.
4. `qa/intra_paper_chunk_role_review.csv`
   - patient/shared-context chunk-role candidates.

## Common Columns

- `run_id`
- `paper_id`
- title
- source category and relevant review flags
- issue type or pack type
- candidate/advisory label
- nearest reviewed examples
- source text path
- chunk id or page range when applicable
- text preview
- reason for inclusion
- reviewer decision
- reviewer notes

## Verification

- Every row links back to a source paper/chunk.
- Review packs are small enough for one sitting.
- Generated rows do not modify upstream registries.

## Clarifying Questions For Manfredi

1. Preferred pack format: CSV only, Markdown summaries, or a small local review
   UI later?
   - Default assumption: CSV first.
2. How many rows should each first pack contain?
   - Default assumption: 20 to 30 rows per pack.
3. Which pack should be prioritised first if time is tight?
   - Default assumption: intra-paper chunk roles and source-category/genre
     audit first, because they unblock later extraction design.
4. What reviewer decisions should be available?
   - Default assumption: `useful`, `not_useful`, `wrong`, `uncertain`,
     `needs_source_review`.
5. Should text previews include enough text for fast triage, or only minimal
   snippets to avoid local duplication?
   - Default assumption: concise previews in QA packs, full source in ignored
     chunk views.

## Acceptance Evidence

- Four review packs are generated from one pilot run.
- Each pack contains enough context for a human decision.
- No pack claims to resolve a canonical SPS review issue automatically.
