# icm-architect

A Claude skill that designs any process, idea, or problem into an **ICM workspace** — folder structure as agent architecture — or restructures an existing folder, repo, or vault into one.

ICM (Interpretable Context Methodology) replaces orchestration code with structure: numbered folders carry sequencing, hierarchy carries context scoping, plain markdown files carry state. One agent, reading the right files at the right moment, does the work of a multi-agent framework — and a human can open any folder and see exactly what state the system is in.

The workspace is a library. The routing files are the catalog: small, stable, they point at everything and store almost nothing. One librarian — one model — walks the building, and the question decides which shelf gets walked to.

- Paper: [Interpretable Context Methodology: Folder Structure as Agent Architecture](https://arxiv.org/abs/2603.16021) (Van Clief & McDermott)
- Community: [Clief Notes](https://www.skool.com/cliefnotes)

## What it does

Two modes:

- **Build** — extracts the structure already present in how you describe your work (the stages, the human gates, what's stable vs. per-run), picks one of six proven forms, and scaffolds the smallest workspace that carries it.
- **Restructure** — audits an existing folder, classifies every file (catalog / contract / factory / product / dead), proposes a migration map for approval, then migrates and validates.

Six forms, one skeleton: **Pipeline** (production line), **Umbrella** (portfolio of pipelines), **Record library** (people/clients/sessions), **Knowledge bundle** (a navigable brain), **Context map** (an organization as a graph), **System map** (a folder later agents will edit — nouns, movements, change-impact). They compose and recurse.

Every result is validated with the **walk test**: an agent with no memory must orient, act, and report status from the files alone.

## Install

**Claude Code:** copy this folder to `~/.claude/skills/icm-architect/` (or `.claude/skills/icm-architect/` inside a project), then ask Claude to "ICM this" / "structure this for agents" / "build me a workspace for X".

**Claude apps:** upload `icm-architect.skill` (build it with the skill-creator packager, or zip the `icm-architect/` folder itself — the folder is the zip root, not its contents) via [Customize → Skills](https://claude.ai/customize/skills).

## Layout

```
icm-architect/
├─ SKILL.md              the method: invariants, build mode, restructure mode, walk test
├─ references/
│  ├─ core.md            five principles, five-layer hierarchy, naming, token discipline
│  ├─ forms.md           the six forms in depth: skeletons, moves, failure modes
│  └─ system-map.md      audit pipeline for the System map form
└─ assets/templates/     copyable starters: CLAUDE.md, CONTEXT.md, stage contract,
                         node card, object/process cards, schema, questionnaire
```

MIT licensed, like the protocol it serves.
