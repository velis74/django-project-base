from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as __
from natural.date import compress
from rest_framework.request import Request

from django_project_base.notifications import send_notification, CONTENT_TYPE_PLAIN_TEXT


def send_register_verification_email_notification(
    request: Request,
    user,
) -> None:
    if (flow_id := request.COOKIES.get("register-flow")) and (
        code := cache.get(f"register_verification_code:{flow_id}")
    ):
        send_notification(
            subject=f"{__('Account confirmation for')} {request.META['HTTP_HOST']}",
            body=f"{__('You or someone acting as you registered an account at')} "
            f"{request.META['HTTP_HOST']}. "
            f"\n\n{__('Your verification code is')}: "
            f"{code} \n\n {__('Code is valid for')} {compress(settings.CONFIRMATION_CODE_TIMEOUT)}.\n\n"
            f"{__('If this was not you or it was unintentional, you may safely ignore this message.')}",
            content_type=CONTENT_TYPE_PLAIN_TEXT,
            recipients=[user.pk],
            user=user.pk,
        )
