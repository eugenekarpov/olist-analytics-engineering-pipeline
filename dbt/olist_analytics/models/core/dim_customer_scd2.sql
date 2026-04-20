with snapshot_rows as (
    select
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        latest_correction_effective_at,
        latest_change_reason,
        coalesce(
            latest_correction_effective_at,
            '1900-01-01'::timestamp
        ) as valid_from,
        dbt_valid_from,
        dbt_valid_to
    from {{ ref('snap_customers') }}
),

scd2_windows as (
    select
        *,
        lead(valid_from) over (
            partition by customer_unique_id
            order by valid_from, dbt_valid_from
        ) as next_valid_from
    from snapshot_rows
)

select
    md5(customer_unique_id || '|' || valid_from::varchar) as customer_key,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    latest_correction_effective_at,
    latest_change_reason,
    valid_from,
    next_valid_from as valid_to,
    case when next_valid_from is null then true else false end as is_current,
    dbt_valid_from as snapshot_valid_from,
    dbt_valid_to as snapshot_valid_to
from scd2_windows
