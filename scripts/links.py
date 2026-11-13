#!/usr/bin/env python3
"""List every relative link and input path that does not resolve. Exit 1 if there are any.

Copy to _tools/ in a workspace and run from anywhere:
    python -I _tools/links.py [ROOT] [--skip FOLDER ...] [--graph FILE]
ROOT defaults to the folder that holds _tools/. Standard library only.

Checks every .md file outside dot-folders, node_modules/, _archive/, _templates/, raw/ and any
folder named with --skip:
  - markdown links [text](path), .md paths in consumes: / produces: frontmatter, and import
    lines such as @AGENTS.md (the one-line pointers CLAUDE.md and GEMINI.md hold).
    Web links, #anchors, {placeholders} and [[wikilinks]] are not checked.
  - backticked paths in list items under an Inputs heading, relative to the file or to ROOT.
    A reference (every-run) input must exist; any other input passes if its folder exists,
    since this run's output may not be made yet.
Fenced code blocks are skipped. Inside a git repository, untracked files that git ignores are
left out too.

--graph FILE also writes the graph it walked, one JSON object per line: first the root (relative
to FILE), then each file (path, type, title, description, tags) and each link between .md files.
viz.py draws it.
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SKIP = {"node_modules", "_archive", "_templates", "raw"}
LINK = re.compile(r"\[[^\]]*\]\((<[^>]+>|[^)\s]+)\)")
TICK = re.compile(r"`([^`\s]+)`")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK_KEYS = re.compile(r"^(?:consumes|produces):\s*(.+)$", re.M)
IMPORT = re.compile(r"^@(\S+\.md)\s*$")


def front_matter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end], text[end + 4:]
    return "", text


def field(front, name):
    m = re.search(rf"^{name}:\s*(.+)$", front, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    if v[:1] not in "\"'":
        v = re.split(r"\s+#", v, maxsplit=1)[0]  # drop a YAML comment
    if len(v) > 1 and v[0] == v[-1] == '"':
        try:
            return json.loads(v)  # YAML double quotes allow \u escapes
        except ValueError:
            return v[1:-1]
    return v[1:-1] if len(v) > 1 and v[0] == v[-1] == "'" else v


def lines_outside_fences(body):
    fence = None
    for line in body.splitlines():
        s = line.lstrip()
        if s.startswith("```") or s.startswith("~~~"):
            mark = s[:3]
            fence = None if fence == mark else (fence or mark)
            continue
        if fence is None:
            yield line


def git_ignored(root, files):
    """The files git ignores and does not track. Empty outside a git repository or without git."""
    if not files:
        return set()
    names = "\0".join(f.relative_to(root).as_posix() for f in files) + "\0"
    try:
        r = subprocess.run(["git", "-C", str(root), "check-ignore", "-z", "--stdin"],
                           input=names.encode("utf-8"), capture_output=True)
    except OSError:  # git not installed
        return set()
    if r.returncode not in (0, 1):  # 128: not a git repository
        return set()
    return {root / n for n in r.stdout.decode("utf-8").split("\0") if n}


def looks_like_path(s):
    if any(c in s for c in "{}<>*?|") or re.match(r"^[a-z]+:", s):
        return False
    return "/" in s or bool(re.search(r"\.\w{1,5}$", s))


def main():
    args, skip, graph_out = sys.argv[1:], set(SKIP), None
    while "--skip" in args:
        i = args.index("--skip")
        skip.add(args[i + 1])
        del args[i:i + 2]
    if "--graph" in args:
        i = args.index("--graph")
        graph_out = Path(args[i + 1]).resolve()
        del args[i:i + 2]
    root = Path(args[0]).resolve() if args else Path(__file__).resolve().parent.parent

    files = sorted(f for f in root.rglob("*.md")
                   if not any(p.startswith(".") or p in skip for p in f.relative_to(root).parts[:-1]))
    ignored = git_ignored(root, files)
    files = [f for f in files if f not in ignored]
    broken, nodes, edges, checked = [], [], [], 0

    def link(f, rel, target):
        nonlocal checked
        if re.match(r"^[a-z]+:", target) or target.startswith("#") or "{" in target:
            return  # web link, anchor, or a template's {placeholder}
        checked += 1
        path = (f.parent / urllib.parse.unquote(target.split("#")[0])).resolve()
        if not path.exists():
            broken.append(f"{rel}: {target}")
        elif path.suffix == ".md" and path != f.resolve():
            try:
                edges.append((rel, Path(os.path.relpath(path, root)).as_posix()))
            except ValueError:  # another drive
                pass

    for f in files:
        rel = f.relative_to(root).as_posix()
        front, body = front_matter(f.read_text(encoding="utf-8-sig", errors="replace"))
        for m in LINK_KEYS.finditer(front):
            for target in re.findall(r"[^\s\[\],\"']+\.md\b", m.group(1)):
                link(f, rel, target)
        title = field(front, "title")
        in_inputs = False
        for line in lines_outside_fences(body):
            h = HEADING.match(line)
            if h:
                in_inputs = h.group(2).strip().lower() == "inputs"
                title = title or (h.group(2) if h.group(1) == "#" else "")
                continue
            imp = IMPORT.match(line.strip())
            if imp and not re.match(r"^(~|/|[A-Za-z]:)", imp.group(1)):  # home or absolute paths aren't the tree's
                link(f, rel, imp.group(1))
            for m in LINK.finditer(line):
                link(f, rel, m.group(1)[1:-1] if m.group(1).startswith("<") else m.group(1))
            if in_inputs and re.match(r"\s*[-*]\s", line):
                strict = "reference" in line.lower()  # every-run inputs must already exist
                for m in TICK.finditer(line):
                    p = m.group(1)
                    if not looks_like_path(p):
                        continue
                    checked += 1
                    hits = [(f.parent / p).resolve(), (root / p).resolve()]
                    if not any(h.exists() or (not strict and h.parent.is_dir()) for h in hits):
                        broken.append(f"{rel}: input `{p}`")
        nodes.append({"node": rel, "type": field(front, "type"), "title": title or f.stem,
                      "description": field(front, "description"), "tags": field(front, "tags")})

    if graph_out:
        try:
            where = Path(os.path.relpath(root, graph_out.parent)).as_posix()
        except ValueError:  # another drive
            where = root.as_posix()
        with graph_out.open("w", encoding="utf-8", newline="\n") as out:
            out.write(json.dumps({"root": where}) + "\n")
            for n in nodes:
                out.write(json.dumps(n, ensure_ascii=False) + "\n")
            for a, b in dict.fromkeys(edges):
                out.write(json.dumps({"edge": [a, b]}, ensure_ascii=False) + "\n")

    for b in broken:
        print(b)
    print(f"{len(files)} files, {checked} links and inputs checked, {len(broken)} broken")
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
