from backend.app.detection.routes import get_detection_model


class AttackModel:
    def predict(self, samples):
        return [1]


class BenignModel:
    def predict(self, samples):
        return [0]


VALID_FLOW = {
    "Flow Duration": 1250,
    "Total Fwd Packets": 20,
    "Total Backward Packets": 10,
    "Flow Bytes/s": 5000,
    "Flow Packets/s": 25,
}


def test_ai_backend_detection_pipeline(client):
    client.app.dependency_overrides[
        get_detection_model
    ] = lambda: AttackModel()

    try:
        response = client.post(
            "/detection/analyze",
            json={
                "flow": VALID_FLOW,
                "event": {},
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "success"
        assert data["features"] == [
            1250.0,
            20.0,
            10.0,
            5000.0,
            25.0,
        ]
        assert data["inference"]["prediction"] == 1
        assert data["threat"]["detected"] is True
        assert data["threat"]["attack_type"] == "ml_detected"
        assert data["threat"]["classification"] == "high"

    finally:
        client.app.dependency_overrides.clear()


def test_signature_detection_integrates_with_backend(client):
    client.app.dependency_overrides[
        get_detection_model
    ] = lambda: BenignModel()

    try:
        response = client.post(
            "/detection/analyze",
            json={
                "flow": VALID_FLOW,
                "event": {
                    "failed_login_attempts": 7,
                },
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["inference"]["prediction"] == 0
        assert data["signature"]["detected"] is True
        assert data["signature"]["attack_type"] == "brute_force"
        assert data["threat"]["detected"] is True
        assert data["threat"]["attack_type"] == "brute_force"
        assert data["threat"]["classification"] == "high"

    finally:
        client.app.dependency_overrides.clear()


def test_benign_flow_returns_normal_threat(client):
    client.app.dependency_overrides[
        get_detection_model
    ] = lambda: BenignModel()

    try:
        response = client.post(
            "/detection/analyze",
            json={
                "flow": VALID_FLOW,
                "event": {},
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["inference"]["prediction"] == 0
        assert data["signature"]["detected"] is False
        assert data["threat"]["detected"] is False
        assert data["threat"]["threat_score"] == 0
        assert data["threat"]["classification"] == "normal"

    finally:
        client.app.dependency_overrides.clear()


def test_invalid_flow_rejected(client):
    client.app.dependency_overrides[
        get_detection_model
    ] = lambda: BenignModel()

    try:
        response = client.post(
            "/detection/analyze",
            json={
                "flow": {
                    "Flow Duration": "invalid",
                },
                "event": {},
            },
        )

        assert response.status_code == 400

    finally:
        client.app.dependency_overrides.clear()


def test_missing_model_configuration(client):
    response = client.post(
        "/detection/analyze",
        json={
            "flow": VALID_FLOW,
            "event": {},
        },
    )

    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "Detection model is not configured."
    )