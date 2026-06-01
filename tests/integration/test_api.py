"""API smoke tests."""

from fastapi.testclient import TestClient

from mtor_nexus.api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Expose a lightweight container readiness endpoint."""

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.6.0"}


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


def test_ai_status_and_refusal_bound_prediction_endpoints() -> None:
    """Expose blocked readiness and refuse unsupported numerical output."""

    status = client.get("/ai/status")
    assert status.status_code == 200
    assert status.json()["scientific_release_ready"] is False
    response = client.post(
        "/ai/predict",
        json={
            "smiles": "C",
            "binding_mode": "atp_competitive",
            "include_cofolding": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["selectivity"]["refusal_reason"] == "out_of_applicability_domain"
    assert response.json()["selectivity"]["per_target_pic50"] == []
    assert response.json()["cofolding"]["status"] == "prepared"


def test_ai_scaffold_endpoint_caps_the_requested_limit() -> None:
    """Return red-tagged computational-only scaffold hypotheses."""

    response = client.get("/ai/scaffolds?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["tag"] == "red_computational_only_unvalidated"
