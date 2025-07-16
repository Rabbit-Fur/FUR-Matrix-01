from flask.testing import FlaskClient


def test_metrics_endpoint(client: FlaskClient):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"gpt_response_seconds" in resp.data
