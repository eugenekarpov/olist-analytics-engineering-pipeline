select
    dead_letter_replay_id,
    batch_id,
    entity_name,
    status,
    rows_replayed,
    replay_source_file,
    dead_letter_uri,
    started_at,
    finished_at,
    error_message
from {{ source('pipeline_audit', 'dead_letter_replays') }}
order by started_at desc
