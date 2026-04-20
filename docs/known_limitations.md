# Known Limitations

## Static Source Dataset

Olist is a static Kaggle dataset. The project simulates change data through
deterministic correction feeds so SCD2 behavior can be demonstrated.

This is acceptable for the first version, but a real production system would
receive changes from operational systems, CDC, or master-data feeds.

## No Terraform Yet

AWS infrastructure is documented but not yet provisioned as code. Terraform is a
good future enhancement after the first manual end-to-end run is working.

## Airflow Runtime Not Containerized Yet

The DAG exists, but the project does not yet include a Docker Compose setup for
local Airflow. For the first AWS run, the DAG can be validated conceptually and
then wired into a local or managed Airflow environment.

## dbt Build Requires Real Redshift

`dbt parse` works locally with dummy profile values, but `dbt compile`, `dbt
build`, and `dbt test` require a real Redshift connection with the expected raw
tables.

## SCD2 Correction Feed Size

The first correction feed generates a small deterministic set of customer and
product changes. This is enough to demonstrate the pattern. A future version
could generate larger and more varied correction streams.

## CSV Raw Format

The first version uses CSV.GZ to keep Redshift COPY easy to inspect and debug.
Parquet could be added later for stronger typing and better compression.

## No Dashboard Yet

Metabase is intentionally deferred. The first version focuses on ingestion,
warehouse loading, dbt modeling, and quality checks.
