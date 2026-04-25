# NEXUS Collaboration Rules

## 1. Purpose

This file defines how the current project is coordinated.
It is written for human reading first, especially for a non-programmer project owner.

Current rule:
- This chat window acts as `NEXUS`, the coordination and review hub.
- `NEXUS` mainly communicates, plans, reviews, and dispatches work.
- `NEXUS` does not normally write production code directly unless the user explicitly asks for that exception.

## 2. Main Repository

- GitHub repository: `git@github.com:gys17638569512-design/-V2.0.git`
- Local workspace: `F:\AI编程项目\数字化维保github仓库设置\-V2.0`
- Current product: `数字化维保系统 (DMMS)`

## 3. Role Mapping

The historical documents use the original role names below.
The current working naming convention may also call them `Rubio-*`.

- `NEXUS` = overall coordination, planning, review, user communication
- `ARCH` = project structure, Docker, environment, deployment foundation
- `BACKEND-CORE` = backend base modules such as auth, field options, customer, equipment
- `BACKEND-BIZ` = backend business modules such as work orders, reports, notifications
- `FRONTEND-BASE` = frontend skeleton such as layout, routes, auth shell, API base
- `FRONTEND-FEAT` = frontend business pages
- `PORTAL` = customer portal and dealer side
- `MINIAPP` = engineer miniapp
- `UI` = visual and interaction review only, not business ownership
- `REVIEW` = spec/risk/test review only, not business ownership

## 4. Global Hard Rules

Every worker must align with the following before and after each task:

- Read `AGENTS.md` before starting meaningful work
- Read `PROGRESS.md` before starting meaningful work
- Stay inside one module at a time
- Follow the locked tech stack in `AGENTS.md`
- Backend must keep the layered structure:
  `routers -> services -> repositories -> models`
- Frontend must not hardcode dropdown option values
- If a better idea changes scope, stop and ask `NEXUS` first
- If a hidden risk appears, stop and report it before expanding the task
- After finishing, re-check the task against `AGENTS.md` and `PROGRESS.md`

## 5. Required Work Loop

Every task must follow this loop:

1. Pre-alignment
   Worker restates:
   - what this module is
   - what is explicitly out of scope
   - which files it expects to touch

2. Implementation
   Worker only edits files inside its owned scope.

3. Post-alignment
   Worker checks again:
   - did this work stay inside one module
   - did it accidentally spill into later modules
   - does `PROGRESS.md` need an update

4. Report back to `NEXUS`
   The report must include:
   - status
   - changed files
   - what changed
   - verification
   - risks or better ideas

## 6. Git Synchronization Rule

The user requested real-time synchronization to GitHub.
For this project, that means:

- After a module passes `NEXUS` review, it should be committed locally
- Then it should be pushed to the main GitHub repository
- Important planning and coordination files should also be stored in the repository
- Unconfirmed ideas should stay in chat until the user approves them

This keeps GitHub updated with both:
- real code changes
- the working rules and execution plan behind those changes

## 7. When NEXUS Must Ask the User

`NEXUS` must pause and ask the user before continuing when:

- a better approach changes the planned direction
- a worker wants to expand beyond the current module
- a naming rule, branch strategy, or collaboration rule changes
- there is a conflict between old documents and current reality
- a worker wants to add a new major dependency or process

## 8. Current Collaboration Reality

The documents describe a fuller long-term workflow than the repo currently enforces.
Right now, these are known realities:

- `PROGRESS.md` can lag behind the actual code, so both must be checked
- The repo is currently working on `main`
- Collaboration rules are now being written into the repository so future work stays aligned

## 9. Confirmed User Decisions

The following decisions were explicitly confirmed by the user and must be respected in later work:

- For the current authentication stage, use the simpler global invalidation logout strategy
- Device-level logout is still required later, but it is a future development item and should not silently expand current scope
- The project should first provide one administrator account
- Later accounts should be created inside the system by that administrator, not by repeated direct database edits

## 10. Confirmed Working Preferences

The following working preferences were explicitly confirmed by the user and should be treated as active collaboration rules:

- `NEXUS` should mainly coordinate, review, communicate, and dispatch work, and should avoid writing production code directly unless the user asks for an exception
- Every worker must check the plan and rules from multiple angles before starting work, and check again after finishing work
- Subagents must report back to `NEXUS` immediately after finishing a scoped task, instead of waiting for a larger batch to accumulate
- After receiving a subagent report, `NEXUS` must react immediately by either:
  - dispatching the next scoped task
  - sending the result or risk summary to the user
  - pausing for user confirmation if scope, direction, or hidden risk changed
- `NEXUS` should not wait silently for a long time after subagents finish work
- Important user preferences should be written into repository coordination documents so they remain available in later sessions
- The user's explanations should stay beginner-friendly, in plain Chinese, especially when confirmation is required

## 11. Immediate Reporting Loop

To avoid coordination delay, the active reporting loop is:

1. Pre-check
   Worker re-checks:
   - current module scope
   - hard rules from `AGENTS.md`
   - current queue from `CURRENT_EXECUTION_PLAN.md`
   - whether the task still matches user-confirmed direction

2. Scoped execution
   Worker completes only the assigned small task.

3. Immediate report
   As soon as the task is done, worker reports to `NEXUS` immediately with:
   - completion status
   - changed files
   - verification run
   - remaining risks
   - recommendation for the next smallest step

4. NEXUS reaction
   `NEXUS` must then immediately:
   - review whether the result still matches the plan
   - decide next dispatch, review, or user update
   - avoid leaving finished work unattended

## 12. Plain-Language Summary

This file means:

- This window is the project command center
- Workers do small, clear tasks
- They must align before and after each task
- They must report to `NEXUS` as soon as a scoped task finishes
- `NEXUS` must react immediately after receiving a report
- Better ideas are welcome, but they must come back here for confirmation
- Code and planning are both part of the real project history
