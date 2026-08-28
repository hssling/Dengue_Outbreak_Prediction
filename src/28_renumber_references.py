"""
28_renumber_references.py
=========================
Renumber the manuscript reference list so that numbering follows order of first
mention in the text, as Springer requires, and rewrite every in-text marker to
match. Idempotent: running it on an already-sequential manuscript is a no-op.

Operates on reports/MANUSCRIPT_IJDSA_R1.md in place.
"""

import re
import sys

MD = "reports/MANUSCRIPT_IJDSA_R1.md"
SPLIT = "## 8. References"


def parse_refs(reflist):
    """Return {number: full reference text} preserving the entry body."""
    refs, cur, buf = {}, None, []
    for line in reflist.splitlines():
        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            if cur is not None:
                refs[cur] = "\n".join(buf).rstrip()
            cur, buf = int(m.group(1)), [m.group(2)]
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        refs[cur] = "\n".join(buf).rstrip()
    return refs


def first_mention_order(body):
    order = []
    for m in re.finditer(r"\^([\d,\s]+)\^", body):
        for tok in re.split(r"[,\s]+", m.group(1).strip()):
            if tok.isdigit() and int(tok) not in order:
                order.append(int(tok))
    return order


def main():
    text = open(MD, encoding="utf-8").read()
    body, reflist = text.split(SPLIT)
    refs = parse_refs(reflist)
    order = first_mention_order(body)

    missing = [n for n in order if n not in refs]
    uncited = [n for n in sorted(refs) if n not in order]
    if missing:
        print(f"ERROR: cited but not in reference list: {missing}")
        return 1
    if uncited:
        print(f"ERROR: in reference list but never cited: {uncited}")
        return 1

    mapping = {old: new for new, old in enumerate(order, start=1)}
    if all(k == v for k, v in mapping.items()):
        print("References already in order of first mention; nothing to do.")
        return 0

    # Rewrite in-text markers in one pass so remapped values are not remapped
    # again (e.g. 14 -> 5 must not then be treated as an original 5).
    def sub(m):
        parts = [p for p in re.split(r"[,\s]+", m.group(1).strip()) if p.isdigit()]
        return "^" + ",".join(str(mapping[int(p)]) for p in parts) + "^"

    new_body = re.sub(r"\^([\d,\s]+)\^", sub, body)

    lines = [""]
    for old in order:
        lines.append(f"{mapping[old]}. {refs[old]}")
    new_reflist = "\n\n".join(lines) + "\n"

    open(MD, "w", encoding="utf-8").write(new_body + SPLIT + "\n" + new_reflist)

    print("Renumbered references by order of first mention:")
    for old in order:
        print(f"  {old:>2} -> {mapping[old]:>2}   {refs[old][:66]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
