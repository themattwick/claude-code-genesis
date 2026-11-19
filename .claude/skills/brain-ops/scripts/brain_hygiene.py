#!/usr/bin/env python3
"""
Health check for a BRAIN/ knowledge base.

`brain hygiene` used to be whatever the model improvised. This makes it a
repeatable report: the same knowledge base always produces the same findings,
so hygiene can be tracked over time and wired into CI.

Checks performed:
  - lifecycle-inconsistency : supersedes/superseded_by not reflected in status
  - broken-link             : links/supersedes target that does not exist
  - stale-index             : INDEX.md missing or older than the newest entry
  - stale-checkpoint        : active checkpoint older than --days, never consolidated
  - missing-frontmatter     : entry indexed only by folder + filename fallback
  - invalid-field           : type/status/confidence/scope outside the documented vocabulary
  - empty-checkpoint        : active checkpoint with no content under any heading
  - checkpoint-incomplete   : new-style checkpoint with empty `Left off` / `Next steps`
  - learning-incomplete     : active learning/pattern without a portable rule or signal
  - possible-duplicate      : two active learnings/patterns/bugs that look like one
  - removal-incomplete      : removal entry missing removed/reason/replacement/return_if
  - promotion-due           : confirmed in 2+ projects but still `scope: project`
  - global-unconfirmed      : `scope: global` without `confidence: confirmed`

Zero external dependencies.

Usage:
    python brain_hygiene.py [path-to-project-root] [--days N] [--strict]

Exit code is 0 unless --strict is passed, in which case any finding exits 1.
"""
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import re

from _brain_common import (LINK_FIELDS, PROMOTE_MIN_PROJECTS, REMOVAL_FIELDS,
                           VALID_CONFIDENCE,
                           VALID_SCOPES, VALID_STATUSES, VALID_TYPES, as_list,
                           collect_entries, content_lines, field_text, find_brain_root,
                           split_sections)

DEFAULT_STALE_DAYS = 14
SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


@dataclass(frozen=True)
class Finding:
    check: str
    severity: str
    path: str
    detail: str


def resolve_target(brain_root: Path, entry: dict, target: str) -> Path | None:
    """Resolve a link target, which may be BRAIN-relative or same-folder."""
    if not target:
        return None
    candidates = [brain_root / target, entry["file"].parent / target]
    for c in candidates:
        if c.exists():
            return c
    return None


def parse_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def check_links(brain_root: Path, entries: list[dict]) -> list[Finding]:
    findings = []
    for e in entries:
        for field in LINK_FIELDS:
            for target in as_list(e["meta"].get(field)):
                if resolve_target(brain_root, e, target) is None:
                    findings.append(Finding(
                        "broken-link", "HIGH", e["path"],
                        f"{field}: -> {target} (no such file)"))
    return findings


def check_lifecycle(brain_root: Path, entries: list[dict]) -> list[Finding]:
    """supersedes/superseded_by must be reflected in the status of both sides."""
    by_path = {e["path"]: e for e in entries}
    findings = []
    for e in entries:
        if e["meta"].get("superseded_by") and e["status"] == "active":
            findings.append(Finding(
                "lifecycle-inconsistency", "HIGH", e["path"],
                "has superseded_by but status is still 'active'"))

        for target in as_list(e["meta"].get("supersedes")):
            resolved = resolve_target(brain_root, e, target)
            if resolved is None:
                continue
            rel = f"{resolved.parent.name}/{resolved.name}"
            other = by_path.get(rel)
            if other and other["status"] == "active":
                findings.append(Finding(
                    "lifecycle-inconsistency", "HIGH", rel,
                    f"superseded by {e['path']} but still marked 'active'"))
    return findings


def check_index(brain_root: Path, entries: list[dict]) -> list[Finding]:
    index = brain_root / "INDEX.md"
    if not entries:
        return []
    if not index.exists():
        return [Finding("stale-index", "MEDIUM", "INDEX.md",
                        "missing - run build_index.py")]
    newest = max(e["file"].stat().st_mtime for e in entries)
    if index.stat().st_mtime < newest:
        return [Finding("stale-index", "MEDIUM", "INDEX.md",
                        "older than the newest entry - run build_index.py")]
    return []


def check_stale_checkpoints(entries: list[dict], days: int) -> list[Finding]:
    findings = []
    now = datetime.now()
    for e in entries:
        if e["type"] != "checkpoint" or e["status"] != "active":
            continue
        dt = parse_date(e["date"])
        if dt is None:
            continue
        age = (now - dt).days
        if age > days:
            findings.append(Finding(
                "stale-checkpoint", "MEDIUM", e["path"],
                f"{age} days old and still active - consolidate then retire"))
    return findings


def check_fields(entries: list[dict]) -> list[Finding]:
    findings = []
    for e in entries:
        if not e["has_frontmatter"]:
            findings.append(Finding(
                "missing-frontmatter", "LOW", e["path"],
                "indexed via folder + filename fallback"))
            continue
        if e["type"] not in VALID_TYPES:
            findings.append(Finding("invalid-field", "MEDIUM", e["path"],
                                    f"unknown type: {e['type']}"))
        if e["status"] not in VALID_STATUSES:
            findings.append(Finding("invalid-field", "MEDIUM", e["path"],
                                    f"unknown status: {e['status']}"))
        if e["confidence"] and e["confidence"] not in VALID_CONFIDENCE:
            findings.append(Finding("invalid-field", "MEDIUM", e["path"],
                                    f"unknown confidence: {e['confidence']}"))
        if e["stated_scope"] not in VALID_SCOPES:
            findings.append(Finding("invalid-field", "MEDIUM", e["path"],
                                    f"unknown scope: {e['stated_scope']}"))
        if e["promotable"]:
            findings.append(Finding(
                "promotion-due", "LOW", e["path"],
                f"confirmed in {len(e['projects'])} projects "
                f"(threshold {PROMOTE_MIN_PROJECTS}) - set `scope: global`"))
        if e["stated_scope"] == "global" and e["confidence"] != "confirmed":
            findings.append(Finding(
                "global-unconfirmed", "LOW", e["path"],
                "scope is global but confidence is not `confirmed`"))
    return findings


def _sections(e: dict) -> dict[str, list[str]]:
    return split_sections(e["file"].read_text(encoding="utf-8", errors="replace"))


def check_checkpoint_content(entries: list[dict]) -> list[Finding]:
    """A checkpoint that is only a title looks like continuity and carries none.

    Only `status: active` is examined: the compaction hook writes `status: skeleton`
    on purpose and the model completes it later; archived ones are history.
    Checkpoints written before the mandatory-field schema have no `Left off` heading
    and are judged only on whether they say anything at all.
    """
    findings = []
    for e in entries:
        if e["type"] != "checkpoint" or e["status"] != "active":
            continue
        sec = _sections(e)
        if not any(content_lines(lines) for lines in sec.values()):
            findings.append(Finding("empty-checkpoint", "MEDIUM", e["path"],
                                    "no content under any heading - only a title"))
            continue
        missing = [name for name, key in (("Left off", "left off"),
                                          ("Next steps", "next steps"))
                   if key in sec and not content_lines(sec[key])]
        if missing:
            findings.append(Finding("checkpoint-incomplete", "MEDIUM", e["path"],
                                    "empty mandatory section: " + ", ".join(missing)))
    return findings


def check_learning_shape(entries: list[dict]) -> list[Finding]:
    """A learning or pattern must hold a portable rule and a recognition signal.

    Without them it is a diary entry: true, and of no use the next time the
    situation comes round. Retired entries are history and are not examined.
    """
    findings = []
    for e in entries:
        if e["type"] not in ("learning", "pattern") or e["status"] != "active":
            continue
        sec = _sections(e)
        whole = "\n".join("\n".join(v) for v in sec.values())
        missing = []
        if not (content_lines(sec.get("rule", [])) or re.search(r"next time\b", whole, re.I)):
            missing.append("a rule (\"Next time [situation], I will [action]\")")
        if not any(content_lines(v) for k, v in sec.items() if "signal" in k):
            missing.append("a recognition signal")
        if missing:
            findings.append(Finding("learning-incomplete", "MEDIUM", e["path"],
                                    "missing " + " and ".join(missing)))
    return findings


_STOP = {"the", "and", "for", "with", "that", "this", "when", "not", "from", "are", "was",
         "into", "must", "should", "never", "always"}


def _tokens(title: str) -> set[str]:
    return {w for w in re.findall(r"[^\W_]+", title.lower()) if len(w) > 2 and w not in _STOP}


def check_duplicates(entries: list[dict]) -> list[Finding]:
    """Heuristic only - it reads titles and tags, not meaning, so it SUGGESTS.

    Two active learnings/patterns/bugs are a possible duplicate when their titles share
    at least 60% of their words (Jaccard), or share 2+ tags and at least a third of
    their words. A real duplicate is a different symptom of the SAME root cause: merge
    by adding an example to the older entry. A false alarm costs one look.
    """
    pool = [e for e in entries
            if e["type"] in ("learning", "pattern", "bug") and e["status"] == "active"]
    findings = []
    for i, a in enumerate(pool):
        for b in pool[i + 1:]:
            ta, tb = _tokens(a["title"]), _tokens(b["title"])
            if not ta or not tb:
                continue
            jac = len(ta & tb) / len(ta | tb)
            shared_tags = len({t.lower() for t in a["tags"]} & {t.lower() for t in b["tags"]})
            if jac >= 0.6 or (shared_tags >= 2 and jac >= 0.34):
                older, newer = sorted((a, b), key=lambda x: x["path"])
                findings.append(Finding(
                    "possible-duplicate", "LOW", newer["path"],
                    f"looks like `{older['path']}` (title overlap {jac:.0%}, "
                    f"{shared_tags} shared tags) - same root cause? add an example there"))
    return findings


def check_removals(entries: list[dict]) -> list[Finding]:
    """A removal without all four fields cannot do its job: without the reason nobody
    can judge it, without a replacement nobody knows where the need went, without a
    return condition nobody knows when it stops applying. `return_if: never` is a
    valid answer - an empty one is not."""
    findings = []
    for e in entries:
        if e["type"] != "removal" or e["status"] != "active":
            continue
        missing = [k for k in REMOVAL_FIELDS if not field_text(e["meta"], k)]
        if missing:
            findings.append(Finding("removal-incomplete", "MEDIUM", e["path"],
                                    "missing frontmatter: " + ", ".join(missing)))
    return findings


def run_checks(brain_root: Path, entries: list[dict], days: int) -> list[Finding]:
    findings = (check_lifecycle(brain_root, entries)
                + check_links(brain_root, entries)
                + check_index(brain_root, entries)
                + check_stale_checkpoints(entries, days)
                + check_fields(entries)
                + check_checkpoint_content(entries)
                + check_learning_shape(entries)
                + check_duplicates(entries)
                + check_removals(entries))
    return sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.check, f.path))


def render(findings: list[Finding], entries: list[dict], days: int) -> str:
    active = sum(1 for e in entries if e["status"] == "active")
    lines = ["# BRAIN hygiene report", ""]
    lines.append(f"Entries: {len(entries)} ({active} active)  ·  "
                 f"stale threshold: {days} days")
    lines.append("")

    if not findings:
        lines.append("No issues found. The knowledge base is healthy.")
        return "\n".join(lines)

    lines.append(f"Findings: {len(findings)}")
    lines.append("")
    current = None
    for f in findings:
        if f.check != current:
            current = f.check
            count = sum(1 for x in findings if x.check == current)
            lines.append(f"## {f.severity} · {f.check} ({count})")
        lines.append(f"- `{f.path}` - {f.detail}")
    lines.append("")
    lines.append("Suggested order: fix HIGH (graph correctness) first, then "
                 "consolidate stale checkpoints, then regenerate the index.")
    return "\n".join(lines)


def main() -> None:
    args = [a for a in sys.argv[1:]]
    strict = "--strict" in args
    days = DEFAULT_STALE_DAYS
    if "--days" in args:
        i = args.index("--days")
        if i + 1 < len(args):
            days = int(args[i + 1])
            del args[i:i + 2]
    args = [a for a in args if not a.startswith("--")]

    start = Path(args[0]).resolve() if args else Path.cwd()
    brain_root = find_brain_root(start)
    if not brain_root:
        print("Could not find a BRAIN/ directory at or above:", start)
        print("Run 'brain init' to set one up.")
        sys.exit(1)

    entries = collect_entries(brain_root)
    findings = run_checks(brain_root, entries, days)
    print(render(findings, entries, days))
    sys.exit(1 if (strict and findings) else 0)


if __name__ == "__main__":
    main()
