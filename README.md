# Zemail Python SDK

[![Latest Version on PyPI](https://img.shields.io/pypi/v/zemail-python.svg?style=flat-square)](https://pypi.org/project/zemail-python/)
[![GitHub Tests Action Status](https://img.shields.io/github/actions/workflow/status/zemailme/zemail-python/ci.yml?branch=main&label=tests&style=flat-square)](https://github.com/zemailme/zemail-python/actions?query=workflow%3ACI+branch%3Amain)
[![Python Version](https://img.shields.io/pypi/pyversions/zemail-python.svg?style=flat-square)](https://pypi.org/project/zemail-python/)
[![License](https://img.shields.io/github/license/zemailme/zemail-python?style=flat-square)](https://github.com/zemailme/zemail-python/blob/main/LICENSE)

The official Python SDK for the [Zemail Developer API](https://zemail.me/api-docs). Create and manage temporary mailboxes, receive emails, and handle attachments programmatically.

---

## Requirements

- Python 3.9 or higher
- `httpx >= 0.24.0`
- `pydantic >= 2.0.0`

---

## Installation

Install the package via `pip`:

```bash
pip install zemail-python
```

Or install the latest development version directly from GitHub:

```bash
pip install git+https://github.com/zemailme/zemail-python.git
```

---

## Quickstart

Initialize the `ZemailClient` with your API key:

```python
from zemail import ZemailClient

client = ZemailClient(api_key="zm_live_your_api_key_here")
```

You can optionally specify an API version, timeout, custom headers, or use it as a context manager:

```python
from zemail import ZemailClient

with ZemailClient(
    api_key="zm_live_your_api_key_here",
    version="2026-04-23",
    timeout=10.0,
    headers={"X-Custom-Header": "value"},
) as client:
    account = client.account.get()
    print(f"Logged in as: {account.email}")
```

---

## Usage

### 1. Account & Subscription

Access your account profile, active subscription plan, and API/mailbox usage limits:

```python
# Get account profile
account = client.account.get()
print(f"Account ID: {account.id}, Email: {account.email}, Tier: {account.tier}")

# Get active subscription
subscription = client.account.subscription()
print(f"Status: {subscription.status}, Tier: {subscription.tier}")

# Get current resource & API usage
usage = client.account.usage()
print("Mailbox Usage:", usage.mailboxes)
print("Storage Usage:", usage.storage)
print("Developer API Usage:", usage.developer_api)
```

---

### 2. Domains

List available domains for mailbox creation:

```python
domains = client.domains.list()

for domain in domains.data:
    print(f"Domain: {domain.name} (Types: {', '.join(domain.allowed_types)})")
```

---

### 3. Mailboxes

#### List Mailboxes
```python
mailboxes = client.mailboxes.list(page=1, limit=10)

for mailbox in mailboxes.data:
    print(f"Mailbox: {mailbox.address} (ID: {mailbox.id})")

if mailboxes.has_more:
    print(f"Next cursor: {mailboxes.next_cursor}")
```

#### Create a Random Mailbox
```python
mailbox = client.mailboxes.create(type="random")
print(f"Created random mailbox: {mailbox.address}")
```

#### Create a Custom Mailbox
```python
mailbox = client.mailboxes.create(
    type="custom",
    domain="zemail.me",
    username="my-inbox",
)
print(f"Created custom mailbox: {mailbox.address}")
```

#### Get Mailbox Details
```python
mailbox = client.mailboxes.get(mailbox_id=123)
print(f"Address: {mailbox.address}, Unread emails: {mailbox.unread_count}")
```

#### Delete a Mailbox
```python
deleted = client.mailboxes.delete(mailbox_id=123)
print(f"Mailbox deleted: {deleted.deleted}")
```

---

### 4. Emails & Attachments

#### List Emails in a Mailbox
```python
# List emails with optional search query and pagination
emails = client.emails.list(
    mailbox_id=mailbox.id,
    page=1,
    limit=25,
    search="verification",
)

for email in emails.data:
    print(f"[{email.id}] From: {email.sender} | Subject: {email.subject}")
```

> **Tip:** You can also access email methods via `client.mailboxes.emails`:
> ```python
> emails = client.mailboxes.emails.list(mailbox_id=mailbox.id)
> ```

#### Get Full Email Details
```python
email = client.emails.get(mailbox_id=mailbox.id, email_id=email_id)

print(f"Subject: {email.subject}")
print(f"Plain text body: {email.body_text}")
print(f"HTML body: {email.body_html}")

# Inspect attachments
for attachment in email.attachments:
    print(f"Attachment: {attachment.name} ({attachment.size} bytes)")
```

#### Mark Email as Read
```python
read_state = client.emails.mark_as_read(mailbox_id=mailbox.id, email_id=email_id)
print(f"Is read: {read_state.is_read}")
```

#### Get Temporary Attachment Download URL
```python
download = client.emails.get_attachment_download_url(
    mailbox_id=mailbox.id,
    email_id=email_id,
    attachment_id="att_123",
)

print(f"Download URL: {download.url}")
print(f"Expires at: {download.expires_at}")
```

#### Delete an Email
```python
deleted = client.emails.delete(mailbox_id=mailbox.id, email_id=email_id)
print(f"Email deleted: {deleted.deleted}")
```

---

## Error Handling

All SDK exceptions inherit from `ZemailAPIError` (which subclasses `ZemailError`):

| Exception | HTTP Status | Description |
|---|---|---|
| `AuthenticationError` | `401` | Invalid API key or unauthorized access |
| `PermissionError` | `403` | Forbidden action or insufficient permissions |
| `NotFoundError` | `404` | Resource (mailbox, email, domain) not found |
| `ValidationError` | `422` | Request validation failure (includes `e.errors`) |
| `InvalidRequestError` | `400`, `422` | Malformed or invalid request parameters |
| `RateLimitError` | `429` | Daily or concurrency rate limit reached |
| `ZemailAPIError` | Any | Generic API exception |
| `ZemailError` | Any | Base SDK exception |

```python
from zemail import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ZemailAPIError,
    ZemailClient,
)

client = ZemailClient(api_key="zm_live_...")

try:
    mailbox = client.mailboxes.create(type="custom")
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print("Errors:", e.errors)
except AuthenticationError as e:
    print(f"Auth error: {e.message}")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
except NotFoundError as e:
    print(f"Not found: {e.message}")
except ZemailAPIError as e:
    print(f"API error [{e.status}]: {e.message}")
```

---

## Development & Testing

Run unit tests with `pytest`:

```bash
pytest
```

Run linting and type checks with `ruff`:

```bash
ruff check .
ruff format --check .
```

Format code with `ruff`:

```bash
ruff format .
```

---

## License

The MIT License (MIT). Please see [LICENSE](LICENSE) for more information.