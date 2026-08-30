#!/usr/bin/env python3
"""Unit tests for the regression matrix's markdown block scoping.

The matrix's ⚠ check is only meaningful if "the same block" means the same LIST
ITEM or TABLE ROW — not the same paragraph. Every case below is a false-pass
that a reviewer actually demonstrated against an earlier version of the scanner.

Usage:
    python3 -B evals/test_matrix_scoping.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("matrix", HERE / "validate_individual_matrix.py")
matrix = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(matrix)

W = matrix.WARN

CASES: list[tuple[str, str, bool]] = [
    # (name, markdown, marker should be visible from ANCHOR)
    (
        "blockquoted ORDERED list: a sibling's marker must not leak",
        f"> 1. ANCHOR text\n> 2. sibling {W} marked\n",
        False,
    ),
    (
        "blockquoted ORDERED list: the item's own marker counts",
        f"> 1. ANCHOR {W} text\n> 2. sibling plain\n",
        True,
    ),
    (
        "a nested item INHERITS a marker from its parent's lead-in",
        f"- parent lead {W} qualifier\n  - ANCHOR child text\n- other\n",
        True,
    ),
    (
        "a nested item does NOT inherit a sibling parent's marker",
        f"- parent lead plain\n  - ANCHOR child\n- other parent {W}\n",
        False,
    ),
    (
        "an EARLIER SIBLING parent's marker must not leak into a later branch",
        f"- first parent {W} marked\n  - first child\n- second parent plain\n  - ANCHOR target\n",
        False,
    ),
    (
        "the correct parent's marker still reaches a later branch's child",
        f"- first parent plain\n  - first child\n- second parent {W} marked\n  - ANCHOR target\n",
        True,
    ),
    (
        "a grandparent's marker reaches a two-deep child",
        f"- grandparent {W} marked\n  - parent plain\n    - ANCHOR deep\n",
        True,
    ),
    (
        "a top-level blockquote is a different container, not a child of the list above",
        f"- prior parent {W} marked\n> - ANCHOR separate top-level blockquote\n",
        False,
    ),
    (
        "a marker on a DESCENDANT must not satisfy an anchor in its parent",
        f"- ANCHOR parent plain\n  - child {W} marked\n- sibling\n",
        False,
    ),
    (
        "a 4-backtick fence containing a 3-backtick line stays closed",
        f"- ANCHOR text\n\n````\n```\n{W} inside code\n```\n````\n",
        False,
    ),
    (
        "a plain fence hides its marker",
        f"- ANCHOR text\n\n```\n{W} inside code\n```\n",
        False,
    ),
    (
        "table rows are independent",
        f"| h | v |\n|---|---|\n| ANCHOR | a |\n| other | {W} b |\n",
        False,
    ),
    (
        "a marker hidden in a link reference definition title does not count",
        f'- ANCHOR real prose\n\n  [rule-ref]: https://example.test "{W}"\n',
        False,
    ),
    (
        "a marker hidden behind a BALANCED-PAREN destination does not count",
        f'- [visible](https://example.test/a_(b) "{W}") ANCHOR\n',
        False,
    ),
    (
        "a marker hidden in an inline link title does not count",
        f'- ANCHOR [visible](https://example.test "{W}")\n',
        False,
    ),
    (
        "a marker hidden in an inline HTML tag attribute does not count",
        f'- ANCHOR <span title="{W}">visible</span>\n',
        False,
    ),
    (
        "a table cell sees its own marker",
        f"| h | v |\n|---|---|\n| ANCHOR | {W} a |\n| other | b |\n",
        True,
    ),
    (
        "a setext heading does not absorb the paragraph after it",
        f"ANCHOR\n------\n\n{W} unrelated following paragraph\n",
        False,
    ),
    (
        "an indented code block hides its marker",
        f"- ANCHOR text\n\n      {W} inside indented code\n",
        False,
    ),
    (
        "a hard-tab sibling is not a descendant",
        f"- outer\n\t- sibling {W} marked\n    - ANCHOR target\n",
        False,
    ),
    (
        "a list parent's marker reaches a table inside the item",
        f"- parent {W} marked\n\n  | h | v |\n  |---|---|\n  | ANCHOR | a |\n",
        True,
    ),
    (
        "a list parent's marker reaches a blockquote nested in the item",
        f"- parent {W} marked\n\n  > ANCHOR quoted text\n",
        True,
    ),
    (
        "an unindented paragraph sees its own marker",
        f"Plain paragraph with ANCHOR and a {W} marker.\n",
        True,
    ),
]


# An anchor must be found in RENDERED PROSE. A proposition sitting inside a JSON
# schema, an indented code block, or a raw HTML block is not stated at all — and
# without this check the enclosing list item's marker would certify it.
ELIGIBILITY: list[tuple[str, str, bool]] = [
    # (name, markdown, ANCHOR should be findable as prose)
    (
        "an anchor inside a fenced block is not stated",
        f"- parent {W} qualifier\n\n  ```\n  ANCHOR\n  ```\n",
        False,
    ),
    (
        "an anchor inside a raw HTML block is not stated",
        f"- parent\n\n  <div>{W} ANCHOR</div>\n",
        False,
    ),
    (
        "an anchor inside an indented code block is not stated",
        f"- parent {W} qualifier\n\n      ANCHOR\n",
        False,
    ),
    (
        "an anchor hidden in a link reference definition title is not stated",
        f'- parent {W} qualifier\n\n  [rule-ref]: https://example.test "ANCHOR"\n',
        False,
    ),
    (
        "an anchor hidden in an inline link title is not stated",
        f'- [visible](https://example.test "ANCHOR") {W}\n',
        False,
    ),
    (
        "an anchor hidden behind a BALANCED-PAREN destination is not stated",
        f'- [visible](https://example.test/a_(b) "ANCHOR") {W}\n',
        False,
    ),
    (
        "an anchor hidden behind an ANGLE-BRACKET destination is not stated",
        f'- [visible](<https://example.test/a b> "ANCHOR") {W}\n',
        False,
    ),
    (
        "an anchor hidden in a link destination is not stated",
        f"- [visible](https://example.test/ANCHOR) {W}\n",
        False,
    ),
    (
        "an anchor hidden in an inline HTML tag attribute is not stated",
        f'- <span title="ANCHOR">visible</span> {W}\n',
        False,
    ),
    (
        "an anchor in inline CODE is stated (code renders; pointers are backticked)",
        f"- see `ANCHOR` here {W}\n",
        True,
    ),
    (
        "link TEXT is displayed, so an anchor there IS stated",
        f"- [ANCHOR visible](https://example.test) {W}\n",
        True,
    ),
    (
        "an anchor in ordinary prose IS stated",
        f"- parent {W} qualifier ANCHOR here\n",
        True,
    ),
    (
        "a prose occurrence is found even when a code occurrence comes first",
        f"```\nANCHOR\n```\n\n- real statement {W} ANCHOR here\n",
        True,
    ),
]


# Raw HTML is prohibited outright in matrix owner documents. Every construct
# below renders to nothing while staying present in the source, so any lexical
# visibility check can be defeated by one of them — and the list is open-ended.
# Banning raw HTML removes the class instead of chasing tags.
PROHIBITED: list[tuple[str, str]] = [
    ("a script element", f"- {W} qualifier <script>ANCHOR</script>\n"),
    ("a hidden span", f"- <span hidden>ANCHOR</span> {W}\n"),
    ("a template element", f"- <template>ANCHOR</template> {W}\n"),
    ("a style element", f"- {W} q <style>ANCHOR</style>\n"),
    ("an aria-hidden span", f'- <span aria-hidden="true">ANCHOR</span> {W}\n'),
    ("an HTML block", f"<div>\nANCHOR\n</div>\n\n- {W} qualifier\n"),
    # Image alt text is in the source and matchable, but a reader sees the image,
    # not the alt — and a second visible occurrence elsewhere must not vouch for it.
    (
        "a reference image's alt text",
        f"- {W} ![ANCHOR][pixel]\n\nANCHOR\n\n[pixel]: data:image/gif;base64,R0lGODlh\n",
    ),
    ("an inline image's alt text", f"- {W} ![ANCHOR](x.png)\n"),
]


# The two constructs the oracle alone cannot judge, exercised through the FULL
# `check()` path rather than a helper. Both are cases where a lexical matcher
# sees the anchor while a reader does not; both must be rejected, and the
# rejection must come from the fail-closed raw-HTML/image prohibition.
END_TO_END: list[tuple[str, str]] = [
    (
        "a reference image whose definition lives elsewhere in the document",
        f"- {W} qualifier ![ANCHOR][pixel]\n\n[pixel]: data:image/gif;base64,R0lGODlh\n",
    ),
    ("inline <script> content", f"- {W} qualifier <script>ANCHOR</script>\n"),
]


def run_end_to_end() -> int:
    """Write each construct into a real owner file and run `check()` on it."""
    failures = 0
    owner = matrix.ROOT / "individual" / "_check_regression_tmp.md"
    for name, body in END_TO_END:
        text = f"# Temp owner\n\n{body}"
        owner.write_text(text, encoding="utf-8")
        try:
            reported: list[str] = []
            matrix.check(
                {
                    "id": "TMP",
                    "owner": f"individual/{owner.name}",
                    "anchors": ["ANCHOR"],
                    "proposition": "temp",
                    "failure_mode": "temp",
                    "authority": "temp",
                    "warn_required": True,
                },
                reported,
            )
        finally:
            owner.unlink()
        if not any("raw HTML is prohibited" in failure for failure in reported):
            failures += 1
            print(
                f"  FAIL {name}: check() did not reject it via the prohibition; "
                f"failures were {reported}"
            )
    return failures


def main() -> int:
    failures = 0
    for name, text, expected in CASES:
        got = W in matrix.block_containing(text, text.find("ANCHOR"))
        if got != expected:
            failures += 1
            print(f"  FAIL {name}: marker visible={got}, expected={expected}")

    for name, text, expected in ELIGIBILITY:
        non_prose = matrix._spans(text)[1]
        got = matrix.find_in_prose(text, "ANCHOR", non_prose) != -1
        if got != expected:
            failures += 1
            print(f"  FAIL {name}: anchor found in prose={got}, expected={expected}")

    for name, text in PROHIBITED:
        if not matrix.raw_html(text):
            failures += 1
            print(f"  FAIL {name}: raw HTML not detected, so the document would be certified")

    # The oracle standing alone: these must be undisplayed even with the
    # prohibition out of the picture.
    for name, text in END_TO_END:
        if matrix.displayed_at(text, text.find("ANCHOR"), "ANCHOR"):
            failures += 1
            print(f"  FAIL {name}: displayed_at() reports the anchor as displayed")

    failures += run_end_to_end()

    total = len(CASES) + len(ELIGIBILITY) + len(PROHIBITED) + 2 * len(END_TO_END)
    if failures:
        print(f"\nFAIL: {failures} of {total} cases")
        return 1
    print(f"PASS: {len(CASES)} block-scoping cases (blockquoted ordered lists, "
          f"nesting inheritance, nested fences, table rows) and "
          f"{len(ELIGIBILITY)} anchor-eligibility cases "
          f"(fenced, indented, raw HTML, link reference definitions, balanced-paren "
          f"destinations) and {len(PROHIBITED)} raw-HTML prohibition cases and "
          f"{len(END_TO_END)} constructs rejected both by the standalone oracle "
          f"and end-to-end through check()")
    return 0


if __name__ == "__main__":
    sys.exit(main())
