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
  - invalid-field           : type/status outside the documented vocabulary

Zero external dependencies.

Usage:
    python brain_hygiene.py [path-to-project-root] [--days N] [--strict]

Exit code is 0 unless --strict is passed, in which case any finding exits 1.
"""
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from _brain_common import (LINK_FIELDS, VALID_STATUSES, VALID_TYPES, as_list,
                           collect_entries, find_brain_root)

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
                f"{age} days old and still active - consolidate then archive"))
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
    return findings


def run_checks(brain_root: Path, entries: list[dict], days: int) -> list[Finding]:
    findings = (check_lifecycle(brain_root, entries)
                + check_links(brain_root, entries)
                + check_index(brain_root, entries)
                + check_stale_checkpoints(entries, days)
                + check_fields(entries))
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
