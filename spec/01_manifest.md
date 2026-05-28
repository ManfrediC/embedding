# Spec 01: Manifest Builder

## Goal

Build a local manifest that joins the SPS review registries into one
experiment-ready table while preserving `paper_id` as the stable key and
keeping `C:\Projects\sps-review` read-only.

## Upstream Inputs

- `C:\Projects\sps-review\data\references\paper_artifact_registry.csv`
- `C:\Projects\sps-review\data\references\source_categorisation_registry.csv`
- `C:\Projects\sps-review\data\references\source_sps_case_count_registry.csv`
- `C:\Projects\sps-review\data\references\case_series_split_registry.csv`
- `C:\Projects\sps-review\data\references\paper_revisit_registry.csv`
- Optional: `text_proceedings_ready_registry.csv` for stage-05 detail.

## Local Outputs

- `data/interim/sps_manifest.csv` or `data/interim/sps_manifest.jsonl`
- `results/manifest_summary.md`
- `results/manifest_summary.json`

Generated outputs stay ignored by git unless a later decision promotes a small
sample fixture.

## Required Fields

- `paper_id`
- reference metadata: title, authors, year, journal, DOI where present
- PDF presence and relative path
- preferred text path and preferred text source
- source category, subtype, confidence, manual-review flags
- count eligibility, likely count, count manual-review flag
- case-series split status and split path when present
- revisit issue counts and highest severity
- skip reason when a row cannot enter downstream embedding steps

## Verification

- Count manifest rows against `paper_artifact_registry.csv`.
- Count included and skipped rows by skip reason.
- Confirm every included row has a preferred text path that exists.
- Confirm no upstream `sps-review` files changed.

## Clarifying Questions For Manfredi

1. Should the manifest include all 1,039 registry rows, including rows without
   local PDFs/text, or only rows eligible for embedding?
   - Default assumption: include all rows and mark missing text/PDF rows as
     skipped.
2. Which output format do you prefer for the first manifest: CSV, JSONL, or
   both?
   - Default assumption: CSV for review plus JSON summary.
3. Should the manifest resolve manual overrides into final columns only, or keep
   both raw and resolved stage fields?
   - Default assumption: keep both when practical, with resolved columns used
     for decisions.
4. Which revisit issues should make a row ineligible rather than just flagged?
   - Default assumption: wrong-source and missing-text rows are ineligible;
     manual-review rows remain eligible but flagged.
5. Should the first manifest be regenerated every run, or should it be versioned
   by run id?
   - Default assumption: deterministic overwrite in `data/interim/`, with a
     timestamped summary under `results/`.

## Acceptance Evidence

- Manifest command runs without paid calls.
- Summary explains all skips.
- Every downstream candidate row has `paper_id`, preferred text path, and source
  provenance.
