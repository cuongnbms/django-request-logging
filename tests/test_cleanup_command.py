from datetime import timedelta

from django.core.management import CommandError, call_command
from django.test import TestCase
from django.utils import timezone

from request_logging.models import RequestLog


def make_log(request_at):
    return RequestLog.objects.create(
        method='GET', hostname='h', path='/', client_ip='1.1.1.1',
        response_code=200, response_time=0.1, request_at=request_at,
    )


class RemoveOldRequestLogTests(TestCase):
    def test_deletes_only_rows_older_than_keep_days(self):
        now = timezone.now()
        old = make_log(now - timedelta(days=10))
        recent = make_log(now - timedelta(days=1))

        call_command('remove_old_request_log', '7d')

        remaining = list(RequestLog.objects.values_list('id', flat=True))
        self.assertEqual(remaining, [recent.id])
        self.assertFalse(RequestLog.objects.filter(id=old.id).exists())

    def test_month_unit_uses_30_days(self):
        now = timezone.now()
        older = make_log(now - timedelta(days=65))
        newer = make_log(now - timedelta(days=20))

        call_command('remove_old_request_log', '1m')

        self.assertFalse(RequestLog.objects.filter(id=older.id).exists())
        self.assertTrue(RequestLog.objects.filter(id=newer.id).exists())

    def test_invalid_value_raises(self):
        with self.assertRaises(CommandError):
            call_command('remove_old_request_log', 'xd')

    def test_invalid_unit_raises(self):
        with self.assertRaises(CommandError):
            call_command('remove_old_request_log', '7y')
