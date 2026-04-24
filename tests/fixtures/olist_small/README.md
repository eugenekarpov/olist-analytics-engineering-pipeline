# Small Olist Fixture

This fixture is a tiny, synthetic Olist-shaped dataset for CI.

- `olist_small.zip` contains the same CSV file names and headers as the full
  Kaggle archive.
- `source_profile_small.json` is the matching source contract.
- `source/` contains the uncompressed CSVs so fixture changes are reviewable.

The fixture is intentionally committed to the repository because it is small
and lets CI run the real ingestion, raw load, reconciliation, and dbt path
without downloading the full dataset.

Regenerate it with:

```powershell
.\.venv\Scripts\python.exe scripts\testing\create_small_fixture_dataset.py
```
