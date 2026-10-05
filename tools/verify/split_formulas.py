"""Split App.Formulas text into (name, expression) pairs - semicolons at depth 0, outside strings and comments."""
import re


def split(text):
    out, buf, depth, i, n = [], [], 0, 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if not in_str and text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if ch == '"':
            if in_str and i + 1 < n and text[i + 1] == '"':
                buf.append('""'); i += 2; continue
            in_str = not in_str
        elif not in_str:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == ";" and depth == 0:
                out.append("".join(buf)); buf = []; i += 1; continue
        buf.append(ch); i += 1
    if "".join(buf).strip():
        out.append("".join(buf))
    pairs = []
    for s in out:
        s = s.strip()
        if not s:
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", s, re.S)
        if not m:
            raise ValueError("cannot parse named formula: " + s[:80])
        pairs.append((m.group(1), m.group(2)))
    return pairs
