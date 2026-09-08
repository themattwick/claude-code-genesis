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
import sys
from datetime import datetime
from pathlib import Path

from _brain_common import collect_entries, find_brain_root, order_types, pluralize_type


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

    # Active entries grouped by type. Known types render in a preferred
    # order; anything else (typos, new types like "worksheet") still gets
    # its own section instead of silently vanishing from the index.
    out.append("## Active knowledge\n")
    present_types = {e["type"] for e in active}
    for t in order_types(present_types):
        group = [e for e in active if e["type"] == t]
        if not group:
            continue
        out.append(f"### {pluralize_type(t)} ({len(group)})\n")
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
