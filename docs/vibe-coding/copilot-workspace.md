# GitHub Copilot Workspace

Copilot reads `.github/copilot-instructions.md`, not `AGENTS.md`, so add a short
pointer file rather than duplicating content:

```markdown
<!-- .github/copilot-instructions.md -->
Follow the rules in /AGENTS.md and the roles in /SKILLS.md for every task in this
repository.
```

- Keep the pointer file minimal — Copilot loads it into every request's context, so
  don't paste the full `AGENTS.md` content in twice.
- For instructions scoped to a specific path (e.g. only `*.test.ts`), Copilot also
  supports `.github/instructions/<name>.instructions.md` files with an
  `applyTo:` glob in frontmatter — use these for anything that shouldn't apply
  repo-wide, keeping the cross-tool `AGENTS.md` general.
