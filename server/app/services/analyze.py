from __future__ import annotations

import re
from typing import Dict, List, Tuple


_re_leading_digits = re.compile(r"^\s*\d+[\.|\)|\-]\s*")
_re_leading_roman = re.compile(r"^\s*[ivxlcdm]+[\.|\)]\s*", re.IGNORECASE)
_re_whitespace = re.compile(r"[\s\t]+")
_re_trailing_punct = re.compile(r"[\:;,.]+$")


def normalize_line(s: str) -> str:
    return (
        str(s or "")
        .lower()
        .strip()
        .replace("\u00a0", " ")
    )


def normalize_for_match(s: str) -> str:
    x = normalize_line(s)
    x = _re_leading_digits.sub("", x)
    x = _re_leading_roman.sub("", x)
    x = _re_whitespace.sub(" ", x)
    x = _re_trailing_punct.sub("", x)
    return x.strip()


def _jaro(s: str, t: str) -> float:
    if s == t:
        return 1.0
    len_s, len_t = len(s), len(t)
    if len_s == 0 or len_t == 0:
        return 0.0

    match_dist = max(len_s, len_t) // 2 - 1
    s_matches = [False] * len_s
    t_matches = [False] * len_t

    matches = 0
    for i in range(len_s):
        start = max(0, i - match_dist)
        end = min(i + match_dist + 1, len_t)
        for j in range(start, end):
            if t_matches[j]:
                continue
            if s[i] != t[j]:
                continue
            s_matches[i] = True
            t_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    # Count transpositions
    k = 0
    transpositions = 0
    for i in range(len_s):
        if not s_matches[i]:
            continue
        while k < len_t and not t_matches[k]:
            k += 1
        if k < len_t and s[i] != t[k]:
            transpositions += 1
        k += 1

    transpositions /= 2

    return (
        (matches / len_s) +
        (matches / len_t) +
        ((matches - transpositions) / matches)
    ) / 3.0


def jaro_winkler(s: str, t: str, scaling: float = 0.1) -> float:
    j = _jaro(s, t)
    # prefix length up to 4
    prefix = 0
    for a, b in zip(s, t):
        if a == b:
            prefix += 1
        else:
            break
        if prefix == 4:
            break

    # Natural-like behavior: boost when similarity is already decent
    if j > 0.7:
        j = j + prefix * scaling * (1.0 - j)
    return min(1.0, max(0.0, j))


def similarity(a: str, b: str) -> float:
    aa = normalize_for_match(a)
    bb = normalize_for_match(b)
    if not aa or not bb:
        return 0.0
    if aa == bb:
        return 1.0
    return jaro_winkler(aa, bb)


def analyze_text_against_template(text: str, template: List[str]) -> Dict:
    lines = [ln.strip() for ln in str(text or "").splitlines()]
    lines = [ln for ln in lines if ln]

    matched: Dict[str, Dict] = {}
    used_idx = set()

    for t in template:
        best = {"score": 0.0, "idx": -1, "line": ""}
        for i, line in enumerate(lines):
            if i in used_idx:
                continue
            if len(line) > 140:
                continue
            sc = similarity(line, t)
            if sc > best["score"]:
                best = {"score": sc, "idx": i, "line": line}
        if best["score"] >= 0.88:
            matched[t] = best
            used_idx.add(best["idx"])

    found: List[str] = []
    missing: List[str] = []
    for t in template:
        if t in matched:
            found.append(t)
        else:
            missing.append(t)

    indices = [matched[t]["idx"] for t in found]
    order_issues: List[Dict] = []
    for i in range(1, len(indices)):
        if indices[i] < indices[i - 1]:
            order_issues.append({
                "type": "ORDER",
                "message": f'Раздел "{found[i]}" расположен раньше, чем предыдущий раздел',
                "section": found[i],
            })
            break

    ok = len(missing) == 0 and len(order_issues) == 0

    return {
        "template": template,
        "found": found,
        "missing": missing,
        "orderIssues": order_issues,
        "ok": ok,
    }
