# OpenCode

OpenCode reads a root-level `AGENTS.md` natively, the same convention Claude Code
uses for `CLAUDE.md` — this kit's `AGENTS.md` is picked up as-is with no pointer file
needed.

- Confirm it's loaded via OpenCode's session/context inspector before relying on it.
- If OpenCode is used alongside Claude Code on the same repo, keep `CLAUDE.md` as the
  thin `@AGENTS.md` import (already set up in this kit) so both tools read one source
  of truth.
