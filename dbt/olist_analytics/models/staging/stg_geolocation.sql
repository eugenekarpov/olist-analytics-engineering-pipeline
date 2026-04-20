select
    geolocation_zip_code_prefix::varchar(16) as geolocation_zip_code_prefix,
    geolocation_lat::decimal(18, 14) as geolocation_lat,
    geolocation_lng::decimal(18, 14) as geolocation_lng,
    lower(trim(geolocation_city))::varchar(256) as geolocation_city,
    upper(trim(geolocation_state))::varchar(2) as geolocation_state,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from {{ source('olist_raw', 'geolocation') }}
