"""Correction feed contracts used by ingestion and raw loading."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeedSpec:
    entity_name: str
    file_name: str
    headers: list[str]
    column_types: dict[str, str]


CUSTOMER_FEED = FeedSpec(
    entity_name="customer_profile_changes",
    file_name="customer_profile_changes.csv.gz",
    headers=[
        "customer_unique_id",
        "effective_at",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
        "change_reason",
    ],
    column_types={
        "customer_unique_id": "varchar(256)",
        "effective_at": "timestamp",
        "customer_zip_code_prefix": "varchar(16)",
        "customer_city": "varchar(256)",
        "customer_state": "varchar(2)",
        "change_reason": "varchar(256)",
    },
)

PRODUCT_FEED = FeedSpec(
    entity_name="product_attribute_changes",
    file_name="product_attribute_changes.csv.gz",
    headers=[
        "product_id",
        "effective_at",
        "product_category_name",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "change_reason",
    ],
    column_types={
        "product_id": "varchar(256)",
        "effective_at": "timestamp",
        "product_category_name": "varchar(256)",
        "product_weight_g": "integer",
        "product_length_cm": "integer",
        "product_height_cm": "integer",
        "product_width_cm": "integer",
        "change_reason": "varchar(256)",
    },
)

CORRECTION_FEEDS = [CUSTOMER_FEED, PRODUCT_FEED]
