# Olist Modern Data Stack

Local-first data engineering project built around the Olist Brazilian
e-commerce dataset. The active stack is Python ingestion, a filesystem raw zone
with S3-style paths, PostgreSQL in Docker, Apache Airflow, and dbt.

The repository is intended to be reviewable without cloud access. Redshift SQL
artifacts are kept as reference material, but the runnable project does not
require AWS or Redshift.

## What It Demonstrates

- End-to-end batch pipeline from CSV archive to analytics marts.
- Deterministic raw-zone contract that can map to local files or object
  storage.
- Row-level validation, dead-letter files, threshold checks, and replay support.
- Warehouse audit tables for batch state, raw load attempts, reconciliation,
  dead-letter events, and replays.
- Airflow orchestration with clear task boundaries and parameterized batch
  runs.
- dbt layers for staging, intermediate logic, snapshots, core dimensions/facts,
  and business marts.
- SCD Type 2 customer and product dimensions using deterministic correction
  feeds.
- Incremental fact loading with late-arriving data handling.
- Small committed fixture dataset and CI gates that exercise the real pipeline
  path quickly.

## High-Level Flow

```text
Olist CSV archive
  -> Python ingestion and validation
  -> local S3-shaped raw zone plus dead-letter zone
  -> PostgreSQL raw and audit schemas
  -> dbt staging, intermediate, snapshots, core, and marts
  -> Airflow-controlled quality gates
```

## Repository Layout

```text
airflow/
  dags/                 Local Airflow DAG plus preserved Redshift DAG.

dbt/
  olist_analytics/      dbt project: sources, models, snapshots, tests,
                        analyses, macros, and profile example.

docker/
  airflow/              Local Airflow image and container entrypoint.

docs/
  architecture.md       System design, orchestration, audit, and reliability.
  data_model.md         Dimensional model, grains, SCD2, facts, and marts.
  ci.md                 GitHub Actions quality-gate strategy.
  diagrams.md           Mermaid architecture and data model diagrams.
  source_contract.md    Generated source-file contract from the Olist archive.
  runbook_macos.md      macOS local setup and execution commands.
  runbook_windows.md    Windows local setup and execution commands.

infra/
  postgres/             Local warehouse DDL for schemas, raw tables, audit,
                        and correction tables.
  redshift/             Reference Redshift DDL and COPY templates.

scripts/
  ingestion/            Source validation, raw file preparation, corrections.
  loading/              PostgreSQL raw load and dead-letter replay.
  orchestration/        Batch-control helpers.
  quality/              Reconciliation checks.
  testing/              Fixture generation.
  utilities/            Profiling, validation, and helper scripts.

tests/
  fixtures/olist_small/ Small synthetic fixture used by CI.
  test_*.py             Python tests for ingestion, dead-letter handling,
                        replay behavior, and CI failure modes.
```

## Main Design Choices

- The local pipeline is the default path; cloud services are not required.
- Raw files are immutable and partitioned by entity, batch date, and run id.
- Structural source-contract failures fail fast, while record-level failures
  are isolated in the dead-letter zone.
- Batch lifecycle is stored in warehouse audit tables instead of relying only
  on Airflow UI state.
- Reconciliation runs before dbt so silent data loss or duplicate raw loads stop
  the pipeline early.
- dbt owns analytical modeling and data quality checks after the raw load.
- CI uses a small deterministic fixture so pull-request checks stay fast while
  still covering the real ingestion, loading, reconciliation, and dbt path.

## Running Locally

Use the OS-specific runbook:

- [Windows runbook](docs/runbook_windows.md)
- [macOS runbook](docs/runbook_macos.md)

Both runbooks cover dependency setup, Docker Compose, manual smoke runs, the
Airflow DAG, dbt execution, CI-style fixture validation, and cleanup.

## Data License

The repository includes the Olist Brazilian E-Commerce Public Dataset archive
for reproducible local runs. See [Data license](DATA_LICENSE.md) for source
attribution and license terms.

## More Documentation

- [Architecture](docs/architecture.md)
- [Data model](docs/data_model.md)
- [CI quality gates](docs/ci.md)
- [Diagrams](docs/diagrams.md)
- [Source contract](docs/source_contract.md)
