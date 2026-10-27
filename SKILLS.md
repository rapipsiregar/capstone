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
- Own the 256-LOC split rule (`AGENTS.md` §3): when a file crosses the threshold,
  decide the split boundary before anyone patches around it.
- Keep the overall plan (`plans/next-enhancements.md`) structured by real
  module/section boundaries, not arbitrary groupings.

**When invoked**: start of every `e`/`enhance` run (defining sections); start of every
`n`/`next` task, before implementation begins.

**Handoff**: hands the Backend/Frontend roles a target file layout and interface
contract, not just a task description.

## 2. Backend Engineer

**Responsibilities**
- Implement API/data-layer logic.
- Wire the mock-vs-live routing required by the Demo/Live switch (`AGENTS.md` §5) and
  the Cloud/Local endpoint switch (`AGENTS.md` §6) — both must resolve through the
  same contract so swapping either setting never changes calling code.
- Keep business logic out of route handlers; route handlers stay thin.

**When invoked**: any task touching data, APIs, or service integration.

**Handoff**: gives Frontend a stable contract (types/schema) to build against; gives
QA the list of new/changed endpoints and their expected error modes.

## 3. Frontend Engineer

**Responsibilities**
- Implement UI for the task, including the Demo/Live and Cloud/Local switcher
  controls where relevant.
- Consume the Backend's contract rather than reaching around it.
- Keep components small and composable, respecting the 256-LOC rule.

**When invoked**: any task with a user-facing surface.

**Handoff**: gives QA the golden-path user flow and the edge cases it's aware of.

## 4. QA / Test Engineer

**Responsibilities**
- During the clarification step (`AGENTS.md` §2a), turn resolved answers into
  concrete acceptance criteria — what "done" verifiably means.
- Write/extend automated tests for the change.
- Run the **verify build integrity** pass: golden path + edge cases + regression
  check on adjacent features, not just "it compiles."
- Reject work back to the relevant role if acceptance criteria aren't met — don't
  patch around a failing check.

**When invoked**: acceptance-criteria drafting during §2a; final verification pass
before a task is marked `[DONE]`.

**Handoff**: reports pass/fail with specifics (what broke, under what input) back to
whichever role owns that surface.

## 5. Hardware & Performance Compatibility Reviewer

**Responsibilities**
- Check the change against realistic hardware/runtime constraints: memory and CPU
  footprint, cross-platform behavior (Windows/Mac/Linux), cross-browser/device
  behavior for UI work, and target-deployment limits (e.g. constrained edge/on-prem
  hardware under the Local mode from `AGENTS.md` §6).
- Flag newly introduced heavy dependencies, OS-specific APIs, or assumptions that
  break under Local/on-premise deployment.
- Flag anything that would degrade badly on lower-spec hardware or slower networks,
  and suggest a lighter-weight alternative when one exists.

**When invoked**: final verification pass, alongside QA, before a task is marked
`[DONE]`; also whenever a task adds a new dependency or changes the deployment/runtime
surface.

**Handoff**: blocks `[DONE]` status until concerns are resolved or explicitly accepted
as a documented trade-off in `docs/feature-list.md`.
