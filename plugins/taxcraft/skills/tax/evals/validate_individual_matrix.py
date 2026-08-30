#!/usr/bin/env python3
"""Regression fixtures for the individual/ module set.

Every entry in individual-regression-matrix.json pins one proposition that a
review caught as wrong or missing. This checker fails if a proposition has been
deleted, reverted to its known-wrong formulation, or stripped of the
point-of-use marker required by authority.md.

Its purpose is to make editorial passes safe: cut freely, then run this. The
documented failure mode of the first cut was that caps and predicates were
removed while the mechanics they constrain were kept, leaving files that read
complete and produce unbounded numbers. Those caps are fixtures here.

Usage:
    python3 -B evals/validate_individual_matrix.py
    python3 -B evals/validate_individual_matrix.py --report   # matrix as a table
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = Path(__file__).resolve().parent / "individual-regression-matrix.json"

WARN = "⚠"


# Block structure comes from a real CommonMark parser. Five consecutive
# hand-rolled scanners were each broken by a construct they did not model
# (blockquoted ordered lists, nested fences, sibling subtrees, quote-vs-indent
# flattening, setext headings, indented code, hard tabs). Parsing is the fix.
try:
    from markdown_it import MarkdownIt
except ModuleNotFoundError:  # fail closed — never silently fall back to a weaker scanner
    print(
        "FAIL: markdown-it-py is required for block scoping.\n"
        "      pip install markdown-it-py",
        file=sys.stderr,
    )
    raise SystemExit(2)

MD = MarkdownIt("commonmark").enable("table")

# Containers whose text governs what is nested inside them.
# `tr_open` (not td/th, which carry no source map) gives table-ROW granularity —
# the documented unit: a marker in one row must not satisfy an anchor in another.
CONTAINERS = {"list_item_open", "blockquote_open", "tr_open"}
# Blocks that are prose in their own right, used when nothing else contains the line.
LEAVES = {"paragraph_open", "heading_open"}
# NOT rendered prose. A proposition stated inside one of these is not stated at
# all — this governs BOTH where an anchor may be found and where a marker counts.
NON_PROSE = {"fence", "code_block", "html_block"}


def _spans(text: str) -> tuple[list[tuple[int, int, str]], set[int]]:
    """(line-range, type) for every block token, plus the set of non-prose lines."""
    spans, non_prose = [], set()
    env: dict = {}
    for token in MD.parse(text, env):
        if token.map is None:
            continue
        lo, hi = token.map
        if token.type in NON_PROSE:
            non_prose.update(range(lo, hi))
        elif token.type in CONTAINERS or token.type in LEAVES:
            spans.append((lo, hi, token.type))
    # Link reference definitions emit NO block token, so their lines would
    # otherwise read as prose — letting an anchor or a marker hide in a link
    # title that is never displayed. `env["references"]` carries their maps.
    for reference in (env.get("references") or {}).values():
        ref_map = reference.get("map") if isinstance(reference, dict) else None
        if ref_map:
            non_prose.update(range(ref_map[0], ref_map[1]))
    return spans, non_prose


# Inline constructs whose text is NOT displayed to a reader: a link/image
# destination and title, and a raw HTML tag. A proposition or a ⚠ hiding in one
# of these is invisible, so it cannot satisfy a fixture.
#
# Masking is done at CHARACTER level and preserves offsets, so line numbers and
# block spans stay valid. Matching against markdown-it's *rendered* text would be
# the other approach, but anchors deliberately carry source syntax (`**bold**`,
# backticked module pointers), so rendered text would break every fixture.
#
# Inline code is deliberately NOT masked: it renders, a reader sees it, and two
# anchors are legitimately backticked module pointers.
INLINE_HTML_TAG = re.compile(r"<[^>\n]*>")


def _link_tail_end(text: str, start: int) -> int | None:
    """Index of the `)` closing an inline link tail beginning at `](`, or None.

    Scans per CommonMark rather than stopping at the first `)`: a destination may
    contain BALANCED parentheses (`https://x/a_(b)`), may be angle-bracketed, and
    may be followed by a quoted or parenthesised title.
    """
    i = start + 2
    n = len(text)

    def skip_space(j: int) -> int:
        while j < n and text[j] in " \t\n":
            j += 1
        return j

    i = skip_space(i)
    if i < n and text[i] == "<":  # <destination>
        i += 1
        while i < n and text[i] not in ">\n":
            i += 2 if text[i] == "\\" else 1
        if i >= n or text[i] != ">":
            return None
        i += 1
    else:
        depth = 0
        while i < n:
            char = text[i]
            if char == "\\":
                i += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            elif char in " \t\n":
                break
            i += 1

    i = skip_space(i)
    if i < n and text[i] in "\"'(":  # optional title
        closer = ")" if text[i] == "(" else text[i]
        i += 1
        while i < n and text[i] != closer:
            i += 2 if text[i] == "\\" else 1
        if i >= n:
            return None
        i += 1
        i = skip_space(i)

    return i if i < n and text[i] == ")" else None


def prose_mask(text: str, non_prose: set[int]) -> str:
    """`text` with every non-displayed region blanked, same length and offsets."""
    masked = list(text)

    def blank(lo: int, hi: int) -> None:
        for i in range(lo, hi):
            if masked[i] != "\n":
                masked[i] = " "

    for match in INLINE_HTML_TAG.finditer(text):
        blank(match.start() + 1, match.end() - 1)

    position = text.find("](")
    while position != -1:
        end = _link_tail_end(text, position)
        if end is not None:
            # Blank the destination and title; keep the delimiters so the
            # surrounding prose (and the displayed link text) still reads.
            blank(position + 2, end)
            position = text.find("](", end)
        else:
            position = text.find("](", position + 2)

    if non_prose:
        offset = 0
        for number, line in enumerate(text.split("\n")):
            if number in non_prose:
                blank(offset, offset + len(line))
            offset += len(line) + 1

    return "".join(masked)


def find_in_prose(text: str, needle: str, non_prose: set[int]) -> int:
    """First occurrence of `needle` that lies wholly in rendered prose.

    Searching raw text would let a proposition 'exist' inside a fenced JSON
    schema, an indented code block, or a raw HTML block. Those are not
    statements of the rule, so they must not satisfy a fixture.
    """
    return prose_mask(text, non_prose).find(needle)


def search_in_prose(text: str, pattern: str, non_prose: set[int]):
    """First regex match lying wholly in rendered prose."""
    return re.search(pattern, prose_mask(text, non_prose))


TAG = re.compile(r"<[^>]+>")
# Elements whose CONTENT is not displayed either. Stripping tags alone would
# leave the content of these reading as visible text.
NON_DISPLAYED_ELEMENT = re.compile(
    r"<(script|style|template)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL
)
ENTITIES = [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'")]
SYNTAX = re.compile(r"[*_`]")
WHITESPACE = re.compile(r"\s+")


def rendered_text(text: str) -> str:
    """The document as a reader sees it, via the renderer itself.

    An INDEPENDENT oracle for the mask: the mask decides where a match may be
    found, this confirms the matched text is actually displayed. Two mechanisms
    agreeing is the point — a bug in the mask alone cannot certify an invisible
    proposition.
    """
    html = TAG.sub("", NON_DISPLAYED_ELEMENT.sub("", MD.render(text)))
    for entity, char in ENTITIES:
        html = html.replace(entity, char)
    return WHITESPACE.sub(" ", html)


def displayed(anchor: str, rendered: str) -> bool:
    """Is `anchor` visible once markdown syntax and line wrapping are normalised?"""
    bare = WHITESPACE.sub(" ", SYNTAX.sub("", anchor)).strip()
    return not bare or bare in rendered


def reference_definitions(text: str) -> str:
    """The document's link reference definitions, as source lines.

    Carried into a single-block render so the block resolves `[x][ref]` the way
    the whole document does. Without them an isolated block renders the reference
    syntax LITERALLY, and the literal text — an image's alt text, say — reads as
    displayed when the real document shows an image instead.
    """
    env: dict = {}
    MD.parse(text, env)
    lines = text.split("\n")
    out = []
    for reference in (env.get("references") or {}).values():
        ref_map = reference.get("map") if isinstance(reference, dict) else None
        if ref_map:
            out.extend(lines[ref_map[0]:ref_map[1]])
    return "\n".join(out)


def displayed_at(text: str, index: int, anchor: str) -> bool:
    """Is `anchor` visible in the rendered output of ITS OWN block?

    Rendering the whole document would let an unrelated visible occurrence
    elsewhere vouch for an invisible one here. Binding the oracle to the block
    containing the match is what ties visibility to the located occurrence.

    The block is rendered WITH the document's link reference definitions
    appended, so a reference image or link defined elsewhere resolves here rather
    than degrading to its literal source text. `rendered_text()` additionally
    drops the content of `<script>`, `<style>` and `<template>`, not just their
    tags.

    SCOPE OF THIS CHECK — do not over-read it. Undisplayed raw HTML is
    open-ended (`hidden`, `aria-hidden`, CSS), so this oracle is NOT
    independently sufficient against images or raw HTML: those are rejected by
    the fail-closed `raw_html()` prohibition in `check()`, which is what actually
    closes that class. The oracle's job is narrower — catching a match that is
    located in prose but not displayed there.
    """
    lo, hi = block_bounds(text, index)
    block = text[lo:hi]
    definitions = reference_definitions(text)
    if definitions:
        block = f"{block}\n\n{definitions}\n"
    return displayed(anchor, rendered_text(block))


def raw_html(text: str) -> list[str]:
    """Every raw-HTML construct or markdown IMAGE in the document.

    Raw HTML is PROHIBITED in matrix owner documents and the checker fails
    closed on it. Rationale: `<script>`, `<template>`, `<style>`, `hidden` and
    `aria-hidden` all render to nothing while remaining present in the source,
    so any lexical visibility check can be defeated by one of them — and the
    list is open-ended. These are tax reference documents with no legitimate use
    for raw HTML, so banning it removes the whole class rather than chasing tags.
    (It also fixes a live bug it caught: bare `<YYYY>` placeholders in prose were
    being parsed as HTML and rendering as nothing.)

    Markdown IMAGES are banned for the same reason: alt text is present in the
    source and readable by a matcher, but a reader sees the image, not the alt.
    There are no images in these documents and no reason for one.
    """
    found = []
    for token in MD.parse(text):
        if token.type == "html_block":
            found.append(f"html_block at line {token.map[0] + 1}")
        elif token.type == "inline":
            for child in token.children or []:
                if child.type == "html_inline":
                    found.append(f"html_inline {child.content[:40]!r}")
                elif child.type == "image":
                    found.append(f"image (alt text is not displayed) {child.content[:40]!r}")
    return found


def line_index(text: str, index: int) -> int:
    return text.count("\n", 0, index)


def _line_offsets(text: str) -> list[int]:
    offsets, pos = [0], 0
    for line in text.split("\n"):
        pos += len(line) + 1
        offsets.append(pos)
    return offsets


def block_bounds(text: str, index: int) -> tuple[int, int]:
    """Character bounds of the innermost block containing `index`, INCLUDING any
    nested content. Used by the `scope: local` co-location check, where an anchor
    in a child item still counts as stated in the same place."""
    target = line_index(text, index)
    spans, _ = _spans(text)
    enclosing = [s for s in spans if s[0] <= target < s[1]]
    if not enclosing:
        return 0, len(text)
    lo, hi, _ = min(enclosing, key=lambda s: (s[1] - s[0], -s[0]))
    offsets = _line_offsets(text)
    return offsets[lo], min(offsets[min(hi, len(offsets) - 1)], len(text))


def block_containing(text: str, index: int) -> str:
    """The governing text for a point-of-use marker check.

    A marker counts if it sits in the anchor's own block, or in the *own text* of
    an enclosing container (a qualification on a parent bullet governs its
    children). It does not count if it sits on a sibling, on a descendant, or
    inside a code block.
    """
    target = line_index(text, index)
    spans, non_prose = _spans(text)
    lines = prose_mask(text, non_prose).split("\n")

    enclosing = [s for s in spans if s[0] <= target < s[1]]
    if not enclosing:
        return ""
    # Innermost first: the smallest span wins ties on start.
    enclosing.sort(key=lambda s: (s[1] - s[0], -s[0]))

    def own_text(lo: int, hi: int) -> str:
        """A container's own lines — excluding any strictly-nested container and
        any code block. Excluding descendants is what stops a marker on a child
        from satisfying an anchor in its parent."""
        nested = {
            line
            for n_lo, n_hi, n_type in spans
            if n_type in CONTAINERS and lo <= n_lo and n_hi <= hi and (n_lo, n_hi) != (lo, hi)
            for line in range(n_lo, n_hi)
        }
        return "\n".join(
            lines[n] for n in range(lo, min(hi, len(lines)))
            if n not in nested and n not in non_prose
        )

    parts = []
    innermost = enclosing[0]
    if innermost[2] in LEAVES:
        parts.append("\n".join(
            lines[n] for n in range(innermost[0], min(innermost[1], len(lines)))
            if n not in non_prose
        ))
        rest = [s for s in enclosing[1:] if s[2] in CONTAINERS]
    else:
        rest = [s for s in enclosing if s[2] in CONTAINERS]
    for lo, hi, _ in rest:
        parts.append(own_text(lo, hi))
    return "\n".join(parts)


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check(entry: dict, failures: list[str]) -> int | None:
    ident = entry["id"]
    owner = ROOT / entry["owner"]

    if not owner.exists():
        failures.append(f"{ident}: owner file missing: {entry['owner']}")
        return None

    text = owner.read_text(encoding="utf-8")
    anchors = entry.get("anchors", [])
    if not anchors:
        failures.append(f"{ident}: entry declares no anchors")
        return None

    _, non_prose = _spans(text)
    for construct in raw_html(text):
        failures.append(
            f"{ident}: raw HTML is prohibited in a matrix owner document "
            f"({entry['owner']}: {construct}) — it can render to nothing while "
            f"remaining searchable, defeating the visibility check"
        )
    found: dict[str, int] = {}
    for anchor in anchors:
        index = find_in_prose(text, anchor, non_prose)
        if index == -1:
            where = (
                " (present, but only inside a code or raw-HTML block, which is "
                "not a statement of the rule)"
                if text.find(anchor) != -1
                else ""
            )
            failures.append(
                f"{ident}: anchor absent from {entry['owner']}: {anchor!r}{where}\n"
                f"        proposition: {entry['proposition']}\n"
                f"        if removed: {entry['failure_mode']}"
            )
            continue
        if not displayed_at(text, index, anchor):
            failures.append(
                f"{ident}: anchor is not DISPLAYED in the rendered document "
                f"(mask and renderer disagree — treat as a checker bug): {anchor!r}"
            )
        found[anchor] = index

    for pattern in entry.get("forbidden", []):
        match = search_in_prose(text, pattern, non_prose)
        if match:
            failures.append(
                f"{ident}: KNOWN-WRONG formulation reappeared in {entry['owner']} "
                f"line {line_of(text, match.start())}: {match.group(0)!r}\n"
                f"        correct: {entry['proposition']}"
            )

    # Which anchor the ⚠ must accompany. Mandatory once a warn-required entry has
    # more than one anchor — defaulting to the first would make anchor ORDER
    # semantic, and silently fragile when anchors are reordered.
    marker_anchor = entry.get("marker_anchor")
    if marker_anchor is None:
        if entry.get("warn_required") and len(anchors) > 1:
            failures.append(
                f"{ident}: warn_required with {len(anchors)} anchors must name "
                f"'marker_anchor' — which anchor the {WARN} governs cannot be inferred"
            )
        marker_anchor = anchors[0]
    elif marker_anchor not in anchors:
        failures.append(f"{ident}: marker_anchor is not one of the entry's anchors")
    marker_index = found.get(marker_anchor)

    # Multi-anchor propositions must declare whether they are stated in one place.
    # `local` enforces co-location; `distributed` documents an intentional spread
    # so it is a recorded decision rather than an unnoticed gap.
    scope = entry.get("scope")
    if len(anchors) > 1 and scope not in {"local", "distributed"}:
        failures.append(
            f"{ident}: multi-anchor entry must declare \"scope\": \"local\" or \"distributed\""
        )
    if scope == "local" and len(found) == len(anchors):
        lo, hi = block_bounds(text, found[marker_anchor])
        stray = [a for a, i in found.items() if not lo <= i < hi]
        if stray:
            failures.append(
                f"{ident}: scope is 'local' but anchors are not co-located in the "
                f"block at {entry['owner']}:{line_of(text, lo)}: {stray}"
            )

    if entry.get("warn_required") and marker_index is not None:
        if WARN not in block_containing(text, marker_index):
            failures.append(
                f"{ident}: point-of-use marker '{WARN}' missing from the block at "
                f"{entry['owner']}:{line_of(text, marker_index)} "
                f"(authority.md requires it where a proposition determines a result)"
            )

    # A sole-ownership claim is only true if no other module restates the fact.
    for pattern in entry.get("no_restatement_outside_owner", []):
        for other in sorted((ROOT / "individual").glob("*.md")):
            if other == owner:
                continue
            other_text = other.read_text(encoding="utf-8")
            match = search_in_prose(other_text, pattern, _spans(other_text)[1])
            if match:
                failures.append(
                    f"{ident}: {entry['owner']} claims sole ownership but "
                    f"individual/{other.name}:{match.group(0)[:60]!r} restates it"
                )

    return line_of(text, marker_index) if marker_index is not None else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true", help="print the matrix as a table")
    args = parser.parse_args()

    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    entries = matrix["entries"]

    ids = [entry["id"] for entry in entries]
    assert len(ids) == len(set(ids)), "duplicate entry IDs in the regression matrix"

    failures: list[str] = []
    lines: dict[str, int | None] = {}
    for entry in entries:
        lines[entry["id"]] = check(entry, failures)

    if args.report:
        width = max(len(entry["owner"]) for entry in entries)
        print(f"{'ID':<5} {'OWNER':<{width}} {'LINE':>5}  {'WARN':<5} AUTHORITY")
        for entry in entries:
            line = lines[entry["id"]]
            print(
                f"{entry['id']:<5} {entry['owner']:<{width}} "
                f"{line if line else '--':>5}  "
                f"{'yes' if entry.get('warn_required') else 'no':<5} {entry['authority']}"
            )
        print()

    if failures:
        print(f"FAIL: {len(failures)} regression(s) in {len(entries)} pinned propositions\n")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    warned = sum(1 for entry in entries if entry.get("warn_required"))
    print(
        f"PASS: {len(entries)} pinned propositions present in their canonical owner; "
        f"{warned} carry the required point-of-use marker; no known-wrong formulation present"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
