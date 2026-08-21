# {Workspace name} — the pipeline

The flow in one line: {plan it, make it, check it, ship it — in your workspace's words}.

| Stage | Job | Input | Output | Human check |
|---|---|---|---|---|
| `01_{name}` | {five words} | {what it reads} | `output/{file}` | {what a person verifies} |
| `02_{name}` | {five words} | 01's output | `output/{file}` | {what a person verifies} |
| `03_{name}` | {five words} | 02's output | `output/{file}` | {what a person verifies} |

Factory (stable, every run): `_shared/{voice.md, rules.md, …}`
Product (new each run): each stage's `output/`

Status is whatever exists: a stage is COMPLETE when its `output/` holds an artifact — a placeholder that only keeps the empty folder in git does not count.
