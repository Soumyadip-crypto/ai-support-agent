import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register():

    unique_id = uuid.uuid4().hex[:8]

    response = client.post(
        "/register",
        json={
            "username": f"autotest{unique_id}",
            "password": "testpass123",
            "email": f"autotest{unique_id}@gmail.com"
        }
    )

    assert response.status_code in [200, 201]


def test_login():

    response = client.post(
        "/login",
        json={
            "username": "autotestuser456",
            "password": "testpass123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_profile_with_valid_token():

    login_response = client.post(
        "/login",
        json={
            "username": "autotestuser456",
            "password": "testpass123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/profile",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "username" in data
    assert data["username"] == "autotestuser456"


def test_profile_with_invalid_token():

    response = client.get(
        "/profile",
        headers={
            "Authorization": "Bearer invalid-token-123"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Invalid or expired token"


def test_profile_without_token():

    response = client.get("/profile")

    assert response.status_code == 401


def test_customer_ownership():

    login_response = client.post(
        "/login",
        json={
            "username": "user2",
            "password": "user2pass"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/customers/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_order_ownership():

    login_response = client.post(
        "/login",
        json={
            "username": "user2",
            "password": "user2pass"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/orders/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_customer_orders_ownership():

    login_response = client.post(
        "/login",
        json={
            "username": "user2",
            "password": "user2pass"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/customers/1/orders",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_agent_requires_authentication():

    response = client.post(
        "/test-agent",
        json={
            "message": "Show me my orders",
            "conversation_id": "pytest-agent-001"
        }
    )

    assert response.status_code == 401


def test_agent_with_valid_token():

    login_response = client.post(
        "/login",
        json={
            "username": "user2",
            "password": "user2pass"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/test-agent",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "message": "Show me my orders",
            "conversation_id": "pytest-agent-002"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "response" in data


def test_agent_invalid_input():

    login_response = client.post(
        "/login",
        json={
            "username": "user2",
            "password": "user2pass"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/test-agent",
        json={
            "message": "",
            "conversation_id": ""
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 422


def test_conversation_hijacking():

    login_response = client.post(
        "/login",
        json={
            "username": "user2",
            "password": "user2pass"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/test-agent",
        json={
            "message": "Show me my orders",
            "conversation_id": "conv-002"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_rate_limiting():

    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi import _rate_limit_exceeded_handler

    test_app = FastAPI()

    test_limiter = Limiter(
        key_func=get_remote_address
    )

    test_app.state.limiter = test_limiter

    test_app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler
    )

    @test_app.get("/rate-test")
    @test_limiter.limit("2/minute")
    def rate_test(request: Request):

        return {
            "message": "success"
        }

    test_client = TestClient(test_app)

    response1 = test_client.get("/rate-test")

    assert response1.status_code == 200

    response2 = test_client.get("/rate-test")

    assert response2.status_code == 200

    response3 = test_client.get("/rate-test")

    assert response3.status_code == 429