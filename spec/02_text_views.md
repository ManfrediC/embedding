# Spec 02: Paper And Chunk Text Views

## Goal

Build local paper-level and chunk-level text views from the manifest, preserving
page/source provenance for every chunk.

## Upstream Inputs

- Manifest from Spec 01.
- Preferred text JSONs under `C:\Projects\sps-review\data\extraction_json\`.
- Optional stage-07 split artefacts when they are reviewed/safe.

## Local Outputs

- `data/interim/paper_text_views.jsonl`
- `data/interim/chunk_text_views.jsonl`
- `results/text_view_summary.md`
- Optional `qa/text_view_sample.csv` for manual inspection.

## Text View Contract

Paper-level rows should include:

- `paper_id`
- source text path
- source kind
- text hash
- page count
- character/token estimates
- source category and review flags

Chunk-level rows should include:

- `chunk_id`
- `paper_id`
- source text path
- source kind
- page start and page end
- chunk order
- text hash
- text preview or full text according to the agreed storage policy
- optional section heading and lexical anchors

## Verification

- Every chunk maps to one manifest row.
- Every chunk has source path, page/location metadata, and hash.
- Empty-text and tiny-text cases are reported explicitly.
- A sample of chunks is manually inspectable without opening PDFs.

## Clarifying Questions For Manfredi

1. Should chunk JSONL store full chunk text, or only hashes/previews plus source
   pointers?
   - Default assumption: store full chunk text in ignored `data/interim/`, but
     keep tracked review samples to previews only.
2. Preferred first chunk size?
   - Default assumption: 500 to 900 tokens with 10 to 15 percent overlap.
3. Should page boundaries be hard boundaries, or may chunks cross pages when
   paragraphs continue?
   - Default assumption: preserve page boundaries where practical, allow
     crossing only with explicit `page_start/page_end`.
4. Should references sections be removed, flagged, or embedded as their own
   role?
   - Default assumption: flag likely references chunks and exclude them from
     first-pass embeddings.
5. Should stage-07 split artefacts be used in the first pass?
   - Default assumption: use only reviewed/safe split artefacts; otherwise keep
     paper-level chunks and flag split manual-review rows.
6. Do you want section labels such as introduction/methods/case/discussion in
   the first version?
   - Default assumption: include heuristic section labels when easy, but do not
     block the pilot on perfect section parsing.

## Acceptance Evidence

- Chunk generation produces a count summary by source category and source kind.
- 100 percent of chunks have traceability fields.
- Manual sample confirms chunks are readable and not dominated by boilerplate.
