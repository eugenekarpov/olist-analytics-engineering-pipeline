"""Create a small corrupt Olist archive for dead-letter demos."""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def corrupt_csv_member(
    data: bytes,
    column_name: str,
    replacement_value: str,
    data_row_number: int,
) -> bytes:
    input_file = io.StringIO(data.decode("utf-8-sig"))
    output_file = io.StringIO()
    reader = csv.DictReader(input_file)

    if reader.fieldnames is None:
        raise ValueError("CSV member has no header row")
    if column_name not in reader.fieldnames:
        raise ValueError(f"{column_name} is not present in the selected CSV member")

    writer = csv.DictWriter(
        output_file,
        fieldnames=reader.fieldnames,
        lineterminator="\n",
    )
    writer.writeheader()

    changed = False
    for index, row in enumerate(reader, start=1):
        if index == data_row_number:
            row[column_name] = replacement_value
            changed = True
        writer.writerow(row)

    if not changed:
        raise ValueError(f"CSV member has fewer than {data_row_number} data rows")

    return output_file.getvalue().encode("utf-8")


def create_demo_archive(
    archive_path: Path,
    output_path: Path,
    member_name: str,
    column_name: str,
    replacement_value: str,
    data_row_number: int,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(archive_path, "r") as source_zip:
        if member_name not in source_zip.namelist():
            raise ValueError(f"{member_name} is not present in {archive_path}")

        with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as target_zip:
            for member in source_zip.infolist():
                data = source_zip.read(member.filename)
                if member.filename == member_name:
                    data = corrupt_csv_member(
                        data=data,
                        column_name=column_name,
                        replacement_value=replacement_value,
                        data_row_number=data_row_number,
                    )
                target_zip.writestr(member, data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", default="olist.zip")
    parser.add_argument(
        "--output",
        default="data/demo/dead_letter/olist_dead_letter_demo.zip",
    )
    parser.add_argument("--member", default="olist_order_payments_dataset.csv")
    parser.add_argument("--column", default="payment_value")
    parser.add_argument("--value", default="not_a_decimal")
    parser.add_argument("--data-row-number", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    create_demo_archive(
        archive_path=Path(args.archive),
        output_path=Path(args.output),
        member_name=args.member,
        column_name=args.column,
        replacement_value=args.value,
        data_row_number=args.data_row_number,
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
