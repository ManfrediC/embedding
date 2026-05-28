# SPSD Paper Embedding Application Plan

Last updated: 2026-05-28.

## Context

This plan describes how to test embeddings on the stiff person spectrum
disorder paper library in `C:\Projects\sps-review\data\pdf_original` while
using the SPS review repo's existing registries and extracted text as the
authoritative context.

The user-supplied posts frame the experiment as a fast embedding-space document
map:

- Cluster large document sets in embedding space, mass-annotate them, and
  visualise them quickly and cheaply.
- Use FlashLib, from the Flash-KMeans team, for fast classical ML operators:
  KMeans, KNN, HDBSCAN, truncated SVD, PCA, exact t-SNE, and MultinomialNB.

For this SPSD corpus, the sensible interpretation is: build a
provenance-preserving embedding map over papers and chunks, cluster it, label
clusters with source metadata and sampled evidence, visualise the corpus, and
use nearest-neighbour search to find related papers or review candidates.
PDF-native or multimodal embeddings can be a later optional branch, but they
are not the first path.

## Corpus State Observed

Observed from `C:\Projects\sps-review` on 2026-05-28:

- `paper_artifact_registry.csv`: 1,039 rows.
- Local PDFs in `data/pdf_original`: 1,027.
- Canonical text JSONs in `data/extraction_json/text`: 1,027.
- Proceedings-ready JSONs in `data/extraction_json/text_proceedings_ready`: 238.
- Source-categorised rows: 1,027.
- Source categories:
  - `single_case_report`: 476.
  - `conference_abstract`: 213.
  - `observational_group_study`: 91.
  - `case_series_or_multi_case`: 89.
  - `unclear_manual_review`: 87.
  - `lab_heavy_clinical_or_translational`: 45.
  - `interventional_study`: 14.
  - `review_article`: 12.
- Count-eligible rows in the stage-06 registry: 1,012.
- Stage-06 rows requiring count manual review: 234.
- Case-series split registry rows: 116, with 37 `split_auto` and 79
  `manual_review_required`.

The existing SPS review plan at
`C:\Projects\sps-review\doc\plans\embeddings_plan.md` was empty when checked.

## Product Survival Brief

- Primary workflow: map, cluster, annotate, visualise, and search SPSD papers
  and passages using embeddings while preserving evidence traceability.
- Core data object and owner: local embedding chunks owned by this experiment
  repo; source documents and canonical registries remain owned by
  `C:\Projects\sps-review`.
- Roles and permissions affected: local single-user research workflow only.
  There is no auth surface in this iteration.
- Lifecycle states: manifest generated, chunks generated, embeddings generated,
  index built, retrieval evaluated, run accepted/rejected.
- External services: none by default. Gemini/OpenAI or other paid APIs require
  explicit approval, cost estimate, and run manifest.
- Admin/support need: enough run metadata to identify which input registry,
  model, chunking policy, and index produced a result.
- Observability need: per-run logs, counts, skips, model id, embedding
  dimensions, query metrics, and sampled retrieval reviews.
- Non-goals: no production app, no canonical review output, no clinical claims
  from embeddings alone, no upstream SPS repo writes.

## Recommended Architecture

### 1. Ingestion Manifest

Create a local manifest from SPS registries, not from raw filename parsing.

Primary inputs:

- `data/references/paper_artifact_registry.csv`.
- `data/references/source_categorisation_registry.csv`.
- `data/references/source_sps_case_count_registry.csv`.
- `data/references/case_series_split_registry.csv`.
- `data/references/paper_revisit_registry.csv`.

Manifest fields should include:

- `paper_id`, title, authors, year, journal, DOI.
- PDF presence and PDF relative path.
- Preferred text path and source kind.
- Source category, subtype, and manual-review flags.
- Case-count eligibility and manual-review flag.
- Case-series split status and split text path when available.
- Revisit status or unresolved issue flag.

Decision rule for preferred text:

1. If a reviewed/safe case-series split exists with `split_status=split_auto`
   and a split text path, optionally create unit-level chunks from that split
   artefact.
2. Else if `text_proceedings_ready_present=true`, use
   `text_proceedings_ready_path`.
3. Else if `text_json_present=true`, use `text_json_path`.
4. Else skip with an explicit reason.

### 2. Chunk Builder

Read SPS text JSONs with page-level provenance. A checked sample showed the
text JSON structure has top-level metadata plus `pages`, where each page has
`page_index` and `text`.

Chunking policy for the first pilot:

- Keep chunks small enough for text embedding models, for example 500 to 900
  tokens with 10 to 15 percent overlap.
- Do not split inside obvious headings when avoidable.
- Preserve page boundaries where possible.
- Store no more text than needed in tracked review artefacts.
- Add a stable `chunk_id`, for example
  `{paper_id}:{source_kind}:p{page_start}-p{page_end}:c{ordinal}`.

Every chunk must carry:

- `paper_id`.
- `chunk_id`.
- `source_text_path`.
- `source_kind`.
- `page_start` and `page_end` when known.
- `text_sha256`.
- model-independent metadata needed for filtering and evaluation.

### 3. Baseline Embedding Map

Start with local text embeddings at two levels:

- document-level vectors for fast corpus mapping and clustering.
- chunk-level vectors for evidence retrieval within papers.

Minimum first run:

- One local sentence/document embedding model.
- A paper-level embedding table with one row per included `paper_id`.
- A chunk-level embedding table or index for evidence lookup.
- Projection outputs for PCA, truncated SVD, UMAP, or t-SNE-style views.
- Cluster assignments and nearest-neighbour links written under `results/`.
- Sampled cluster/retrieval review rows written under `qa/`.

A local baseline matters because it proves the workflow and gives a zero-cost
comparator before trying GPU acceleration or paid services.

### 4. Clustering, Annotation, And Visualisation

The core experiment should test whether embedding-space structure helps the SPS
review work.

Candidate analyses:

- KMeans clusters over document vectors, annotated by dominant source category,
  year range, paper titles, and sampled terms.
- HDBSCAN clusters to find dense themes while leaving outliers explicit.
- KNN graphs to find near-duplicate papers, related case reports, or papers
  with similar clinical phenotypes.
- PCA or truncated SVD for cheap global projections.
- UMAP or t-SNE for human-review visual maps if dependencies are available.
- MultinomialNB or a simple linear classifier as a baseline for predicting
  source category from vectors or sparse text features.

Mass annotation should be deterministic first:

- cluster size.
- dominant source categories.
- count-review/manual-review rate.
- proceedings proportion.
- top titles/authors/years.
- representative chunks selected by centrality or nearest to centroid.

LLM-generated cluster labels can be added later only after approval if a paid
model is involved. They must be stored as annotations, not facts.

### 5. Optional FlashLib / GPU Analysis

FlashLib is not an embedding model. It is relevant after embeddings exist.

Potential uses:

- KNN for fast neighbour search over large chunk sets.
- KMeans or HDBSCAN for topic/phenotype clusters.
- PCA, truncated SVD, UMAP, or t-SNE for reviewable visual maps.
- MultinomialNB as a fast supervised baseline for source categories.

Decision rule:

- Use ordinary local CPU tooling first on the 1,027-paper corpus.
- Try FlashLib only if GPU dependencies are available and the chunk count or
  runtime makes CPU tooling inconvenient.
- Keep any GPU benchmark separate from retrieval-quality claims.

### 6. Optional Gemini Embedding 2 Pilot

Only after explicit approval:

- Estimate token/document cost before running.
- Start with a small stratified sample, not the full 1,027-PDF corpus.
- Compare text-only chunk embeddings against PDF/document-native embeddings
  where the official API limits permit.
- Treat any PDF-native result as a retrieval signal, not extracted clinical
  data.
- Log model id, dimensions, truncation behaviour, skipped files, errors, and
  cost.

Gemini Embedding 2 is most interesting here if it can improve retrieval from
visually awkward PDFs, tables, figures, scanned pages, or proceedings material.
If the task is only text chunk search, a local or cheaper text embedder may be
the better default.

## Evaluation Plan

Evaluate both retrieval quality and map usefulness before comparing models.

Map and clustering evaluation:

- Agreement between clusters and known source categories without forcing source
  category to be the only good structure.
- Enrichment of manual-review flags, proceedings abstracts, reviews,
  interventional studies, and translational papers in specific clusters.
- Human review of representative papers per cluster.
- Stability across random seeds or modest changes in chunking/model choice.
- Outlier list usefulness: duplicate sources, wrong-source candidates, noisy
  OCR, or papers needing review.

Build a small judged query set before comparing retrieval models.

Recommended query classes:

- Known-paper lookup: title fragments, author/year hints, and distinctive paper
  phrases.
- Concept retrieval: clinically meaningful SPSD concepts chosen by the user,
  with expected papers judged from retrieved source evidence.
- Source-category retrieval: queries expected to retrieve single case reports,
  conference abstracts, reviews, interventional studies, and translational
  papers.
- Proceedings localisation: queries that should retrieve the relevant abstract
  rather than the whole proceedings supplement.
- Manual-review triage: queries that may help inspect rows currently marked for
  source, count, or split review without automatically resolving them.

Metrics:

- cluster purity/enrichment for source category and review flags.
- adjusted Rand index or normalized mutual information against source category
  as a descriptive check, not the sole target.
- silhouette or density diagnostics where appropriate.
- nearest-neighbour review yield for duplicate or related-paper discovery.
- recall@5 and recall@10 for known-paper queries.
- MRR for known-paper and known-concept queries.
- precision@10 from manual review for exploratory clinical queries.
- source-path traceability rate; target 100 percent.
- skipped input count with reasons.
- duplicate or near-duplicate retrieval rate.

The first useful acceptance bar is not "best model". It is: the whole path from
registry row to chunk to retrieval result is reproducible, traceable, and good
enough to reveal whether a broader model comparison is worth doing.

## Suggested Milestones

### M0: Scaffold and Plan

Status: complete in this repo.

Evidence:

- Repo layout exists.
- Operating docs exist.
- This plan exists.

### M1: Manifest Builder

Deliverable:

- `data/interim/sps_manifest.csv` or JSONL.
- A summary report in `results/`.

Checks:

- Counts match the upstream registry counts or explain all skips.
- No upstream files are modified.

### M2: Chunk Builder

Deliverable:

- `data/interim/chunks.jsonl`.
- Chunking summary by source category and source kind.

Checks:

- 100 percent of chunks have `paper_id`, source path, location metadata, and
  `text_sha256`.
- A small sample is manually inspected in `qa/`.

### M3: Local Baseline Map

Deliverable:

- Paper-level and chunk-level local embeddings under `data/processed/`.
- Local vector index under `data/processed/`.
- Projection, cluster, and nearest-neighbour outputs under `results/`.

Checks:

- Every vector row links to `paper_id` and source metadata.
- Clusters and nearest-neighbour outputs include source paths and chunk ids
  where applicable.
- Runtime and storage footprint are recorded.

### M4: Cluster And Retrieval Review

Deliverable:

- `qa/cluster_review_sample.csv`.
- `qa/retrieval_eval_queries.csv`.
- Metrics report describing cluster structure, map usefulness, and retrieval
  baseline behaviour.

Checks:

- Cluster annotations are deterministic or explicitly marked as model-generated.
- Representative papers are evidence-backed.
- Query expectations are evidence-backed.
- Ambiguous queries are marked ambiguous rather than forced.

### M5: Optional Multimodal/API or GPU Experiment

Deliverable:

- Separate approved run manifest and metrics.

Checks:

- Explicit approval was obtained before paid/API or large GPU setup work.
- Cost, skips, truncation, and model settings are logged.
- Results are compared against the local baseline.

## Premortem

Premortem frame: it is 6 months from now and this embedding experiment failed.
The likely causes and mitigations are:

1. The project embedded the wrong text layer.
   - Failure story: proceedings supplements and multi-case papers were indexed
     as whole documents, so retrieval surfaced noisy context instead of the
     relevant abstract or case unit.
   - Assumption: raw extracted text was close enough.
   - Warning signs: many retrieved chunks mention unrelated abstracts; searches
     over conference titles return broad supplement pages.
   - Mitigation: use proceedings-ready text first, respect split-auto case
     series outputs, and flag manual-review rows.

2. The pilot looked impressive but was not measurable.
   - Failure story: demos found plausible passages, but there was no judged
     query set, cluster review sample, stability check, or way to compare
     maps.
   - Assumption: subjective map quality would be obvious.
   - Warning signs: screenshots and anecdotes replace metrics.
   - Mitigation: build a cluster review sample and query set before broad
     model comparison.

3. Chunking destroyed the evidence trail.
   - Failure story: results returned relevant text but could not be traced back
     to page, paper, source file, or processing layer.
   - Assumption: text snippets would be enough.
   - Warning signs: chunks without `paper_id`, duplicate chunk ids, or missing
     page metadata.
   - Mitigation: enforce chunk schema and tests before embedding.

4. Clusters were over-labelled.
   - Failure story: a cluster got a confident clinical label from a few
     representative papers, then that label was treated as true for every paper
     in the cluster.
   - Assumption: embedding neighbours share the same clinical facts.
   - Warning signs: cluster labels appear in reports without representative
     evidence or uncertainty.
   - Mitigation: label clusters as navigation aids, keep representative
     evidence attached, and never assign clinical facts to papers by cluster
     membership alone.

5. OCR and PDF quality were treated as model problems.
   - Failure story: retrieval missed key papers because source text was noisy,
     but the error was blamed on the embedding model.
   - Assumption: all 1,027 text JSONs were equally reliable.
   - Warning signs: high retrieval failure among OCR-heavy or flagged papers.
   - Mitigation: include extraction-quality flags in metadata and stratify
     evaluation by OCR/text-quality status.

6. Embeddings were over-interpreted as clinical evidence.
   - Failure story: clusters or neighbours were described as scientific facts
     without source review.
   - Assumption: semantic closeness equals evidence.
   - Warning signs: reports make clinical claims without cited chunks.
   - Mitigation: retrieval can suggest evidence to inspect; it cannot publish
     clinical conclusions without source verification.

7. API costs or limits distorted the design.
   - Failure story: a full-corpus multimodal run was started before checking
     limits and cost, then failed or became too expensive to repeat.
   - Assumption: PDF-native embeddings would be cheap enough for all PDFs.
   - Warning signs: no cost estimate, no pilot sample, no skipped-file report.
   - Mitigation: local baseline first; paid/API runs require approval, sample,
     estimate, and cap.

## Safeguard Gates

- Product/architecture: passed for planning; no implementation yet.
- Security: no secrets written; `env/*.env` ignored.
- Data/performance: generated bulk outputs ignored by default; no vectors
  created yet.
- External integrations: not active; paid/API calls blocked pending approval.
- Operations: future runs must log counts, skips, model id, and metrics.
- Verification: scaffold verified by filesystem inspection only; no code tests
  exist yet.

## Source Links

- User-supplied X link:
  `https://x.com/neural_avb/status/2059519009079628122?s=20`
- User-supplied X link:
  `https://x.com/Andy_ShuoYang/status/2059441289763139677?s=20`
- Gemini Embedding 2:
  `https://deepmind.google/models/gemini/embedding/`
- Gemini Embedding 2 paper page:
  `https://huggingface.co/papers/2605.27295`
- FlashLib project:
  `https://flashml-org.github.io/`
- FlashLib repository:
  `https://github.com/FlashML-org/flashlib`

## Ideas For Supporting `sps-review` With Embeddings

This section is grounded in the current `sps-review` project state rather than
in embeddings as a generic RAG feature.

The upstream project goal is not just "search papers". It is to turn an SPSD
systematic-review library into reproducible, evidence-linked review artefacts:
PDF linkage, extracted text, source routing, proceedings-localised text,
extractable SPSD case counts, attribution-safe case-series units, then
downstream individual/group extraction and quality assessment. As of this
planning pass, stages 01-07 are the mature core; LangExtract, summaries, quality
assessment, and the 83-column master-table work are still preliminary. The
current revisit registry shows the largest live queues are case-count review,
proceedings trim/QC, and case-series split review.

Embeddings can help most if they are treated as a navigation and triage layer
over those existing contracts. They should not overwrite stage decisions or
infer clinical facts by similarity alone.

### 1. A Corpus Map For Review Steering

Build a paper-level embedding map with one vector per `paper_id`, using the
same preferred-text rule as downstream stages:

1. reviewed/safe case-series split artefact when appropriate;
2. proceedings-ready text when present;
3. otherwise canonical extracted text;
4. skip with a reason if no usable text exists.

Use source category, proceedings status, count-review flags, case-series split
status, OCR/text-quality flags, year, journal, and revisit-stage labels as
overlay metadata. The first visualisation should answer practical questions:

- Are `unclear_manual_review` papers isolated, or do they sit inside obvious
  known-category clusters?
- Are proceedings-like papers separated from full case reports after stage 05?
- Do count-review rows concentrate in a few textual patterns?
- Are there outlier papers whose nearest neighbours suggest wrong-source,
  duplicate, OCR, or routing problems?

This is the most direct FlashLib-shaped use case: KMeans/HDBSCAN for structure,
KNN for neighbours, PCA/SVD/t-SNE/UMAP for reviewable maps, and deterministic
cluster annotations from existing registries.

### 2. Revisit Queue Prioritisation

Use embeddings to order human review work, not to close it automatically.

For each revisit queue, compute nearest neighbours to already-settled papers
and produce a review sheet with:

- target paper and issue type;
- nearest reviewed neighbours;
- neighbour source categories/counts/split statuses;
- representative snippets and source paths;
- a suggested review priority, with a reason.

High-value queues:

- 234 stage-06 case-count review rows.
- 173 stage-05 proceedings trim rows.
- 133 stage-05b proceedings QC follow-up rows.
- 79 stage-07 case-series split review rows.
- 20 source-categorisation manual-review rows.

The decision rule should remain conservative: embeddings can say "this looks
like these reviewed examples", never "therefore the count/category is X".

### 3. Proceedings Boundary And QC Support

Proceedings are a major source of noise because full supplements contain many
unrelated abstracts. Embeddings could support stage 05 in three ways:

- Build abstract/block embeddings within proceedings PDFs and retrieve the
  block nearest to the target paper title, authors, and Covidence metadata.
- Compare the accepted proceedings-ready text against the whole proceedings PDF
  to detect suspiciously broad or off-topic trims.
- Cluster unresolved proceedings QC cases by failure mode: wrong abstract,
  multiple similar titles, title absent, author mismatch, supplement index
  issue, or OCR noise.

This would complement the existing title/author/boundary logic. It should feed
review packs under `qa/`, not silently rewrite `text_proceedings_ready/`.

### 4. Genre And Source-Type Assignment

The source-category registry is central because it controls count eligibility,
LangExtract mode, case-series splitting, and quality workflow. Embeddings can
make this layer easier to audit and, eventually, easier to assign for new or
uncertain papers.

The useful framing is "genre" rather than only topic. The model should help
distinguish the role a paper plays in the review:

- single case report;
- case series or multi-case paper;
- observational group study;
- interventional study;
- conference abstract or proceedings item;
- review article;
- lab-heavy clinical/translational paper with little extractable patient-level
  data;
- non-clinical/basic-science or methods-heavy paper;
- unclear/manual-review item.

Potential workflow:

- Build document-level and abstract/opening-section embeddings for every
  paper, because genre signals are often strongest in titles, abstracts,
  methods, and headings.
- Build source-type prototypes from reviewed/high-confidence rows in
  `source_categorisation_registry.csv` and manual-review overrides.
- Train a simple classifier over embeddings and sparse lexical features as a
  weak advisory model, not as the source of truth.
- For each uncertain paper, report the top candidate genres, nearest reviewed
  examples, and why the assignment is ambiguous.
- Add an explicit abstention class. If the nearest neighbours are mixed or the
  paper lies near a boundary, route it to manual review rather than forcing a
  type.
- Treat `lab_heavy_clinical_or_translational` as a first-class target because
  those papers can mention SPSD patients while still containing little
  extractable clinical case data.
- Surface papers whose embedding-neighbour genre distribution disagrees with
  their current `source_category`.
- Find category boundary cases, especially between `single_case_report`,
  `case_series_or_multi_case`, `observational_group_study`,
  `conference_abstract`, and lab-heavy/translational papers.

Useful output: a `qa/source_category_embedding_audit.csv` with target category,
candidate genre probabilities or ranks, nearest-neighbour category mix,
abstention/disagreement flags, and evidence snippets.

Acceptance check for this idea should be measured against reviewed rows:

- top-1 and top-3 genre agreement on reviewed source-category examples;
- abstention rate on true boundary cases;
- zero silent high-confidence assignments for papers that reviewed routing says
  are wrong-source, unclear, or manual-review;
- separate reporting for lab-heavy/translational papers, because they are a
  known downstream hazard for over-extraction.

### 5. Stage-06 Case Count Assistance

Stage 06 is already designed around evidence-bearing candidate packages and
manual escalation. Embeddings could support that design without replacing it:

- Retrieve similar reviewed papers for a target count-review row.
- Retrieve within-paper windows similar to known count-evidence phrases:
  "we report a case", "two patients", "series of", "n =",
  "patients with SPS", "controls", "literature review", and diagnosis-specific
  subgroup wording.
- Cluster false-positive numeric contexts: ages, titres, years, scale scores,
  percentages, controls, sample counts, and literature totals.
- Add a neighbour-derived advisory field to candidate packages:
  "similar reviewed papers resolved as single-case default" or
  "similar rows were manual-review because subgroup denominator was unclear".

This could reduce reviewer time by presenting better evidence windows and known
failure analogues. It must not auto-accept counts from neighbouring papers.

### 6. Case-Series Split Support

Stage 07 needs attribution-safe unit boundaries. Embeddings can help find
regularities in case-series structure:

- Embed paragraphs/sections within case-series papers and cluster paragraphs
  that look like individual case vignettes, shared methods, shared discussion,
  tables, or aggregate summaries.
- For the 79 manual-review split rows, retrieve nearest split-auto papers and
  show their unit boundary patterns.
- Detect papers where patient labels, table rows, and narrative sections do not
  agree, which should stay in manual review.
- Support a visual "case boundary candidate" sheet with candidate units,
  source pages, shared-context blocks, and similar reviewed examples.

The output should support the existing stage-07 review workflow and respect the
same rule: attribution ambiguity escalates to review.

### 7. Intra-Paper Chunk Typing

A particularly useful within-paper idea is to embed text chunks from one paper
and separate them by evidence role:

- general/background material, usually introduction or discussion;
- methods or shared cohort context;
- patient-1-specific vignette;
- patient-2-specific vignette;
- other patient-specific vignettes;
- table rows or compact case summaries;
- aggregate/multiple-patient findings;
- references, boilerplate, and irrelevant text.

This would support the project more directly than a generic paper-level map.
The goal is not just to find similar papers; it is to identify which parts of a
paper should be read together for extraction.

Recommended design:

- Chunk each paper with page and section provenance, preserving adjacency.
- Build embeddings for chunks and also keep lexical anchors such as
  `Case 1`, `Patient 2`, `Subject A`, `Table 1`, and `patients`.
- Use reviewed stage-07 split-auto papers and single-case gold material as
  examples of known chunk roles.
- Combine semantic similarity with document order. Adjacent chunks with similar
  role and consistent patient labels should merge; semantically similar chunks
  with different patient labels should stay separate.
- Represent output as advisory chunk-role spans, for example:
  `shared_context`, `unit_candidate:p1`, `unit_candidate:p2`,
  `aggregate_context`, `background`, `ignore_reference`.

This could help in several SPS review tasks:

- Stage 07: propose attribution-safe unit boundaries before human review.
- Stage 06: distinguish a true case count from background literature counts or
  aggregate cohort denominators.
- LangExtract: feed patient-specific chunks to individual extraction and shared
  context chunks as linked context, instead of sending the whole paper.
- 83-column extraction: retrieve field evidence from the right patient-specific
  span rather than from the introduction or another patient's vignette.
- Quality assessment: keep design/methods chunks separate from case narratives.

The review artefact should be a small, readable table such as
`qa/intra_paper_chunk_role_review.csv` with:

- `paper_id`;
- `chunk_id`;
- page range;
- proposed role;
- patient/unit label if any;
- nearest reviewed role examples;
- source text preview;
- confidence and ambiguity flags.

Important guardrail: embeddings should not assign a clinical fact to patient 1
because the chunk is near another patient-1 chunk. Patient attribution must come
from local labels, ordering, table structure, or reviewed context. If the role
or patient label is ambiguous, the chunk should be marked for review.

This is an ideal early pilot because it can be evaluated against existing
stage-07 reviewed material and does not require paid API calls. A first pass
could use 10 to 20 papers: several split-auto case series, several manual-review
case series, a few single-case reports, and a few observational/group papers.

### 8. LangExtract Example And Prompt Support

The LangExtract example plan already says manually extracted datasheet rows
should be paired with source quotes and reviewed before becoming examples.
Embeddings can accelerate the quote-linking and diversity-selection parts:

- For each manual datasheet value, retrieve candidate quote spans from the
  corresponding extracted text.
- Find semantically similar accepted examples for each target field, so new
  examples cover language variation rather than duplicating easy cases.
- Select few-shot examples by diversity across phenotype, treatment, outcome,
  antibody, publication type, and OCR quality.
- Build held-out evaluation sets by finding near-neighbour papers to accepted
  examples, then withholding them to test generalisation.

This is likely one of the highest-leverage uses because the current prompt
examples are sparse while the manual datasheet exports are rich.

### 9. 83-Column Master Table Evidence Retrieval

The 83-column master-table plan requires every filled value to have supporting
evidence metadata. Embeddings can become the field-level evidence candidate
generator:

- Build query templates from each dictionary field's definition and entry
  guidance.
- Retrieve top candidate chunks per field per paper.
- Feed only those chunks into a deterministic/LLM extractor for that field.
- Store negative evidence explicitly when no suitable chunk is found.
- Compare field-specific retrieval coverage against manual rows before any
  broad extraction run.

This converts a huge long-document extraction problem into many small
evidence-retrieval problems. The risk is missing evidence through poor queries,
so the retrieval layer needs recall-oriented evaluation against the manual
datasheet examples.

### 10. Duplicate, Wrong-Source, And OCR QC

Some review failures are not semantic extraction failures; they are source
quality failures. Embeddings can help flag them:

- Near-duplicate paper vectors may reveal duplicate PDFs, repeated abstracts,
  or multiple Covidence records for the same source.
- A PDF/text embedding far from its title/metadata embedding may suggest wrong
  PDF attachment or bad extraction.
- Chunks dominated by references, headers, unrelated abstracts, or OCR artefacts
  can cluster together and become a text-quality review queue.
- Outlier detection can identify local PDFs whose content does not resemble the
  SPSD corpus despite matching filenames.

This should feed `paper_revisit_registry` candidates only after manual review;
do not mutate upstream source linkage automatically.

### 11. Phenotype And Treatment Landscape Exploration

Once the canonical extraction path is stable, embeddings can support exploratory
scientific orientation:

- cluster papers by phenotype language: classic SPS, stiff-limb, PERM,
  cerebellar/epilepsy overlap, paraneoplastic/amphiphysin, glycine receptor,
  GAD65, paediatric, immune-checkpoint-inhibitor-associated;
- map treatment language: benzodiazepines, baclofen, IVIG, plasma exchange,
  rituximab, steroids, immunosuppressants, symptomatic response;
- find under-reviewed islands of the literature;
- identify papers likely to be useful background/context but not extractable
  case data.

These maps are hypothesis-generation and review-navigation tools. Any clinical
claims still require extraction from source evidence.

### 12. Suggested Implementation Order

The first useful embedding feature should be boring and auditable:

1. Build a manifest from `paper_artifact_registry.csv` and the key downstream
   registries.
2. Build paper-level and chunk-level text views with hashes and source paths.
3. Generate local embeddings on a 50-paper stratified corpus pilot and a 10 to
   20 paper intra-paper chunk-role pilot.
4. Produce KNN neighbours, simple clusters, a 2D projection, and advisory
   within-paper chunk roles.
5. Create four review packs:
   - source-category/genre disagreement candidates;
   - proceedings QC neighbours;
   - case-count manual-review neighbours;
   - intra-paper patient/shared-context chunk-role candidates.
6. Have the user judge whether the packs save review time.
7. Only then scale to all 1,027 text JSONs or try FlashLib/GPU acceleration.

Acceptance evidence for this first pass:

- every output row links back to `paper_id`, source text path, and chunk/page;
- intra-paper role outputs distinguish advisory labels from reviewed facts;
- no upstream `sps-review` files are modified;
- at least one review pack contains actionable candidates that a human can
  accept, reject, or mark uncertain;
- false confidence is avoided: neighbour/cluster labels are advisory only.
