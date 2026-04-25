# Current Execution Plan

## 1. What We Are Building First

The first stage is not the whole long-term SaaS scope.
The first stage is the core PC management workflow.

Plain-language meaning:
- get the backend foundation running
- get the PC admin side running
- connect the most important daily workflow first

The first target workflow is:

`login -> customer -> equipment -> work order -> report`

## 2. Current Priorities

Priority order for the current stage:

1. Backend foundation
2. Frontend foundation
3. Data foundation
4. Login and permission basics
5. Work order core workflow
6. Report minimum closed loop

## 3. Module Queue

This is the current recommended queue.
`NEXUS` may adjust the next step after review, but should not change direction silently.

1. `M01` Project initialization and Docker foundation
   Current status: completed and pushed to repository, verified by review

2. `F01` Frontend initialization, routes, and layout framework
   Current status: completed: full layout shell, route skeleton, Dashboard, Placeholder component, and AppLayout all committed

3. `M02` Database models and Alembic base
   Current status: completed and pushed to repository

4. `M03` Authentication
   Current status: completed and pushed to repository, including first-admin bootstrap and token invalidation hardening

5. `M04` Field options
   Current status: completed: CRUD API, seeded baseline dropdown data, migration, and tests committed

6. `M05` Customer management
   Current status: completed: list, detail, create, update, delete, manager isolation, soft delete, and tests verified

7. `M06` to `M08`
   Current status: `M06` completed: contacts list, create, update, soft delete, manager isolation, and tests verified; `M07` to `M08` pending

8. `F02` to `F10`
   Login, dashboard, customer pages, equipment pages, work order pages

## 4. What Is Intentionally Not First

The following are important, but not the first battle:

- customer portal
- dealer side
- miniapp
- white-label features
- OCR
- OSS upload
- WebSocket notifications
- advanced reporting and statistics

Reason:
- starting too wide will reduce control
- the team needs one stable main workflow first

## 5. Review Rule Before Each New Module

Before starting a new module, `NEXUS` must check:

- Does this match `AGENTS.md`?
- Does this still match `PROGRESS.md`?
- Does this still match the first-stage goal?
- Did the previous module really finish verification?
- Is there any better idea that needs user confirmation first?

## 6. Confirmed Product Decisions

The following decisions were explicitly confirmed by the user and should be treated as active project rules unless changed later.

### 6.1 Logout Strategy

Current confirmed rule:

- M03 uses the simpler and safer "global invalidation" logout strategy
- In plain language, when the system forces a token chain to become invalid, all active sessions for that user become invalid together

Reason:

- this is the most stable and lowest-risk way to finish the current authentication stage
- it keeps M03 small enough to complete cleanly

Recorded future requirement:

- device-level logout is still wanted later
- that means the future system should be able to log out one device without forcing all devices offline
- this is not part of the current M03 scope
- this should be added to later development content when the auth/session design is expanded

### 6.2 First Admin Account

Current confirmed rule:

- the system should first provide one administrator account
- after the system is fully developed enough to be used normally, other accounts should be created inside the system by that administrator

Plain-language meaning:

- we do not depend on manually creating every future user in the database
- we first solve the "how do we get the first real admin into the system" problem
- after that, normal user creation should be handled through system management features, not database handwork

Implementation direction:

- in the near term, the project should provide a safe way to initialize the first admin account
- later account expansion should be handled by admin-side user management capabilities

## 7. Review Rule After Each Module

After a module finishes, `NEXUS` must check:

- Was the module scope respected?
- Were tests or builds run?
- Does `PROGRESS.md` need updating?
- Should the result be committed and pushed now?
- Is the next module still the right next module?

## 8. Plain-Language Summary

This file means:

- we are not trying to build everything at once
- we are building the main backbone first
- each module must be checked before start and after finish
- if a better path appears, it comes back to the user for confirmation
