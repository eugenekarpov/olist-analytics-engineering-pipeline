select
    order_id::varchar(256) as order_id,
    order_item_id::integer as order_item_id,
    product_id::varchar(256) as product_id,
    seller_id::varchar(256) as seller_id,
    shipping_limit_date::timestamp as shipping_limit_date,
    price::decimal(18, 2) as price,
    freight_value::decimal(18, 2) as freight_value,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from {{ source('olist_raw', 'order_items') }}
