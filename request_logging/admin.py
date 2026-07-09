from django.contrib import admin
import json
from django.utils.html import format_html

from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('client_ip', 'user_id', 'hostname', 'method', 'path', 'response_code', 'display_response_time',
                    'request_at')
    search_fields = ('client_ip', 'path', 'user__username')
    search_help_text = 'Search by client ip, path or username'
    show_full_result_count = False

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'user', 'client_ip', 'display_headers',
                )
            }
        ),
        (
            'Request',
            {
                'fields': (
                    'hostname', ('method', 'path'), 'display_request_params',
                    'request_at',
                )
            }
        ),
        (
            'Response',
            {
                'fields': (
                    'response_code', 'display_response_time'
                )
            }
        ),
    )

    @admin.display(description='response time', ordering='response_time')
    def display_response_time(self, obj):
        if obj.response_time:
            return "{:.3f}".format(obj.response_time)
        return self.get_empty_value_display()

    @admin.display(description='request params')
    def display_request_params(self, obj):
        return self.format_json(obj.request_params) if obj.request_params else '-'
    
    @admin.display(description='headers')
    def display_headers(self, obj):
        return self.format_json(obj.headers) if obj.headers else '-'

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def format_json(self, content, indent=4):
        content = json.dumps(content, indent=indent)
        return format_html('<pre>{}</pre>', content)
