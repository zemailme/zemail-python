from .client import ZemailClient
from .exceptions import (
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ValidationError,
    ZemailAPIError,
    ZemailError,
)

__version__ = "1.1.1"

__all__ = [
    "ZemailClient",
    "ZemailError",
    "ZemailAPIError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "InvalidRequestError",
    "ValidationError",
    "RateLimitError",
]
