# OpenHands Agent

OpenHands prefers a root-level `AGENTS.md` as always-on context injected at
conversation start — this kit's `AGENTS.md` needs no changes or pointer file.

- **V0**: repo-specific instructions can additionally live in
  `.openhands/microagents/repo.md`.
- **V1**: prefer `.openhands/skills/` for repo-specific skills; `.openhands/microagents/`
  is still read for backward compatibility.
- If you want the `SKILLS.md` roles loaded as on-demand context (rather than always
  injected), convert each role into a microagent/skill file under
  `.openhands/skills/<role>/` with the appropriate frontmatter trigger.
