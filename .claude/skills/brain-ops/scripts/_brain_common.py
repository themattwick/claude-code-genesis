#!/usr/bin/env python3
"""
Shared helpers for the brain-ops scripts.

Locating BRAIN/, parsing entry frontmatter and normalizing entries must behave
identically for every tool that reads the knowledge base — otherwise the index
and the hygiene report can disagree about the same file. This module is the
single source of truth for that logic.

Zero external dependencies, so the scripts stay portable.
"""
import re
from pathlib import Path

ENTRY_DIRS = ["handoffs", "checkpoints", "sessions", "decisions", "bugs",
              "learnings", "patterns", "glossary", "reference", "specs"]
SKIP_FILES = {"INDEX.md", "README.md", "QUICK-REFERENCE.md"}

# A directory holding this file contains MATERIAL, not entries: sample output,
# a prototype, imported documents, anything that lives in BRAIN/ as evidence
# attached to an entry rather than as an entry itself. It and everything below
# it is skipped by every tool that reads the knowledge base.
#
# Why a marker file and not a name pattern or a type allowlist: a pattern like
# "prototyp*" silently stops working the day someone names a directory
# differently, and skipping unknown TYPES would also silence the case this
# check exists for — a real entry with a typo in its type. A marker is visible
# when you open the directory and says what it means.
#
# Measured on a real base: without it, 47 prototype files written in a
# different format (OKF concepts and rules, `type: Business Rule`) produced 50
# MEDIUM hygiene findings, every one a false positive. A control that reports
# noise stops being read.
NOT_ENTRIES_MARKER = ".not-brain-entries"
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

VALID_TYPES = {"checkpoint", "session", "decision", "bug", "learning",
               "pattern", "handoff", "glossary", "reference", "spec"}
VALID_STATUSES = {"active", "superseded", "archived"}

LINK_FIELDS = ("links", "supersedes", "superseded_by")

# Section order in the generated index. Reference material (decisions,
# glossary, specs, reference) surfaces before working history. Any type not
# listed here still gets its own section — appended alphabetically —
# instead of silently vanishing from the index.
PREFERRED_TYPE_ORDER = ["decision", "glossary", "spec", "learning", "pattern",
                        "bug", "reference", "handoff", "session", "checkpoint"]

# Section-header plurals that don't follow the plain "+s" rule.
TYPE_PLURALS = {"glossary": "Glossary terms"}


def order_types(present_types) -> list[str]:
    """Preferred types first (if present), then any others alphabetically."""
    ordered = [t for t in PREFERRED_TYPE_ORDER if t in present_types]
    ordered += sorted(set(present_types) - set(ordered))
    return ordered


def pluralize_type(entry_type: str) -> str:
    return TYPE_PLURALS.get(entry_type, f"{entry_type.capitalize()}s")


def find_brain_root(start: Path) -> Path | None:
    """Locate a BRAIN/ directory at or above the start path."""
    candidates = [start / "BRAIN", start]
    candidates += [p / "BRAIN" for p in start.parents]
    for c in candidates:
        if (c / "checkpoints").exists() or c.name == "BRAIN" and c.exists():
            return c
    return None


def parse_frontmatter(text: str) -> dict:
    """Parse a leading --- ... --- YAML-ish block. Supports scalars and [lists]."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip("\n")
    meta: dict = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip() for v in value[1:-1].split(",") if v.strip()]
            meta[key] = items
        else:
            meta[key] = value
    return meta


def extract_title(text: str, fallback: str) -> str:
    """First markdown H1, else a humanized filename."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def humanize(filename: str) -> str:
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}(-\d{4})?-", "", Path(filename).stem)
    return stem.replace("-", " ")


def read_entry(path: Path, folder: str, brain_root: Path) -> dict:
    """Build a normalized entry record, applying fallbacks for missing fields.

    `path` in the record is relative to BRAIN/ and POSIX-separated, so it is
    usable as a link target and as a stable identity key on every platform.
    For an entry sitting directly in a known folder this is exactly the old
    "<folder>/<name>" — the change is only visible for nested entries.

    `group` is the sub-path between the folder and the file ("" at the top
    level). It lets a caller keep a nested collection together instead of
    letting its members flood the flat table for their type.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = parse_frontmatter(text)
    date_match = DATE_RE.search(path.name)
    rel = path.relative_to(brain_root)
    # relative_to() yields "." for a file sitting directly in the folder. Compare
    # against it exactly — stripping dots would also mangle a real directory name
    # that happens to contain one.
    sub = rel.parent.relative_to(folder).as_posix()
    return {
        "type": meta.get("type", folder.rstrip("s")),
        "status": meta.get("status", "active"),
        "date": meta.get("date") or (date_match.group(1) if date_match else "—"),
        "tags": meta.get("tags", []),
        "title": extract_title(text, humanize(path.name)),
        "path": rel.as_posix(),
        "group": "" if sub == "." else sub,
        "has_frontmatter": bool(meta),
        "meta": meta,
        "file": path,
    }


def collect_entries(brain_root: Path) -> list[dict]:
    """Read every entry under the known BRAIN/ subfolders, at any depth.

    ⚠️ It recurses, and that is the point. The first version globbed one level
    deep, so a folder holding a nested collection — a wayfinder map with its
    tickets, a spec with its research notes — was indexed as ZERO entries and
    nothing said so. Measured on a real base: 80 files under specs/, 10 in the
    index, 70 invisible, and the gap had been there since the first run. An
    index that silently omits most of a folder is worse than no index, because
    it looks complete.
    """
    entries = []
    for folder in ENTRY_DIRS:
        d = brain_root / folder
        if not d.exists():
            continue
        for path in sorted(d.rglob("*.md")):
            if path.name in SKIP_FILES or is_material(path, d):
                continue
            entries.append(read_entry(path, folder, brain_root))
    return entries


def is_material(path: Path, folder_root: Path) -> bool:
    """True when the file sits in (or under) a directory marked as material.

    The marker applies to everything below it, not only to its own directory —
    a prototype bundle has its own subfolders and marking each one separately
    is a rule nobody would keep.
    """
    d = path.parent
    while True:
        if (d / NOT_ENTRIES_MARKER).exists():
            return True
        if d == folder_root or d.parent == d:
            return False
        d = d.parent


def as_list(value) -> list[str]:
    """Normalize a frontmatter field that may be a scalar or a list."""
    if not value:
        return []
    return value if isinstance(value, list) else [value]
