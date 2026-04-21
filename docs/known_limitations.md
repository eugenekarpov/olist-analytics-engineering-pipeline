# Known Limitations

## Static Source Dataset

Olist is a static Kaggle dataset. The project simulates change data through
deterministic correction feeds so SCD2 behavior can be demonstrated.

This is acceptable for the first version, but a real production system would
receive changes from operational systems, CDC, or master-data feeds.

## No Terraform Yet

AWS infrastructure is documented but not yet provisioned as code. Terraform is a
good future enhancement after the first manual end-to-end run is working.

## Local Airflow Uses SQLite

The project includes a Docker Compose Airflow runtime, but it intentionally uses
SQLite and `SequentialExecutor` for local testing. This is fine for a pet
project, but a production Airflow deployment should use a metadata database such
as Postgres and a production executor.

## dbt Build Requires Real Redshift

`dbt parse` works locally with dummy profile values, but `dbt compile`, `dbt
build`, and `dbt test` require a real Redshift connection with the expected raw
tables.

## SCD2 Correction Feed Size

The first correction feed generates a small deterministic set of customer and
product changes. This is enough to demonstrate the pattern. A future version
could generate larger and more varied correction streams.

dbt snapshots capture changes across runs. The core SCD2 dimensions also add a
baseline business-effective row so a single final-date demo run still has valid
pre-correction dimension keys.

## CSV Raw Format

The first version uses CSV.GZ to keep Redshift COPY easy to inspect and debug.
Parquet could be added later for stronger typing and better compression.

## No Dashboard Yet

Metabase is intentionally deferred. The first version focuses on ingestion,
warehouse loading, dbt modeling, and quality checks.
