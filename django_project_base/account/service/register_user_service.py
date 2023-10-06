from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as __
from natural.date import compress
from rest_framework.request import Request

from django_project_base.account.constants import REGISTER_USER_ACCOUNT_VERIFICATION_CODE
from django_project_base.notifications.email_notification import EMailNotification
from django_project_base.notifications.models import DjangoProjectBaseMessage


def send_register_verification_email_notification(
    request: Request,
    user,
) -> None:
    code_ck = REGISTER_USER_ACCOUNT_VERIFICATION_CODE + "SESSION NEKAJ"
    code = get_random_string(length=6)
    cache.set(code_ck, code, timeout=settings.CONFIRMATION_CODE_TIMEOUT)

    EMailNotification(
        message=DjangoProjectBaseMessage(
            subject=f"{__('Account confirmation for')} {request.META['HTTP_HOST']}",
            body=f"{__('You or someone acting as you registered an account at')} "
            f"{request.META['HTTP_HOST']}. "
            f"\n\n{__('Your verification code is')}: "
            f"{code} \n\n {__('Code is valid for')} {compress(settings.CONFIRMATION_CODE_TIMEOUT)}.\n\n"
            f"{__('If this was not you or it was unintentional, you may safely ignore this message.')}",
            footer="",
            content_type=DjangoProjectBaseMessage.PLAIN_TEXT,
        ),
        raw_recipents=[user.pk],
        persist=True,
        recipients=[user.pk],
        user=user.pk,
        project=None,
    ).send()
