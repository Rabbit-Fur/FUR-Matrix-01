from __future__ import annotations

from flask import Blueprint, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

monitoring = Blueprint("monitoring", __name__)

# Metrics
GPT_RESPONSE_TIME = Histogram("gpt_response_seconds", "Time spent waiting for GPT responses")
GPT_ERROR_COUNT = Counter("gpt_errors_total", "Number of GPT errors")


@monitoring.route("/metrics")
def metrics() -> Response:
    """Expose Prometheus metrics."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
