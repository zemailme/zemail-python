from typing import Any, Dict, Optional

import httpx

from .exceptions import (
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ValidationError,
    ZemailAPIError,
)
from .resources.account import AccountResource
from .resources.domains import DomainsResource
from .resources.emails import EmailsResource
from .resources.mailboxes import MailboxesResource


class ZemailClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://zemail.me/api",
        version: Optional[str] = "2026-04-23",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.version = version

        default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "zemail-python-sdk/1.3.0",
        }
        if self.version:
            default_headers["Zemail-Version"] = self.version
        if headers:
            default_headers.update(headers)

        self.http_client = httpx.Client(
            base_url=self.base_url, headers=default_headers, timeout=httpx.Timeout(timeout)
        )

        self.account = AccountResource(self)
        self.domains = DomainsResource(self)
        self.mailboxes = MailboxesResource(self)
        self.emails = EmailsResource(self)

    def _handle_error_response(self, response: httpx.Response):
        try:
            data = response.json()
            error = data.get("error", {})
        except ValueError:
            error = {
                "message": response.text,
                "type": "unknown_error",
                "code": "unknown",
            }

        status = response.status_code
        message = error.get("message", "An error occurred")
        err_type = error.get("type", "unknown_error")
        code = error.get("code", "unknown")
        param = error.get("param")
        request_id = error.get("request_id")

        if status == 401:
            raise AuthenticationError(message, err_type, code, status, param, request_id)
        elif status == 403:
            raise PermissionError(message, err_type, code, status, param, request_id)
        elif status == 404:
            raise NotFoundError(message, err_type, code, status, param, request_id)
        elif status == 422:
            if code == "validation_failed":
                errors = error.get("errors", {})
                raise ValidationError(message, code, status, param, request_id, errors)
            raise InvalidRequestError(message, err_type, code, status, param, request_id)
        elif status == 400:
            raise InvalidRequestError(message, err_type, code, status, param, request_id)
        elif status == 429:
            raise RateLimitError(message, err_type, code, status, param, request_id)
        else:
            raise ZemailAPIError(message, err_type, code, status, param, request_id)

    def request(self, method: str, path: str, **kwargs) -> Any:
        response = self.http_client.request(method, path, **kwargs)
        if not response.is_success:
            self._handle_error_response(response)

        # Some endpoints might return empty responses, handling 204 or no content
        if response.content:
            return response.json()
        return None

    def get(self, path: str, **kwargs) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> Any:
        return self.request("POST", path, **kwargs)

    def delete(self, path: str, **kwargs) -> Any:
        return self.request("DELETE", path, **kwargs)

    def close(self):
        self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
