-- Audit tables for local PostgreSQL load and dbt observability.

create table if not exists audit.load_runs (
    load_run_id varchar(128) not null,
    batch_id varchar(128) not null,
    entity_name varchar(128) not null,
    source_uri varchar(1024),
    target_table varchar(256) not null,
    status varchar(32) not null,
    rows_loaded bigint,
    started_at timestamp not null,
    finished_at timestamp,
    error_message varchar(65535)
);

create table if not exists audit.dbt_runs (
    dbt_run_id varchar(128) not null,
    batch_id varchar(128) not null,
    command varchar(1024) not null,
    status varchar(32) not null,
    started_at timestamp not null,
    finished_at timestamp,
    error_message varchar(65535)
);

create table if not exists audit.dead_letter_events (
    dead_letter_event_id varchar(256) not null,
    batch_id varchar(128) not null,
    load_run_id varchar(128) not null,
    entity_name varchar(128) not null,
    source_uri varchar(1024),
    dead_letter_uri varchar(1024),
    total_rows bigint not null,
    valid_rows bigint not null,
    failed_rows bigint not null,
    threshold_max_rows bigint not null,
    threshold_max_rate decimal(18, 8) not null,
    reason_summary varchar(65535),
    created_at timestamp not null
);

create table if not exists audit.dead_letter_replays (
    dead_letter_replay_id varchar(256) not null,
    batch_id varchar(128) not null,
    entity_name varchar(128) not null,
    dead_letter_uri varchar(1024) not null,
    target_table varchar(256) not null,
    replay_source_file varchar(512) not null,
    status varchar(32) not null,
    rows_replayed bigint,
    started_at timestamp not null,
    finished_at timestamp,
    error_message varchar(65535)
);
