from django.test import RequestFactory, TestCase

from request_logging.middlewares import get_ip_client


class GetIpClientTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_prefers_ip_address_header(self):
        request = self.factory.get('/', HTTP_IP_ADDRESS='1.1.1.1',
                                   HTTP_CF_CONNECTING_IP='2.2.2.2',
                                   HTTP_X_FORWARDED_FOR='3.3.3.3')
        self.assertEqual(get_ip_client(request), '1.1.1.1')

    def test_falls_back_to_cf_connecting_ip(self):
        request = self.factory.get('/', HTTP_CF_CONNECTING_IP='2.2.2.2, 9.9.9.9',
                                   HTTP_X_FORWARDED_FOR='3.3.3.3')
        self.assertEqual(get_ip_client(request), '2.2.2.2')

    def test_falls_back_to_x_forwarded_for(self):
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='3.3.3.3, 8.8.8.8')
        self.assertEqual(get_ip_client(request), '3.3.3.3')

    def test_falls_back_to_remote_addr(self):
        request = self.factory.get('/', REMOTE_ADDR='4.4.4.4')
        self.assertEqual(get_ip_client(request), '4.4.4.4')
