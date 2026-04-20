with item_facts as (
    select
        order_purchase_timestamp::date as order_purchase_date,
        order_id,
        order_item_key,
        customer_unique_id,
        price,
        freight_value,
        gross_item_amount,
        allocated_payment_value,
        delivery_days,
        is_delivered_late
    from {{ ref('fact_order_items') }}
    where order_purchase_timestamp is not null
),

order_level as (
    select
        order_purchase_date,
        order_id,
        customer_unique_id,
        sum(gross_item_amount) as order_gross_revenue,
        sum(coalesce(allocated_payment_value, gross_item_amount)) as order_payment_revenue
    from item_facts
    group by
        order_purchase_date,
        order_id,
        customer_unique_id
),

item_daily as (
    select
        order_purchase_date,
        sum(gross_item_amount) as gross_revenue,
        sum(coalesce(allocated_payment_value, gross_item_amount)) as allocated_payment_revenue,
        sum(price) as product_revenue,
        sum(freight_value) as freight_revenue,
        count(distinct order_item_key) as items_count,
        avg(delivery_days) as average_delivery_days,
        sum(case when is_delivered_late then 1 else 0 end) as late_deliveries_count
    from item_facts
    group by order_purchase_date
),

order_daily as (
    select
        order_purchase_date,
        count(distinct order_id) as orders_count,
        count(distinct customer_unique_id) as customers_count,
        avg(order_gross_revenue) as average_order_value,
        avg(order_payment_revenue) as average_paid_order_value
    from order_level
    group by order_purchase_date
)

select
    item_daily.order_purchase_date,
    item_daily.gross_revenue,
    item_daily.allocated_payment_revenue,
    item_daily.product_revenue,
    item_daily.freight_revenue,
    order_daily.orders_count,
    order_daily.customers_count,
    item_daily.items_count,
    order_daily.average_order_value,
    order_daily.average_paid_order_value,
    item_daily.average_delivery_days,
    item_daily.late_deliveries_count
from item_daily
left join order_daily
    on item_daily.order_purchase_date = order_daily.order_purchase_date
