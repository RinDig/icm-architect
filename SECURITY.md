# Security and access

## Workspace and tool scope

Use this skill only with a workspace root and input/output paths approved by the owner. Its build and restructure workflows read source files and create or update workspace files. Restructuring can also move or remove originals after the existing approval, backup and parity checks in `SKILL.md`.

The optional Python scripts read local content and may write indexes, graph data and HTML. Review a script and its exact arguments before running it. Resolve symlinks and paths outside the workspace with the owner rather than treating a reference as access approval. Do not read credentials or unrelated home-directory files.

Enforce path restrictions and tool permissions in the host runtime or sandbox. Documentation is not an access-control mechanism. In Agent Skills clients, `allowed-tools` may preapprove tools; it is not a portable permission ceiling. This contribution deliberately does not add broad tool grants merely to satisfy a scanner.

## Visualization dependencies and sensitive content

The Python generator `scripts/viz.py` uses the standard library. Its generated HTML loads these version-pinned browser dependencies from jsDelivr:

- Cytoscape.js 3.28.1: `https://cdn.jsdelivr.net/npm/cytoscape@3.28.1/dist/cytoscape.min.js`
- marked 12.0.0: `https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js`

Generating the HTML and opening it in a browser are separate actions. Opening it requires network access to the CDN. The generated HTML embeds note bodies and metadata; loaded third-party JavaScript runs in that page and can access its contents. Version pinning is not the same as a verified integrity hash, and the current script tags have no Subresource Integrity attributes.

Treat generated HTML as a copy of its source content with the same confidentiality requirements. Do not publish or share it without approval. For sensitive or untrusted input, skip the interactive viewer and use the plain Markdown/index/graph files, or have the owner review an offline, locally vendored viewer first. An offline viewer is not implemented by this documentation change. The current viewer renders Markdown into HTML without a sanitization layer; it should not be treated as a safe renderer for adversarial content.

## Static scan observation — 26 October 2026

This is a contributor observation, not maintainer certification or an installation approval.

| Field | Observed value |
| --- | --- |
| Repository revision | `8bc2f5610d3843b3ffa31a142effe6b6337fef3c` (before this documentation change) |
| Scanner | NVIDIA SkillSpector 2.12.0 |
| Mode | Static only, `--no-llm` |
| Risk assessment | 14/100, LOW; recommendation CAUTION |
| Findings | Two MEDIUM-severity findings; no suppressions |
| Bounded component coverage | 26/26 components inspected |
| Overall completeness | Partial: 14 unresolved local path-like references |
| LLM-assisted or behavioral evaluation | Not performed |

The original scan ran against a shallow checkout, including local Git metadata under the scanner's bounded profile. VCS object/history files were excluded by that profile. The report's 100% bounded component coverage does not mean complete semantic or runtime coverage.

### Finding interpretation

- **LP3 — undeclared tool scope:** the scanner detected file-read, file-write and network capabilities without a `permissions` or `allowed-tools` declaration. The scope guidance above makes intended use explicit, but actual host enforcement remains unverified. This is not evidence of exfiltration, nor does prose fix runtime permissions.
- **EA2 — "without asking":** the match was the original `SKILL.md` line 53: "Who else touches this, and what do they need to find without asking you?" In context it asks about discoverability for colleagues, not autonomous high-impact action. The contributor considers this a likely false positive. The sentence is unchanged and no scanner suppression was added.

Unresolved path-like references may describe files produced when the skill scaffolds a workspace; they are not automatically missing packaged dependencies. Each requires contextual review. Static scanning cannot establish that a skill is safe to install or that host permissions are enforced.

### Reproduce

With SkillSpector already installed in an isolated environment, scan a checkout of the exact revision above:

```sh
skillspector --version
skillspector scan /path/to/icm-architect --no-llm --format json --output report.json
```

Inspect `risk_assessment`, `issues` and `analysis_completeness`, not just the exit code. SkillSpector can return exit code 0 for CAUTION. This observation is pinned to the original source and scanner version; it is not a claim about later revisions, including this contribution.
