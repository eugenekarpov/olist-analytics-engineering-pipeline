select
    batch_id,
    load_run_id,
    entity_name,
    failed_rows,
    valid_rows,
    total_rows,
    threshold_max_rows,
    threshold_max_rate,
    reason_summary,
    dead_letter_uri,
    created_at
from {{ source('pipeline_audit', 'dead_letter_events') }}
order by created_at desc
