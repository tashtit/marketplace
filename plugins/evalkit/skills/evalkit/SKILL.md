---
name: evalkit
description: Evaluate and compare skills and models. Route a request to the right evalkit tool — static authoring review of one or two skills, dynamic worktree harnesses that run the same coding task while varying a skill's presence / one skill vs another / one model vs another, or cleanup of the worktrees those harnesses leave behind. Use when asked to review, compare, evaluate, benchmark, or measure a skill or model, or to clean up evaluation worktrees.
---

# Evalkit

Evalkit is a toolkit of six evaluation and review skills. This router selects the
right one; each sibling skill carries its own detailed procedure and triggers on
its own specific phrasing. Use this router when the request is general ("help me
evaluate my skills") and hand off to the specific skill once the intent is clear.

## Choosing a skill

| The user wants to… | Use | Kind | Cost |
| --- | --- | --- | --- |
| Review how well **one** skill is authored | `review-skill` | Static, read-only | Cheap |
| Compare how well **two** skills are authored | `compare-skills` | Static, read-only | Cheap |
| Measure whether a skill **changes task outcomes** (with vs without) | `evaluate-skill` | Dynamic, worktrees | Expensive |
| Compare **two skills** head-to-head on the same task | `benchmark-skills` | Dynamic, worktrees | Expensive |
| Compare **two models** on the same task | `compare-models` | Dynamic, worktrees | Expensive |
| List or remove leftover evaluation worktrees | `remove-worktrees` | Utility | Cheap |

## Static vs dynamic

- **Static** skills (`review-skill`, `compare-skills`) read a skill's files and
  judge authoring quality. They run no coding task and create no worktrees. Prefer
  these when the question is "is this skill well written?"
- **Dynamic** skills (`evaluate-skill`, `benchmark-skills`, `compare-models`) run a
  real coding task under two isolated git worktrees, varying exactly one factor,
  and compare cost, tokens, gates, and review findings. They spawn two headless
  sessions and leave worktrees on disk. Prefer these when the question is "does
  this actually produce better results?"

## Routing rules

1. If the request names authoring quality and one or two skills, route to
   `review-skill` / `compare-skills`.
2. If the request asks about task outcomes, effect, or head-to-head performance,
   route to the matching dynamic skill. Confirm before starting if the request is
   ambiguous — a dynamic run spends two headless sessions. Never guess a missing
   task or skill; ask for it.
3. If the request is about cleaning up worktrees, route to `remove-worktrees`,
   which defaults to listing only.

Each sibling skill also triggers directly on its own description, so an explicit
request (or `/<skill-name>`) reaches it without going through this router.
