import pickle


class AttackModel:
    def predict(self, samples):
        return [1 for _ in samples]


class BenignModel:
    def predict(self, samples):
        return [0 for _ in samples]


VALID_FLOW = {
    "Flow Duration": 1250,
    "Total Fwd Packets": 20,
    "Total Backward Packets": 10,
    "Flow Bytes/s": 5000,
    "Flow Packets/s": 25,
}


def save_model(tmp_path, model):
    model_path = tmp_path / "test_model.pkl"

    with model_path.open("wb") as model_file:
        pickle.dump(model, model_file)

    return model_path


def test_detection_e2e_ml_attack(
    client,
    tmp_path,
    monkeypatch,
):
    model_path = save_model(
        tmp_path,
        AttackModel(),
    )

    monkeypatch.setenv(
        "MODEL_PATH",
        str(model_path),
    )

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

    assert data["inference"]["status"] == "success"
    assert data["inference"]["prediction"] == 1

    assert data["signature"]["detected"] is False

    assert data["threat"]["detected"] is True
    assert data["threat"]["attack_type"] == "ml_detected"
    assert data["threat"]["threat_score"] == 100
    assert data["threat"]["classification"] == "high"


def test_detection_e2e_benign_flow(
    client,
    tmp_path,
    monkeypatch,
):
    model_path = save_model(
        tmp_path,
        BenignModel(),
    )

    monkeypatch.setenv(
        "MODEL_PATH",
        str(model_path),
    )

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

    assert data["inference"]["prediction"] == 0
    assert data["signature"]["detected"] is False

    assert data["threat"]["detected"] is False
    assert data["threat"]["attack_type"] is None
    assert data["threat"]["threat_score"] == 0
    assert data["threat"]["classification"] == "normal"


def test_detection_e2e_signature_attack(
    client,
    tmp_path,
    monkeypatch,
):
    model_path = save_model(
        tmp_path,
        BenignModel(),
    )

    monkeypatch.setenv(
        "MODEL_PATH",
        str(model_path),
    )

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
    assert data["signature"]["severity"] == "high"

    assert data["threat"]["detected"] is True
    assert data["threat"]["attack_type"] == "brute_force"
    assert data["threat"]["threat_score"] == 90
    assert data["threat"]["classification"] == "high"