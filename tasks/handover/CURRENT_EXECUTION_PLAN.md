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
   Current status: completed in local workspace and awaiting repository synchronization review

2. `F01` Frontend initialization, routes, and layout framework
   Notes:
   - the repo already has a light frontend skeleton
   - this module should first align the existing skeleton with the official plan

3. `M02` Database models and Alembic base
   Notes:
   - create the proper model and migration foundation
   - do not jump into business API logic yet

4. `M03` Authentication

5. `M04` Field options

6. `M05` to `M08`
   Customer, contacts, sites, equipment

7. `F02` to `F10`
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

## 6. Review Rule After Each Module

After a module finishes, `NEXUS` must check:

- Was the module scope respected?
- Were tests or builds run?
- Does `PROGRESS.md` need updating?
- Should the result be committed and pushed now?
- Is the next module still the right next module?

## 7. Plain-Language Summary

This file means:

- we are not trying to build everything at once
- we are building the main backbone first
- each module must be checked before start and after finish
- if a better path appears, it comes back to the user for confirmation
