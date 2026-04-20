select
    lower(trim(product_category_name))::varchar(256) as product_category_name,
    lower(trim(product_category_name_english))::varchar(256) as product_category_name_english,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from {{ source('olist_raw', 'product_category_translation') }}
