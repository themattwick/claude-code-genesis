# Contributing to Genesis

## How to Create a Skill

Each skill lives in `.claude/skills/<skill-name>/` and contains:

```
.claude/skills/my-skill/
├── SKILL.md          # Required: skill definition with YAML frontmatter
├── scripts/          # Optional: helper scripts
└── templates/        # Optional: template files
```

### SKILL.md Format

```yaml
---
name: my-skill
description: >
  One-line description that Claude uses to trigger this skill.
  Be specific — Claude reads this to decide when to activate.
metadata:
  short-description: "Brief summary"
  category: "workflow"
  tags: ["tag1", "tag2"]
---

# my-skill — Title

## What it does
...
```

### Guidelines

- One skill = one clear responsibility
- Keep SKILL.md under 200 lines
- Test in a real project before submitting
- Follow the brain-ops pattern for operation-style skills

## Submitting a Skill

1. Fork the repo
2. Add your skill under `.claude/skills/`
3. Update `docs/SKILL_DIRECTORY.md` with your skill's entry
4. Open a PR with a description of what problem it solves

## Questions

Open a [GitHub Discussion](https://github.com/themattwick/claude-code-genesis/discussions).
