# CI Quality Gates

The GitHub Actions workflow is split into focused jobs so a failing check points
to a useful layer instead of one opaque pipeline failure.

## Workflow

```text
lint
  -> Ruff, SQLFluff, and pre-commit checks.

python-unit
  -> Python syntax, source-contract fixture validation, unit tests,
     and targeted negative data-quality tests.

dbt-static
  -> dbt parse without a warehouse connection.

airflow-imports
  -> Docker Compose validation, Airflow image build, metadata database startup,
     and isolated DAG imports.

fixture-integration
  -> Small fixture end-to-end path through PostgreSQL, reconciliation, dbt
     snapshots/build/tests, and batch-control checks.
```

## Small Fixture Dataset

The committed fixture lives in `tests/fixtures/olist_small`.

It contains:

- `olist_small.zip`, with the original Olist file names and headers.
- `source_profile_small.json`, the matching source contract.
- `source/`, reviewable uncompressed CSVs.

The fixture is synthetic, small, and referentially consistent. It exercises real
joins, correction feed generation, reconciliation, dbt snapshots, core models,
marts, and tests without requiring the full Kaggle archive in CI.

## What CI Tests

Happy path:

- source contract validation against the small fixture archive;
- raw file preparation with row-level validation;
- generated correction feeds;
- PostgreSQL raw load;
- batch control state transitions;
- source-to-raw reconciliation;
- dbt staging and intermediate build;
- dbt snapshots;
- dbt core and mart build;
- dbt tests.

Failure modes:

- source contract failure when a required column is missing;
- corrupt source row being routed to the dead-letter path;
- dead-letter threshold failure;
- reconciliation gate failure.

The full `olist.zip` run remains a local/manual validation path. Use the
[Windows runbook](runbook_windows.md) or [macOS runbook](runbook_macos.md) for
the concrete local commands.
