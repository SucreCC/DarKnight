ARG PYTHON_VERSION=3.12

# --- Build dashboard (Vue) ---
FROM node:20-bookworm-slim AS dashboard
WORKDIR /build

COPY darknight/dashboard/package.json darknight/dashboard/package-lock.json ./
RUN npm ci

COPY darknight/dashboard/ ./
ENV VITE_BASE_URL=
ENV VITE_API_URL=/api/v1
ENV VITE_BASE_PATH=./
RUN npm run build

# --- Build Python deps + Xray core ---
FROM python:${PYTHON_VERSION}-slim AS build

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        unzip \
        gcc \
        python3-dev \
        libpq-dev \
    && curl -fsSL https://github.com/Gozargah/Marzban-scripts/raw/master/install_latest_xray.sh | bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN python -m pip install --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt

# --- Runtime ---
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONUNBUFFERED=1 \
    PROJECT_HOME=/app \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

ARG PYTHON_VERSION=3.12
ENV PYTHON_LIB_PATH=/usr/local/lib/python${PYTHON_VERSION}/site-packages

COPY --from=build ${PYTHON_LIB_PATH} ${PYTHON_LIB_PATH}
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /usr/local/share/xray /usr/local/share/xray

COPY alembic.ini pyproject.toml requirements.txt /app/
COPY darknight/ /app/darknight/
COPY xray_api/ /app/xray_api/
COPY docker/config.yaml /app/darknight/config.yaml
COPY docker/entrypoint.sh /entrypoint.sh
COPY --from=dashboard /build/dist /app/darknight/dashboard/dist

RUN chmod +x /entrypoint.sh \
    && mkdir -p /app/data/logs

EXPOSE 33100

ENTRYPOINT ["/entrypoint.sh"]
