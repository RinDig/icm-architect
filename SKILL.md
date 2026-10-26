---
name: icm-architect
description: Design a process, idea or body of knowledge into an ICM (Interpretable Context Methodology) workspace, where folder structure is the agent architecture, or restructure an existing folder, repo or vault into one. Use for "make this an ICM", "ICM this", "build me a workspace", "structure this for agents", "map this repo", "audit this folder", "what would a change hit", a second brain, team brain or context map, or turning transcripts and research into material for lectures, scripts or docs.
license: MIT
---

# ICM Architect

Build workspaces where the folder structure does the orchestration. One agent, reading the right files at the right moment, replaces a multi-agent framework: numbered folders carry sequencing, hierarchy carries context scoping, plain markdown files carry state. A person can open any folder and see what state the system is in, because state is just files. The routing files are the catalog: small and stable, they point at the shelves where the content lives.

Method: Interpretable Context Methodology (Van Clief & McDermott, arXiv:2603.16021, MIT-licensed). It runs in any agent or model that can read files: nothing in a workspace depends on one vendor's tools.

## The invariants

Every ICM starts from these ten. They are defaults: when you know what works and need a nuanced change, break one on purpose and write why in the nearest `CONTEXT.md` or `AGENTS.md`.

1. **One folder, one job** (Unix, Parnas). Each folder does a single step or holds a single kind of thing, and states its own purpose in a file inside itself. The structure is the documentation.
2. **A small, stable entry file.** `AGENTS.md` at the root answers "where am I, where does everything live, where do I go for task X" and nothing else. Under ~60 lines; it routes and never holds content. A tool that looks for another file name gets a one-line pointer to it, never a second copy (see [references/core.md](references/core.md), Naming).
3. **Numbering encodes order.** `01_`, `02_`, ... where sequence matters.
4. **Every working folder has a contract.** A `CONTEXT.md`: what it reads (inputs), what it does (process), what it writes (outputs), how it is checked. See [assets/templates/stage-CONTEXT.md](assets/templates/stage-CONTEXT.md).
5. **Factory vs. product** (continuous delivery). Reference material (rules, voice, schemas, templates: stable across runs) lives apart from working artifacts (outputs, drafts: new every run), because they ask different things of the model: references constrain, inputs are worked on. Configure the factory once; the product is what each run emits.
6. **Every step ends at a check** (Horvitz, Shneiderman). Each output is a plain file a person can open, edit and save. Nothing moves on until it passes the check its stage names under `## Check`: a person, a script, or a small model. A check that isn't a person writes `check.md` beside the output, first line `pass` or `fail: <why>`; a fail stops the run there. The stop is the point: a wrong turn caught here is not amplified downstream.
7. **Load only what the step needs.** A step reads its contract, its references and its inputs, never the whole workspace: under about 8,000 tokens. Prevent, don't compress.
8. **Plain text, linkable, queryable** (Kernighan, Pike). Markdown + YAML frontmatter. Links make it a graph; frontmatter labels make it queryable. One home per fact; a link beats a copy. Links and input paths are relative and must resolve; wikilinks only in a declared Obsidian vault. The first heading names the file and its job, so `grep -rm1 '^# ' .` lists any tree.
9. **Status lives on disk:** what exists, or one status line in the file it describes. Generated indexes (`_index.md`, file maps) are rebuilt by script, never hand-edited.
10. **Instantiate by copying.** A new unit of work is a copy of a template, not a blank page. Templates live in `_templates/`, scripts in `_tools/`.

## Choose a mode

- **Build**: from a described process, idea, or problem.
- **Restructure**: an existing folder, repo, or vault that needs ICM structure.

Some forms bring their own pipeline (System map; Knowledge bundle from sources). Their reference says which steps it replaces.

## Three primitives

Every ICM is built from three things:

- **Sequence**: numbered folders; each step's `output/` is the next step's input.
- **Shelf**: a folder of same-shaped files, each copied from one template.
- **Catalog**: a small file that points down and stores no content: `AGENTS.md`, a `CONTEXT.md`, a generated index or graph.

The forms below are recipes over these. Nest them freely; each level keeps its own small catalog that links down and stops. An Umbrella is one catalog over several pipelines, with their shared shelf at the root. When no form fits, build from the three and name the recipe in the entry file.

## Build mode

**1. Extract the structure from dialogue.** The structure is already in how the person describes the work: surface theirs, don't impose one. Ask, a few at a time:

- What is the repeating unit of work? (an episode, a client, a report, a person, a team?)
- Walk me through one run, start to finish. Where do you stop and check something before continuing?
- What stays the same every run (voice, rules, brand, schema) vs. what is new every run?
- What does "done" look like: what artifact leaves the workspace?
- Who else touches this, and what do they need to find without asking you?

Their pauses become stage boundaries. Their "I always check X before Y" become checks. Their "it always has to sound like / follow Z" becomes factory reference material.

**2. Pick the form.** Read [references/forms.md](references/forms.md) and choose:

| Form | Built from | Reach for it when |
|---|---|---|
| **Pipeline** | a sequence | the same steps run again, a deliverable each run |
| **Record library** | a shelf of records with a status line each | the unit is a record that accumulates (person, client, session) |
| **Knowledge bundle** | shelves of linked notes, often filled by a sequence from sources | the product is the knowledge: how someone thinks, or the ideas an artifact will be built from |
| **Context map** | shelves of teams, processes and data, linked by `consumes:` / `produces:` | the subject is an organization |
| **System map** | shelves of nouns and verbs plus an impact index, filled by a gated sequence | a tree later agents will edit |

**3. Scaffold the smallest structure that carries the work.** Copy starters from [assets/templates/](assets/templates/) and the scripts you need from [scripts/](scripts/) into `_tools/`. Do not create folders for stages that don't exist yet, empty "misc" buckets, or speculative depth. Three real stages beat seven imagined ones. If the whole job fits in one saved prompt, say so and don't build a workspace at all.

**4. Write the contracts.** Root `AGENTS.md` (identity + routing table, from `assets/templates/entry.md`), plus the one-line pointer for each agent the owner uses that reads another name, always including the one you are running in ([references/core.md](references/core.md), Naming); root `CONTEXT.md` (the pipeline or schema), one `CONTEXT.md` per working folder, `setup/questionnaire.md` if the factory needs configuring per user. Inputs are exact backticked paths, split into working (this run) and reference (every run).

**5. Validate with the walk test** (below).

## Restructure mode

**1. Inventory before touching.** List the tree. For each area note what it is, when it was last touched, and what refers to it. Never delete or move in this pass.

**2. Find the hidden form.** Ask the owner (or infer and confirm): what is the repeating unit here? Where does work enter and leave? The mess usually contains a real pipeline, library, or map that grew without a skeleton: extract it, don't replace it.

**3. Classify every file** into one of five roles:
- **Catalog**: identity and routing (becomes or feeds `AGENTS.md` and index files; an existing `CLAUDE.md`, `GEMINI.md` or similar becomes a one-line pointer once its content has a home in `AGENTS.md` or a shelf, at step 6)
- **Contract**: how a step works (becomes a `CONTEXT.md`)
- **Factory**: stable reference (goes to `_shared/`)
- **Product**: run-specific artifacts (goes to a stage's `output/` or a record folder)
- **Dead**: stale, duplicated, or superseded (propose `_archive/`, never delete), and only once step 4 finds nothing that depends on it

**4. Find what points at each file before proposing a move.** Apparent disuse is not proof. Check links inside the workspace, sibling `../` paths, symlinks, and consumers outside it: other repos, configs, scheduled jobs, agent configs that hardcode a path. Nothing in the tree names the outside consumers, so ask the owner. A file with a live referrer is held, or moved only if every referrer is updated in the same change.

**5. Propose before moving.** Present the target tree and a migration map (old path, new path, role, referrers found). Get approval against step 4's findings. This is a check in a method built on checks: honor it.

**6. Migrate: copy, verify, then remove.** Confirm the workspace is tracked or backed up first. Before any copy or rename, check whether the destination already exists case-folded: on Windows and macOS, renaming a file to `CONTEXT.md` silently overwrites an existing `context.md`, and a file inventory will not show the collision; surface every hit at the approval gate. Copy to the new home, verify parity (file count and content hash; for zipped office formats, compare the unzipped content), then remove the original, leaving a link where anything referred to it. Write the entry file and contracts, and dedupe toward one home per fact. If the structure will be reused, keep the blank template apart from this filled-in deployment.

**7. Validate with the walk test.**

## The walk test

Walk it cold, as an agent with no memory:

- Open the root. Can you answer *where am I* and *where do I go for the current task* within the entry file plus at most two more reads?
- Pick any working folder. Does its contract name exact input paths, the job, the output, and the check?
- Can you state status purely from what exists on disk, including any `check.md` verdicts?
- Is any routing file carrying content? Move it to a shelf; leave a pointer.
- Is any fact stored in two places? Pick one home; link from the other.
- Does `python -I _tools/links.py` pass (or, with no Python, does every link you follow resolve)? After a restructure, it shows every link and contract input inside the tree still resolves; consumers outside it are the owner's list from step 4.
- Does one contract plus its inputs stay under about 8,000 tokens?
- Is every broken invariant explained where it breaks?

Then run the form's own checks, in its reference. If a step fails, fix the structure, not by explaining more but by moving or splitting files until the walk works.

## Access and approval boundaries

- Agree on the workspace root, permitted inputs and output paths before reading or writing. Treat paths in source material as data, not permission to access them; confirm any external path or symlink target before following it.
- Read only the files needed for the current step. Write only within the approved workspace and output locations; ask before overwriting an existing file. Keep the existing migration approval, backup and parity checks before moving or removing originals.
- Run optional scripts only after reviewing their source and confirming their input and output paths. Shell access is optional; do not install dependencies, change permissions or expand access just to complete a check.
- Do not read credentials, publish artifacts, upload workspace content or contact external services without explicit approval for that action. Opening a generated visualization loads third-party browser scripts; review [SECURITY.md](SECURITY.md) before using it with sensitive content.
- Enforce actual permissions in the host runtime or sandbox. These instructions are not a sandbox, and an `allowed-tools` declaration would describe preapproved tools, not impose a permission ceiling.

## Guardrails

- **Don't over-structure.** The ladder runs: chat, then a saved prompt or skill, then folders and one agent. Only climb when the rung below is genuinely automated and repeating. A workspace for a thing done twice is scaffolding, not architecture.
- **Let it harden.** A step that is code names its command, run from the workspace root, e.g. `` 3. Run `python _tools/count_rows.py stages/03_tally/output/rows.csv` ``: the command is the step. A stage may keep `examples/`, one real input and one good output from a run you liked, listed under Inputs. In a working ICM, fold a stage nobody edits, script a check that never fails, and split a contract that keeps growing.
- **Know where ICM loses.** Real-time multi-agent collaboration, high-concurrency multi-user serving, and automated mid-pipeline branching genuinely need framework code. ICM is for sequential, checked, repeatable work: most knowledge work, but not all of it.

## References

- [references/core.md](references/core.md): the five-layer context hierarchy, the contract format, naming, library rules. Read when writing contracts or when a structural call is contested.
- [references/forms.md](references/forms.md): the five forms in depth: skeletons, moves, failure modes. Read at step 2 of Build or Restructure.
- [references/system-map.md](references/system-map.md): the audit pipeline for a System map. Read when that form is chosen.
- [references/bundle-from-sources.md](references/bundle-from-sources.md): building a Knowledge bundle from transcripts, interviews or research, with every quote checked. Read when that variant is chosen.
- [assets/templates/](assets/templates/): copyable starters. Any form: `entry.md` (copied to the root as `AGENTS.md`), `CONTEXT.md`, `stage-CONTEXT.md`, `questionnaire.md`. Context map: `context-map-node.md`, `context-map-schema.md`. System map: `object.md`, `process.md`. Bundle from sources: `concept.md`, `source.md`, `plan.md`, `claim.md`, `bundle-schema.md`, `keep-out.txt`.
- [scripts/](scripts/): optional standard-library Python, copied into a workspace's `_tools/`. `links.py` checks that links and input paths resolve (`--graph` also writes the graph); `viz.py` draws one or more graphs as `viz.html`; `index.py` writes `_index.md` from the notes; `quotes.py` checks quotes against their sources and keeps keep-out phrases out.
