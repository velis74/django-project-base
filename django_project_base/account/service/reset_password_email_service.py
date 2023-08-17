from typing import Any, Dict

import swapper
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as __
from natural.date import compress
from rest_framework.request import Request
from rest_registration.exceptions import UserNotFound
from rest_registration.signers.reset_password import ResetPasswordSigner
from rest_registration.utils.users import get_user_verification_id

from django_project_base.account.constants import RESET_USER_PASSWORD_VERIFICATION_CODE
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType as NotificationTypeDPB
from django_project_base.notifications.email_notification import EMailNotification
from django_project_base.notifications.models import DjangoProjectBaseMessage


def send_reset_password_verification_email(request: Request, user, send=False) -> Dict:
    if not send:
        return {}
    signer = ResetPasswordSigner(
        {
            "user_id": get_user_verification_id(user),
        },
        request=request,
    )

    # template_config_data = _get_email_template_config_data(
    # request, user, NotificationType.RESET_PASSWORD_VERIFICATION)
    # notification_data = {
    #     "params_signer": signer,
    # }
    # notification = create_verification_notification(
    #     NotificationType.RESET_PASSWORD_VERIFICATION, user, user.email, notification_data, template_config_data
    # )

    code_ck = RESET_USER_PASSWORD_VERIFICATION_CODE + str(user.pk)
    code = get_random_string(length=6)
    cache.set(code_ck, code, timeout=settings.CONFIRMATION_CODE_TIMEOUT)

    EMailNotification(
        message=DjangoProjectBaseMessage(
            subject=f"{__('Password recovery for')} {request.META['HTTP_HOST']}",
            body=f"{__('You or someone acting as you requested a password reset for your account at')} "
            f"{request.META['HTTP_HOST']}. "
            f"\n\n{__('Your verification code is')}: "
            f"{code} \n\n {__('Code is valid for')} {compress(settings.CONFIRMATION_CODE_TIMEOUT)}.\n\n"
            f"{__('If this was not you or it was unintentional, you may safely ignore this message.')}",
            footer="",
            content_type=DjangoProjectBaseMessage.PLAIN_TEXT,
        ),
        raw_recipents=[user.pk],
        project=swapper.load_model("django_project_base", "Project").objects.get(slug=request.current_project_slug),
        persist=True,
        level=NotificationLevel.INFO,
        type=NotificationTypeDPB.STANDARD,
        recipients=[user.pk],
    ).send()

    return signer.get_signed_data()


def find_user_by_send_reset_password_link_data(data: Dict[str, Any], **kwargs: Any):
    query = kwargs["serializer"].validated_data if kwargs.get("serializer", None) else data
    user = get_user_model().objects.filter(**query).first()
    if user:
        return user
    raise UserNotFound()
