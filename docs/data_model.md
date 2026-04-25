# Data Model

## Modeling Goals

The dbt project demonstrates dimensional modeling, grain discipline, SCD Type 2
history, incremental fact loading, and business-facing marts.

## Source Entities

The Olist source contract covers customers, geolocation, order items, payments,
reviews, orders, products, sellers, and product category translation.

Detailed file names, row counts, columns, and raw warehouse types live in
[source_contract.md](source_contract.md).

## Core Model

### `fact_order_items`

Grain:

```text
one row per order_id + order_item_id
```

This grain keeps product, seller, price, freight, and delivery metrics at the
natural order-item level. Order-level payment values are allocated to items in
proportion to item gross amount.

Key measures include price, freight, gross item amount, allocated payment value,
delivery days, delivery delay days, and late-delivery flags.

### `dim_customer_scd2`

Business key: `customer_unique_id`.

Tracked attributes: zip prefix, city, and state. The dimension demonstrates how
customer profile or address changes affect historical facts.

### `dim_product_scd2`

Business key: `product_id`.

Tracked attributes include category, English category name, weight, and physical
dimensions. The dimension demonstrates category and product-attribute
corrections over time.

### `dim_seller`

Business key: `seller_id`.

This is a Type 1 dimension, which keeps the project focused while still giving a
contrast with the SCD2 customer and product dimensions.

### `dim_date`

Business key: `date_day`.

Used for purchase, approval, delivery, and estimated delivery dates.

### `dim_order_status`

Small reference dimension for Olist order status values such as `created`,
`approved`, `shipped`, `delivered`, `unavailable`, and `canceled`.

## SCD2 Strategy

Olist is a static dataset, so the project generates deterministic correction
feeds to make Type 2 behavior visible across batch dates:

```text
customer_profile_changes
product_attribute_changes
```

dbt snapshots use the `check` strategy. Core SCD2 dimensions expose business
effective windows as `valid_from`, `valid_to`, and `is_current`, while retaining
dbt snapshot timestamps separately for processing-time lineage.

Facts join to SCD2 dimensions by the business event timestamp, so historical
orders resolve to the customer and product attributes that were valid at the
time of purchase.

## Incremental Fact Loading

`fact_order_items` is incremental. Each run reprocesses the widest needed
window across:

- the configured late-arriving lookback;
- the earliest visible customer correction;
- the earliest visible product correction.

This keeps fact-to-dimension surrogate keys correct when a correction is
business-effective in the past.

## Marts

### `mart_daily_revenue`

Grain: one row per purchase date.

Metrics include gross revenue, product revenue, freight revenue, order count,
customer count, item count, average order value, delivery days, and late
deliveries.

### `mart_monthly_arpu`

Grain: one row per month.

Metrics include active customers, total revenue, ARPU, orders per customer,
average order value, and repeat-customer rate.

## Data Quality

dbt tests cover source and staging keys, accepted values, non-negative monetary
fields, fact grain, dimension relationships, SCD2 window validity, current-row
uniqueness, payment allocation balance, and mart metric formulas.
