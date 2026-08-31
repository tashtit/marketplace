---
name: mock-design-interview
description: Conduct a mock system design interview about an implementation the candidate already built. Scopes to one attempt directory, reads it and its git history, recovers session transcripts to tell prompted from unprompted decisions, then asks questions one at a time — probing decisions made, using symptom scenarios for concerns missed, following up when answers are thin — and ends with a level assessment. Invoke only on an explicit request to be interviewed, grilled, or assessed on a design. Never invoke it to write, fix, or review code, nor in a session that helped build the code under interview.
---

# Mock Design Interview

Interview the candidate about a system they have built. Questions come from probe seeds in the
bundled `system-design-concerns` library, graded against its `level-expectations.md`. Resolve its
path with `scripts/library-path.sh read` and read those files directly — the library is data, not
a skill to invoke.

## Run only when asked, and only in a fresh session

**Run this only on an explicit request to be interviewed, grilled, or assessed on a design.** It
is never background help while someone writes code, and an implementation existing in the
repository is not a reason to start one.

**If you helped build the system, you cannot interview about it.** You already know why every
line exists, you are invested in the choices, and you will unconsciously ask only what you know
the candidate can answer. Say so and ask them to start a new session.

"Fresh" means fresh *for this exercise*. A session that worked on unrelated code is fine — what
disqualifies you is having built the implementation under interview.

Two other requests look like this one and are not: **do not use this skill to write, fix, or
review an implementation** — an interview reports what an answer revealed, it does not repair the
code — and do not use it on an attempt that does not exist yet. There must already be something
built to interview about.

The cleanest way to guarantee a fresh session is to keep this plugin **disabled while the
implementation is being built** and enable it for the interview. The bundled library is the answer
key, so a build session that can read it is a build session that will.

## The two rules

**1. Never name the concern you are probing.** Describe a symptom and let the candidate find the
cause. "Reads are at 800ms, the index is being used, CPU is flat — walk me through it" tells you
whether they know. "Did you consider caching?" hands over the answer and measures nothing.

**2. Never accept a thin answer to be agreeable.** A weak answer gets a follow-up, not a nod.
The candidate is here to find gaps before a real interviewer does — agreeableness is the one
failure mode that makes this worthless. If an answer is wrong, say it is wrong.

## Setup

### 1. Establish scope

**Do not assume the repository is the task.** A practice repository usually holds several
implementations — often the same problem attempted more than once — alongside unrelated code.
Interviewing across the whole repository mixes unrelated designs and grades the wrong code.

**One directory per attempt is the convention to ask for.** A directory is a better boundary than
a branch, for one reason that decides it: the working directory is what the session store records
and it never changes, while a branch name can be renamed mid-task and split the transcript in two.
A directory also groups re-attempts for free — `url-shortener/attempt-2` next to `attempt-1`.

Ask for the directory first. A branch on top is fine and gives a cleaner diff, but it is a bonus,
not the key.

```bash
ls -d */ */*/                  # what attempts exist
git log --oneline -15          # recent activity, if committed
```

**Never interview the tooling.** `.claude/` holds these skills, and shared library code (for
example a reusable cache or storage helper) may live outside any attempt directory. Neither is a
practice attempt. If the candidate's answer turns on shared code, read it for context — but the
attempt under interview is the directory they named, and shared code is only evidence insofar as
this attempt uses it.

Establish, before reading anything:

- **Which directory** — the attempt under interview. If the candidate names a branch instead, that
  works too; derive the paths from it.
- **Which attempt.** If the same problem appears more than once, ask which one. The most recent is
  the usual choice, but the candidate may want an older one.
- **Committed or not.** Uncommitted work is fine — see step 3 — but you need to know which, since
  it decides whether history exists to read at all.
- **Session length.** Default to 8–12 questions.

If the target is ambiguous, list what you found and ask. Guessing wastes the session.

Everything after this point is scoped to that directory. When you quote code, quote from inside
the scope — referencing a neighbouring exercise reveals immediately that you are interviewing the
wrong thing.

### 2. Read the artifact

Read the attempt directory. That is the whole scope — no diff arithmetic required:

```bash
ls -R <dir>
```

Cover: data model, identifier scheme, read path, write path, expiry handling, response semantics,
tests, configuration. Form your own view of what was decided and what was skipped **before**
asking anything.

Ignore code outside the directory, even when it is relevant-looking. A cache in a *different*
attempt is not evidence about this one.

If the attempt happens to be on its own branch, `git diff --stat <base>...HEAD` is a faster
summary. Use three-dot, not two-dot: three-dot diffs against the merge base, so a practice branch
left behind while `main` moved on is not credited with unrelated commits.

### 3. Read the history, if there is any

The final state tells you what exists, not what was *decided*. A design reached after three
reversals reads identically to one that was right immediately — and the reversals are the
interesting part.

```bash
git log --oneline -- <dir>     # the decision sequence
git log -p -- <dir>            # how the design evolved
```

What arrived late, got reverted, or was rewritten shows where the candidate's understanding
changed. Those are the strongest probe anchors, because you can ask about a decision they already
revisited once — and an early-and-unchanged decision is worth probing differently from a hard-won
one.

**Uncommitted work is not a problem.** `git diff -- <dir>` and `git status` still bound the scope,
and the session transcript in step 4 carries the decision sequence regardless. Do not ask the
candidate to commit for the interview's benefit, and do not treat a clean history as a gap in the
evidence — history is a bonus signal here, not a requirement.

Never run an unscoped `git log`. The repository holds every other attempt, and an unscoped log
pulls them all in.

### 4. Reconstruct who raised what

The level bars turn on whether a concern was raised *unprompted* — see `level-expectations.md`.
When the candidate directed an agent to write the code, that distinction lives in the transcript,
not the repo.

**Find the sessions by the files they touched.** The attempt directory is the key, and it is the
most reliable one available: file paths are recorded on every edit and never change, whereas a
branch name can be renamed mid-task and split the transcript across two names.

**Match on a fully-qualified path, not a bare directory name.** `LIKE` is a substring match with no
notion of path boundaries, so a short or generic fragment silently matches unrelated work —
`'%src%'` matches sessions across every project on the machine, and `'%attempt-1%'` matches every
problem's first attempt. Anchor the pattern with enough of the path to be unambiguous, and wrap it
in slashes so it cannot match a partial segment:

```sql
SELECT s.id, s.branch, s.created_at, COUNT(DISTINCT f.file_path) AS files
FROM session_files f
JOIN sessions s ON s.id = f.session_id
WHERE f.file_path LIKE '%/<repo>/<problem>/<attempt>/%'
GROUP BY s.id ORDER BY s.created_at
```

Include the repository segment even though every attempt lives there: worktrees carry a different
directory name from the main checkout, and the problem segment alone is not unique across machines.
Get the real prefix from `git rev-parse --show-toplevel` rather than guessing it.

Sanity-check the result before trusting it: the returned `file_path` values must all sit inside the
attempt directory. If any point elsewhere, the pattern is too loose — tighten it and re-run rather
than filtering by eye, because the same pattern feeds the measurement query below.

Prefer `source: "local"` if the cloud store is unavailable.

**If no session store exists at all**, say so and continue without this axis. The transcript is how
the prompted/unprompted distinction is measured, so without it the level bars that turn on
"unprompted" cannot be applied — report the assessment as covering the design only, and ask the
candidate directly who raised each concern rather than inferring it. An answer given about one's
own history is weaker evidence than a recorded prompt; label it as such instead of scoring it the
same.

**Several sessions is normal, not an error** — a multi-day exercise, a context limit, a later fix.
Treat them as **one transcript in sequence** ordered by `created_at`, because a concern raised in
session 1 is not raised again in session 3, and grading only the last would score the candidate's
summary rather than their thinking. Never assume one session per attempt.

**Then catch the sessions that changed no files.** Planning, design, and review sessions carry no
edits, so the query above misses them entirely — and they hold the strongest unprompted evidence,
because a concern raised there was raised *before* any code existed. Sweep the directory that the
edit sessions ran in:

```sql
SELECT id, cwd, branch, created_at, summary
FROM sessions
WHERE cwd IN (SELECT DISTINCT cwd FROM sessions WHERE id IN (<ids from above>))
ORDER BY created_at
```

`cwd` is stable where branch is not: in a worktree that was renamed mid-task, the sessions keep one
`cwd` while `branch` splits in two. That is why this sweep uses `cwd` and not `branch`.

**Check each returned `cwd` before trusting the sweep.** A session's `cwd` is where it was launched,
not where it wrote — sessions do edit files outside their own `cwd`. When that happens the `cwd` is
some *other* repo, and sweeping it imports that repo's entire history: one observed case pulled in
**35 unrelated sessions**. So:

- If the `cwd` is inside the practice repository or the attempt directory, the sweep is sound —
  keep all of it.
- If the `cwd` points somewhere else, discard the sweep for that `cwd`. Do not try to salvage it by
  reading summaries; a plausible-looking summary from another project is exactly the failure mode.
  Note the transcript as partial and continue — a missing planning session costs you one axis,
  whereas a foreign one produces confident fabrications.

If a session under a valid `cwd` looks like a genuinely different task, ask rather than assume —
but differing branch names alone are usually just a rename.

**Then join files to turns — this is the measurement.** `session_files.turn_index` records which
turn changed a file, so joining it to `turns` at the same index gives you the prompt that caused
each change:

```sql
SELECT s.id, f.turn_index, f.tool_name, f.file_path,
       substr(t.user_message, 1, 300) AS prompt
FROM sessions s
JOIN session_files f ON f.session_id = s.id
LEFT JOIN turns t
  ON t.session_id = f.session_id AND t.turn_index = f.turn_index
WHERE f.file_path LIKE '%/<repo>/<problem>/<attempt>/%'
ORDER BY s.created_at, f.turn_index
```

Order by `s.created_at` **then** `turn_index`: `turn_index` restarts at 0 in every session, so
ordering by it alone interleaves a later session's opening turns with an earlier session's middle.
That would scramble the very sequence you are trying to establish.

Read the result directly: if the cache appears at turn 9 and the turn-9 prompt says "add caching",
the candidate raised it. If the prompt says "make the read path faster", the agent chose it. If the
prompt is about something else entirely, the agent volunteered it and the candidate may never have
noticed — the most interesting case of all, and worth probing as if the concern were absent.

A `NULL` prompt means the `LEFT JOIN` found no turn at that index — treat it as *unknown*, never as
"no prompt". It happens when the file row belongs to a turn still in flight, so the index sits one
past the last saved turn. Confirm with `SELECT MAX(turn_index) FROM turns WHERE session_id = '<id>'`
before reading anything into it.

Pull full turns (`SELECT turn_index, user_message, assistant_response FROM turns WHERE
session_id = '<id>'`) only for the turns that matter. Reading everything wastes the budget you
need for the interview itself.

For each concern, record: **candidate first**, **agent first**, or **neither**. A concern the
agent introduced unprompted is not evidence of the candidate's judgment — but noticing and
interrogating it during review is.

**When the transcript is missing or thin.** Commit refs are recorded inconsistently, sessions get
pruned, and work done outside a session leaves no turns at all. Do not infer prompting from
commit messages or code comments — that is guessing, and a confident wrong claim about who raised
what is worse than none. Say the prompting axis cannot be measured, interview on depth alone, and
note in the debrief that the level estimate is unanchored on that axis.

### 5. Select probes

Load the probe file matching the problem class. Choose seeds that:

- **Probe real decisions** — anchored to what is actually in their code.
- **Probe real gaps** — a concern absent from the repo, asked as a symptom.
- **Span levels** — some mid, some senior, at least two staff+.

Skip seeds whose concern does not apply to the design. A concern that cannot apply cannot be
graded.

## Conducting it

**One question at a time**, via `ask_user`. Never batch. Never number the questions or announce
which concern is coming.

**Generate wording live** from the seed plus their code. Say "your `POST /urls` handler does a
synchronous insert, then…" — not the seed's generic phrasing. Reference their actual function
names, tables, and endpoints.

**Follow up before moving on.** Judge each answer against the seed's *Looking for*:

| Answer quality | Response |
| --- | --- |
| Correct and complete | Acknowledge briefly, optionally push one level deeper |
| Right direction, missing the mechanism | Use the seed's follow-up |
| Confidently wrong | Say so plainly, then ask the question that exposes it |
| "I don't know" | Ask what they *would* check to find out |

Two follow-ups per probe is usually enough. Do not interrogate to exhaustion.

**Stay in role.** No hints, no leading, no partial answers. If they ask whether they are right,
do not resolve it until the debrief — real interviews do not.

**Never grade beyond the sources.** Where a probe carries a "do not grade this" note, honor it.
If the candidate raises something no source establishes a bar for, engage with it but score
nothing.

## Debrief

Only after the questions are done.

**Per concern:** who raised it first (candidate / agent / neither), how the answer held up, and
what the follow-up revealed.

**Level assessment.** Name the highest bar cleared and quote the specific expectation from
`level-expectations.md` that supports it. Be precise about what separates them from the next
level — "you reached read-heaviness when I asked, but staff+ requires structuring the design
around it from the start."

**The three most valuable things they got wrong**, with what a strong answer contains.

**What was cleanly right.** Short. This section is not the point of the exercise.

**Progress, if this problem was attempted before.** One directory per attempt makes this cheap:
earlier attempts are sibling directories, so compare against them and say what improved and what
recurred. A concern missed twice is a more useful finding than any single-session score. Compare
only against attempts at the *same* problem — a `problem/attempt-N` layout makes them identifiable
without any guessing.

### Scoring honestly

- Grade the **answers**, not the code. Working code with an answer that cannot explain it is a
  gap, and it is the gap a real interviewer will find.
- A concern the agent introduced and the candidate never questioned is **not** the candidate's
  point.
- "Correctly decided it was unnecessary" requires a *reason*, given before you asked. Silence is
  not a decision.
- **Shared code cuts both ways.** Pulling in a shared cache or storage helper is not the same as
  reasoning about whether this problem needs one. Ask why it applies here; a candidate who wired it
  in because it existed has demonstrated less than one who argued for it. Conversely, deliberately
  *not* reusing it, with a reason, is a real answer.
- Do not inflate to be encouraging. A debrief with no real findings means the interview was too
  easy — say that instead of manufacturing praise.

## Anti-patterns

- **Naming the concern.** "Have you thought about caching?" — the answer is now free.
- **Interviewing the whole repo.** Every attempt lives here, so grading code from another attempt —
  or from an earlier attempt at the same problem — produces confidently wrong findings.
- **Sweeping a `cwd` that belongs to another repo.** A session's `cwd` is where it launched, not
  where it wrote. If it points outside the practice repository, that sweep imports a foreign
  project's history — drop it rather than reading its summaries.
- **Crediting work from another exercise.** Solving something well last week is not evidence
  about this implementation.
- **Assuming one session per attempt.** There are usually several. The concern was raised once,
  early; grading the last session alone scores the summary, not the thinking.
- **Keying the transcript on the branch name.** A renamed worktree branch leaves its earliest
  sessions under the old name. File paths and `cwd` do not move; branch names do.
- **Matching sessions on a bare directory name.** `LIKE '%src%'` or `LIKE '%attempt-1%'` pulls in
  unrelated repos and other problems' attempts. Qualify the path and check the returned paths.
- **Discarding sessions with no file changes.** Planning and review sessions carry the strongest
  unprompted evidence precisely because nothing was written yet.
- **Asking the candidate to commit for the interview's benefit.** Uncommitted work is fully
  interviewable; the transcript carries the decision sequence either way.
- **Interviewing the tooling or the shared library.** `.claude/` and any shared code are not
  practice attempts. Reusing a shared helper is a decision worth probing; writing it is not part
  of this attempt.
- **Asking what the code already answers.** Ask *why*, not *what*.
- **Accepting vocabulary as understanding.** "I used Redis because it's fast" names a product,
  not a property. Push.
- **Batching questions.** An interview is a conversation.
- **Softening a wrong answer.** The most expensive habit in this whole skill.
- **Grading unbanked concerns.** If no source set the bar, there is no bar.
- **Reading a `NULL` prompt as "unprompted".** It means no turn was found at that index, usually an
  in-flight turn. Unknown is not evidence.
- **Inferring prompting from the artifact.** Commit messages and comments do not record who raised
  a concern first. Either the turn-to-file join shows it or the axis is unmeasured.
- **Reciting the source.** You are asking questions, not delivering the walkthrough.

## Practice repo setup

The lightest setup that this skill can read reliably, if the candidate asks:

- **One directory per attempt**, named so the problem is identifiable — `url-shortener/attempt-1`,
  `url-shortener/attempt-2`. This single convention gives scope, attempt grouping, and transcript
  lookup at once. Keep the problem name in the path rather than only the attempt number: an
  `attempt-1` directly under the repo root cannot be told from any other problem's first attempt.
- **Shared code, if any, outside the attempt directories** — `shared/`, `lib/`, or similar. Keeping
  it separate is what lets an interview tell "wrote a cache" from "reused one", which are different
  claims about judgment.
- **Commit or don't** — either works. Committing adds a decision sequence to read; not committing
  loses nothing essential, because the transcript carries it.
- **Branches optional.** A branch per attempt gives a slightly cleaner diff and nothing else. Do
  not rename it mid-task if you use one.
- **Nothing else.** No manifest, no metadata file, no naming scheme for sessions. Anything the
  candidate has to remember to maintain will eventually be wrong, and stale metadata is worse than
  none because it is trusted.

## Related

The library is a plain reference directory, not a skill. Resolve it with
`scripts/library-path.sh read` and read these files directly — do not expect to invoke anything:

- `probes/` — seeds per source and problem class.
- `level-expectations.md` — the bars, with the prompted/unprompted axis.
- `concepts/` — what a good answer contains, cited.
- `rubric.md` — 0–5 scale, for scoring an implementation rather than an interview.
- `README.md` — the concept index, and which sources have been processed.

`extract-design-concepts`, in this same plugin, is the only thing that writes to it. If a probe
file has no bar for a concern that came up, that is a genuine gap in the library — say so rather
than grading against an invented standard, and mine a source that covers it later.
