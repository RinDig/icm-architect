# Agent entry pointer stubs

Copy each block into the named file at the workspace root. Replace `{Workspace name}` once — all three stubs together. These are generated files: regenerate them as a set whenever the workspace name changes; never hand-edit one individually; never add content to them. The instructions live in `workspace.md`, nowhere else.

## CLAUDE.md (Claude Code auto-load)

```markdown
# {Workspace name} — Claude Code Entry Point

This is the auto-loaded entry point for Claude Code. All project instructions, workspace structure, and routing are in `workspace.md` in this directory.

Read `workspace.md` now before doing any work.
```

## AGENTS.md (Codex and most agents' auto-load)

```markdown
# {Workspace name} — Codex Entry Point

This is the auto-loaded entry point for Codex. All project instructions, workspace structure, and routing are in `workspace.md` in this directory.

Read `workspace.md` now before doing any work.
```

## GEMINI.md (Gemini CLI auto-load)

```markdown
# {Workspace name} - Gemini Entry Point

This is the Gemini entry point for the {Workspace name} workspace.

Read `workspace.md` before doing any work.

Follow the ICM-style workspace routing:
- Do not load every workspace at once.
- Enter the specific sub-workspace before working.
- Load only the files needed for the current task.
- Treat folder structure as context architecture, not decoration.

Equivalent agent entry points:
- Codex: `AGENTS.md`
- Claude Code: `CLAUDE.md`
- Gemini: `GEMINI.md`
```

## Notes

- For nested workspaces (umbrella form), each sub-workspace gets its own `workspace.md` plus this same trio of stubs; the root's `workspace.md` routes into them.
- If a tool isn't used in this workspace, omit its stub rather than leaving a dead pointer.
