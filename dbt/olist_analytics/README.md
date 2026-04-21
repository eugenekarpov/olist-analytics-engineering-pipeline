# olist_analytics dbt Project

This dbt project transforms Olist raw tables in Redshift into staging models,
SCD2 dimensions, a core star schema, and business marts.

## Setup

Copy the profile example to your dbt profiles directory or point dbt to this
project directory with `DBT_PROFILES_DIR`.

```powershell
copy dbt\olist_analytics\profiles.yml.example dbt\olist_analytics\profiles.yml
```

Then set Redshift environment variables from the root `.env.example`.

## Useful Commands

```powershell
dbt debug
dbt parse
dbt source freshness
dbt snapshot --vars '{batch_date: "2018-09-01"}'
dbt build --select staging
dbt test
```

The project includes a schema naming macro that maps dbt custom schemas directly
to Redshift schemas such as `staging`, `intermediate`, `core`, and `marts`.

## Data Quality Tests

Besides schema tests, the project includes singular tests for the most important
pipeline invariants:

- `fact_order_items` must match the cleaned staging order-item grain exactly.
- Order-level payments must balance with item-level allocated payment values.
- Customer and product SCD2 windows must be positive and non-overlapping.
- Daily revenue and monthly ARPU marts must match their component formulas.
