# {Workspace name}
<!-- Layer 0 (L0): Workspace identity. Orientation for any session starting in this directory. ~800 tokens max. -->

## What This Is

{One or two sentences: what this workspace is and what leaves it. If it is a multi-workspace directory, say so — each sub-folder is a distinct workspace with its own workspace.md; enter a sub-workspace to do work within it.}

## Workspace Map

| Folder / Workspace | Purpose | Entry Point |
|---|---|---|
| `{stages/}` | {the pipeline, in execution order} | [{first stage CONTEXT}](stages/01_…/CONTEXT.md) |
| `_shared/` | factory: rules and reference that never change per run | browse directly |
| `_templates/` | blank starters — new work is a copy, not a blank page | browse directly |
| `setup/` | one-time factory configuration | [setup/questionnaire.md](setup/questionnaire.md) |

## Routing

**{Task A}?** → Open `{path/}` — your agent auto-loads CLAUDE.md / AGENTS.md / GEMINI.md, which point back here.

**Starting a new unit of work?** → Copy `_templates/{template}/` → rename → populate its brief. Never work directly in the template folder.

**Asked for status?** → Scan what exists in `output/` folders. Report what exists; don't open everything.

## Working Principles (applies across all workspaces)

- Each workspace loads only the context it needs. Do not load all workspaces at once.
- {Stable rules that hold everywhere: brand boundaries, voice locations, factory/product split.}

## Current State

- **{unit}**: {one line: where things stand, and which file to check for live status.}
