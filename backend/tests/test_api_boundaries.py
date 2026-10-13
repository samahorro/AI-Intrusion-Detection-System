def test_register_rejects_missing_username(client):
    response = client.post(
        "/auth/register",
        json={
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 422


def test_register_rejects_missing_password(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "boundaryuser",
        },
    )

    assert response.status_code == 422


def test_register_rejects_wrong_field_type(client):
    response = client.post(
        "/auth/register",
        json={
            "username": {
                "invalid": "object",
            },
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 422


def test_register_rejects_malformed_json(client):
    response = client.post(
        "/auth/register",
        content='{"username": "boundaryuser",',
        headers={
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 422


def test_login_rejects_missing_password(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "boundaryuser",
        },
    )

    assert response.status_code == 422


def test_login_rejects_wrong_username_type(client):
    response = client.post(
        "/auth/login",
        json={
            "username": [
                "not",
                "a",
                "string",
            ],
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 422


def test_capture_start_rejects_missing_interface(
    authenticated_client,
):
    response = authenticated_client.post(
        "/capture/start",
        json={},
    )

    assert response.status_code == 422


def test_capture_start_rejects_wrong_interface_type(
    authenticated_client,
):
    response = authenticated_client.post(
        "/capture/start",
        json={
            "interface": {
                "name": "Wi-Fi",
            },
        },
    )

    assert response.status_code == 422


def test_capture_start_rejects_malformed_json(
    client,
):
    response = client.post(
        "/capture/start",
        content='{"interface":',
        headers={
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 422


def test_capture_start_rejects_get_method(client):
    response = client.get(
        "/capture/start",
    )

    assert response.status_code == 405


def test_capture_status_rejects_post_method(client):
    response = client.post(
        "/capture/status",
    )

    assert response.status_code == 405


def test_unknown_backend_route_returns_not_found(
    client,
):
    response = client.get(
        "/backend-route-that-does-not-exist",
    )

    assert response.status_code == 404