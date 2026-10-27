# Antigravity CLI

Antigravity (Google) reads a root-level `AGENTS.md` natively as its primary
standing-instructions file — no changes needed, this kit's `AGENTS.md` is picked up
as-is.

- **Verify it's loaded**: run `agy inspect` in the project root; it lists loaded
  config sources and should show `AGENTS.md`.
- **Global rules** (apply to every project, not just this one) live in
  `~/.gemini/GEMINI.md` — keep that file for personal cross-project preferences only;
  project-specific rules belong in `AGENTS.md`.
- **Workspace-only rules** (not meant to travel with the repo) can go in
  `.agents/rules/` instead.
- **Skills**: Antigravity supports directory-based Skills loaded only when relevant.
  If you want the `SKILLS.md` roles enforced more strictly, mirror each role as a
  `.agents/skills/<role>/SKILL.md` package; otherwise the plain `SKILLS.md` reference
  from `AGENTS.md` §4 is sufficient.
