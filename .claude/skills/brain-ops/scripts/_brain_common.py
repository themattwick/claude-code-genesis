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

ENTRY_DIRS = ["handoffs", "checkpoints", "sessions", "decisions",
              "bugs", "learnings", "patterns", "reference", "specs"]
SKIP_FILES = {"INDEX.md", "README.md", "QUICK-REFERENCE.md"}
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

VALID_TYPES = {"checkpoint", "session", "decision", "bug", "learning",
               "pattern", "handoff", "reference", "spec"}
VALID_STATUSES = {"active", "superseded", "archived"}

LINK_FIELDS = ("links", "supersedes", "superseded_by")

# Section order in the generated index. Reference material (decisions,
# specs, reference) surfaces before working history. Any type not listed
# here still gets its own section — appended alphabetically — instead of
# silently vanishing from the index.
PREFERRED_TYPE_ORDER = ["decision", "spec", "learning", "pattern",
                        "bug", "reference", "handoff", "session", "checkpoint"]

# Section-header plurals that don't follow the plain "+s" rule.
TYPE_PLURALS: dict[str, str] = {}


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


def read_entry(path: Path, folder: str) -> dict:
    """Build a normalized entry record, applying fallbacks for missing fields."""
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = parse_frontmatter(text)
    date_match = DATE_RE.search(path.name)
    return {
        "type": meta.get("type", folder.rstrip("s")),
        "status": meta.get("status", "active"),
        "date": meta.get("date") or (date_match.group(1) if date_match else "—"),
        "tags": meta.get("tags", []),
        "title": extract_title(text, humanize(path.name)),
        "path": f"{folder}/{path.name}",
        "has_frontmatter": bool(meta),
        "meta": meta,
        "file": path,
    }


def collect_entries(brain_root: Path) -> list[dict]:
    """Read every entry under the known BRAIN/ subfolders."""
    entries = []
    for folder in ENTRY_DIRS:
        d = brain_root / folder
        if not d.exists():
            continue
        for path in sorted(d.glob("*.md")):
            if path.name in SKIP_FILES:
                continue
            entries.append(read_entry(path, folder))
    return entries


def as_list(value) -> list[str]:
    """Normalize a frontmatter field that may be a scalar or a list."""
    if not value:
        return []
    return value if isinstance(value, list) else [value]
