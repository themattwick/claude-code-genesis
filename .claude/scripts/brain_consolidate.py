#!/usr/bin/env python3
"""
brain_consolidate.py
Helper for the `brain consolidate` command.

Purpose:
    Assist with synthesizing raw material across Project BRAIN into
    higher-quality structured knowledge.

Usage:
    python brain_consolidate.py
    python brain_consolidate.py /path/to/project
"""

import sys
from pathlib import Path
from datetime import datetime


def get_recent_files(folder: Path, limit: int = 8) -> list[Path]:
    if not folder.exists():
        return []
    files = [f for f in folder.iterdir() if f.is_file() and f.suffix == ".md"]
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[:limit]


def find_brain_dir(root: Path) -> Path:
    for name in ["BRAIN", "memory"]:
        p = root / name
        if p.exists() and p.is_dir():
            return p
    return root / "BRAIN"


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    brain_dir = find_brain_dir(root)

    print("=" * 80)
    print("BRAIN CONSOLIDATE — PREPARATION REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Project: {root}")
    print("=" * 80)
    print()

    print("## RECENT RAW MATERIAL (good candidates for consolidation)")
    for sub in ["checkpoints", "sessions"]:
        files = get_recent_files(brain_dir / sub, 6)
        if files:
            print(f"\n[{sub}/]")
            for f in files:
                print(f"  - {f.name}")

    print("\n## RECENT STRUCTURED ENTRIES (watch for overlap)")
    for sub in ["decisions", "bugs", "learnings"]:
        files = get_recent_files(brain_dir / sub, 5)
        if files:
            print(f"\n[{sub}/]")
            for f in files:
                print(f"  - {f.name}")

    print("\n" + "=" * 80)
    print("CONSOLIDATION GUIDANCE")
    print("=" * 80)
    print("""
Focus on turning volume into clarity:

- Group related checkpoints and notes
- Extract real decisions, hard cases, and reusable insights
- Create or improve entries in decisions/, bugs/, learnings/, patterns/
- Mark consolidated raw material as processed

This improves the long-term signal quality of Project BRAIN.
""")


if __name__ == "__main__":
    main()
