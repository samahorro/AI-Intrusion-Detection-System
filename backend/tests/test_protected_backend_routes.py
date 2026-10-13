def test_capture_interfaces_requires_authentication(
    client,
):
    response = client.get("/capture/interfaces")

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authentication required."
    )


def test_capture_status_requires_authentication(
    client,
):
    response = client.get("/capture/status")

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authentication required."
    )


def test_capture_stats_requires_authentication(
    client,
):
    response = client.get("/capture/stats")

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authentication required."
    )


def test_capture_flows_requires_authentication(
    client,
):
    response = client.get("/capture/flows")

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authentication required."
    )


def test_capture_start_requires_authentication(
    client,
):
    response = client.post(
        "/capture/start",
        json={
            "interface": "Wi-Fi",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authentication required."
    )


def test_capture_stop_requires_authentication(
    client,
):
    response = client.post("/capture/stop")

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authentication required."
    )


def test_detection_analyze_requires_authentication(
    client,
):
    response = client.post(
        "/detection/analyze",
        json={
            "flow": {},
            "event": {},
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authentication required."
    )