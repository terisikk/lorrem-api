FROM python:3.11-slim-buster as base

WORKDIR /app

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.4.0

RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
COPY *.py ./
COPY lorrem ./lorrem

RUN poetry config virtualenvs.in-project true && \
    poetry install --only=main --no-root && \
    poetry build

RUN poetry build && /venv/bin/pip install dist/*.whl

FROM base as final

COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/dist .
COPY docker-entrypoint.sh .
COPY conf ./conf

RUN ./.venv/bin/pip install *.whl

CMD ["./docker-entrypoint.sh"]
