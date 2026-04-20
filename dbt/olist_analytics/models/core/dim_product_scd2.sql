with snapshot_rows as (
    select
        product_id,
        product_category_name,
        product_category_name_english,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm,
        latest_correction_effective_at,
        latest_change_reason,
        coalesce(
            latest_correction_effective_at,
            '1900-01-01'::timestamp
        ) as valid_from,
        dbt_valid_from,
        dbt_valid_to
    from {{ ref('snap_products') }}
),

scd2_windows as (
    select
        *,
        lead(valid_from) over (
            partition by product_id
            order by valid_from, dbt_valid_from
        ) as next_valid_from
    from snapshot_rows
)

select
    md5(product_id || '|' || valid_from::varchar) as product_key,
    product_id,
    product_category_name,
    product_category_name_english,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    latest_correction_effective_at,
    latest_change_reason,
    valid_from,
    next_valid_from as valid_to,
    case when next_valid_from is null then true else false end as is_current,
    dbt_valid_from as snapshot_valid_from,
    dbt_valid_to as snapshot_valid_to
from scd2_windows
