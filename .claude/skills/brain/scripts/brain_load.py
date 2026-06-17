#!/usr/bin/env python3
"""
memory_load.py
Helper for the `memory` skill (Claude side).

Purpose:
    Quickly load and present the current state of Project BRAIN at any moment.

Usage:
    python memory_load.py
    python memory_load.py "C:\CLAUDE"
    python memory_load.py .

When the user says:
    "brain load"
    "brain "
    "memory briefing"
    "memory current state"

...run this script to get a fast, structured overview of where things stand right now.
"""

import sys
from pathlib import Path
from datetime import datetime

def find_latest_handoff(root: Path) -> Path | None:
    patterns = ["*HANDOFF*.md", "*handoff*.md", "*_HANDOFF*.md", "*_handoff*.md"]
    candidates = []
    for pattern in patterns:
        candidates.extend(root.glob(pattern))
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None

def get_recent_files(folder: Path, limit: int = 3) -> list[Path]:
    if not folder.exists():
        return []
    files = [f for f in folder.iterdir() if f.is_file() and f.suffix == ".md"]
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[:limit]

def read_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"[Error reading {path.name}: {e}]"

def find_brain_dir(root: Path) -> Path | None:
    """Prefer BRAIN/ (new canonical name). Fall back to legacy 'memory/' for old projects."""
    for name in ["BRAIN", "memory"]:
        candidate = root / name
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def main():
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
    else:
        candidates = [Path("C:/CLAUDE"), Path.cwd()]
        root = next((c for c in candidates if find_brain_dir(c)), Path.cwd())

    brain_dir = find_brain_dir(root)
    if brain_dir is None:
        print(f"ERROR: Could not find BRAIN/ (or legacy memory/) directory under {root}")
        sys.exit(1)

    print(f"[info] Using Project BRAIN at: {brain_dir}")

    print("=" * 80)
    print("PROJECT BRAIN — CURRENT STATUS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Project root: {root}")
    print("=" * 80)
    print()

    handoff = find_latest_handoff(root)
    if handoff:
        print("## LATEST HANDOFF / SUMMARY DOCUMENT")
        print(f"File: {handoff.name}")
        print("-" * 80)
        lines = read_file_safe(handoff).splitlines()
        for line in lines[:50]:
            print(line)
        if len(lines) > 50:
            print("... (truncated)")
        print()

    brain_dir = find_brain_dir(root) or (root / "BRAIN")
    checkpoints_dir = brain_dir / "checkpoints"
    recent_checkpoints = get_recent_files(checkpoints_dir, 3)
    print("## RECENT CHECKPOINTS")
    for cp in recent_checkpoints:
        print(f"- {cp.name}")
    print()

    decisions_dir = brain_dir / "decisions"
    recent_decisions = get_recent_files(decisions_dir, 3)
    print("## RECENT DECISIONS")
    for d in recent_decisions:
        print(f"- {d.name}")
    print()

    bugs_dir = brain_dir / "bugs"
    recent_bugs = get_recent_files(bugs_dir, 3)
    print("## RECENT HARD CASES / BUGS")
    for b in recent_bugs:
        print(f"- {b.name}")

    print("\n" + "=" * 80)
    print("End of current state briefing.")
    print("=" * 80)

if __name__ == "__main__":
    main()

