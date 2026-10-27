# Antigravity IDE

Same config model as the [Antigravity CLI](antigravity-cli.md) — the IDE and CLI
share the same agent harness.

- Root-level `AGENTS.md` is read automatically before any agent starts work in the
  workspace; this kit's `AGENTS.md` needs no changes.
- Global, cross-project preferences: `~/.gemini/GEMINI.md`.
- Project-only, non-shared rules: `.agents/rules/` in the workspace.
- Skills (directory-based, loaded on demand) live under `.agents/skills/` if you want
  to promote a `SKILLS.md` role into a dedicated loadable package.
- To confirm the IDE picked up `AGENTS.md`, open the agent's context/inspector panel
  and check the loaded-files list.
