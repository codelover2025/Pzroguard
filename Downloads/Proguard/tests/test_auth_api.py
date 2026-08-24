def test_login_success(client, user):
    response = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "StrongPass123"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["message"] == "login_successful"
    assert payload["user"]["username"] == "alice"


def test_login_missing_payload_fields(client):
    response = client.post("/api/auth/login", json={"username": ""})
    assert response.status_code == 400
    assert response.get_json()["error"] == "bad_request"


def test_login_invalid_credentials(client, user):
    response = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "WrongPass"},
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "invalid_credentials"


def test_lockout_after_repeated_failures(client, app, user):
    app.config["AUTH_MAX_LOGIN_ATTEMPTS"] = 2
    app.config["AUTH_LOCKOUT_SECONDS"] = 30

    for _ in range(2):
        client.post("/api/auth/login", json={"username": "alice", "password": "WrongPass"})

    response = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "StrongPass123"},
    )
    assert response.status_code == 429
    assert response.get_json()["error"] == "too_many_attempts"


def test_me_requires_auth(client, user):
    response = client.get("/api/auth/me")
    assert response.status_code in (302, 401)


def test_me_and_change_password_flow(client, user):
    login_resp = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "StrongPass123"},
    )
    assert login_resp.status_code == 200

    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.get_json()["username"] == "alice"

    weak_resp = client.post(
        "/api/auth/change-password",
        json={"current_password": "StrongPass123", "new_password": "short"},
    )
    assert weak_resp.status_code == 400
    assert weak_resp.get_json()["error"] == "weak_password"

    change_resp = client.post(
        "/api/auth/change-password",
        json={"current_password": "StrongPass123", "new_password": "EvenStrongerPass123"},
    )
    assert change_resp.status_code == 200

    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200

    relogin_resp = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "EvenStrongerPass123"},
    )
    assert relogin_resp.status_code == 200

