# codex-universal-fur.Dockerfile – FUR QUM Enhanced
FROM ghcr.io/openai/codex-universal:latest

# Set labels for provenance
LABEL maintainer="FUR QUM"
LABEL org.opencontainers.image.source="https://github.com/Rabbit-Fur/try"
LABEL codex.variant="fur-qum"

# Optional: Preinstall FUR CLI tools or scripts
COPY core/universal/setup.py /opt/fur/setup.py
ENV PYTHONPATH=/opt/fur

# Ensure latest language tools and validators are active
RUN pip install --upgrade ruff black isort mypy pyright uv &&     poetry config virtualenvs.in-project true &&     echo "✅ Codex Universal FUR enhanced image ready."
