FROM apache/airflow:2.10.5-python3.11

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/

COPY pyproject.toml uv.lock /tmp/project-deps/

RUN cd /tmp/project-deps \
    && /bin/uv export --quiet --frozen --no-dev --no-emit-project --format requirements-txt --output-file /tmp/project-requirements.txt \
    && pip install --no-cache-dir -r /tmp/project-requirements.txt
