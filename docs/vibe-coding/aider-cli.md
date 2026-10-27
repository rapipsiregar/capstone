# Aider CLI

Aider does not auto-load `AGENTS.md`; tell it to read the file explicitly.

- One-off: `aider --read AGENTS.md --read SKILLS.md`
- Persistent: add to `.aider.conf.yml` in the project root:
  ```yaml
  read:
    - AGENTS.md
    - SKILLS.md
  ```
- `--read` files are loaded read-only into context (Aider won't try to edit them),
  which is the correct mode for rules files.
