import pytest

from zemail import ZemailClient
from zemail.exceptions import AuthenticationError, RateLimitError, ValidationError


def test_client_initialization(api_key):
    client = ZemailClient(api_key=api_key)
    assert client.api_key == api_key
    assert client.base_url == "https://zemail.me/api"
    assert client.http_client.headers["Authorization"] == f"Bearer {api_key}"
    assert client.http_client.headers["Zemail-Version"] == "2026-04-23"
    assert client.http_client.headers["User-Agent"] == "zemail-python-sdk/1.3.0"


def test_client_custom_options(api_key):
    client = ZemailClient(
        api_key=api_key,
        base_url="https://custom.zemail.me/api/",
        version="2026-05-01",
        timeout=15.0,
        headers={"X-Custom-Header": "custom-value"},
    )
    assert client.base_url == "https://custom.zemail.me/api"
    assert client.http_client.headers["Zemail-Version"] == "2026-05-01"
    assert client.http_client.headers["X-Custom-Header"] == "custom-value"
    assert client.http_client.timeout.read == 15.0


def test_auth_error(client, mock_api):
    mock_api.get("/account").respond(
        status_code=401,
        json={
            "error": {
                "type": "authentication_error",
                "code": "invalid_api_key",
                "message": "Invalid API key provided",
                "request_id": "req_123",
            }
        },
    )
    with pytest.raises(AuthenticationError) as exc:
        client.account.get()

    assert exc.value.status == 401
    assert exc.value.code == "invalid_api_key"
    assert exc.value.request_id == "req_123"


def test_validation_error(client, mock_api):
    mock_api.post("/mailboxes").respond(
        status_code=422,
        json={
            "error": {
                "type": "invalid_request_error",
                "code": "validation_failed",
                "message": "Validation failed",
                "errors": {"username": ["Too short"]},
            }
        },
    )
    with pytest.raises(ValidationError) as exc:
        client.mailboxes.create(type="custom", username="a")

    assert exc.value.status == 422
    assert exc.value.errors == {"username": ["Too short"]}


def test_rate_limit_error(client, mock_api):
    mock_api.get("/mailboxes").respond(
        status_code=429,
        json={
            "error": {
                "type": "rate_limit_error",
                "code": "rate_limit_exceeded",
                "message": "Too many requests",
            }
        },
    )
    with pytest.raises(RateLimitError) as exc:
        client.mailboxes.list()

    assert exc.value.status == 429
