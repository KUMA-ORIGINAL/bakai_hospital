FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.13-slim

ENV PROJECT_DIR=/app
WORKDIR $PROJECT_DIR

RUN apt update && apt install -y --no-install-recommends gettext && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache --prefer-binary /wheels/*

COPY . .
RUN chmod +x ./app_entrypoint.dev.sh

# (опционально для безопасности)
# RUN useradd -m appuser
# USER appuser

CMD ["sh", "/app/app_entrypoint.dev.sh"]
