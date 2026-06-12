import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as __
from natural.date import compress
from rest_framework.request import Request

from django_project_base.notifications import send_notification, CONTENT_TYPE_PLAIN_TEXT

logger = logging.getLogger(__name__)


def send_register_verification_email_notification(
    request: Request,
    user,
) -> None:
    # _register_flow_id is set on the request before the event fires (cookie not yet in request.COOKIES)
    flow_id = getattr(request, "_register_flow_id", None) or request.COOKIES.get("register-flow")
    logger.info("send_register_verification_email_notification: user=%s flow_id=%s", getattr(user, 'pk', user), flow_id)
    if not flow_id:
        logger.warning("send_register_verification_email_notification: no register-flow id found, skipping")
        return
    code = cache.get(f"register_verification_code:{flow_id}")
    logger.info("send_register_verification_email_notification: cache key=register_verification_code:%s code_found=%s", flow_id, bool(code))
    if not code:
        logger.warning("send_register_verification_email_notification: no cache entry for flow_id=%s, skipping", flow_id)
        return
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
