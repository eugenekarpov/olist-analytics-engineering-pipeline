select
    customer_id::varchar(256) as customer_id,
    customer_unique_id::varchar(256) as customer_unique_id,
    customer_zip_code_prefix::varchar(16) as customer_zip_code_prefix,
    lower(trim(customer_city))::varchar(256) as customer_city,
    upper(trim(customer_state))::varchar(2) as customer_state,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from {{ source('olist_raw', 'customers') }}
