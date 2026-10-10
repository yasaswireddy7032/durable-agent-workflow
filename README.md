# Durable Agent Workflow

A SQLite-backed workflow state machine with approval gates, an audit log, and idempotent local execution.

**Status:** runnable portfolio reference implementation. Uses synthetic or hand-authored demonstration data. No employer code, customer data, or production performance claims.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
python -m unittest -v
```

The default command prints a reproducible JSON demonstration. See `app.py` for the reusable Python API. `example-output.json` records the locally executed demo; it is not an external benchmark.

## Architecture

Request → idempotency check → pending approval → approved → local tool → completed. SQLite transactions make the state transition and local audit atomic.

## Validation

Tests exercise failure cases and behavioral invariants, in addition to the executable demo. The included `github-actions-tests.yml` defines tests and the demo on pushes and pull requests. Install it as `.github/workflows/tests.yml` to activate CI. CI has not run on GitHub until this repository is published.

## Limitations and next steps

This is an agent workflow foundation, not an autonomous LLM agent. No authentication, remote tools, retries, or distributed workers. Approval authority must be enforced by the application. Add an outbox for remote effects; never claim global exactly-once execution.

## Container

```bash
docker build -t durable-agent-workflow .
docker run --rm durable-agent-workflow
```

The Docker recipe is provided; local validation uses Python, not Docker.

## Responsible use

Review the code and understand its assumptions before deploying. Keep credentials in environment variables and exclude private data from commits. This project is an educational engineering baseline, not a production-certified service.
