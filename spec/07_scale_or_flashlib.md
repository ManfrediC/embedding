# Spec 07: Scale Or FlashLib Decision

## Goal

Decide whether to scale from the pilot to all 1,027 text JSONs and whether to
introduce FlashLib/GPU acceleration.

## Inputs

- Pilot run manifests.
- Review-pack evaluation from Spec 06.
- Runtime and storage metrics from Specs 03 and 04.

## Possible Outcomes

- Stop: pilot did not provide enough review value.
- Revise: adjust chunking, model, role taxonomy, or review pack design.
- Scale CPU/local: run all eligible text JSONs with existing local tooling.
- Add GPU/FlashLib: use FlashLib only if scale/runtime justifies dependency
  work.
- Add paid/API model branch: only with explicit approval and a cost cap.

## Verification Before Scaling

- Pilot review packs are judged useful enough.
- All outputs remain traceable to source paths and chunks.
- Runtime and storage are acceptable.
- No upstream `sps-review` writes are required.
- Generated full-corpus outputs remain ignored unless a small fixture is
  deliberately promoted.

## Clarifying Questions For Manfredi

1. What threshold should trigger full-corpus scaling?
   - Default assumption: at least one review pack is clearly useful and no
     serious provenance or overclaiming issue appears.
2. What runtime would make CPU tooling unacceptable?
   - Default assumption: only consider FlashLib if full-corpus CPU KNN/clustering
     is slow enough to interrupt iteration.
3. Do you want FlashLib installed/tested on this machine if CPU tooling is
   already adequate?
   - Default assumption: no; avoid dependency work until needed.
4. Should full-corpus outputs be disposable experiment artefacts or promoted to
   durable local assets?
   - Default assumption: disposable/generated until reviewed.
5. Should any paid embedding/API branch be considered after the local pilot?
   - Default assumption: no paid branch without a separate explicit approval,
     cost estimate, and narrow sample.

## Acceptance Evidence

- A written decision says stop, revise, scale locally, add FlashLib, or design a
  paid/API branch.
- The decision cites pilot evidence rather than enthusiasm alone.
- Any next implementation phase has its own updated spec.
