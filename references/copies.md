# Copies across repositories

Invariant 10 instantiates by copying inside one workspace. This reference covers the next case: one template, kept in its own place, copied into several other repositories that each live on their own. The rule that shapes everything below is **no runtime link**: an instance never imports, symlinks or calls back into the place it came from. Someone who clones the instance alone, on a machine that has never seen the template, gets a working tree.

## The way in: first copy

A first copy is made by a script, not by hand, so it can check before it writes:

- It refuses if the target already holds the tree; a first copy never overwrites.
- It copies only what the template's version control tracks at one known commit, and writes that commit into the instance.
- Every placeholder in the template has a value, or nothing is written.
- The instance gets a small values file (`_values.md`: one `name = value` line per placeholder, plus the commit). The leading underscore keeps it out of the tree's own routing; it belongs to the instance.
- Each copied node carries an `origin:` line in its frontmatter: its path in the template and the commit, e.g. `stages/01_draft/CONTEXT.md@1a2b3c4`.
- Any scripts the tree needs are copied too, with a provenance file next to them (commit, list of files, what they need installed). A tool the tree only finds on someone's `PATH` is a hidden runtime link.

After the first copy the instance belongs to its repository. It is edited there like any other file.

## The way back: a changed node as a copy

When an instance changes a node and the template should learn from it, the change travels back the same way it came: as a copy, never as a pull from the instance. Whoever notices it (a person or an agent) drops a note into the template's intake shelf:

| Part | Content |
|---|---|
| Node | path in the template |
| Origin | the `origin:` line of the changed file, unchanged |
| Reason | two or three lines: what went wrong, what the change does |
| File | the changed node, unchanged, values still filled in |
| Values | a copy of the instance's `_values.md` |

On the template side, put the placeholders back in place of the values, then compare against the template file at the commit in `origin:`. What remains is the candidate. It goes through the template's normal change process like any other change request; nothing is merged automatically.

## Keeping an instance current

A first copy deliberately doesn't update. Bringing an existing instance up to a newer template is its own piece of work in the instance's repository, by that repository's rules: compare each node's `origin:` against the template, take what applies, keep what the instance changed on purpose, and record the new commit. An instance that is many commits behind is a decision, not a fault.

## Failure modes

- **A link disguised as a copy:** a relative path, a symlink, or a script on `PATH` that points back into the template. Clone the instance alone into an empty place and run it there.
- **Edits flowing back unreviewed:** an instance pushing straight into the template. The intake shelf exists so that one project's local fix doesn't become everyone's default.
- **Project names in the template:** examples and placeholders stay generic. The evidence for a change lives with the note, not in the template text.
