from unittest import mock

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from request_logging.middlewares import RequestLogMiddleware
from request_logging.models import RequestLog
from request_logging.settings import REQUEST_LOGGING_SETTINGS


def build_middleware(status_code=200):
    def get_response(request):
        return HttpResponse('ok', status=status_code)
    return RequestLogMiddleware(get_response)


class MiddlewareDbLogTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @mock.patch.dict(REQUEST_LOGGING_SETTINGS,
                     {'ENABLE_DB_LOG': True, 'ENABLE_PYTHON_LOG': False, 'DB_LOG_SAMPLE': 1})
    def test_creates_db_log_with_expected_fields(self):
        middleware = build_middleware(status_code=201)
        request = self.factory.get('/orders/?q=1&q=2&page=3',
                                   HTTP_HOST='example.com',
                                   REMOTE_ADDR='4.4.4.4',
                                   HTTP_USER_AGENT='pytest-agent')
        response = middleware(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(RequestLog.objects.count(), 1)
        log = RequestLog.objects.get()
        self.assertEqual(log.method, 'GET')
        self.assertEqual(log.path, '/orders/')
        self.assertEqual(log.hostname, 'example.com')
        self.assertEqual(log.client_ip, '4.4.4.4')
        self.assertEqual(log.response_code, 201)
        self.assertEqual(log.request_params, {'q': ['1', '2'], 'page': ['3']})
        self.assertEqual(log.headers.get('HTTP_USER_AGENT'), 'pytest-agent')
        self.assertIsNone(log.user_id)
        self.assertGreaterEqual(log.response_time, 0)

    @mock.patch.dict(REQUEST_LOGGING_SETTINGS,
                     {'ENABLE_DB_LOG': True, 'ENABLE_PYTHON_LOG': False, 'DB_LOG_SAMPLE': 1,
                      'WHITELIST_PATHS': ['/admin/jsi18n/']})
    def test_whitelisted_path_is_skipped(self):
        middleware = build_middleware()
        request = self.factory.get('/admin/jsi18n/')
        middleware(request)
        self.assertEqual(RequestLog.objects.count(), 0)

    @mock.patch.dict(REQUEST_LOGGING_SETTINGS,
                     {'ENABLE_DB_LOG': False, 'ENABLE_PYTHON_LOG': False})
    def test_both_disabled_skips_everything(self):
        middleware = build_middleware()
        request = self.factory.get('/orders/')
        middleware(request)
        self.assertEqual(RequestLog.objects.count(), 0)

    @mock.patch.dict(REQUEST_LOGGING_SETTINGS,
                     {'ENABLE_DB_LOG': True, 'ENABLE_PYTHON_LOG': False, 'DB_LOG_SAMPLE': 0})
    def test_sample_zero_never_writes(self):
        middleware = build_middleware()
        request = self.factory.get('/orders/')
        middleware(request)
        self.assertEqual(RequestLog.objects.count(), 0)

    @mock.patch.dict(REQUEST_LOGGING_SETTINGS,
                     {'ENABLE_DB_LOG': True, 'ENABLE_PYTHON_LOG': False, 'DB_LOG_SAMPLE': 1})
    def test_db_error_is_swallowed_and_response_returned(self):
        middleware = build_middleware()
        request = self.factory.get('/orders/')
        with mock.patch.object(RequestLog.objects, 'create', side_effect=Exception('boom')):
            response = middleware(request)
        self.assertEqual(response.content, b'ok')

    @mock.patch.dict(REQUEST_LOGGING_SETTINGS,
                     {'ENABLE_DB_LOG': False, 'ENABLE_PYTHON_LOG': True})
    def test_python_log_only_writes_no_db_row(self):
        middleware = build_middleware()
        request = self.factory.get('/orders/')
        with self.assertLogs('request_logging', level='INFO') as cm:
            middleware(request)
        self.assertEqual(RequestLog.objects.count(), 0)
        self.assertTrue(any('/orders/' in line for line in cm.output))
