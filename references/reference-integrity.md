# Reference Integrity — the move-safety gate

Restructure mode's job is to move files without breaking anything. The walk test proves the *result* is navigable. It does **not** prove the *move itself* was safe. This gate fills that hole: before any file is proposed for a move, prove what depends on it. It is [impact analysis](https://en.wikipedia.org/wiki/Change_impact_analysis) applied to a folder — the same discipline a data team applies before altering a shared table.

## The one principle: presence is not position

A file's apparent disuse is not evidence that moving it is safe. The two are unrelated:

- The **oldest, most obviously superseded** file can be the **most referenced** — old outputs get wired into downstream scripts precisely because they were the stable ones.
- A file with **zero references you can see** can still be load-bearing, because you only searched where it was easy to look.

So the gate is not "does this look dead?" It is "**can I enumerate everything that points at this, everywhere it could point from?**" Until you can, the file is not classifiable as Dead — it is unproven.

## The four scopes

A reference can reach a file from four places. A search that covers only the first is the usual cause of a broken restructure.

1. **In-vault** — other files inside the workspace that name this path.
2. **Sibling-path** — relative `../other-folder/` references inside scripts or configs. These break the moment you regroup folders, even though nothing "outside" is involved.
3. **Symlink** — links pointing into or out of the move candidate. A moved target orphans the link; a moved link orphans nothing but disappears.
4. **External / cross-boundary** — the scope the walk test is structurally blind to: **other repositories, deploy scripts, cron jobs, running systems** that hardcode a path into this workspace. These cannot be updated atomically with your move, which makes them the highest-risk class. A workspace that looks self-contained rarely is.

Anything a scope turns up is **Blocked**, not Dead. A Blocked file is held in place (or moved only if every referrer is updated in the same change). Record the referrers on the migration map so the human approves against facts.

## Location durability (a fifth check, once per workspace)

Before trusting a workspace at all, confirm it lives somewhere durable. Outputs written into an **ephemeral or ignored location** — a temp dir, a git worktree, anything under a `.gitignore` — exist only until that location is cleaned up. Verify the workspace root is tracked/backed up before you reorganize *within* it; reorganizing files that were one cleanup away from gone is rearranging deck chairs.

## Migrate safely: copy, verify, then remove

A move is `copy → verify → remove`, never a single `mv` you trust:

1. **Copy** the file or subtree to its new home.
2. **Verify parity** — file count and content hash (or byte-for-byte compare) between source and destination. Zip-based formats (`.pptx`, `.docx`, `.xlsx`) embed metadata, so compare *unzipped content*, not the archive's outer hash.
3. **Remove** the original only after parity passes. Leave a pointer where a copy lived if anything referenced it.

A partial or corrupted copy that you never verified looks exactly like a successful one until someone opens the file.

## Illustrative commands (adapt to your tools)

ICM runs under any agent, so treat these as *shapes of the check*, not required tooling.

```sh
# 1. in-vault references to a move candidate
grep -rIl 'candidate-name' . --exclude-dir='candidate-name'

# 2. sibling-path (../) references among candidates
grep -rnI -e '\.\./[A-Za-z0-9_-]*/' . | grep -i 'candidate-name'

# 3. symlinks into/out of the tree
find . -type l -exec ls -l {} +

# 4. external / cross-boundary referrers (search OTHER repos and configs)
grep -rIl 'workspace-name' ~/other-repos ~/deploy ~/.config 2>/dev/null

# 5. durability: is the workspace root ignored or untracked?
git check-ignore -v . ; git ls-files . | head -1   # empty tracked-list = unbacked

# migrate parity
diff <(cd SRC && find . -type f | sort) <(cd DEST && find . -type f | sort)
```

## The gate, in one line

**Zero visible references is not a green light — it is an unfinished search.** Prove the dependencies, then move; verify the move, then delete.
