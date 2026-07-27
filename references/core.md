# ICM Core

The canon, distilled from the ICM paper (arXiv:2603.16021) and production workspaces. Read this when writing contracts, arguing a structural call, or checking a workspace against the method.

Contents: Five principles · Five-layer hierarchy · Stage contract format · Parallel stages and the join · Naming conventions · Library rules · Token discipline · Where ICM loses

## The five design principles

Each is borrowed from fifty-year-old, still-standing engineering practice:

1. **One stage, one job** (Unix / Parnas). Each stage handles a single step and writes to its own folder. A stage that fetches does not also filter; a stage that filters does not also format.
2. **Plain text as the interface** (Kernighan & Pike). Stages communicate through markdown and JSON. No binary formats, no databases in the loop, no proprietary serialization. Any human with a text editor can inspect or modify any artifact.
3. **Layered context loading.** Agents load only what the current stage needs — prevention, not compression. Within content, reference material (internalize as constraints) is kept structurally separate from working artifacts (process as input), because they ask different things of the model.
4. **Every output is an edit surface** (Horvitz / Shneiderman). Each intermediate output is a file a human can open, edit, and save before the next stage runs. The next stage reads whatever the human left there.
5. **Configure the factory, not the product** (continuous delivery). Set up preferences, brand, style, and structure once; every run emits a new deliverable from the same configuration.

The consequence, stated once: *stage sequencing is the folder numbering; context scoping is the folder hierarchy; state management is the files on disk; coordination is one folder's output being another folder's input.* The filesystem does the work a framework would do in code.

## The five-layer context hierarchy

| Layer | Typical file | Question it answers | Role | Size |
|---|---|---|---|---|
| L0 | `CLAUDE.md` | Where am I? | routing | 300–800 tokens |
| L1 | root `CONTEXT.md` | Where do I go? | routing | 200–500 tokens |
| L2 | stage `CONTEXT.md` | What do I do? | **the control point** | 200–500 tokens |
| L3 | `references/`, `_shared/` | What rules apply? | factory (stable) | 500–2k tokens |
| L4 | `output/`, run artifacts | What am I working with? | product (per-run) | varies |

- L0–L2 are the catalog: small, stable, no content payload.
- L2 is the control surface of the whole system — its Inputs section is what makes context selection explicit, editable, and auditable instead of left to agent judgment.
- L3 vs L4 is the factory/product split. L3 = the recipe (voice.md, design-system.md, schema.md). L4 = the ingredients and the dish (research-output.md, draft.md).
- Large L3 collections get their own internal `CONTEXT.md` router — the L1 routing pattern applied recursively. The hierarchy is self-similar at every depth; apply it inside any folder that grows past easy scanning.

## Stage contract format

Every working folder carries a `CONTEXT.md` shaped like this (copy from `assets/templates/stage-CONTEXT.md`):

```markdown
# 02_script — turn research into a script

One job: write the script from the research output.

## Inputs
- Working (this run): ../01_research/output/research.md
- Reference (every run): ../../_shared/voice.md
- Reference (every run): references/structure.md

## Process
1. Read the research output.
2. Draft to the structure in structure.md, in the tone of voice.md.
3. Keep under 90 seconds spoken.

## Outputs
- script_draft.md → output/

## Human check
Read the draft aloud. Verify the argument order survived from research. Edit in place; the next stage reads whatever is here.
```

Rules: inputs are exact paths, split working vs reference. The process is numbered and short — constraints live in L3 files, not restated here. Exactly one human check, stated as something a person does, not a vague "review."

## Parallel stages and the join

Folder numbering is a total order, so a plain `01/02/03` line can only say "after." When steps are genuinely independent — three scans that all read the same brief, none of which reads another's output — numbering them in sequence asserts a dependency that does not exist, and an agent walking the workspace cold will believe it. The structure is the documentation; a structure that lies is a defect, not a style choice. Give independent steps one number and different letters:

```
stages/
├─ 01_scope/          → output/brief.md
├─ 02a_market/        reads 01
├─ 02b_competitors/   reads 01
├─ 02c_regulatory/    reads 01
└─ 03_synthesis/      reads 02a + 02b + 02c
```

Status still comes from scanning `output/`; it simply reads as a checklist rather than a cursor. `02a ✓ 02b ✓ 02c ▢` says one branch is outstanding and the synthesis is blocked — more informative than a single position on a line.

The stage after a fan is a **join**, and its contract does the waiting (copy from `assets/templates/join-CONTEXT.md`). It names every sibling output as an exact working input and states what it is waiting for. No new mechanism is needed — the Inputs section already carries this. When branches contradict each other, the join surfaces the conflict as an editable file instead of quietly picking a winner; that contradiction is a finding, and putting it in front of a person before the expensive downstream work is the same move as any other stage boundary.

Two limits, both real:

- **Fan width is bounded by human attention, not by compute.** The bottleneck in an ICM is the human gate, not model wall-clock — parallelising three stages that each need twenty minutes of review saves seconds and creates a review pile. Two to four branches. If the work is wider and uniform (score twelve processes, audit thirty files), the repeating unit is a record, not a stage: use a record library and let the index log be the join.
- **A fan is declared, never inferred at run time.** Independence is a fact about the work, settled when the workspace is designed. A run that decides its own width cannot name its inputs — it has to glob them — and the structure stops being readable before it executes. See *Where ICM loses*.

## Naming conventions

- Stage folders: `NN_kebab-name` (`01_research`). Ordinal-only prefixes (`00-tracker.md`) for ordered files inside a folder.
- Concurrent stages share a number and differ by a letter: `02a_market`, `02b_competitors`. Same number means no ordering between them; the next integer runs after all of them. The letter is not a priority — `02a` and `02b` are peers, and a run may do them in any order or at once.
- Meta/system folders get an underscore prefix and sort to the top: `_meta/`, `_system/`, `_shared/`, `_config/`, `_templates/`, `_index/`, `_archive/`. Underscore = "about the workspace, not of the work."
- Records and nodes: kebab-case slugs for machine-facing files, or human-readable Title Case where a person browses daily (an Obsidian vault). Pick one per workspace and write the choice into the schema — drift between schema and files is the most common decay.
- Typed content files may prefix their type: `data-customer-list.md`.
- Entry file: `CLAUDE.md` for Claude Code, `AGENTS.md` for other agents. If both exist, one is generated from the other or is a one-line pointer — never two hand-maintained copies.
- Templates are blank, named for what they produce, and live together: `_templates/pilot-brief.md`.

## Library rules

- **The catalog holds no books.** Routing files point at everything and store almost nothing. When a routing file grows, it is absorbing payload — move the payload to a shelf.
- **One home per fact; a link beats a copy.** Duplication is how structures rot.
- **Generated indexes are never hand-edited.** A file map built from frontmatter by a script cannot drift; a hand-curated one always does. If an index matters, script it and schedule the rebuild.
- **The structure is the documentation.** If something needs explaining, the explanation goes in that folder's `CONTEXT.md`, not in a wiki elsewhere and not in anyone's head. A new collaborator should understand the whole pipeline by reading the CONTEXT files top to bottom, without running anything.
- **Method and instance live apart.** The blank, reusable template of a structure is a different artifact from any filled-in deployment of it. When a structure proves out, extract the template before it tangles with the data.
- **Working sessions end in artifacts.** A workshop, interview, or planning call that produces only slides or vibes has failed the structure; it should end with files the structure can shelve.

## Token discipline

A stage's full context — entry + contract + references + inputs — should land around 2,000–8,000 tokens. That keeps the model in the range where it performs best and keeps every load auditable. A monolithic everything-prompt for the same pipeline typically runs 30k–50k tokens, most of it irrelevant to the current step; ICM never loads those tokens rather than compressing them later. If a stage's context balloons: split the stage, tighten the Inputs list, or push detail down into an L3 file the contract points at but doesn't inline.

## Where ICM loses

Name these honestly rather than overclaiming:

- **Real-time multi-agent collaboration** — agents responding to each other in tight loops need message-passing infrastructure; file handoffs are too slow.
- **High concurrency** — many users hitting one pipeline needs queueing, state isolation, deployment. ICM is local-first by design.
- **Automated mid-pipeline branching** — a human choosing between two alternative stages at a gate is natural; the *system* branching on AI output mid-run pushes ICM toward becoming the framework it replaced. A fan is not a branch and does not fall under this: every lettered sibling always runs, and the width is fixed when the workspace is written, so nothing is decided at run time. Branching *selects* a path; that selection is where ICM should hand off to framework code.

The claim is not that ICM replaces frameworks everywhere. The claim is that for sequential, human-reviewed, repeatable workflows — most knowledge work — the framework is more complexity than the problem requires, and that complexity costs opacity, fragility, and developer dependency.
