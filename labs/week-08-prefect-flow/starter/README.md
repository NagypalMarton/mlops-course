# Week 8 Lab — Prefect Flow

Week 7 made the checks run without anyone asking. That creates a new question: **how do you know
it ran?**

A scheduled job that fails and reports nothing looks exactly like a job that works. Nobody sees
it and nobody complains. You find out on the day you need what it was supposed to produce. The
lecture's cold open is a nightly backup that had been failing for a month before anyone needed
it.

This week the training pipeline becomes a **flow**. Every run leaves a record: which steps ran,
in what order, how many attempts each took, how each one ended, and who was told.

Week 7 = *the gate runs whether or not you remember it.*
Week 8 = *you can prove it ran, see why it failed, and make it run again.*

## What you already have

Everything from Weeks 1–7, unchanged: the Compose stack, MLflow, DVC with Silo, the
`validate → prepare → train → evaluate → gate` pipeline, both contracts, the gate, `make ci` and
both GitHub Actions workflows. **Week 8 changes no model, no metric and no threshold.**

New this week:

- **Prefect**, the orchestrator: `prefect==3.8.2`, pinned together with the server image of the
  same version.
- **A fifth service** in `compose.yaml`: a Prefect server. It stores its data in a second database
  in the Postgres container you already have.
- `tasks.py` and `flows.py`. Most of the tasks are written. Your job is to put them together,
  decide where retries belong, and make the flow check its own work.

You already have a DAG runner: `dvc repro`. The first thing to understand this week is why you
need a second one. **DVC tells you what is out of date. Prefect tells you what happened.** The
flow calls `dvc repro` as one task and handles everything DVC does not: the network calls, the
retries, the runtime parameters, the schedule, and the record that any of it happened.

## Based on (official tutorials)

- **Prefect quickstart (primary template):** https://docs.prefect.io/v3/get-started/quickstart
- **Flows and tasks:** https://docs.prefect.io/v3/concepts/flows · https://docs.prefect.io/v3/concepts/tasks
- **Retries:** https://docs.prefect.io/v3/how-to-guides/workflows/retries
- **Self-hosting a server:** https://docs.prefect.io/v3/advanced/self-hosted
- **Deployments and schedules:** https://docs.prefect.io/v3/how-to-guides/deployments/create-schedules
- **Testing flows (`prefect_test_harness`):** https://docs.prefect.io/v3/how-to-guides/workflows/test-workflows

**Deviations from those sources** (five, each for a stated reason):

1. **The flow calls `dvc repro`, it does not replace it.** The quickstart builds a flow out of
   plain Python tasks. This project already has a pipeline that hashes its inputs and skips
   stages that are up to date. Rebuilding it as Prefect tasks would make the flow diagram look
   tidier and lose that.
2. **A self-hosted server on the course's existing Postgres**, not SQLite and not Prefect Cloud.
   It needs a second database, created by `init-prefect-db.sh` when the Postgres volume is
   **first** created.
3. **`.serve()`, not work pools.** `.serve()` is one process that waits for scheduled runs and
   needs no work pool, worker or infrastructure block. Work pools are how production does it, and
   the lecture covers when you would switch.
4. **Retries are taught by where they must not go.** The tutorial shows how to add them. This
   lab asks where they would do harm.
5. **`prefect_test_harness` for tests, and `task.fn(...)` wherever possible.** Calling the
   undecorated function costs nothing, while a real flow run inside the harness costs about a
   second. The lab's tests are built on that difference.

Two self-hosting traps, both already handled in `.env.example`: the client's `PREFECT_API_URL`
needs the **`/api` suffix**, and the server setting is **`PREFECT_SERVER_DATABASE_CONNECTION_URL`**.
Older blog posts use a name that no longer works.

## Prerequisites

- Weeks 1–7 working: `uv`, Docker, Git.
- If you are reusing a Postgres volume from an earlier week, it will not have the `prefectdb`
  database. See Troubleshooting.

## Setup

```bash
# 1. Stop any other lab stack — they all share the 55xx host ports
cd ../../week-07-ci-workflow/solution && make down; cd -

cp .env.example .env
make sync          # --all-groups; Prefect adds 55 packages to the lock
make up            # FIVE services now: postgres, s3, mc, mlflow, prefect
make data-v2       # rebuild the DVC-tracked dataset from the committed raw batches
make repro         # the Week 7 pipeline, unchanged: should end with a GO
make prefect-ui    # prints the UI address: http://127.0.0.1:5520
```

Open the Prefect UI now. It is empty, and that is what the week is about: until today, nothing
recorded that any of your pipeline runs happened.

`uv run pytest -q` should be green from the start. With the stack **down** (which is how the
autograder runs it):

```
178 passed, 24 skipped
```

12 of those skips are in `tests/test_flows.py`. Each has a `@pytest.mark.skip` marker naming
Exercises 1–5, and the file is grouped by exercise. Delete a marker when you implement the piece
it covers, and the test then checks your work. The other 12 are infrastructure guards. With the
stack **up**, the 8 MLflow-link tests among them run too.

`tests/test_scope.py` is new, and it is course infrastructure rather than an exercise. It fails
if the code imports a tool from a later week. Prefect installs some of those tools as its own
dependencies. Having them installed is fine. Importing them is not.

## Exercises

Six exercises, cumulative, one `make` target each. **Three are written** (2, 5 and 6). Put those
answers in a file called `answers.md` in this directory, and **commit it with your code**. It is
part of your submission, and it is read alongside your solution.

### Exercise 1 — Tasks and a flow (`make flow`)

Fill in `training_flow` in `flows.py`. The TODO lists the tasks in order. Build the `overrides`
from the flow's parameters, then call the tasks.

Two orderings matter, and both fail silently if you get them wrong:

- `write_params` must run **before** `run_pipeline`, and `verify_params_applied` **after** it.
  The question is not whether you set the parameter. It is whether the thing that decides what is
  stale saw it.
- `notify` must run on the **failure** path too. A flow that only reports its successes is the
  cold open again.

Then run `make flow` and open the run in the UI. Find the task list, each task's state and
duration, and the log lines from `dvc repro` inside `run_pipeline`.

**What proves it:** `make flow` ends with `Finished in state Completed()`, the gate verdict is
`GO`, `reports/last_run.txt` records it, and your metrics are byte-identical to Week 7. The run
shows up in the UI with every task in it.

### Exercise 2 — Who owns what (`make flow-dvc`) — **written**

`make flow-dvc` prints DVC's graph next to a pointer to Prefect's. Look at both. DVC's graph is
about **content**: which files depend on which. Prefect's is about **execution**: what ran, when,
and how it ended.

1. Name **three** things Prefect gives you that DVC cannot, and **one** thing DVC gives you that
   Prefect cannot.
2. `run_pipeline` calls `dvc repro` as a **single** task. What would break if you split it into
   one Prefect task per DVC stage? Is there a situation where splitting it would be the right
   call?

### Exercise 3 — Retries where they belong (`make flow-retry`)

Set the retry policy in `NETWORK_RETRIES` at the top of the retry section in `tasks.py`: a number
of retries, an exponential backoff, and jitter. The policy is already applied to the tasks that
talk to Silo. Leave every other task without retries.

Answer two questions in one sentence each, in the comment above `NETWORK_RETRIES`:

- (a) Why would `retries=3` on `run_pipeline` be **worse than useless**?
- (b) Retrying is safe only if running the same operation twice does no harm. Which of the
  tasks that retry is **not** safe to repeat? What would a retry do there, and how much does the
  existing check in that task protect you?

**What proves it:**

- Remove the skip markers on the three retry-policy tests and the two harness tests. Then run
  `make flow-retry`. One test fails twice and then succeeds. Another fails every time and still
  fails after its retries run out. Both check state and call counts, not log text.
- *(Optional, on the live stack.)* Run `docker compose stop s3`, then `make flow-register`,
  which pushes to Silo, and watch the delays between retries grow. Then run `docker compose start s3`. A retry
  policy you have never seen retry is just a comment.

### Exercise 4 — Parameters that reach DVC (`make flow-params`)

A flow parameter passed straight into a Python function is **invisible to `dvc repro`**. DVC
hashes `params.yaml`, sees no change, skips `train`, and the run reports success with the
*previous* model. The cache is correct and the result is wrong. That is why `write_params` puts
runtime parameters into `params.yaml` before the pipeline runs.

Relying on everyone remembering that step is not enough, so check that it worked. Implement
`verify_params_applied` in `tasks.py`. `dvc.lock` records the parameter **values** each stage
used. Compare them with the values the flow was asked to run, and fail loudly, naming both values,
when they disagree.

Then prove the check actually checks something:

1. `make flow-params` runs with `impute_strategy=mean`. `train` and `evaluate` re-run, and the
   metrics move.
2. `make flow-params C=0.01` changes the regularisation. Watch what the gate does with the result.
3. Comment out the `write_params` call in `flows.py` and run `make flow-params C=0.005`.
   `run_pipeline` should **complete**, and your check should then **fail the flow**. If the run
   ends green, your check does not work. Restore `write_params` afterwards.

**What proves it:** the four parameter tests in `tests/test_flows.py` pass, and step 3 fails at
`verify_params_applied` with both numbers in the message.

`make flow-params` restores `params.yaml` afterwards for convenience. A real scheduled run
deliberately leaves the change in place. The docstring of `write_params` explains why, and what
it costs when two runs happen at once.

### Exercise 5 — Partial failure (`make flow-fail`) — **written**

`make flow-fail` adds an impossible row to a raw batch and runs the flow. The fault is in the
**data**, so the flow fails partway through rather than before it starts. The target puts the
batch, the dataset and the DVC pointer back afterwards.

Run it, then find the run in the UI and look at `reports/last_run.txt` **before** you read the
terminal output.

1. Which tasks ran, which failed, and which never started? What state did the flow end in?
2. What is on disk now, and what is **not**? Answer for the state right after the failure,
   before the target restored anything.
3. If you had run `dvc repro` right after the failure, what would it have done, and why?
4. Did `notify` run? What would you have known about this run if it had not?

`test_a_failing_task_stops_the_tasks_after_it` shows the same behaviour on a three-task toy
flow. Remove its skip marker and compare it with what you saw.

### Exercise 6 — The unattended run (`make serve`) — **written**

Implement `scheduled_flow` in `flows.py`. It pulls the current data first, because a scheduled run
cannot assume anyone has updated the workspace, and then runs the training flow. It does **not**
register or promote.

Then run `make serve`. It serves the flow on a cron schedule (every 5 minutes by default; set
`CRON='* * * * *'` to wait less). Leave it running until at least **one scheduled run has
fired**, check it in the UI, then stop it with Ctrl-C. A deployment that never fired shows
nothing. Record the flow-run name and its final state.

1. The gate is now the only thing between a clock and a trained model. Is that enough? If not,
   what else would you require before a model trained at 03:00, seen by nobody, reaches users?
2. What should be notified, and to whom?
3. What should happen on the **second** failure in a row that should not happen on the first?
4. Which failure of a scheduled job does **none** of this catch? (Think about the cold open.)

### Finish — commit your work

```bash
git status          # answers.md must appear; .env and .venv/ must NOT
git add labs/week-08-prefect-flow/starter
git commit -m "week08: prefect flow, retries and written answers"
```

Commit your code and `answers.md`. At the top of `answers.md`, put the name and final state of
the scheduled run from Exercise 6. If `git status` shows `params.yaml` as modified, a flow run
did not restore it. Check the diff and restore it before you commit, unless you meant to change
it.

## Make targets

| Target | What it does |
| --- | --- |
| `make flow` | the training flow, recorded in the Prefect UI (Exercise 1) |
| `make flow-dvc` | the two graphs side by side (Exercise 2) |
| `make flow-retry` | runs the retry tests (Exercise 3) |
| `make flow-params` | a runtime override that reaches DVC. `C=...` or `IMPUTE=...` (Exercise 4) |
| `make flow-fail` | a partial failure, fully reversible (Exercise 5) |
| `make serve` | a scheduled deployment. `CRON=...` to override (Exercise 6) |
| `make flow-register` | the flow with `dvc push` and registration, against the live stack |
| `make prefect-ui` | print the UI address |
| `make test-flows` | just this week's tests |

Every Week 4–7 target still works, including `make ci`, `make repro`, `make gate` and both
GitHub Actions workflows.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `No Prefect server at ...` | stack down | `make up` |
| Every API call returns 404 | `PREFECT_API_URL` is missing the `/api` suffix | copy it from `.env.example` |
| Prefect container restarts in a loop | `prefectdb` is missing. The init script only runs when the Postgres volume is **first** created | `make down-v && make up` (this also wipes MLflow's data) |
| `PREFECT_API_DATABASE_CONNECTION_URL` has no effect | the setting was renamed | use `PREFECT_SERVER_DATABASE_CONNECTION_URL` |
| `Scheduled_FlowModel is not fully defined` | a flow parameter Prefect cannot serialise | keep flow signatures to strings, numbers and booleans, as the `training_flow` docstring explains |
| `dvc pull failed` with no detail | Silo credentials were not passed to the subprocess | see `_dvc_env` in `tasks.py` |
| A flow succeeds but the model did not change | `write_params` did not run before the pipeline | that is what Exercise 4's check is for |
| `data/measurements.csv is missing` | a fresh clone. The dataset is DVC-tracked, not committed | `make data-v2` |
| A flow test takes about 8 seconds instead of 1 | it runs a flow without the harness, so Prefect starts a temporary server | use the `prefect_harness` fixture, or `task.fn(...)` |
| Port already in use | another week's stack is running | `make down` in that lab first |

## Submission

Your submission is the commit from **Finish** above. It contains your code, and `answers.md` with
the scheduled run's name and state at the top. `.env` and `.venv/` must not be in it.
