---
name: timeboxed-pdca-goal
description: Project-local workflow for timeboxed or budgeted goals. Use when the user says "1h Goal", "2h Goal", "timebox", "時間枠", "時間を余らせるな", "自律的にPlan", "PDCAで回す", or asks Codex to continue autonomously instead of stopping at the first green checkpoint.
---

# Timeboxed PDCA Goal

Use this skill when a user gives a timeboxed or budgeted goal and expects
autonomous progress across multiple green checkpoints.

## Core Rule

A green checkpoint is a checkpoint, not the end of a timeboxed Goal.

Treat the timebox as usable work budget, not merely a deadline. Do not stop
after one vertical slice when substantial budget remains and useful follow-up
work exists.

## Required Loop

1. Create or update `Tasks.md` with the timeboxed goal, acceptance gates, and a
   short PDCA backlog.
2. Plan at least:
   - Cycle 0: setup, branch, baseline, or merge/push hygiene
   - Cycle 1: first vertical slice
   - Cycle 2: expected improvement cycle
   - Cycle 3+: optional next cycles
3. After every green checkpoint, run a Remaining Budget Decision.
4. Continue into the next highest-value cycle unless a stop condition applies.
5. Commit meaningful green checkpoints when the work changes tracked files.

## Remaining Budget Decision

After each green checkpoint, explicitly decide:

- How much time/budget appears to remain?
- What defects, gaps, or next useful improvements did the last cycle reveal?
- Which next PDCA cycle gives the most value within the remaining budget?
- Is continuing blocked, unsafe, explicitly stopped, or too small to fit?

If more than roughly 25% of the requested timebox remains and a useful cycle
fits, continue. Do not mark the Goal complete only because tests passed.

## Stop Conditions

Finish a timeboxed Goal only when one of these is true:

- The requested timebox is mostly consumed.
- At least two PDCA cycles are complete and no valuable next cycle fits.
- The user explicitly asks to stop, pause, or only report status.
- Continuing would be unsafe, destructive, externally visible without approval,
  or blocked on missing user/external input.

## Final Answer

Report:

- PDCA cycles completed.
- Verification run.
- Why work stopped.
- Useful next cycles still available.

If work stopped after only one vertical slice, explain which stop condition
made that acceptable.
