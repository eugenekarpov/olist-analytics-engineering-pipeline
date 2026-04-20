"""Prepare Olist raw files and optionally upload them to S3.

The script reads the Kaggle `olist.zip` archive, validates source headers
against `docs/source_profile.json`, writes gzip-compressed CSV files with
ingestion metadata columns, and can upload those files to an S3 raw zone.

S3 upload requires boto3, but local file preparation uses only the standard
library. This keeps the first development loop simple while preserving the
production path.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile


SOURCE_SYSTEM = "olist_kaggle"
METADATA_COLUMNS = ["_batch_id", "_loaded_at", "_source_file", "_source_system"]


@dataclass(frozen=True)
class SourceEntity:
    file_name: str
    entity_name: str
    columns: list[str]


@dataclass(frozen=True)
class PreparedFile:
    entity_name: str
    local_path: Path
    s3_key: str
    row_count: int


def utc_now_string() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_source_entities(profile_path: Path) -> list[SourceEntity]:
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    return [
        SourceEntity(
            file_name=entity["file_name"],
            entity_name=entity["entity_name"],
            columns=[column["name"] for column in entity["columns"]],
        )
        for entity in profile
    ]


def clean_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def validate_archive(zip_file: ZipFile, entities: Iterable[SourceEntity]) -> None:
    archive_names = set(zip_file.namelist())
    missing_files = [
        entity.file_name
        for entity in entities
        if entity.file_name not in archive_names
    ]
    if missing_files:
        raise ValueError(f"Missing expected files: {', '.join(missing_files)}")


def validate_header(actual_header: list[str], entity: SourceEntity) -> None:
    if actual_header != entity.columns:
        raise ValueError(
            f"Unexpected header for {entity.file_name}. "
            f"Expected {entity.columns}, got {actual_header}"
        )


def s3_key_for(prefix: str, entity_name: str, batch_date: str, run_id: str) -> str:
    normalized_prefix = prefix.strip("/")
    return (
        f"{normalized_prefix}/raw/{entity_name}/"
        f"batch_date={batch_date}/run_id={run_id}/{entity_name}.csv.gz"
    )


def prepare_entity(
    zip_file: ZipFile,
    entity: SourceEntity,
    output_dir: Path,
    s3_prefix: str,
    batch_date: str,
    run_id: str,
    loaded_at: str,
) -> PreparedFile:
    output_path = output_dir / "raw" / entity.entity_name / f"{entity.entity_name}.csv.gz"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    row_count = 0

    with zip_file.open(entity.file_name) as raw_file:
        text_reader = (line.decode("utf-8-sig") for line in raw_file)
        reader = csv.DictReader(text_reader)

        if reader.fieldnames is None:
            raise ValueError(f"{entity.file_name} has no header row")

        validate_header(reader.fieldnames, entity)

        with gzip.open(output_path, mode="wt", encoding="utf-8", newline="") as output_file:
            fieldnames = [*entity.columns, *METADATA_COLUMNS]
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                row["_batch_id"] = run_id
                row["_loaded_at"] = loaded_at
                row["_source_file"] = entity.file_name
                row["_source_system"] = SOURCE_SYSTEM
                writer.writerow(row)
                row_count += 1

    return PreparedFile(
        entity_name=entity.entity_name,
        local_path=output_path,
        s3_key=s3_key_for(s3_prefix, entity.entity_name, batch_date, run_id),
        row_count=row_count,
    )


def upload_to_s3(bucket: str, prepared_files: Iterable[PreparedFile]) -> None:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("boto3 is required for S3 upload. Install project dependencies first.") from exc

    s3_client = boto3.client("s3")
    for prepared_file in prepared_files:
        s3_client.upload_file(
            str(prepared_file.local_path),
            bucket,
            prepared_file.s3_key,
        )
        print(f"Uploaded s3://{bucket}/{prepared_file.s3_key}")


def render_manifest(prepared_files: list[PreparedFile], output_dir: Path, bucket: str | None) -> None:
    manifest = {
        "generated_at": utc_now_string(),
        "bucket": bucket,
        "files": [
            {
                "entity_name": prepared_file.entity_name,
                "local_path": str(prepared_file.local_path),
                "s3_uri": (
                    f"s3://{bucket}/{prepared_file.s3_key}"
                    if bucket
                    else None
                ),
                "s3_key": prepared_file.s3_key,
                "row_count": prepared_file.row_count,
            }
            for prepared_file in prepared_files
        ],
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", default="olist.zip")
    parser.add_argument("--profile", default="docs/source_profile.json")
    parser.add_argument("--output-dir", default="data/prepared")
    parser.add_argument("--s3-prefix", default="olist")
    parser.add_argument("--s3-bucket")
    parser.add_argument("--batch-date", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--no-clean", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    archive_path = Path(args.archive)
    profile_path = Path(args.profile)
    output_dir = Path(args.output_dir)

    if args.upload and not args.s3_bucket:
        raise ValueError("--s3-bucket is required when --upload is set")

    if not args.no_clean:
        clean_output_dir(output_dir)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    entities = load_source_entities(profile_path)
    loaded_at = utc_now_string()

    with ZipFile(archive_path) as zip_file:
        validate_archive(zip_file, entities)
        prepared_files = [
            prepare_entity(
                zip_file=zip_file,
                entity=entity,
                output_dir=output_dir,
                s3_prefix=args.s3_prefix,
                batch_date=args.batch_date,
                run_id=args.run_id,
                loaded_at=loaded_at,
            )
            for entity in entities
        ]

    render_manifest(prepared_files, output_dir, args.s3_bucket)

    for prepared_file in prepared_files:
        print(
            f"Prepared {prepared_file.entity_name}: "
            f"{prepared_file.row_count} rows -> {prepared_file.local_path}"
        )

    if args.upload:
        upload_to_s3(args.s3_bucket, prepared_files)


if __name__ == "__main__":
    main()
