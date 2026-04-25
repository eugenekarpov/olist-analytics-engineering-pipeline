select
    batch_id,
    batch_date,
    orchestration_run_id,
    dag_id,
    status,
    started_at,
    updated_at,
    finished_at,
    raw_manifest_uri,
    correction_manifest_uri,
    error_message
from {{ source('pipeline_audit', 'batch_runs') }}
order by updated_at desc
