#!/usr/bin/env python3
"""Draw one or more graph files written by links.py into one viz.html.

    python -I _tools/viz.py graph.jsonl [more.jsonl ...] [-o viz.html] [--all-bodies]

Writes viz.html beside the first graph file unless -o names another path. Standard library only.
The page loads cytoscape, marked and DOMPurify from jsDelivr, pinned by integrity hash, so viewing
it needs the internet. Note HTML is sanitized before it is shown.
- A note whose access_tier is set to anything but public keeps its body out of the page (its node,
  title and links stay); --all-bodies puts every body in.
- A node is a .md file; catalogs and logs (AGENTS.md and its pointers, index.md, _index.md,
  log.md) are left out because they link to everything.
- Colors follow the frontmatter type, most common type first. The first node shown is the
  most-linked one.
- Draw several graph files together and the links between them become edges.
"""
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PALETTE = ["#1d4ed8", "#15803d", "#c2410c", "#7e22ce", "#b45309", "#0e7490",
           "#b91c1c", "#0f766e", "#ea580c", "#475569", "#be185d", "#4d7c0f"]
CATALOGS = {"agents.md", "claude.md", "gemini.md", "index.md", "_index.md", "log.md"}
PUBLIC_TIERS = {"", "public"}
LINK = re.compile(r"""\[([^\]]*)\]\((<[^>]+>|[^)\s]+)(?:\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?\s*\)""")


def script_safe(value):
    """JSON that can sit inside a <script> block: no '<' can open or close a tag."""
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


def load(path):
    root, nodes, edges = None, [], []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            item = json.loads(line)
            if "root" in item:
                root = (path.resolve().parent / item["root"]).resolve()  # relative to the graph file
            elif "node" in item:
                nodes.append(item)
            elif "edge" in item:
                edges.append(item["edge"])
    return root, nodes, edges


def body_of(path):
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def heading_of(path):
    if path.exists():
        for line in body_of(path).splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return ""


def main():
    args = sys.argv[1:]
    out, all_bodies = None, "--all-bodies" in args
    args = [a for a in args if a != "--all-bodies"]
    if "-o" in args:
        i = args.index("-o")
        out = Path(args[i + 1]).resolve()
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    graphs = [load(Path(a)) for a in args]
    out = out or Path(args[0]).resolve().parent / "viz.html"
    many = len(graphs) > 1

    folders = [root.name for root, _, _ in graphs]
    ids, nodes, names, withheld = {}, [], [], {}
    for root, items, _ in graphs:
        names.append(heading_of(root / "AGENTS.md") or heading_of(root / "CLAUDE.md") or heading_of(root / "index.md") or root.name)
        prefix = root.name if folders.count(root.name) == 1 else f"{root.parent.name}/{root.name}"
        for n in items:
            if Path(n["node"]).name.lower() in CATALOGS:
                continue
            nid = (f"{prefix}/" if many else "") + n["node"][:-3]
            ids[(root / n["node"]).resolve()] = nid
            tier = (n.get("access_tier") or "").strip().lower()
            if tier not in PUBLIC_TIERS and not all_bodies:
                withheld[nid] = tier
            tags = [t.strip() for t in (n.get("tags") or "").strip("[]").split(",") if t.strip()]
            nodes.append({"data": {"id": nid, "label": n["title"], "type": n["type"] or "untyped",
                                   "description": n["description"], "tags": tags, "size": 30,
                                   "resource": Path(os.path.relpath(root / n["node"], out.parent)).as_posix()}})

    edges = set()
    for root, _, items in graphs:
        for a, b in items:
            src, dst = ids.get((root / a).resolve()), ids.get((root / b).resolve())
            if src and dst and src != dst:
                edges.add((src, dst))

    def rewrite(file):
        def fix(m):
            label, target = m.group(1), m.group(2)
            raw = target[1:-1] if target.startswith("<") else target
            if re.match(r"^[a-z]+:", raw) or raw.startswith("#"):
                return m.group(0)
            path = (file.parent / urllib.parse.unquote(raw.split("#")[0])).resolve()
            if path in ids:
                return f"[{label}](/{ids[path]}.md)"
            if path.exists():
                return f"[{label}]({urllib.parse.quote(Path(os.path.relpath(path, out.parent)).as_posix())})"
            return m.group(0)
        return LINK.sub(fix, body_of(file))

    bodies = {nid: f"*Body left out: access_tier is {withheld[nid]}. Rerun viz.py with --all-bodies to include it.*"
              if nid in withheld else rewrite(path) for path, nid in ids.items()}

    degree = {}
    for s, t in edges:
        degree[s] = degree.get(s, 0) + 1
        degree[t] = degree.get(t, 0) + 1
    top = max(degree.values(), default=1)
    counts = {}
    for n in nodes:
        n["data"]["size"] = round(16 + 26 * (degree.get(n["data"]["id"], 0) / top) ** 0.5)
        counts[n["data"]["type"]] = counts.get(n["data"]["type"], 0) + 1
    types = sorted(counts, key=lambda t: (-counts[t], t))
    palette = {t: PALETTE[i % len(PALETTE)] for i, t in enumerate(types)}
    for n in nodes:
        n["data"]["color"] = palette[n["data"]["type"]]
    nodes.sort(key=lambda n: (types.index(n["data"]["type"]), n["data"]["id"]))

    bundle = {"nodes": nodes, "bodies": bodies, "types": types, "palette": palette,
              "edges": [{"data": {"id": f"{s}__{t}", "source": s, "target": t}} for s, t in sorted(edges)],
              "root": max(degree, key=degree.get) if degree else (nodes[0]["data"]["id"] if nodes else "")}
    values = {"__NAME__": script_safe(" + ".join(names)), "__DATA__": script_safe(bundle)}
    html = re.sub(r"__NAME__|__DATA__", lambda m: values[m.group(0)], SHELL)  # one pass: a value can't hold a token
    with out.open("w", encoding="utf-8", newline="\n") as f:  # Python 3.9 has no write_text(newline=)
        f.write(html)
    print(f"wrote {out.name}: {len(nodes)} nodes, {len(edges)} edges")
    if withheld:
        print(f"left out {len(withheld)} non-public bodies (access_tier); --all-bodies includes them")


SHELL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Graph</title>
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.28.1/dist/cytoscape.min.js" integrity="sha384-J7Q85oZE4GJ/e7+n2aOQsLXfDwwfnA8S2nZAL5BpFsfpCF84zQD7LroZ/dMnLgex" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js" integrity="sha384-NNQgBjjuhtXzPmmy4gurS5X7P4uTt1DThyevz4Ua0IVK5+kazYQI1W27JHjbbxQz" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.1.6/dist/purify.min.js" integrity="sha384-+VfUPEb0PdtChMwmBcBmykRMDd+v6D/oFmB3rZM/puCMDYcIvF968OimRh4KQY9a" crossorigin="anonymous"></script>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  font-size: 14px;
  color: #0f172a;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  height: 100vh;
}
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}
.title strong { font-size: 16px; margin-right: 8px; }
.muted { color: #64748b; font-size: 12px; }
.controls { display: flex; gap: 8px; }
.controls input, .controls select, .controls button {
  font-size: 13px;
  padding: 5px 8px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  background: #fff;
}
.controls input { width: 220px; }
.controls button { cursor: pointer; background: #f1f5f9; }
.controls button:hover { background: #e2e8f0; }

main {
  display: flex;
  flex: 1;
  min-height: 0;
}
#graph {
  flex: 1 1 60%;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  min-width: 0;
  position: relative;
}
#detail {
  flex: 0 0 40%;
  overflow-y: auto;
  padding: 18px 22px;
  background: #fff;
}
#detail-empty {
  text-align: center;
  margin-top: 40px;
}

.detail-header { margin-bottom: 12px; }
.detail-header h1 {
  font-size: 18px;
  margin: 4px 0 2px;
  font-weight: 600;
}
.type-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  background: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
dl.frontmatter {
  display: grid;
  grid-template-columns: 90px 1fr;
  row-gap: 4px;
  column-gap: 12px;
  margin: 8px 0 12px;
  font-size: 13px;
}
dl.frontmatter dt {
  color: #64748b;
  font-weight: 500;
}
dl.frontmatter dd { margin: 0; }
dl.frontmatter a { color: #2563eb; word-break: break-all; }

.tag {
  display: inline-block;
  padding: 1px 6px;
  margin: 0 4px 2px 0;
  border-radius: 4px;
  background: #f1f5f9;
  color: #475569;
  font-size: 11px;
}

hr { border: none; border-top: 1px solid #e2e8f0; margin: 14px 0; }

#detail-body { font-size: 13px; line-height: 1.55; }
#detail-body h1 {
  font-size: 16px; margin: 18px 0 6px;
  padding-bottom: 4px; border-bottom: 1px solid #e2e8f0;
}
#detail-body h2 { font-size: 14px; margin: 14px 0 4px; }
#detail-body h3 { font-size: 13px; margin: 12px 0 4px; }
#detail-body p { margin: 6px 0; }
#detail-body code {
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 12px;
  font-family: ui-monospace, "SF Mono", Consolas, monospace;
}
#detail-body pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 10px 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12px;
}
#detail-body pre code { background: transparent; color: inherit; padding: 0; }
#detail-body ul, #detail-body ol { padding-left: 22px; margin: 6px 0; }
#detail-body li { margin: 2px 0; }
#detail-body table { border-collapse: collapse; margin: 8px 0; }
#detail-body th, #detail-body td {
  border: 1px solid #e2e8f0; padding: 4px 8px; font-size: 12px;
}
#detail-body a.internal { color: #2563eb; cursor: pointer; }
#detail-body a.external { color: #2563eb; }

#detail-backlinks { margin-top: 18px; }
#detail-backlinks h2 { font-size: 13px; color: #64748b; margin-bottom: 6px; }
#detail-backlinks ul { padding-left: 18px; }
#detail-backlinks a { color: #2563eb; cursor: pointer; }

</style>
</head>
<body>
<header>
  <div class="title">
    <strong id="bundle-name"></strong>
    <span class="muted">markdown graph</span>
  </div>
  <div class="controls">
    <input id="search" type="search" placeholder="Search title / id / tag">
    <select id="filter-type">
      <option value="">All types</option>
    </select>
    <select id="layout">
      <option value="cose">cose (force)</option>
      <option value="concentric">concentric</option>
      <option value="breadthfirst">breadth-first</option>
      <option value="circle">circle</option>
      <option value="grid">grid</option>
    </select>
    <button id="reset">Reset view</button>
  </div>
</header>

<main>
  <section id="graph"></section>
  <section id="detail">
    <div id="detail-empty" class="muted">Click a node to see its details.</div>
    <article id="detail-content" hidden>
      <header class="detail-header">
        <span class="type-chip" id="detail-type"></span>
        <h1 id="detail-title"></h1>
        <div class="muted" id="detail-id"></div>
      </header>
      <dl class="frontmatter">
        <dt>Description</dt><dd id="detail-description"></dd>
        <dt>Resource</dt><dd id="detail-resource"></dd>
        <dt>Tags</dt><dd id="detail-tags"></dd>
      </dl>
      <hr>
      <div id="detail-body"></div>
      <section id="detail-backlinks" hidden>
        <h2>Cited by</h2>
        <ul id="backlinks-list"></ul>
      </section>
    </article>
  </section>
</main>

<script>
window.BUNDLE_NAME = __NAME__;
window.BUNDLE = __DATA__;
</script>
<script>
(function () {
  const bundle = window.BUNDLE;
  const bundleName = window.BUNDLE_NAME;
  document.title = `${bundleName} — graph`;
  document.getElementById("bundle-name").textContent = bundleName;

  // Populate type filter
  const typeSelect = document.getElementById("filter-type");
  for (const t of bundle.types) {
    const opt = document.createElement("option");
    opt.value = t;
    opt.textContent = t;
    typeSelect.appendChild(opt);
  }

  // Build reverse-link index for backlinks
  const backlinks = {};
  for (const edge of bundle.edges) {
    const { source, target } = edge.data;
    (backlinks[target] ||= []).push(source);
  }

  // Look up node label/type by id
  const nodeIndex = {};
  for (const n of bundle.nodes) nodeIndex[n.data.id] = n.data;

  const cy = cytoscape({
    container: document.getElementById("graph"),
    elements: [...bundle.nodes, ...bundle.edges],
    style: [
      {
        selector: "node",
        style: {
          "background-color": "data(color)",
          "label": "data(label)",
          "color": "#0f172a",
          "font-size": 11,
          "text-valign": "bottom",
          "text-margin-y": 4,
          "text-wrap": "wrap",
          "text-max-width": 120,
          "width": "data(size)",
          "height": "data(size)",
          "border-width": 1,
          "border-color": "#0f172a",
        },
      },
      {
        selector: "node:selected",
        style: {
          "border-width": 3,
          "border-color": "#f59e0b",
        },
      },
      {
        selector: "edge",
        style: {
          "width": 1.5,
          "line-color": "#cbd5e1",
          "target-arrow-color": "#cbd5e1",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          "arrow-scale": 0.9,
        },
      },
      {
        selector: "edge:selected",
        style: {
          "line-color": "#f59e0b",
          "target-arrow-color": "#f59e0b",
          "width": 2.5,
        },
      },
      {
        selector: ".dim",
        style: { "opacity": 0.15 },
      },
    ],
    layout: { name: "cose", animate: false, padding: 30 },
    wheelSensitivity: 0.2,
  });

  cy.on("tap", "node", (evt) => showDetail(evt.target.id()));
  cy.on("tap", (evt) => {
    if (evt.target === cy) clearSelection();
  });

  document.getElementById("layout").addEventListener("change", (e) => {
    cy.layout({ name: e.target.value, animate: false, padding: 30 }).run();
  });

  document.getElementById("reset").addEventListener("click", () => {
    cy.fit(null, 30);
    clearSelection();
  });

  document.getElementById("search").addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    if (!q) {
      cy.elements().removeClass("dim");
      return;
    }
    cy.nodes().forEach((n) => {
      const d = n.data();
      const hay =
        (d.label || "").toLowerCase() + " " +
        d.id.toLowerCase() + " " +
        (d.tags || []).join(" ").toLowerCase();
      n.toggleClass("dim", !hay.includes(q));
    });
    cy.edges().forEach((edge) => {
      const src = edge.source();
      const tgt = edge.target();
      edge.toggleClass("dim", src.hasClass("dim") || tgt.hasClass("dim"));
    });
  });

  document.getElementById("filter-type").addEventListener("change", (e) => {
    const t = e.target.value;
    if (!t) {
      cy.elements().removeClass("dim");
      return;
    }
    cy.nodes().forEach((n) => {
      n.toggleClass("dim", n.data("type") !== t);
    });
    cy.edges().forEach((edge) => {
      edge.toggleClass("dim", edge.source().hasClass("dim") || edge.target().hasClass("dim"));
    });
  });

  function clearSelection() {
    cy.elements().unselect();
    document.getElementById("detail-empty").hidden = false;
    document.getElementById("detail-content").hidden = true;
  }

  function showDetail(conceptId) {
    const data = nodeIndex[conceptId];
    if (!data) return;
    cy.elements().unselect();
    const node = cy.getElementById(conceptId);
    if (node) node.select();

    document.getElementById("detail-empty").hidden = true;
    const content = document.getElementById("detail-content");
    content.hidden = false;

    const chip = document.getElementById("detail-type");
    chip.textContent = data.type;
    chip.style.background = data.color;

    document.getElementById("detail-title").textContent = data.label;
    document.getElementById("detail-id").textContent = conceptId;
    document.getElementById("detail-description").textContent = data.description || "—";

    const resourceEl = document.getElementById("detail-resource");
    resourceEl.innerHTML = "";
    if (data.resource) {
      const a = document.createElement("a");
      a.href = data.resource;
      a.textContent = data.resource;
      a.target = "_blank";
      a.rel = "noopener";
      a.className = "external";
      resourceEl.appendChild(a);
    } else {
      resourceEl.textContent = "—";
    }

    const tagsEl = document.getElementById("detail-tags");
    tagsEl.innerHTML = "";
    if (data.tags && data.tags.length) {
      for (const t of data.tags) {
        const span = document.createElement("span");
        span.className = "tag";
        span.textContent = t;
        tagsEl.appendChild(span);
      }
    } else {
      tagsEl.textContent = "—";
    }

    const body = bundle.bodies[conceptId] || "";
    const bodyEl = document.getElementById("detail-body");
    bodyEl.innerHTML = DOMPurify.sanitize(marked.parse(body, { breaks: false, gfm: true }));
    rewriteInternalLinks(bodyEl);

    const bl = backlinks[conceptId] || [];
    const blSection = document.getElementById("detail-backlinks");
    const blList = document.getElementById("backlinks-list");
    blList.innerHTML = "";
    if (bl.length) {
      blSection.hidden = false;
      for (const src of bl) {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.textContent = nodeIndex[src]?.label || src;
        a.dataset.target = src;
        a.addEventListener("click", () => showDetail(src));
        li.appendChild(a);
        const muted = document.createElement("span");
        muted.className = "muted";
        muted.textContent = ` (${src})`;
        li.appendChild(muted);
        blList.appendChild(li);
      }
    } else {
      blSection.hidden = true;
    }

    cy.animate({ center: { eles: node }, zoom: Math.max(cy.zoom(), 1.0) }, { duration: 200 });
  }

  function rewriteInternalLinks(root) {
    root.querySelectorAll("a[href]").forEach((a) => {
      const href = a.getAttribute("href");
      if (!href) return;
      if (href.startsWith("/") && href.endsWith(".md")) {
        const target = href.slice(1, -3);
        if (nodeIndex[target]) {
          a.className = "internal";
          a.setAttribute("href", "javascript:void(0)");
          a.addEventListener("click", (e) => {
            e.preventDefault();
            showDetail(target);
          });
          return;
        }
      }
      a.className = "external";
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener");
    });
  }

  // Show the most-linked node first
  const initial =
    bundle.nodes.find((n) => n.data.id === bundle.root) ||
    bundle.nodes[0];
  if (initial) showDetail(initial.data.id);
})();

</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
