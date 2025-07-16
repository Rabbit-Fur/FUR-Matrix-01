# Monitoring with Prometheus and Grafana

This project exposes application metrics compatible with Prometheus. The metrics endpoint is available at `/metrics` and can be scraped by a Prometheus server.

```txt
GET /metrics
```

## Grafana Dashboard

You can visualize the metrics using Grafana. Below is a minimal dashboard JSON that displays GPT response times and error rates.

```json
{
  "dashboard": {
    "panels": [
      {
        "type": "graph",
        "title": "GPT Response Time",
        "targets": [{"expr": "gpt_response_seconds"}]
      },
      {
        "type": "graph",
        "title": "GPT Errors",
        "targets": [{"expr": "gpt_errors_total"}]
      }
    ]
  }
}
```

Import this JSON into Grafana to get started.
