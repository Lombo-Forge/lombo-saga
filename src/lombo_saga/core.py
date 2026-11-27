"""The decisions. Pure: no network, no disk, no clock, so tests need no fakes.

A rule is a collection title, name patterns and optionally authors. A series matches when its name
matches a pattern (case-insensitive, * and ? wildcards) and, if authors are given, one of them is a
folder in its path (an Author/Title layout). Series are only ever added, never taken out.
"""

import fnmatch
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


class RuleError(ValueError):
    """The rules file is not usable. The message says why."""


@dataclass(frozen=True)
class Rule:
    title: str
    names: tuple[str, ...]
    authors: tuple[str, ...] = ()


def _strings(value: object, what: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
        raise RuleError(f"{what} must be a list of non-empty strings")
    return tuple(v.strip() for v in value)


def parse_rules(raw: object) -> list[Rule]:
    """{"Title": ["pattern", ...]} or {"Title": {"names": [...], "authors": [...]}}."""
    if not isinstance(raw, dict) or not raw:
        raise RuleError("the file must hold at least one rule, as an object keyed by collection title")
    rules = []
    for title, body in raw.items():
        what = f"rule {title!r}"
        spec = {"names": body} if isinstance(body, list) else body
        if not str(title).strip() or not isinstance(spec, dict) or set(spec) - {"names", "authors"}:
            raise RuleError(f"{what}: expected a title with 'names' and optionally 'authors'")
        names = _strings(spec.get("names"), f"{what} names")
        authors = _strings(spec.get("authors", []), f"{what} authors")
        if not names:
            raise RuleError(f"{what} needs at least one name pattern")
        if not authors and any(not n.strip("*? ") for n in names):
            raise RuleError(f"{what}: a pattern of only wildcards needs authors, or it matches every series")
        rules.append(Rule(str(title).strip(), names, authors))
    return rules


def matches(series: Mapping[str, Any], rule: Rule) -> bool:
    names = [str(series[k]).casefold() for k in ("name", "originalName", "localizedName") if series.get(k)]
    if not any(fnmatch.fnmatchcase(n, p.casefold()) for n in names for p in rule.names):
        return False
    if not rule.authors:
        return True
    path = str(series.get("lowestFolderPath") or series.get("folderPath") or "").replace("\\", "/").casefold()
    return any(a.casefold() in path.split("/") for a in rule.authors)


def wanted(series: Sequence[Mapping[str, Any]], rule: Rule) -> list[int]:
    return sorted(int(s["id"]) for s in series if matches(s, rule))


def find(collections: Sequence[Mapping[str, Any]], title: str) -> tuple[int | None, str | None]:
    """(collection id, or None to create one; why this title must be left alone, or None)."""
    same = [c for c in collections if str(c.get("title", "")).casefold() == title.casefold()]
    if len(same) > 1:
        return None, f"{len(same)} collections have this name"
    if not same:
        return None, None
    if same[0].get("source"):
        return None, "it is synced from an outside service"
    return int(same[0]["id"]), None
