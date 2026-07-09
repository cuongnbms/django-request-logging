import logging

from datetime import timedelta
from django.core.management import BaseCommand, CommandError
from django.utils import timezone
from ...models import RequestLog

logger = logging.getLogger(__name__)

BATCH_SIZE = 10000


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('keep', type=str, help='time range to keep request log: 1d (day), 1m (month)')

    def handle(self, *args, **options):
        keep = options.get('keep')
        try:
            value = int(keep[:-1])
        except ValueError:
            raise CommandError("keep must look like '7d' or '1m'")
        unit = keep[-1:]

        now = timezone.now()
        if unit == 'd':
            min_request_at = now - timedelta(days=value)
        elif unit == 'm':
            min_request_at = now - timedelta(days=value * 30)
        else:
            raise CommandError("unit must be 'd' (day) or 'm' (month)")

        logger.info('delete request log before %s', min_request_at)
        base_qs = RequestLog.objects.filter(request_at__lt=min_request_at)
        total = 0
        while True:
            ids = list(base_qs.values_list('id', flat=True)[:BATCH_SIZE])
            if not ids:
                break
            deleted, _ = RequestLog.objects.filter(id__in=ids).delete()
            total += deleted
        logger.info('delete request log before %s done, %s rows removed', min_request_at, total)