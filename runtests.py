#!/usr/bin/env python3
"""Standalone test runner for the request_logging app.

Usage:
    python runtests.py          # run the full suite
    python runtests.py tests.test_middleware   # run a subset
"""
import sys

import django
from django.conf import settings


def configure():
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'request_logging',
        ],
        MIDDLEWARE=[
            'request_logging.middlewares.RequestLogMiddleware',
        ],
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        USE_TZ=True,
        LOGGING_CONFIG=None,
    )
    django.setup()


def main():
    configure()
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    labels = sys.argv[1:] or ['tests']
    failures = test_runner.run_tests(labels)
    sys.exit(bool(failures))


if __name__ == '__main__':
    main()
