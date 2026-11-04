.PHONY: up down down-v logs ps sync data-v2 dvc-push dvc-pull dvc-status \
        validate predict repro dag metrics link gate baseline-sync register \
        promote promote-champion trace test test-fast test-unit test-data \
        test-eval lint ensure-data ensure-env ci ct-local gate-summary \
        install-ci uninstall-ci flow serve-mlflow serve-api bench image \
        run-image kind-up kind-down k8s-deploy k8s-status

# The commands of the training pipeline, the CI checks and the serving lab.
# The README's "Make targets" table lists the ones this lab uses.

# DVC reads the AWS_* names, so scripts/dvc.py maps the Silo credentials from
# .env onto them. Keeping this in Python makes the targets work on Windows too.
DVC = uv run python scripts/dvc.py

# ── The Compose stack ────────────────────────────────────────────────────────

up:
	docker compose up -d --wait

## Stop the services; the data stays in the volumes.
down:
	docker compose down

## Stop the services and delete the volumes.
down-v:
	docker compose down -v

logs:
	docker compose logs -f

ps:
	docker compose ps

sync:
	uv sync --all-groups

# ── Data and DVC ─────────────────────────────────────────────────────────────

## Build dataset version 2: both batches. The pipeline uses this one.
data-v2:
	uv run python src/main.py build-data --version 2

dvc-push:
	$(DVC) push

dvc-pull:
	$(DVC) pull

## Compare the workspace, the cache and the remote.
dvc-status:
	$(DVC) status
	$(DVC) status --cloud

# ── Data contracts ───────────────────────────────────────────────────────────

## Check the data against the ingestion contract. Exits 1 when the data fails.
validate:
	uv run python src/main.py validate

## Check one request against the contract, then score it.
predict:
	uv run python src/main.py predict --payload example

# ── Pipeline, gate and registry ──────────────────────────────────────────────

## Run the pipeline: validate, prepare, train, evaluate, gate. Only stale stages run.
repro:
	$(DVC) repro

dag:
	$(DVC) dag
	@echo "--- as mermaid ---"
	$(DVC) dag --mermaid

metrics:
	$(DVC) metrics show

## Force a new training run, so MLflow gets a new run with its metrics.
link:
	$(DVC) repro -f -s train
	$(DVC) repro -f -s evaluate
	$(DVC) repro

## The release decision. Exits 1 on a NO-GO and writes the report either way.
gate:
	uv run python src/main.py gate

## Copy the champion's metrics into the baseline, which raises the bar.
baseline-sync:
	uv run python src/main.py baseline-sync

## Register the model. Refuses unless reports/gate.json records a GO.
register:
	uv run python src/main.py register

## Move the staging alias. Refuses without a GO.
promote:
	uv run python src/main.py promote

## Move the staging and champion aliases.
promote-champion:
	uv run python src/main.py promote --champion

## Follow the chain from the champion alias to the run, the data and the gate verdict.
trace:
	uv run python src/main.py trace

# ── Tests and CI ─────────────────────────────────────────────────────────────

## Every test. Tests that need the stack or a DVC repo skip themselves without it.
test:
	uv run pytest tests/ -v

## The tests that need neither the stack nor a DVC repo.
test-fast:
	uv run pytest tests/ -v -m "not live and not dvc"

test-unit:
	uv run pytest tests/ -q -m "unit"

test-data:
	uv run pytest tests/ -q -m "data and not live and not dvc"

test-eval:
	uv run pytest tests/ -q -m "eval and not live and not dvc"

lint:
	uv run ruff check src tests

## Stop with a hint when the DVC-tracked dataset is missing, as on a fresh clone.
ensure-data:
	uv run python scripts/ensure.py data

## Copy .env.example to .env when there is no .env, as on a CI runner.
ensure-env:
	uv run python scripts/ensure.py env

## What ci.yml runs: lint, the tests, the pipeline and the gate.
ci: ensure-env ensure-data lint test-fast repro gate
	@echo
	@echo "CI passed: lint, tests, pipeline, gate."

## What ct.yml runs: retrain and gate, without a code change.
ct-local: ensure-env ensure-data
	$(MAKE) --no-print-directory repro
	$(MAKE) --no-print-directory gate

## The gate verdict as markdown, for $GITHUB_STEP_SUMMARY.
gate-summary:
	@uv run python src/main.py gate-summary

## Copy the workflows to .github/workflows at the repository root, where GitHub runs them.
install-ci:
	@root=$$(git rev-parse --show-toplevel) && mkdir -p "$$root/.github/workflows" && \
	  for f in .github/workflows/*.yml; do \
	    cp "$$f" "$$root/.github/workflows/week09-$$(basename $$f)"; \
	    echo "installed -> .github/workflows/week09-$$(basename $$f)"; \
	  done
	@echo "Commit and push to run them. \`make uninstall-ci\` removes them again."

uninstall-ci:
	@root=$$(git rev-parse --show-toplevel) && \
	  rm -f "$$root"/.github/workflows/week09-*.yml && echo "removed week09-*.yml"

# ── Prefect flow ─────────────────────────────────────────────────────────────

## Run the training flow. Needs the stack: the CLI refuses without a Prefect server.
flow: ensure-env ensure-data
	uv run python src/main.py flow

# ── Serving (this lab) ───────────────────────────────────────────────────────

## Exercise 1: MLflow's server for the champion, on port 5540.
## `--env-manager local` uses this Python instead of rebuilding the model's environment.
serve-mlflow: ensure-env
	uv run python scripts/mlflow_serve.py \
	  --env-manager local -p 5540 --host 127.0.0.1

## Exercise 2: your service, on port 5541. It reads models/model.pkl, so it needs no stack.
serve-api: ensure-data
	uv run python src/main.py serve-api --port $(or $(PORT),5541)

## Exercise 3: batch and online scoring of the 192 test rows.
bench: ensure-data
	uv run python src/main.py bench

## Exercise 4: build the image with the model in it. Refuses unless the gate verdict is GO.
## With the stack up, the image records the champion's version; without it, "unknown".
image: ensure-env
	uv run python scripts/build_image.py

## Exercise 4: run the image on its own, on port 5542.
run-image:
	docker run --rm -p $(or $(PORT),5542):8000 --name diabetes-api diabetes-api:local

## Exercise 5: create or delete the local cluster.
kind-up:
	kind create cluster --name mlops
	kubectl cluster-info --context kind-mlops

kind-down:
	kind delete cluster --name mlops

## Exercise 5: copy the image onto the kind node, then apply the manifests.
k8s-deploy:
	kind load docker-image diabetes-api:local --name mlops
	kubectl apply -f k8s/
	kubectl rollout status deployment/diabetes-api --timeout=120s
	@echo
	@echo "  kubectl port-forward svc/diabetes-api 5543:80"
	@echo "  curl localhost:5543/health"

## Exercise 5: the pods, and the pods behind the Service.
k8s-status:
	@kubectl get pods -l app=diabetes-api -o wide
	@echo
	@kubectl describe service diabetes-api | grep -E "^(Name|Selector|Endpoints):"
