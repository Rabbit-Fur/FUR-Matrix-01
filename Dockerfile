# syntax=docker/dockerfile:1

# ⛏️ Builder stage
FROM python:3.11-slim AS builder
WORKDIR /app

# 🛠️ Install build tools and create wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# 🔧 Runtime stage
FROM python:3.11-slim AS runtime
WORKDIR /app

# 🔍 Install runtime dependencies for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 📦 Install prebuilt wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# 📝 Copy application code
COPY . .

# 👤 Create non-root user
RUN useradd --create-home --uid 10001 appuser
USER 10001

# 🌐 Expose application port and define healthcheck
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD curl --fail http://127.0.0.1:8080/health || exit 1

# ⏰ Default command
CMD ["python", "main_app.py"]

