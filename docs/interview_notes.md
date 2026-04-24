# Interview Notes

## Elevator Pitch

This project implements a production-like batch analytics platform for an
e-commerce dataset using Python, a local S3-shaped raw zone, PostgreSQL 18,
Apache Airflow, and dbt.

The first design targeted AWS S3 and Amazon Redshift. Because Redshift access
was not available, the project was adapted into a fully reproducible local
version while preserving the same architectural contracts: immutable raw files,
warehouse raw tables, dbt transformations, SCD2 dimensions, incremental facts,
and quality gates.

## What This Project Demonstrates

- Local-first data warehouse development with Docker.
- Storage contract abstraction: filesystem locally, S3 later.
- Warehouse load pattern with idempotent raw loads and audit rows.
- Batch control state machine independent of Airflow UI state.
- Reconciliation control totals before publishing transformed models.
- Orchestration with Airflow.
- dbt project structure and layered modeling.
- Source contracts and schema validation.
- Dead Letter Pattern with threshold-based record rejection.
- Dimensional modeling and star schema design.
- SCD Type 2 dimensions with dbt snapshots.
- Business-effective SCD2 joins from fact tables.
- Incremental fact loading with a late-arriving data lookback.
- Multi-grain modeling through order-level payment allocation to item-grain
  facts.
- Data quality gates across sources, staging, core, and marts.
- Small fixture CI with both happy-path and targeted failure-mode checks.
- Trade-off discussion between local reproducibility and cloud-native services.

## Architecture Talking Points

The raw landing zone keeps deterministic paths:

```text
data/raw/olist/raw/<entity>/batch_date=<date>/run_id=<run_id>/<entity>.csv.gz
```

That shape intentionally mirrors S3 keys. In a cloud deployment the same logical
contract can be backed by `s3://<bucket>/olist/raw/...`; locally it is backed by
the filesystem.

PostgreSQL raw tables are append-only and include metadata columns:

```text
_batch_id
_loaded_at
_source_file
_source_system
```

In the local pipeline, `_batch_id` is the stable logical batch identifier
derived from `batch_date`. The Airflow `run_id` identifies a concrete load
attempt and stays in the raw path/audit metadata.

dbt owns the transformation logic. Staging models are views, dimensions and
marts are tables, and the main fact table is incremental.

Airflow provides the operational wrapper:

- task-level retries;
- explicit task boundaries;
- backfill parameters;
- failure visibility;
- separation between ingestion, load, snapshots, build, and test.

The warehouse also stores `audit.batch_runs`, so batch state is queryable even
outside Airflow:

```text
STARTED -> SOURCE_VALIDATED -> RAW_PREPARED -> RAW_LOADED
  -> RAW_RECONCILED -> DBT_SNAPSHOT_INPUTS_BUILT
  -> DBT_SNAPSHOTTED -> DBT_BUILT -> TESTED
```

`FAILED` can be recorded from any state. The helper refuses accidental backward
transitions, which protects reruns and manual recovery work from overwriting the
true latest batch state.

Reconciliation is the guard between raw loading and dbt. For each entity, the
pipeline checks:

```text
source rows = prepared valid rows + dead-letter rows
raw loaded rows = prepared valid rows + successful replay rows
```

The point is to catch silent data loss or accidental duplicates, not just hard
SQL failures.

CI uses a committed small fixture instead of the full Kaggle archive. The PR
workflow runs fast Python checks, dbt parsing, Airflow DAG imports, and a
PostgreSQL-backed fixture integration path. It also includes targeted negative
tests for schema drift, dead-letter threshold breaches, and reconciliation
failures. The interview story is: "I keep the CI dataset small, but I still
exercise the same contracts and quality gates that the full pipeline uses."

## Dead Letter Pattern Talking Points

The project keeps two failure classes separate:

- Source-contract failures are batch-level problems. Missing files, changed
  headers, or unexpected source row counts fail fast before ingestion.
- Record-level failures are data-quality problems. Invalid integer, decimal,
  timestamp, or varchar values are written to a dead-letter file instead of
  being sent to PostgreSQL `COPY`.

Dead-letter paths mirror the raw path contract:

```text
data/raw/olist/dead_letter/<entity>/batch_date=<date>/run_id=<run_id>/<entity>.csv.gz
```

Each dead-letter row keeps the original fields plus operational metadata:

```text
_batch_id
_loaded_at
_source_file
_source_system
_source_row_number
_dead_letter_stage
_dead_letter_reason
_dead_lettered_at
```

The pipeline uses threshold mode. A run continues only when both rejected row
count and rejected row rate stay within the configured limits. Accepted
rejections are recorded in `audit.dead_letter_events`; threshold breaches stop
the DAG before warehouse load while leaving the dead-letter files available for
inspection.

Replay is intentionally separate from the main batch load. After a dead-letter
file is corrected, `scripts/loading/replay_dead_letters.py` validates the fixed
rows, deletes any prior replay rows for the same `replay_id`, inserts the fixed
rows into the raw table, and records `audit.dead_letter_replays`.

The interview story is: "I do not let one bad row poison the whole raw load when
the business has agreed on a threshold, but I also do not hide the bad data. It
is isolated, counted, audited, and replayable after correction."

## Dimensional Modeling Talking Points

The central fact is `fact_order_items`.

Grain:

```text
one row per order_id + order_item_id
```

This grain was chosen because Olist order items naturally contain product,
seller, price, and freight. Payments are at order grain, so the project
allocates payment value to item grain proportionally by `price + freight_value`.

Dimensions:

- `dim_customer_scd2`
- `dim_product_scd2`
- `dim_seller`
- `dim_order_status`
- `dim_date`

Marts:

- `mart_daily_revenue`
- `mart_monthly_arpu`

## SCD2 Talking Points

Olist is a static Kaggle dataset, so the project generates deterministic
correction feeds to simulate production master-data changes.

Examples:

- customer address/profile changes;
- product category reclassification;
- product weight and size corrections.

The correction generator only publishes changes visible as of the current
`batch_date`. This makes historical backfills meaningful.

dbt snapshots use the `check` strategy. The core SCD2 dimensions expose
business-effective windows:

```text
valid_from
valid_to
is_current
snapshot_valid_from
snapshot_valid_to
```

The fact table joins to SCD2 dimensions using `order_purchase_timestamp` and the
business-effective `valid_from` / `valid_to` window.

## Incremental Loading Talking Points

`fact_order_items` is incremental and uses a late-arriving data lookback:

```text
lookback_days = 3
```

The incremental model also widens its reprocessing boundary when generated
correction feeds contain business-effective changes in the past.

## Trade-Offs

PostgreSQL is not a Redshift replacement for distributed columnar performance,
but it is a strong local warehouse stand-in for this project because it supports
schemas, transactions, `COPY`, dbt, and a familiar SQL dialect.

S3 is not required locally, but the project preserves the S3 path contract. That
keeps the codebase easy to explain and leaves a clean route back to AWS.

The AWS design is intentionally retained in `infra/redshift`, `infra/aws`, and
the preserved AWS DAG. The main branch prioritizes reproducibility.

## Future Enhancements

- Add MinIO if a local S3-compatible object store becomes useful.
- Add Metabase dashboards.
- Add nightly/manual full-dataset CI if a hosted dataset location is added.
- Store prepared raw files as Parquet.
- Add Terraform for the AWS path.
- Re-enable Redshift as an alternate deployment target when access is available.
