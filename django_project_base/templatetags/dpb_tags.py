from django import template
from hijack.templatetags.hijack_tags import is_hijacked

register = template.Library()


@register.filter
def is_request_hijacked(request):
    return is_hijacked(request)
