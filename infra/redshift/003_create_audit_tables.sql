-- Audit tables for pipeline and Redshift COPY observability.

create table if not exists audit.load_runs (
    load_run_id varchar(128) not null encode zstd,
    batch_id varchar(128) not null encode zstd,
    entity_name varchar(128) not null encode zstd,
    source_uri varchar(1024) encode zstd,
    target_table varchar(256) not null encode zstd,
    status varchar(32) not null encode zstd,
    rows_loaded bigint encode az64,
    started_at timestamp not null encode az64,
    finished_at timestamp encode az64,
    error_message varchar(65535) encode zstd
)
diststyle auto
sortkey(started_at);

create table if not exists audit.dbt_runs (
    dbt_run_id varchar(128) not null encode zstd,
    batch_id varchar(128) not null encode zstd,
    command varchar(1024) not null encode zstd,
    status varchar(32) not null encode zstd,
    started_at timestamp not null encode az64,
    finished_at timestamp encode az64,
    error_message varchar(65535) encode zstd
)
diststyle auto
sortkey(started_at);
