# Django Request Logging

Django Request Logging is a Django app that logs detailed request information, such as URL, method, headers, and response time. It outputs logs to the console and can optionally store them in the database for long-term tracking, making it easier to monitor, debug, and analyze user interactions with your application.

## Install

```bash
pip install git+https://github.com/cuongnbms/django-request-logging.git@v1.4#egg=django-request-logging
```

## Setup

```python
INSTALLED_APPS = [
    'request_logging',
    ...
]

MIDDLEWARE = [
    ...
    'request_logging.middlewares.RequestLogMiddleware',
]

REQUEST_LOGGING = {
    'WHITELIST_PATHS': ["/admin/jsi18n/"],
    'ENABLE_PYTHON_LOG': True,
    'ENABLE_DB_LOG': True,
    'DB_LOG_SAMPLE': 1,
    'LOG_HEADER_KEYS': ["HTTP_USER_AGENT", "HTTP_X_FORWARDED_FOR", "REMOTE_ADDR", "HTTP_REFERER"],
}
```

Run migrations:

```bash
python3 manage.py migrate
```

## Settings

All settings are optional and fall back to the defaults shown above.

| Key | Default | Description |
| --- | --- | --- |
| `WHITELIST_PATHS` | `["/admin/jsi18n/"]` | Request paths to skip entirely. |
| `ENABLE_PYTHON_LOG` | `True` | Emit an access-log line via the `request_logging` logger. |
| `ENABLE_DB_LOG` | `True` | Persist each request to the `RequestLog` table. |
| `DB_LOG_SAMPLE` | `1` | Fraction of requests to store in the database (`0`–`1`). Use e.g. `0.1` to sample 10% under high traffic. |
| `LOG_HEADER_KEYS` | `["HTTP_USER_AGENT", "HTTP_X_FORWARDED_FOR", "REMOTE_ADDR", "HTTP_REFERER"]` | `request.META` keys to capture into the stored `headers` field. |

## Cleaning up old logs

The `RequestLog` table grows quickly. Use the bundled management command to prune old rows (deletes in batches, safe on large tables):

```bash
# keep the last 7 days
python3 manage.py remove_old_request_log 7d

# keep the last 3 months
python3 manage.py remove_old_request_log 3m
```

The argument is `<value><unit>` where unit is `d` (days) or `m` (months). Schedule it via cron/Celery beat to keep the table bounded.

## Running tests

The suite is self-contained (SQLite in-memory, no extra config). From the repo root:

```bash
python -m venv .venv
.venv/bin/pip install "Django>=4.0"
.venv/bin/python runtests.py
```

Run a subset with e.g. `python runtests.py tests.test_middleware`.
