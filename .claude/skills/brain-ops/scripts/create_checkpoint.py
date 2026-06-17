#!/usr/bin/env python3
"""
Simple helper for brain-ops skill.
Creates a properly named checkpoint file in memory/checkpoints/.

Usage:
    python create_checkpoint.py "Short title of what was done"
"""
import sys
from datetime import datetime
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_checkpoint.py \"Short descriptive title\"")
        sys.exit(1)

    title = " ".join(sys.argv[1:])
    slug = title.lower().replace(" ", "-").replace(":", "").replace("/", "-")[:60]

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M")
    filename = f"{date_str}-{time_str}-{slug}.md"

    # Try to find BRAIN/checkpoints (preferred) or legacy memory/checkpoints
    candidates = [
        Path("BRAIN/checkpoints"),
        Path("memory/checkpoints"),
        Path("../BRAIN/checkpoints"),
        Path("../memory/checkpoints"),
        Path("../../BRAIN/checkpoints"),
        Path("../../memory/checkpoints"),
        Path("C:/CLAUDE/BRAIN/checkpoints"),
        Path("C:/CLAUDE/memory/checkpoints"),
    ]

    target_dir = None
    for c in candidates:
        if c.exists():
            target_dir = c
            break

    if not target_dir:
        print("Could not find BRAIN/checkpoints/ (or legacy memory/checkpoints/) directory.")
        print("Please run this from inside the project (or C:\\CLAUDE) or provide full path.")
        sys.exit(1)

    filepath = target_dir / filename

    template = f"""# Checkpoint — {title}

**Time:** {now.strftime("%Y-%m-%d %H:%M")}  
**Focus:** 

## Completed since last checkpoint


## Key artifacts / numbers


## Open questions / next steps


## Memory entries touched

"""

    filepath.write_text(template, encoding="utf-8")
    print(f"Created: {filepath}")
    print("Now fill in the sections and commit the knowledge.")

if __name__ == "__main__":
    main()
