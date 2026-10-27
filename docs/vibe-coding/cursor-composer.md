# Cursor Composer

Cursor does not read `AGENTS.md` natively — it uses its own rules format. Point
Composer at this kit's rules with a small pointer rule rather than duplicating
content:

1. Create `.cursor/rules/agents.mdc` (the current, non-deprecated format — the old
   single `.cursorrules` file still works but is legacy) with:
   ```
   ---
   alwaysApply: true
   ---
   Read and follow AGENTS.md and SKILLS.md at the project root before doing any work.
   ```
2. Keep the actual rules in `AGENTS.md`/`SKILLS.md` as the source of truth — the
   `.mdc` file is just a pointer, so Cursor and Claude Code/other tools never drift
   out of sync.
3. For rules that should only apply to certain paths (e.g. only `src/api/**`), add
   additional scoped `.mdc` files under `.cursor/rules/` with a `globs:` frontmatter
   key — that's Cursor-specific and doesn't belong in the cross-tool `AGENTS.md`.
