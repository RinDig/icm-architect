#!/usr/bin/env python3
"""Check that every quoted line appears word for word in its raw source, and that nothing on the
keep-out list appears outside the raw sources. Exit 1 on any problem; read the warnings too.

Copy to _tools/ in a bundle built from sources and run from anywhere:
    python -I _tools/quotes.py [ROOT] [--show-cuts]
ROOT defaults to the folder that holds _tools/. Standard library only.

A quote is  "verbatim line" (key position)  where
  key       names a file in sources/raw/ (its name without the extension, or a short name
            declared in _meta/sources.txt as  key = filename)
  position  a timestamp or range for transcripts (12:30, 1:02:15, 12:30-13:05), or a page or
            page range for documents (page 2, p2, pp 4-5)
Transcripts are timed when their lines start with **[12:30]** or [12:30]; a paragraph's text may sit
on the same line or on the lines below, up to the next timestamp. A document is paged when
it has lines that read  Page 1, Page 2 ... ; any other source is matched anywhere and its position
is not checked. A cut inside a quote is written ... and each piece is checked in order.
A timed quote is accepted within one paragraph of its cited position, since a line can straddle two.
Every bullet under an "In their words" heading must be a cited quote, and a cut must not drop a
negation. Keep-out phrases (_meta/keep-out.txt, one per line, whole words, any case) fail anywhere
outside sources/raw/ and _meta/, frontmatter included; a Hebrew or Arabic phrase also fails with a
prefix attached (ל, ו, ש..., ال, و, ب...). --show-cuts lists what every cut drops.
Matching works in any script: case, accents and Hebrew or Arabic vowel marks are ignored.
"""
import bisect
import re
import sys
import unicodedata
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SKIP_DIRS = {"raw", "_meta", "_tools", "_templates", ".git"}
NOT_NOTES = {"index.md", "_index.md", "log.md", "agents.md", "claude.md", "gemini.md", "context.md"}
TIME = r"\d+(?::\d+)+"
QUOTE = re.compile(r'"([^"\n]+?)"\s*\(([A-Za-z0-9_.-]+)(?:\s+([^)]*))?\)')
ANY_QUOTE = re.compile(r'"([^"\n]+)"')
POSITION = re.compile(rf"({TIME})(?:\s*[–-]\s*({TIME}))?")
PAGE_POSITION = re.compile(r"(?:\bpp?\.?|\bpages?)\s*(\d+)(?:\s*[–-]\s*(\d+))?", re.I)
PAGE_LINE = re.compile(r"^\s*\[?page\s+(\d+)\]?\s*$", re.I)
CITATION_LIKE = re.compile(rf"{TIME}|\bpp?\.?\s*\d+|\bpages?\b|§", re.I)
WORDS_HEADING = re.compile(r"#{1,6}\s*in\s+(their|his|her|the speaker'?s?)\s+words", re.I)
NEGATION = re.compile(r"\b(never|not|no|none|nothing|nobody|without|cannot|neither|nor|hardly|"
                      r"cant|dont|doesnt|didnt|isnt|arent|wasnt|werent|wont|wouldnt|shouldnt|couldnt)\b")

TIMESTAMP_LINE = re.compile(rf"\s*(?:\*\*)?\[({TIME})\](?:\*\*)?\s*(.*)")
# Letters that attach to the front of a word: Hebrew ו ה ב כ ל מ ש, Arabic و ف ب ك ل س and ال.
PREFIXES = {"hebrew": "(?:[ובכלמשה]{1,3})?", "arabic": "(?:[وفبكلس]{0,2}(?:ال)?)?"}

problems, warnings, cuts = [], [], []


def strip_marks(s):
    """Drop accents and vowel marks (niqqud, harakat), so marked and unmarked text match."""
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm(s):
    s = strip_marks(s).casefold().replace("’", "'").replace("'", "")
    return re.sub(r"\s+", " ", re.sub(r"[\W_]+", " ", s)).strip()


def secs(t):
    n = 0
    for part in t.split(":"):
        n = n * 60 + int(part)
    return n


def straighten(text):
    return text.replace("“", '"').replace("”", '"')


def match_in_order(pieces, haystack):
    """Return (missing_piece, gaps): the first piece not found in order, and the text between pieces."""
    pos, gaps = 0, []
    for k, piece in enumerate(pieces):
        i = haystack.find(piece, pos)
        if i < 0:
            return piece, gaps
        if k:
            gaps.append(haystack[pos:i])
        pos = i + len(piece)
    return None, gaps


def load_sources(root):
    raw = root / "sources" / "raw"
    files = {p.stem: p for p in sorted(raw.glob("*")) if p.is_file()} if raw.exists() else {}
    aliases = root / "_meta" / "sources.txt"
    if aliases.exists():
        for line in aliases.read_text(encoding="utf-8-sig").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, name = (x.strip() for x in line.split("=", 1))
                if (raw / name).is_file():
                    files[key] = raw / name
                else:
                    problems.append(f"_meta/sources.txt: {key} -> {name} is not in sources/raw/")
    sources = {}
    for key, path in files.items():
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        paras = []
        for line in text.splitlines():
            m = TIMESTAMP_LINE.match(line)
            if m:
                paras.append([secs(m.group(1)), m.group(2)])
            elif paras:  # text below its timestamp belongs to that paragraph
                paras[-1][1] += " " + line
        if paras:
            sources[key] = ("timed", [(t, norm(words)) for t, words in paras])
            continue
        pages, current = {}, None
        for line in text.splitlines():
            m = PAGE_LINE.match(line)
            if m:
                current = int(m.group(1))
                pages[current] = []
            elif current is not None:
                pages[current].append(line)
        if pages:
            sources[key] = ("paged", {n: norm(" ".join(lines)) for n, lines in pages.items()})
        else:
            sources[key] = ("plain", norm(text))
    return sources


def check_quote(text, key, position, sources):
    """Return (error or None, warning or None, cut gaps)."""
    pieces = [norm(p) for p in re.split(r"\.\.\.|…", text) if norm(p)]
    if not pieces:
        return "the quote has no words to check", None, []
    if len(pieces) > 1 and any(len(p.split()) < 2 for p in pieces):
        return "a piece of a cut quote is too short to verify", None, []
    kind, data = sources[key]
    if kind == "plain":
        missing, gaps = match_in_order(pieces, data)
        return (f"not found in the source: {missing[:60]}" if missing else None), None, gaps
    if kind == "paged":
        m = PAGE_POSITION.search(position or "")
        if not m:
            return "the citation has no page", None, []
        first, last = int(m.group(1)), int(m.group(2) or m.group(1))
        absent = [n for n in range(first, last + 1) if n not in data]
        if absent:
            return f"page {absent[0]} is not in the source", None, []
        missing, gaps = match_in_order(pieces, " ".join(data[n] for n in range(first, last + 1)))
        return (f"not found on the cited page: {missing[:60]}" if missing else None), None, gaps
    m = POSITION.search(position or "")
    if not m:
        return "the citation has no timestamp", None, []
    start, end = secs(m.group(1)), secs(m.group(2) or m.group(1))
    times = [t for t, _ in data]
    lo, hi = bisect.bisect_right(times, start) - 1, bisect.bisect_right(times, end) - 1
    wide = " ".join(p for _, p in data[max(0, lo - 1): hi + 2])
    missing, gaps = match_in_order(pieces, wide)
    if missing:
        return f"not found near that position: {missing[:60]}", None, gaps
    tight = " ".join(p for _, p in data[max(0, lo): hi + 1])
    if match_in_order(pieces, tight)[0]:
        return None, "found in a neighboring paragraph, not the cited one", gaps
    return None, None, gaps


def body_of(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def script_of(phrase):
    for c in phrase:
        name = unicodedata.name(c, "")
        if name.startswith(("HEBREW", "ARABIC")):
            return name.split()[0].lower()
        if c.isalpha():
            return None
    return None


def keep_out_patterns(root):
    """Whole-word patterns, matched against text with its marks stripped."""
    path = root / "_meta" / "keep-out.txt"
    lines = (strip_marks(x.strip()) for x in path.read_text(encoding="utf-8-sig").splitlines()) if path.exists() else ()
    return [re.compile(r"(?<!\w)" + PREFIXES.get(script_of(p), "") + re.escape(p) + r"(?!\w)", re.I)
            for p in lines if p and not p.startswith("#")]


def check_words_sections(rel, body, sources):
    """Every bullet under 'In their words' must be a cited quote."""
    inside = False
    for line in straighten(body).splitlines():
        if line.lstrip().startswith("#"):
            inside = bool(WORDS_HEADING.match(line.strip()))
            continue
        if inside and re.match(r"\s*[-*]\s", line):
            if not any(m.group(2) in sources for m in QUOTE.finditer(line)):
                problems.append(f"{rel}: a bullet under 'In their words' has no cited quote: {line.strip()[:60]}")


def main():
    args = [a for a in sys.argv[1:] if a != "--show-cuts"]
    root = Path(args[0]).resolve() if args else Path(__file__).resolve().parent.parent
    sources = load_sources(root)
    keep_out = keep_out_patterns(root)

    files = sorted(f for f in root.rglob("*.md") if not SKIP_DIRS & set(f.relative_to(root).parts))
    notes, quotes = 0, 0
    for f in files:
        rel = f.relative_to(root).as_posix()
        text = f.read_text(encoding="utf-8-sig", errors="replace")
        if keep_out and any(p.search(strip_marks(text)) for p in keep_out):  # every file, frontmatter included
            problems.append(f"{rel}: contains a phrase from _meta/keep-out.txt")
        if f.name.lower() in NOT_NOTES:
            continue
        notes += 1
        body = body_of(text)
        check_words_sections(rel, body, sources)
        text_q, cited = straighten(body), set()
        for m in QUOTE.finditer(text_q):
            quote, key, position = m.group(1), m.group(2), m.group(3)
            cited.add(m.start())
            if key not in sources:
                if CITATION_LIKE.search(position or ""):
                    problems.append(f"{rel}: unknown source key '{key}' for: {quote[:50]}")
                continue
            quotes += 1
            error, warn, gaps = check_quote(quote, key, position, sources)
            where = f"{rel} ({key} {position or ''})".replace(" )", ")")
            if error:
                problems.append(f"{where}: {error}")
            if warn:
                warnings.append(f"{where}: {warn}")
            if "..." in quote or "…" in quote:
                cuts.append((where, quote, gaps))
                dropped = [g for g in gaps if NEGATION.search(g)]
                if dropped and not error:
                    problems.append(f"{where}: a cut drops a negation: ...{dropped[0][:60]}...")
        for m in ANY_QUOTE.finditer(text_q):
            if m.start() not in cited and len(m.group(1).split()) >= 8:
                warnings.append(f"{rel}: quoted words with no citation: {m.group(1)[:60]}")

    print(f"{notes} notes, {quotes} quotes checked, {len(cuts)} with cuts")
    if "--show-cuts" in sys.argv:
        for where, quote, gaps in cuts:
            print(f"  cut in {where}: \"{quote[:80]}\" drops: " + " | ".join(g[:50] for g in gaps))
    if warnings:
        print(f"{len(warnings)} warning(s), read them:")
        for w in warnings:
            print("  " + w)
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("ok: every quote matches its source")


if __name__ == "__main__":
    main()
