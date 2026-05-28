# GOALS

## Primary Goal

Build a reproducible embedding testbed for the SPSD paper library that can
answer: which embedding, clustering, annotation, visualisation, and retrieval
approach best helps map and triage the existing SPS review corpus while
preserving source provenance?

## Acceptance Evidence

The first useful milestone is complete when:

- A local manifest can be generated from the SPS review registries.
- Manifest counts match the expected upstream counts or explain every skip.
- Chunks can be generated from preferred text JSONs with `paper_id`, source
  path, chunk id, text hash, and page/location metadata.
- A baseline local embedding run can index and cluster a small pilot set.
- Cluster assignments, nearest-neighbour outputs, and projection coordinates
  link back to source papers and chunks.
- A judged review set reports cluster usefulness and retrieval recall@k or MRR,
  plus examples of retrieved source evidence.
- No paid API call, secret exposure, or write to the upstream SPS repo occurs
  without explicit approval.

## Non-Goals

- Do not replace the SPS review extraction pipeline.
- Do not infer or publish clinical facts from embeddings alone.
- Do not make the vector index, cluster labels, or projections canonical
  research artefacts until they have a validation and review contract.
- Do not optimise for scale before the small pilot proves value.

## Boundaries

- Upstream source: `C:\Projects\sps-review`.
- Local outputs: `data/`, `results/`, and `qa/` in this repo.
- Secrets: `env/*.env`, ignored by git.
- Cost: zero by default; any paid run needs explicit approval and a cost cap.

## Stop Conditions

Stop and ask before:

- Running paid model/API calls.
- Installing large or GPU-specific dependencies.
- Modifying `C:\Projects\sps-review`.
- Running destructive commands or deleting generated artefacts outside this
  repo.
- Treating retrieval results as clinical evidence without source review.
