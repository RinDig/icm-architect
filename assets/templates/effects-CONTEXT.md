<!-- TEMPLATE for <repo>/map/effects/CONTEXT.md — the change-impact index. This is a
     CATALOG of which cards to open, NOT a second copy of their waterfalls. Never create it
     empty. Placeholders: {REPO}. Delete this comment when you fill it in. -->
# If you are changing X, open these

This is an index, not an analysis. It answers "where do I start reading" in one line
and then gets out of the way — the actual Hits / Does not hit lives on the card, and
the exhaustive fan-in lives in `../graph/<path>.md`. **If this file and a card
disagree, the CARD is authoritative and this file is the bug.**

Entries are phrased as the change an editor is about to make, in their words.

| if you are changing… | open these cards first | and this graph node | does not hit (first-order) |
|---|---|---|---|
| {a concrete change, e.g. "the format of a location id"} | `../objects/{cluster}/{noun}.md`, then `../objects/{cluster}/{neighbour}.md` | {the graph node for fan-in, a pinned golden test, a mirrored grammar in another module} | {the obvious wrong next noun — one clause, a pointer, never a waterfall} |
| {a table's columns} | `../objects/{cluster}/{table}.md` | {every writer named under Surfaces; whether another repo owns the object} | {a look-alike table or view this change does NOT reach} |
| {a shared registry or contract} | `../objects/{cluster}/{registry}.md` | {the test that fails on an unregistered entry} | {a neighbouring registry this one is never cross-wired to} |

The last column names the obvious wrong next noun — one clause, a pointer, never a
waterfall.

## What belongs here

- A change that reaches further than the file you are editing. That is the whole bar.
- Changes that LOOK local and are not: a shared grammar mirrored in two modules, a
  registry with a completeness test, a column two repos read, a value that must stay
  byte-identical on both sides of an index or a cache key.

## What does not

- Anything the graph already answers mechanically ("who imports this file").
- A waterfall copied off a card. Link the card.
- A change that touches one file and nothing else.

Last updated: YYYY-MM-DD HH:MM TZ
