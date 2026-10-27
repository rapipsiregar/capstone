# Cursor IDE

Same rules mechanism as [Cursor Composer](cursor-composer.md) — Composer is Cursor's
agent mode within the same IDE, sharing `.cursor/rules/`.

- Add the `.cursor/rules/agents.mdc` pointer rule described in cursor-composer.md
  once; it applies to both chat/Tab completions and Composer/Agent mode.
- Check **Settings → Rules** in the IDE to confirm the rule is active and
  `alwaysApply: true` (so it's loaded on every request, not just glob-matched files).
- If migrating an existing project off legacy `.cursorrules`, move its content into
  `AGENTS.md`/`SKILLS.md` first, then replace `.cursorrules` with the pointer `.mdc`
  file — don't maintain both.
