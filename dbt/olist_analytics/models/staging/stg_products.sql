select
    product_id::varchar(256) as product_id,
    lower(trim(product_category_name))::varchar(256) as product_category_name,
    product_name_lenght::integer as product_name_length,
    product_description_lenght::integer as product_description_length,
    product_photos_qty::integer as product_photos_qty,
    product_weight_g::integer as product_weight_g,
    product_length_cm::integer as product_length_cm,
    product_height_cm::integer as product_height_cm,
    product_width_cm::integer as product_width_cm,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from {{ source('olist_raw', 'products') }}
