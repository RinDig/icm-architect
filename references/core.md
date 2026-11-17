# ICM Core

The detail behind the invariants, from the ICM paper (arXiv:2603.16021) and production workspaces. Read this when writing contracts, arguing a structural call, or checking a workspace against the method.

Contents: Five-layer hierarchy · Contract format · Naming · Library rules · Keeping steps small

## The five-layer context hierarchy

| Layer | Typical file | Question it answers | Role | Size |
|---|---|---|---|---|
| L0 | `AGENTS.md` | Where am I? | routing | 300–800 tokens |
| L1 | root `CONTEXT.md` | Where do I go? | routing | 200–500 tokens |
| L2 | stage `CONTEXT.md` | What do I do? | **the control point** | 200–500 tokens |
| L3 | `references/`, `_shared/` | What rules apply? | factory (stable) | 500–2k tokens |
| L4 | `output/`, run artifacts | What am I working with? | product (per-run) | varies |

- L0–L2 are the catalog: small, stable, no content payload.
- L2 is the control surface of the whole system. Its Inputs section is what makes context selection explicit, editable, and auditable instead of left to agent judgment.
- L3 vs L4 is the factory/product split. L3 is the recipe (voice.md, design-system.md, schema.md); L4 is the ingredients and the dish (research-output.md, draft.md).
- A large L3 collection gets its own internal `CONTEXT.md` router: the L1 routing pattern applied recursively, inside any folder that grows past easy scanning.

## Contract format

Every working folder carries a `CONTEXT.md` shaped like this (copy from `assets/templates/stage-CONTEXT.md`):

```markdown
# 02_script - turn research into a script

One job: write the script from the research output.

## Inputs
- Working (this run): `../01_research/output/research.md`
- Reference (every run): `../../_shared/voice.md`
- Reference (every run): `references/structure.md`

Do NOT load: other stages' references, earlier runs, the whole `_shared/` folder.

## Process
1. If an input is missing or empty, stop and say which.
2. Draft to the structure in structure.md, in the tone of voice.md.
3. Keep it under 90 seconds spoken.

## Outputs
- `script_draft.md` -> `output/`

## Check
A person reads the draft aloud and confirms the argument order survived from research. Edit in place; the next stage reads whatever is here.
```

Rules: inputs are exact backticked paths, split working vs reference. The process is numbered and short; constraints live in L3 files, not restated here, and a step that is code names its command. Commands run from the workspace root and say `python`; use `python3` or `py` where that is the name. Exactly one check, stated as something a person, a script or a small model does, never a vague "review". A check that isn't a person writes `check.md` beside the output, first line `pass` or `fail: <why>`. That first line is the verdict and nothing else, so a script can gate on it exactly (`head -n 1 check.md` is `pass`, not `pass (…)`); who or what judged, and on what evidence, goes on the lines below.

## Naming

- The entry file is `AGENTS.md`. A tool that reads another name gets a one-line pointer, never a second copy (syntax as of October 2026): `CLAUDE.md` holds `@AGENTS.md` for Claude Code; `GEMINI.md` holds `@./AGENTS.md` for Gemini CLI; anything else gets a file that says "Read AGENTS.md first."
- Stage folders: `NN_kebab-name` (`01_research`). Ordinal-only prefixes (`00-tracker.md`) for ordered files inside a folder.
- Underscore folders are about the workspace, not of the work, and sort to the top: `_shared/` (the factory), `_templates/`, `_tools/` (scripts), `_meta/` (schema and rules), `_archive/`.
- Records and nodes: kebab-case slugs for machine-facing files, or Title Case where a person browses daily (an Obsidian vault). Pick one per workspace and write the choice into the schema; drift between schema and files is the most common decay.
- Typed content files may prefix their type: `data-customer-list.md`.
- Templates are blank, named for what they produce, and live together: `_templates/pilot-brief.md`.

## Library rules

- **The catalog holds no books.** Routing files point at everything and store almost nothing. When a routing file grows, it is absorbing payload: move the payload to a shelf.
- **One home per fact; a link beats a copy.** Duplication is how structures rot.
- **Generated indexes are never hand-edited.** An index built from frontmatter by a script (`_tools/index.py`) cannot drift; a hand-curated one always does.
- **The structure is the documentation.** If something needs explaining, the explanation goes in that folder's `CONTEXT.md`, not in a wiki elsewhere and not in anyone's head. A new collaborator should understand the pipeline by reading the CONTEXT files top to bottom, without running anything.
- **Method and instance live apart.** The blank, reusable template of a structure is a different artifact from any filled-in deployment of it. When a structure proves out, extract the template before it tangles with the data.
- **Working sessions end in artifacts.** A workshop, interview, or planning call that produces only slides has failed the structure; it should end with files the structure can shelve.

## Keeping steps small

A step's full context (entry file, contract, references, inputs) should stay under about 8,000 tokens. That keeps every load auditable. A monolithic everything-prompt for the same pipeline typically runs 30k–50k tokens, most of it irrelevant to the current step; ICM never loads those tokens rather than compressing them later. If a step's context balloons, split the stage, tighten the Inputs list, or push detail down into an L3 file the contract points at but doesn't inline.
