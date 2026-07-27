# {NN}_{stage-name} — {the job in five words}

One job: {reconcile the parallel branches into a single {artifact}}.

## Waits for
{NN-1}a, {NN-1}b, {NN-1}c — every one of those `output/` folders must be
non-empty. If any is empty, stop and name which one; do not proceed on
partial input.

## Inputs
- Working (this run): ../{NN-1}a_{branch}/output/{file}
- Working (this run): ../{NN-1}b_{branch}/output/{file}
- Working (this run): ../{NN-1}c_{branch}/output/{file}
- Reference (every run): ../../_shared/{rules-file}.md

Do NOT load: {the branches' own reference folders — their constraints were
applied upstream and restating them here re-does work already done}.

## Process
1. Read every branch output.
2. {Merge, following the reference constraints.}
3. Where branches contradict each other, flag the contradiction inline
   rather than choosing — the choice belongs to the human check.

## Outputs
- {artifact}.md → output/

## Human check
Read the flagged contradictions first — each is a decision you own, not the
model's. Resolve them in place. Nothing downstream runs while a flag is open.
