# icm-architect

An agent skill that designs any process, idea, or problem into an **ICM workspace** (folder structure as agent architecture), or restructures an existing folder, repo, or vault into one. It follows the open [Agent Skills](https://agentskills.io) format, so it works in any agent that reads `SKILL.md` (Codex, Gemini CLI, Hermes Agent, Claude Code, Cursor, GitHub Copilot and others) and in any model you hand the folder to.

ICM (Interpretable Context Methodology) replaces orchestration code with structure: numbered folders carry sequencing, hierarchy carries context scoping, plain markdown files carry state. One agent, reading the right files at the right moment, does the work of a multi-agent framework, and a person can open any folder and see what state the system is in.

- Paper: [Interpretable Context Methodology: Folder Structure as Agent Architecture](https://arxiv.org/abs/2603.16021) (Van Clief & McDermott)
- Community: [Clief Notes](https://www.skool.com/cliefnotes)

## What it does

Two modes:

- **Build**: extracts the structure already present in how you describe your work (the stages, the checks, what's stable vs. per-run), picks a form, and scaffolds the smallest workspace that carries it.
- **Restructure**: audits an existing folder, classifies every file (catalog / contract / factory / product / dead), finds what points at each one, proposes a migration map for approval, then migrates and validates.

Every ICM is built from three primitives: a **sequence** (numbered steps, each one's output the next one's input), a **shelf** (a folder of same-shaped files), and a **catalog** (a small file that points down). The forms are recipes over them: **Pipeline**, **Record library**, **Knowledge bundle** (including one built from transcripts and research, with every quote checked against its source), **Context map**, and **System map**. They nest.

Every step ends at a **check** (a person, a script, or a small model) so a wrong turn is caught before the next step amplifies it. Every result is validated with the **walk test**: an agent with no memory must orient, act, and report status from the files alone.

The workspaces it builds are plain folders and markdown with `AGENTS.md` as the entry file, the name most agents read by default; tools that look for another name get a one-line pointer to it. Nothing in a workspace depends on one vendor.

## Security and access

Review [SECURITY.md](SECURITY.md) for workspace access boundaries, approvals, visualization CDN dependencies and the limitations of static security scanning. The optional Python tools use the standard library, but the generated visualization loads third-party JavaScript in the browser.

## Install

Keep the folder named `icm-architect`: a skill's name must match its folder.

| Agent | Put the `icm-architect/` folder in |
|---|---|
| Codex | `~/.agents/skills/` (all projects) or `.agents/skills/` in a repo |
| Gemini CLI | `~/.gemini/skills/` or `~/.agents/skills/`, or install it with `gemini skills install` and this repo's Git URL |
| Hermes Agent | `~/.hermes/skills/`, or list `~/.agents/skills` under `skills.external_dirs` in its config |
| Claude Code | `~/.claude/skills/` or `.claude/skills/` in a project |
| Claude apps | zip the folder (the folder itself is the zip root) and upload it under Customize → Skills |
| Cursor, GitHub Copilot and other Agent Skills clients | that client's skills folder |
| Any other agent or model | give it the folder and say "use this skill", or paste `SKILL.md` and then each file it points you to |

One copy in `~/.agents/skills/` serves Codex and Gemini CLI, and Hermes can be pointed at it.

Then ask your agent to "ICM this", "structure this for agents", or "build me a workspace for X".

## What's inside

- `SKILL.md`: the method. Load it first; it routes to the rest.
- `references/`: the detail, read only when a step needs it.
- `assets/templates/`: blank starters a workspace copies.
- `scripts/`: optional standard-library Python 3 that a workspace copies into `_tools/`. They check that links and input paths resolve, draw a workspace (or several) as one interactive graph, generate indexes, and check quotes against their sources. An agent without a shell can skip them.

MIT licensed, like the protocol it serves.
