import time

from .models import RequestLog
from .settings import REQUEST_LOGGING_SETTINGS
import logging
import random

logger = logging.getLogger('request_logging')


def get_ip_client(request):
    client_ip_address = request.META.get('HTTP_IP_ADDRESS')
    if client_ip_address:
        return client_ip_address

    x_cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if x_cf_connecting_ip:
        ip = x_cf_connecting_ip.split(',')[0]
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    return ip


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        start_at = time.time()

        response = self.get_response(request)
        if not REQUEST_LOGGING_SETTINGS['ENABLE_PYTHON_LOG'] and not REQUEST_LOGGING_SETTINGS['ENABLE_DB_LOG']:
            return response

        try:
            if request.path in REQUEST_LOGGING_SETTINGS['WHITELIST_PATHS']:
                return response

            client_ip = get_ip_client(request)

            headers = {}
            for k in REQUEST_LOGGING_SETTINGS["LOG_HEADER_KEYS"]:
                headers[k] = request.META.get(k, '')

            data = {
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'method': request.method,
                'hostname': request.META.get('HTTP_HOST', ''),
                'path': request.path,
                'request_params': dict(request.GET),
                'client_ip': client_ip,
                'headers': headers,
                'response_code': response.status_code,
                'response_time': time.time() - start_at,
            }

            if REQUEST_LOGGING_SETTINGS['ENABLE_DB_LOG']:
                if random.random() < REQUEST_LOGGING_SETTINGS["DB_LOG_SAMPLE"]:
                    RequestLog.objects.create(**data)

            if REQUEST_LOGGING_SETTINGS['ENABLE_PYTHON_LOG']:
                user_id = data["user_id"] if data["user_id"] else "-"
                logger.info('%s %s %sms %s %s %s %s "%s"',
                            data['client_ip'], data['response_code'], int(data['response_time'] * 1000), user_id,
                            data['method'], data['path'], request.META.get('HTTP_REFERER', '-'), request.META.get('HTTP_USER_AGENT', '-'))
            
        except Exception as e:
            logger.exception(e)

        return response
