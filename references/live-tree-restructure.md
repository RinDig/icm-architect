# Restructuring a tree that is live

Restructure mode assumes you can move a file and then check the result. That assumption fails
the moment the tree is in use: sessions have directories in it open, scheduled jobs read paths
inside it, other repositories hardcode paths into it, and an agent harness keeps its own copy of
where things were. The walk test proves the *result* is navigable. Nothing in it proves the
*move* did not break something that was running while you made it.

This is the field record from one such restructure: a home directory of roughly seventy
top-level entries, a dozen repositories, several agent accounts, four repository maps and a
nightly drift report, done over four phases with everything in daily use throughout.

## When this applies

Ask three questions before designing anything. Does something other than a human read a path in
this tree — a scheduled job, a daemon, a deploy config, an agent's session state? Do other
repositories name paths inside it? Is anyone working in it right now? One yes and the tree is
live. Two or three and the ordering below is not optional.

The distinguishing symptom is that the failures are *silent*. A job whose input path moved
does not error; it finds nothing and reports success on an empty set. A config pointing at a
renamed directory falls back to a default. You will not find these by walking the new tree,
because the new tree is fine. You find them by knowing, before you move, who read what.

## 1. Census before design

Do not design the target structure first. Inventory what exists and who touches it, and let
the structure fall out. Four things worth a written record, kept and cited by row rather than
finished and discarded:

**Who has the tree open.** List the live sessions and processes rooted anywhere inside it,
with their working directory and how long they have been idle. A session that has been idle for
two days with no children is a different decision than one mid-edit.

**Every working copy and its parent.** Detached checkouts, worktrees, clones, each mapped back
to the repository it belongs to. A working copy living outside its own repository is what a
later "cleanup" deletes by accident.

**Every credential-shaped name, never opened.** Name-and-kind only: a path, what sort of secret
it looks like, which tool owns it. Reading them is not part of the inventory and never becomes
part of it.

**What runs on a schedule.** Cron entries, launch agents, systemd units, CI schedules, each
with the paths it reads and writes. These are the consumers that will not complain.

## 2. The method's own corpus

The plan, the specs, the census records — the documents driving the restructure — usually live
somewhere in the tree being restructured. Moving them mid-run pulls the ground out from under
the run.

Copy the corpus into its new home at the very start, and leave the original in place as the
working reference for as long as anything cites it. At close, archive the original: copy,
repoint every referrer, then delete. Never a bare move while the run is reading it, and never a
pointer stub left behind in place of a file whose referrers you have already repointed — a stub
that nothing points at is just a second copy of the truth waiting to drift.

## 3. The consumers register

The highest-value artifact of the whole exercise, and it costs one table. Any time a task
writes a path that a later phase will rename, it appends a row: the consumer as `file:line`,
what the path points at today, what it must become, why, and which task registered it. Not a
mental note, not a comment in the commit. A row in one file that every phase reads.

A phase closes only when every row is either DONE with the evidence that closed it, or
explicitly RE-REGISTERED for a later phase with the reason it is still open. Nothing is dropped
silently. Many of ours came from a task noticing a consumer in passing while doing something
else, which is exactly the knowledge that evaporates between sessions.

The rows that matter most are the ones a search cannot find: an oblique mention in a handoff
document, a path assembled at runtime from two variables, a comment naming a file without its
extension.

## 4. One move primitive

Every move goes through one function, and the guard is the whole point:

- source exists, destination does not → move
- source gone, destination exists → already done, record it, exit success
- anything else (both present, neither present) → halt, touch nothing

The third branch is what makes a half-finished run safe to re-run. Both present means someone
else has been here, or a previous run was interrupted between the move and the record; neither
present means your row is wrong. Both are questions, not situations to resolve automatically.

Each move appends one manifest row: identifier, old absolute path, new absolute path, kind,
size or file count, and a content hash for files. The hash proves the bytes survived the move,
not anything about the content.

The manifests are the ledger, and the redirects index is *generated* from them, never maintained
by hand. That buys what hand-maintenance never delivers: when a file moves twice, the generator
chains the second move onto the first, so a document citing the original path still resolves.
Ours reached a few thousand rows across a couple of hundred manifests.

## 5. Gates

Two kinds, and they are different in kind, not degree.

**Before a phase that mutates a live tree:** confirm zero other sessions are rooted at it. Not
"probably none" — enumerate them, and if one is there, either wait or record the decision to
proceed and why.

**After:** a cold walk test (an agent with no context, given only the entry file, answering real
questions in a bounded number of reads), a count of top-level entries against the expected
number, and an actual exercise of every consumer you rewrote. Run the job. Open the config. Do
not read the diff and call it verified.

Our first cold walk scored 3 of 4, and the failure was routing, not structure: the entry
document's row for "daemons" sent the reader down a branch that never mentioned the nightly job.
Two cells of one table fixed it. That is the normal outcome. The walk test finds *phrasing*
defects far more often than structural ones, which is why it must be run cold, by something that
has not been reading the plan all week.

Owner gates — merging a pull request, rotating a credential, deleting something — are listed and
waited on. An agent does not execute them quietly because they looked mechanical.

## 6. Worktrees

One convention, written down once: a working copy lives inside its own repository, under a
predictable directory, named for its branch. Never as a sibling of the repository, and never in
a shared scratch area.

Enforce it with a pre-tool hook that inspects the command before it runs and refuses the rest.
Warn everywhere by default; hard-refuse for the repositories you explicitly arm. The reason to
automate it is not tidiness. A working copy outside its repository is invisible to every
per-repository sweep, which is what makes "delete the stray directory" a data-loss event.

For any change to a repository other people share, branch from the freshly fetched trunk
reference, not the local branch of the same name — a local `main` is a bookmark from whenever
someone last pulled. Measure the gap first. Ours was hundreds of commits on one repository, and
a patch authored on that base would not have applied at all.

## 7. Shared-repo hygiene

Work like this produces documents that are useful to collaborators and paths that are nobody
else's business. Both end up in the same commit unless something stops them.

Before every commit that touches a repository other people read, run a grep gate: absolute
home paths, the operator's username, the vocabulary of private shelves and sensitivity tiers,
session identifiers, and the trailers agent tooling appends. The gate needs an allow-list,
because the same string is often the repository's own identifier — a column family, a tracked
filename, a schema name. The rule that survived contact: a hit that is a substring of a real
identifier on the trunk is *listed* and not renamed; a hit in prose is reworded. The gate reads
zero after exclusions, and the exclusions are written down.

The mirror of this rule matters too. Do not document what a given person or role *cannot* do.
Describe the mechanism, not the permission.

## 8. After landing

A restructure decays. Budget for a report, not a repair job.

A nightly job that walks the tree and *reports*, never fixes: stale generated artifacts
(compare by content hash first, only then by rebuild-and-diff), working copies outside the
convention, documents missing required frontmatter, credential-shaped filenames (names only), a
delta against the recorded top-level baseline, and redirect rows whose targets no longer exist.
One headline line — drift count and failure count, both always present — surfaced by a
session-start hook, so the number is in front of someone every morning.

Report failures separately from drift: a step that *failed to run* is not zero drift, and if it
lands in the same number nobody notices the job is broken. And expect the count to be flat, not
zero. Ours settled at 66 items and stayed there across several unattended nights. A steady
number is the signal; a moving one is the alarm.

## 9. What surprised us

**A committed generated artifact can never be "current" by commit identity.** Our graph
generator stamps the commit it was built from, and that stamp is by construction the *parent* of
the commit that adds the graph — the graph is part of the commit. Every consumer testing "built
at equals HEAD" therefore called every real map stale, forever. The fix is to record a content
hash of the parsed source set beside the artifact and test currency by content, which also
survives the many commits that touch no source file at all.

**A rename does not stop at the filesystem.** An agent harness stores the absolute working
directory in its own session state; a CLI stores project links in its own config. Our mover
rewrote both, and its first version still missed about 1,600 subagent transcripts per project
because the walk was capped at two levels, and silently rewrote nothing in one CLI config
because the live schema nested project links a level deeper than the fixture did. A verify pass
that re-searched for the old string found both. No test did.

**A search that bypasses the repository's ignore rules over-matches into agent state.** The
convenient raw grep is not the ignore-aware one, and the difference shows up as hundreds of hits
inside tooling directories you did not mean to touch.

**A hook that reads command text sees the text, not the value.** A guard inspecting
`git worktree add "$DEST"` sees the literal `$DEST` and refuses it. This is correct behaviour
and worth knowing before you write the command.

**Check every claimed fix against the old system's real artifacts.** The recurring failure was
never a wrong fix. It was a *plausible* fix verified against a fixture that had drifted from
production. Read the live file, the live schema, the actual formula. A fix that survives a
genuine attempt to disprove it is the only kind worth landing on something people depend on.
