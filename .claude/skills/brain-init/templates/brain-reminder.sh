#!/bin/bash
# Example hook: BRAIN reminder
# Place in .claude/hooks/ and make executable if using Claude Code

echo "=== Project BRAIN Reminder ==="
echo "Important insights from this session should be written to the 'BRAIN/' directory."
echo "Recommended locations (C:\CLAUDE\BRAIN or project-local BRAIN/):"
echo "  - BRAIN/learnings/"
echo "  - BRAIN/bugs/"
echo "  - BRAIN/decisions/"
echo "  - BRAIN/patterns/"
echo ""
echo "For mid-session notes during long work, use BRAIN/checkpoints/"