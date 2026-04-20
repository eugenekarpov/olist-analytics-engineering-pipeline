select
    md5(order_status) as order_status_key,
    order_status,
    case
        when order_status = 'delivered' then true
        else false
    end as is_successful_status,
    case
        when order_status in ('canceled', 'unavailable') then true
        else false
    end as is_failed_status
from (
    select distinct order_status
    from {{ ref('stg_orders') }}
    where order_status is not null
) as statuses
