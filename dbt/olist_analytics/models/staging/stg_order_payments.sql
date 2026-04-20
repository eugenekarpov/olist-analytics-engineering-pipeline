select
    order_id::varchar(256) as order_id,
    payment_sequential::integer as payment_sequential,
    lower(trim(payment_type))::varchar(64) as payment_type,
    payment_installments::integer as payment_installments,
    payment_value::decimal(18, 2) as payment_value,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from {{ source('olist_raw', 'order_payments') }}
