# Skills & Roles

Five roles an agent applies during `n`/`next` execution (see `AGENTS.md`). One agent
can play all of them in sequence; a multi-agent harness may spawn each as a separate
subagent for a fresh-context pass. Order matters: Architect → Backend/Frontend → QA →
Hardware/Compatibility.

## 1. Software Architect

**Responsibilities**
- Decide where new code lives; keep module boundaries clean.
- Prefer deep modules (few, well-bounded files with simple interfaces) over shallow
  ones (many tiny files) — this is what makes a codebase navigable for an agent.
- Own the 256-LOC split rule (`AGENTS.md` Agent Instructions §3): when a file crosses
  the threshold, decide the split boundary before anyone patches around it.
- Keep the overall plan (`NEXT_AND_ENHANCEMENT.md`) structured by real module/section
  boundaries with exactly 3 small tasks per section (one goal, one proof).

**When invoked**: start of every `e`/`enhance` run (defining sections); start of every
`n`/`next` task, before implementation begins.

**Handoff**: hands the Backend/Frontend roles a target file layout and interface
contract, not just a task description.

## 2. Backend Engineer

**Responsibilities**
- Implement API and data-layer logic using FastAPI, Pydantic, and SQLite.
- Enforce authentic data pipeline without fake/mock/duplicate data (`AGENTS.md` §12) and
  ensure all endpoints deliver dynamic data from dataset (`AGENTS.md` §13).
- Integrate authentic IndoBERT transformer inference and empirical SHAP XAI calculation
  (`AGENTS.md` §1 & §2), ensuring metrics are calculated from `test.csv` without hardcoding.
- Keep business logic in `backend/services/`; route handlers in `backend/api/` stay thin.

**When invoked**: any task touching data, APIs, IndoBERT model, or service integration.

**Handoff**: gives Frontend a stable contract (schema/JSON) to build against; gives
QA the list of new/changed endpoints and their expected error modes.

## 3. Frontend Engineer

**Responsibilities**
- Implement UI for the task using Vanilla JS / HTML5 / CSS3 with `Chart.js` via CDN.
- Follow UI design rules strictly (`AGENTS.md` §15): anti-slop principles, taste-skill
  app-screen conventions (`references/app-screens.md`), no emoji as UI, honest media
  text placeholders (`AGENTS.md` §14), and adherence to `DESIGN.md`.
- Consume Backend REST APIs dynamically without hardcoding values in HTML/JS (`AGENTS.md` §13).
- Keep components small and composable, respecting the 256-LOC rule (`AGENTS.md` Agent Instructions §3).

**When invoked**: any task with a user-facing surface.

**Handoff**: gives QA the golden-path user flow and the edge cases it's aware of.

## 4. QA / Test Engineer

**Responsibilities**
- During the clarification step (`AGENTS.md` §2a), turn resolved answers into
  concrete acceptance criteria — what "done" verifiably means.
- Write and extend automated tests using `pytest` following the TDD workflow (`AGENTS.md` §9).
- Enforce the 4-layer UI Definition of Done (`AGENTS.md` §15):
  1. `lint.mjs --app` without new FAILs.
  2. `inspect.mjs --app` 0 FAIL at 1440px, 768px, and 390px.
  3. Anti-slop Delivery Gate PASS per item with evidence.
  4. Real browser visual verification via `browser_subagent` (`AGENTS.md` §8).
- Reject work back to the relevant role if acceptance criteria aren't met.

**When invoked**: acceptance-criteria drafting during §2a; final verification pass
before a task is marked `[x]`.

**Handoff**: reports pass/fail with specifics (terminal outputs, screenshots) back to
whichever role owns that surface.

## 5. Hardware & Performance Compatibility Reviewer

**Responsibilities**
- Check the change against realistic hardware and runtime constraints: local GPU
  (NVIDIA RTX 3050 Laptop 6 GB VRAM), CPU RAM (~15 GB), and inference latency (< 1.5s).
- Verify PyTorch CUDA vs CPU compatibility and ensure heavy binary weights (>100 MB)
  are excluded from git tracking (`.gitignore` / Hugging Face Hub).
- Check responsive behavior across breakpoints (Desktop 1440px, Tablet 768px, Mobile 390px).
- Flag newly introduced heavy dependencies, unnecessary polling, or memory leaks.

**When invoked**: final verification pass alongside QA before a task is marked `[x]`;
also whenever a task adds a new dependency or modifies model loading/inferencing.

**Handoff**: blocks `[x]` status until performance and compatibility concerns are resolved
or explicitly documented in `docs/feature-list.md`.
