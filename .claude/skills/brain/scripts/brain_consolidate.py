#!/usr/bin/env python3
"""
brain_consolidate.py
Helper for the `brain consolidate` command (Claude side).

Purpose:
    Assist with synthesizing raw material across Project BRAIN into higher-quality
    structured knowledge.

    This is knowledge synthesis, not context compression.
"""

import sys
from pathlib import Path
from datetime import datetime

def get_recent_files(folder: Path, limit: int = 8) -> list[Path]:
    if not folder.exists():
        return []
    files = [f for f in folder.iterdir() if f.is_file() and f.suffix == ".md"]
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[:limit]

def main():
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
    else:
        root = Path("C:/CLAUDE") if (Path("C:/CLAUDE") / "BRAIN").exists() or (Path("C:/CLAUDE") / "memory").exists() else Path.cwd()

    def find_brain_dir(r: Path) -> Path:
        for name in ["BRAIN", "memory"]:
            p = r / name
            if p.exists() and p.is_dir():
                return p
        return r / "BRAIN"

    brain_dir = find_brain_dir(root)

    print("=" * 80)
    print("brain  — PREPARATION REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Project: {root}")
    print("=" * 80)
    print()

    print("## RECENT RAW MATERIAL (good candidates for consolidation)")
    for sub in ["checkpoints", "sessions"]:
        folder = brain_dir / sub
        files = get_recent_files(folder, 6)
        if files:
            print(f"\n[{sub}/]")
            for f in files:
                print(f"  - {f.name}")

    print("\n## RECENT STRUCTURED ENTRIES (watch for overlap)")
    for sub in ["decisions", "bugs", "learnings"]:
        folder = brain_dir / sub
        files = get_recent_files(folder, 5)
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
- Consider marking consolidated raw material (e.g. "consolidated into 2026-05-27-xxx.md")

This improves the long-term signal quality of the Project Brain.
""")

if __name__ == "__main__":
    main()

