
import pickle


# --------------------------------------------------
# TEST MODELS
# --------------------------------------------------

class AttackModel:
    def predict(self, samples):
        return [1 for _ in samples]


class BenignModel:
    def predict(self, samples):
        return [0 for _ in samples]


class ProbabilityAttackModel:
    """
    Lightweight model for testing ML probability-based scoring.
    """

    classes_ = [0, 1]

    def predict(self, samples):
        return [1 for _ in samples]

    def predict_proba(self, samples):
        return [[0.15, 0.85] for _ in samples]


class LowerProbabilityAttackModel:
    """
    Lightweight model with lower attack probability.
    """

    classes_ = [0, 1]

    def predict(self, samples):
        return [1 for _ in samples]

    def predict_proba(self, samples):
        return [[0.25, 0.75] for _ in samples]


# --------------------------------------------------
# INVALID MODEL OUTPUT TEST FIXTURES
# --------------------------------------------------

class InvalidPredictionModel:
    """
    Simulate an ML model returning an unsupported label.
    """

    def predict(self, samples):
        return ["unknown" for _ in samples]


class InvalidProbabilityAttackModel:
    """
    Simulate an ML model returning an invalid
    attack probability greater than 1.0.
    """

    classes_ = [0, 1]

    def predict(self, samples):
        return [1 for _ in samples]

    def predict_proba(self, samples):
        return [[-0.2, 1.2] for _ in samples]


# --------------------------------------------------
# TEST INPUT
# --------------------------------------------------

VALID_FLOW = {
    "Flow Duration": 1250,
    "Total Fwd Packets": 20,
    "Total Backward Packets": 10,
    "Flow Bytes/s": 5000,
    "Flow Packets/s": 25,
}


# --------------------------------------------------
# MODEL ARTIFACT HELPER
# --------------------------------------------------

def save_model(tmp_path, model):
    model_path = tmp_path / "test_model.pkl"

    with model_path.open("wb") as model_file:
        pickle.dump(model, model_file)

    return model_path


# --------------------------------------------------
# ML ATTACK DETECTION
# --------------------------------------------------

def test_detection_e2e_ml_attack(
    authenticated_client,
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

    response = authenticated_client.post(
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


# --------------------------------------------------
# BENIGN FLOW DETECTION
# --------------------------------------------------

def test_detection_e2e_benign_flow(
    authenticated_client,
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

    response = authenticated_client.post(
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


# --------------------------------------------------
# BRUTE FORCE SIGNATURE DETECTION
# --------------------------------------------------

def test_detection_e2e_signature_attack(
    authenticated_client,
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

    response = authenticated_client.post(
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


# --------------------------------------------------
# ML PROBABILITY-BASED SCORING
# --------------------------------------------------

def test_detection_e2e_ml_probability_scoring(
    authenticated_client,
    tmp_path,
    monkeypatch,
):
    model_path = save_model(
        tmp_path,
        ProbabilityAttackModel(),
    )

    monkeypatch.setenv(
        "MODEL_PATH",
        str(model_path),
    )

    response = authenticated_client.post(
        "/detection/analyze",
        json={
            "flow": VALID_FLOW,
            "event": {},
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["inference"]["prediction"] == 1
    assert data["inference"]["attack_probability"] == 0.85

    assert data["signature"]["detected"] is False

    assert data["threat"]["detected"] is True
    assert data["threat"]["attack_type"] == "ml_detected"
    assert data["threat"]["threat_score"] == 85
    assert data["threat"]["classification"] == "high"


# --------------------------------------------------
# PORT SCAN SIGNATURE END-TO-END TEST
# --------------------------------------------------

def test_detection_e2e_port_scan_signature(
    authenticated_client,
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

    response = authenticated_client.post(
        "/detection/analyze",
        json={
            "flow": VALID_FLOW,
            "event": {
                "ports_scanned": 25,
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["inference"]["prediction"] == 0

    assert data["signature"]["detected"] is True
    assert data["signature"]["attack_type"] == "port_scan"
    assert data["signature"]["severity"] == "medium"

    assert data["threat"]["detected"] is True
    assert data["threat"]["attack_type"] == "port_scan"
    assert data["threat"]["threat_score"] == 60
    assert data["threat"]["classification"] == "medium"


# --------------------------------------------------
# COMBINED DETECTION - HIGHER ML SCORE
# --------------------------------------------------

def test_combined_detection_uses_higher_ml_score(
    authenticated_client,
    tmp_path,
    monkeypatch,
):
    model_path = save_model(
        tmp_path,
        ProbabilityAttackModel(),
    )

    monkeypatch.setenv(
        "MODEL_PATH",
        str(model_path),
    )

    response = authenticated_client.post(
        "/detection/analyze",
        json={
            "flow": VALID_FLOW,
            "event": {
                "ports_scanned": 25,
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["inference"]["prediction"] == 1
    assert data["inference"]["attack_probability"] == 0.85

    assert data["signature"]["detected"] is True
    assert data["signature"]["severity"] == "medium"

    assert data["threat"]["detected"] is True
    assert data["threat"]["attack_type"] == "port_scan"
    assert data["threat"]["threat_score"] == 85
    assert data["threat"]["classification"] == "high"


# --------------------------------------------------
# COMBINED DETECTION - HIGHER SIGNATURE SCORE
# --------------------------------------------------

def test_combined_detection_uses_higher_signature_score(
    authenticated_client,
    tmp_path,
    monkeypatch,
):
    model_path = save_model(
        tmp_path,
        LowerProbabilityAttackModel(),
    )

    monkeypatch.setenv(
        "MODEL_PATH",
        str(model_path),
    )

    response = authenticated_client.post(
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

    assert data["inference"]["attack_probability"] == 0.75

    assert data["signature"]["detected"] is True
    assert data["signature"]["severity"] == "high"

    assert data["threat"]["detected"] is True
    assert data["threat"]["attack_type"] == "brute_force"
    assert data["threat"]["threat_score"] == 90
    assert data["threat"]["classification"] == "high"


# --------------------------------------------------
# TASK 7 - INVALID ML PREDICTION API TEST
# --------------------------------------------------

def test_detection_e2e_invalid_prediction_returns_400(
    authenticated_client,
    tmp_path,
    monkeypatch,
):
    """
    An unsupported ML prediction must return HTTP 400.
    """

    model_path = save_model(
        tmp_path,
        InvalidPredictionModel(),
    )

    monkeypatch.setenv(
        "MODEL_PATH",
        str(model_path),
    )

    response = authenticated_client.post(
        "/detection/analyze",
        json={
            "flow": VALID_FLOW,
            "event": {},
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert "detail" in data
    assert "Unrecognized model prediction" in data["detail"]


# --------------------------------------------------
# TASK 7 - INVALID ML PROBABILITY API TEST
# --------------------------------------------------

def test_detection_e2e_invalid_probability_returns_400(
    authenticated_client,
    tmp_path,
    monkeypatch,
):
    """
    An invalid attack probability must return HTTP 400.

    The ML inference module validates attack
    probabilities before threat scoring occurs.
    """

    model_path = save_model(
        tmp_path,
        InvalidProbabilityAttackModel(),
    )

    monkeypatch.setenv(
        "MODEL_PATH",
        str(model_path),
    )

    response = authenticated_client.post(
        "/detection/analyze",
        json={
            "flow": VALID_FLOW,
            "event": {},
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert "detail" in data
    assert (
        "Attack probability must be finite and between 0 and 1"
        in data["detail"]
    )
