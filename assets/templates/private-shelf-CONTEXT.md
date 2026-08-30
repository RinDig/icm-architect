# _private — the sensitivity shelf

Last updated: YYYY-MM-DD HH:MM TZ   ·   mode 700   ·   owner: the human only

## The load rule (binding on every agent and every account that can reach this tree)
1. Nothing under this shelf is loaded unless the current task names the file.
2. **Tier 0 files are never opened by an agent.** Report path and kind only. Rotation, pasting, and copying of a credential are human acts.
3. Tier 1 and Tier 2 files may be read only when the task requires their content, and their content is never quoted outward — not into Slack, a PR, a commit message, a doc, an artifact, a memory file, or a transcript summary. Report aggregates, never rows.
4. Never infer from this shelf. A fact learned here is not carried into another context unless the owner says so.
5. Nothing here is deleted by an agent. Superseded items stay; the owner deletes.

## Tiers
| Tier | Folder | Holds |
|---|---|---|
| T0 | `credentials/` | env files, token snapshots, gate credentials, `.bak` copies of credential files |
| T1 | `people/` | PINs, HR rosters, onboarding drafts that carried credentials |
| T2 | `financial/` | raw customer/financial exports (accounting-system extracts, invoices, sales YTD) |

## Credential register — stores that stay in place (path · kind · owner tool)
Agents may `ls -la` these to confirm existence; never `cat`.
| Path | Kind | Owner tool |
|---|---|---|
| <path> | <kind> | <owner tool> |
