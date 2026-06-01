"""API smoke tests."""

from fastapi.testclient import TestClient

from mtor_nexus.api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Expose a lightweight container readiness endpoint."""

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.5.0"}


def test_graph_endpoint() -> None:
    """Serve the normalized seed graph."""

    response = client.get("/graph")
    assert response.status_code == 200
    assert len(response.json()["nodes"]) >= 215


def test_disease_endpoint() -> None:
    """Serve the normalized Phase 4 disease overlay."""

    response = client.get("/diseases")
    assert response.status_code == 200
    assert len(response.json()["disease_classes"]) == 8


def test_drug_endpoint() -> None:
    """Serve the normalized Phase 5 inhibitor and bioactivity overlay."""

    response = client.get("/drugs")
    assert response.status_code == 200
    assert len(response.json()["drugs"]) == 23
