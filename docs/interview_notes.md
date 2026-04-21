# Interview Notes

## Elevator Pitch

This project implements a production-like batch analytics platform for an
e-commerce dataset using AWS S3, Amazon Redshift, Apache Airflow, and dbt.

The pipeline lands raw source data in S3, loads it to Redshift with COPY,
transforms it with dbt into staging, SCD2 dimensions, a core star schema, and
business marts. Airflow orchestrates ingestion, warehouse loading, snapshots,
dbt builds, tests, retries, and backfills.

## What This Project Demonstrates

- Cloud data lake landing pattern with S3.
- Warehouse loading with Redshift COPY.
- Orchestration with Airflow.
- dbt project structure and layered modeling.
- Source contracts and schema validation.
- Dimensional modeling and star schema design.
- SCD Type 2 dimensions with dbt snapshots.
- Business-effective SCD2 joins from fact tables.
- Incremental fact loading with a 3-day late-arriving data lookback.
- Multi-grain modeling through order-level payment allocation to item-grain facts.
- Data quality gates across sources, staging, core, and marts.
- Interview-ready trade-off discussions.

## Architecture Talking Points

S3 is used as an immutable raw landing zone. Files are written with deterministic
keys that include entity, `batch_date`, and `run_id`.

Redshift raw tables are append-only and include metadata columns:

```text
_batch_id
_loaded_at
_source_file
_source_system
```

dbt owns the transformation logic. Staging models are views, dimensions and
marts are tables, and the main fact table is incremental.

Airflow provides the operational wrapper:

- task-level retries;
- explicit task boundaries;
- backfill parameters;
- failure visibility;
- separation between ingestion, load, snapshots, build, and test.

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

dbt snapshots use the `check` strategy. The snapshot metadata is preserved, but
the core SCD2 dimensions expose business-effective windows:

```text
valid_from
valid_to
is_current
snapshot_valid_from
snapshot_valid_to
```

The dimensions include an initial baseline row from the source attributes, then
use snapshot rows for changed states. This makes the demo robust even if the
first warehouse run is executed at the final Olist batch date.

The fact table joins to SCD2 dimensions using `order_purchase_timestamp` and the
business-effective `valid_from` / `valid_to` window.

## Incremental Loading Talking Points

`fact_order_items` is incremental and uses a late-arriving data lookback:

```text
lookback_days = 3
```

Each incremental run reprocesses recent business dates so delayed records or
corrections can be incorporated without rebuilding the full fact table.

## Data Quality Talking Points

Data quality is enforced in layers:

- Source tests check required keys.
- Staging tests check uniqueness, relationships, accepted values, and
  non-negative measures.
- Core tests check surrogate keys and fact-to-dimension relationships.
- SCD2 tests check current-row uniqueness and non-overlapping windows.
- Mart tests validate revenue and ARPU calculations.

## Trade-Offs

CSV.GZ is used for the first version because it keeps Redshift COPY simple and
easy to debug. Parquet could be added later for better compression and typed
storage.

Raw tables are append-only. Deduplication and latest-record selection happen in
dbt staging/intermediate models. This preserves load history and supports audit
debugging.

Seller is modeled as Type 1 in the first version to contrast with customer and
product Type 2 dimensions.

Marts are tables instead of incremental models because they are small aggregates
in this dataset. This keeps the first version easier to validate.

## Future Enhancements

- Add PostgreSQL as an OLTP source.
- Load Olist into PostgreSQL.
- Add Apache NiFi with CDC from PostgreSQL to S3.
- Add Metabase dashboards.
- Add Terraform for AWS infrastructure.
- Add CI for dbt parse/build checks.
- Store raw prepared files as Parquet.
- Add data observability tooling.
