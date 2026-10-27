# VS Code (Copilot Chat / Agent Mode)

VS Code's built-in Copilot Chat and Agent Mode use the same
`.github/copilot-instructions.md` mechanism described in
[copilot-workspace.md](copilot-workspace.md) — set that up once and both the
Workspace and the editor's inline chat/agent mode pick it up.

- Enable `github.copilot.chat.codeGeneration.useInstructionFiles` in VS Code settings
  if instructions aren't being applied automatically.
- Path-scoped instructions: `.github/instructions/<name>.instructions.md` with an
  `applyTo:` glob, same as Copilot Workspace.
- These files should stay thin pointers to `AGENTS.md`/`SKILLS.md` — see
  copilot-workspace.md for the exact pointer snippet.
