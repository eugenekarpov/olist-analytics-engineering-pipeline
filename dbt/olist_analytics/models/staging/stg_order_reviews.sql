select
    review_id::varchar(256) as review_id,
    order_id::varchar(256) as order_id,
    review_score::integer as review_score,
    nullif(trim(review_comment_title), '')::varchar(1024) as review_comment_title,
    nullif(trim(review_comment_message), '')::varchar(65535) as review_comment_message,
    review_creation_date::timestamp as review_creation_date,
    review_answer_timestamp::timestamp as review_answer_timestamp,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from {{ source('olist_raw', 'order_reviews') }}
