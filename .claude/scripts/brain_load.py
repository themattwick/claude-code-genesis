#!/usr/bin/env python3
"""
brain_load.py
Helper for the `brain` skill.

Purpose:
    Quickly load and present the current state of Project BRAIN at any moment.

Usage:
    python brain_load.py
    python brain_load.py /path/to/project
    python brain_load.py .
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
    for name in ["BRAIN", "memory"]:
        candidate = root / name
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def main():
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
    else:
        root = Path.cwd()

    brain_dir = find_brain_dir(root)
    if brain_dir is None:
        print(f"ERROR: Could not find BRAIN/ (or legacy memory/) under {root}")
        print("Run: /brain setup")
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

    for section, label in [
        ("checkpoints", "RECENT CHECKPOINTS"),
        ("decisions", "RECENT DECISIONS"),
        ("bugs", "RECENT HARD CASES / BUGS"),
    ]:
        files = get_recent_files(brain_dir / section, 3)
        print(f"## {label}")
        for f in files:
            print(f"  - {f.name}")
        if not files:
            print("  (none yet)")
        print()

    print("=" * 80)
    print("End of current state briefing.")
    print("=" * 80)


if __name__ == "__main__":
    main()
