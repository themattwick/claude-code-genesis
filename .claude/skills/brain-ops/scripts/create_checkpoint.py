#!/usr/bin/env python3
"""
Creates a checkpoint in BRAIN/checkpoints/ from the mandatory-field schema
(adapted from the ck skill in ECC, affaan-m/ECC, MIT).

Usage:
    python create_checkpoint.py "Short title" \\
        --summary "state in at most 10 words" \\
        --left-off "src/auth/session.py:88 - refresh test fails" \\
        --next "fix the refresh test" --next "run the full suite"
    python create_checkpoint.py "Short title" --strict   # refuse without both fields

`Left off` and `Next steps` are mandatory. Without them the file is still written
(continuity beats nothing) with a warning - unless --strict, which refuses. The
sections are then left EMPTY on purpose, so `brain hygiene` reports the checkpoint
until they are filled in. A checkpoint that is only a title looks like continuity
and carries none.
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path


def slugify(title: str) -> str:
    return title.lower().replace(" ", "-").replace(":", "").replace("/", "-")[:60]


def find_target_dir() -> Path | None:
    candidates = [
        Path("BRAIN/checkpoints"),
        Path("memory/checkpoints"),
        Path("../BRAIN/checkpoints"),
        Path("../memory/checkpoints"),
        Path("../../BRAIN/checkpoints"),
        Path("../../memory/checkpoints"),
        Path.cwd() / "BRAIN" / "checkpoints",
        Path.cwd() / "memory" / "checkpoints",
    ]
    return next((c for c in candidates if c.exists()), None)


def render(title: str, now: datetime, summary: str, left_off: str, steps: list[str]) -> str:
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
    return f"""---
type: checkpoint
status: active
date: {now.strftime("%Y-%m-%d")}
tags: []
---

# Checkpoint — {title}

**Time:** {now.strftime("%Y-%m-%d %H:%M")}

## Summary
{summary}

## Left off
{left_off}

## Next steps
{numbered}

## Decisions
| What | Why |
|---|---|
|  |  |

## Blockers
-

## Numbers / artifacts
-

## Memory entries created in this block
-
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a BRAIN checkpoint.")
    ap.add_argument("title", nargs="+", help="short title")
    ap.add_argument("--summary", default="", help="state of the work, at most 10 words")
    ap.add_argument("--left-off", default="", help="one concrete place: file, function or error")
    ap.add_argument("--next", action="append", default=[], dest="steps",
                    help="a next step, in order; repeat the flag")
    ap.add_argument("--strict", action="store_true",
                    help="refuse to write unless --left-off and --next are given")
    args = ap.parse_args()

    title = " ".join(args.title)
    steps = [s.strip() for s in args.steps if s.strip()]
    left_off = args.left_off.strip()

    missing = [n for n, v in (("--left-off", left_off), ("--next", steps)) if not v]
    if missing:
        print("WARNING: mandatory field(s) not given: " + ", ".join(missing), file=sys.stderr)
        print("         Left off and Next steps must be filled in before this checkpoint "
              "is worth anything.", file=sys.stderr)
        if args.strict:
            print("Refusing to write (--strict).", file=sys.stderr)
            return 1
    words = len(args.summary.split())
    if words > 10:
        print(f"WARNING: --summary has {words} words; keep it to 10 or fewer.", file=sys.stderr)

    target_dir = find_target_dir()
    if not target_dir:
        print("Could not find BRAIN/checkpoints/ (or legacy memory/checkpoints/) directory.")
        print("Please run this from inside a project that has a BRAIN/ directory.")
        return 1

    now = datetime.now()
    filepath = target_dir / f"{now.strftime('%Y-%m-%d-%H%M')}-{slugify(title)}.md"
    filepath.write_text(render(title, now, args.summary.strip(), left_off, steps),
                        encoding="utf-8")
    print(f"Created: {filepath}")
    if missing:
        print("Fill in the empty mandatory sections now; `brain hygiene` will flag them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
