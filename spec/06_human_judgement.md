# Spec 06: Human Judgement Of Review Value

## Goal

Have Manfredi judge whether the review packs save time or reveal useful
candidate issues before scaling the workflow.

## Inputs

- Review packs from Spec 05.
- Run summaries from Specs 03 and 04.

## Local Outputs

- `qa/review_pack_decisions/<run_id>_decisions.csv`
- `results/review_pack_evaluation/<run_id>_summary.md`
- Optional updated questions for the next pilot.

## Evaluation Questions

- Did the pack surface papers you would not otherwise have prioritised?
- Did nearest neighbours or examples reduce review time?
- Were any advisory labels misleading?
- Which pack was highest value?
- Which output columns were missing or noisy?
- Did any result risk overclaiming?

## Suggested Metrics

- useful row rate;
- misleading row rate;
- uncertain row rate;
- median time per reviewed row if measured;
- number of rows promoted to a later manual review queue;
- number of design changes required before scaling.

## Clarifying Questions For Manfredi

1. What would count as "saves review time" for this pilot?
   - Default assumption: at least one pack has a clear useful-row rate above 50
     percent or surfaces a genuinely actionable QC candidate.
2. Do you want to review all packs yourself, or should one pack be prioritised?
   - Default assumption: review a small balanced sample from all four.
3. Should review decisions be recorded in CSV, Markdown, or both?
   - Default assumption: CSV decisions plus a Markdown summary.
4. Should unclear results be used to tune the next pilot or excluded?
   - Default assumption: keep unclear results and use them to refine chunking,
     role labels, or pack columns.
5. Is the goal of the first judgement pass speed, correctness, novelty, or
   reviewer comfort?
   - Default assumption: correctness and reviewer comfort first.

## Acceptance Evidence

- Human review decisions are recorded.
- At least one proceed/revise/stop decision is made for each pack.
- Scaling is blocked until this evidence exists.
