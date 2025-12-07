FROM python:3.11 AS builder


WORKDIR /app/backend


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY backend/requirements.txt .


RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt


FROM python:3.11-slim


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/* \
    && rm -rf /wheels


COPY backend/main.py .

EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]