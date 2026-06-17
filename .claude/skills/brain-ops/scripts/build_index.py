#!/usr/bin/env python3
"""
Generates BRAIN/INDEX.md — a single, auto-maintained entry point for `brain load`.

Scans every entry in BRAIN/, reads its frontmatter (with graceful fallbacks for
legacy entries that have none), and writes a structured index: a current-state
header plus tables grouped by entry type. Active and superseded/archived entries
are separated so stale knowledge stops competing with current knowledge.

Zero external dependencies — a minimal frontmatter parser keeps this portable.

Usage:
    python build_index.py [path-to-project-root]
"""
import re
import sys
from datetime import datetime
from pathlib import Path

ENTRY_DIRS = ["handoffs", "checkpoints", "sessions",
              "decisions", "bugs", "learnings", "patterns"]
SKIP_FILES = {"INDEX.md", "README.md", "QUICK-REFERENCE.md"}
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


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
    }


def collect_entries(brain_root: Path) -> list[dict]:
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


def render_table(entries: list[dict]) -> str:
    rows = ["| Date | Title | Tags |", "|------|-------|------|"]
    for e in sorted(entries, key=lambda x: x["date"], reverse=True):
        tags = ", ".join(f"`{t}`" for t in e["tags"]) or "—"
        rows.append(f"| {e['date']} | [{e['title']}]({e['path']}) | {tags} |")
    return "\n".join(rows)


def render_index(entries: list[dict]) -> str:
    active = [e for e in entries if e["status"] == "active"]
    retired = [e for e in entries if e["status"] != "active"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    out = [f"# BRAIN — Index\n", f"_Auto-generated {now}. Do not edit by hand — "
           f"run `build_index.py`._\n"]

    # Current state
    handoffs = [e for e in active if e["type"] == "handoff"]
    checkpoints = [e for e in active if e["type"] == "checkpoint"]
    out.append("## Current state\n")
    if handoffs:
        latest = sorted(handoffs, key=lambda x: x["date"], reverse=True)[0]
        out.append(f"- **Latest handoff:** [{latest['title']}]({latest['path']}) "
                   f"({latest['date']})")
    if checkpoints:
        latest_cp = sorted(checkpoints, key=lambda x: x["date"], reverse=True)[0]
        out.append(f"- **Last checkpoint:** [{latest_cp['title']}]({latest_cp['path']}) "
                   f"({latest_cp['date']})")
    out.append(f"- **Active entries:** {len(active)}  ·  "
               f"**Retired:** {len(retired)}\n")

    # Active entries grouped by type
    out.append("## Active knowledge\n")
    for t in ["decision", "learning", "pattern", "bug", "handoff",
              "session", "checkpoint"]:
        group = [e for e in active if e["type"] == t]
        if not group:
            continue
        out.append(f"### {t.capitalize()}s ({len(group)})\n")
        out.append(render_table(group) + "\n")

    # Retired (superseded / archived) — kept out of the way
    if retired:
        out.append("## Retired (superseded / archived)\n")
        out.append(render_table(retired) + "\n")

    # Hygiene note: entries still missing frontmatter
    legacy = [e for e in entries if not e["has_frontmatter"]]
    if legacy:
        out.append(f"## Needs frontmatter ({len(legacy)})\n")
        out.append("These entries were indexed via fallback (folder + filename). "
                   "Add frontmatter to make them filterable:\n")
        for e in legacy:
            out.append(f"- `{e['path']}`")
        out.append("")

    return "\n".join(out)


def main() -> None:
    start = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    brain_root = find_brain_root(start)
    if not brain_root:
        print("Could not find a BRAIN/ directory at or above:", start)
        sys.exit(1)

    entries = collect_entries(brain_root)
    index_path = brain_root / "INDEX.md"
    index_path.write_text(render_index(entries), encoding="utf-8")
    print(f"Wrote {index_path}  ({len(entries)} entries indexed)")


if __name__ == "__main__":
    main()
