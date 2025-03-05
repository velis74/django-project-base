import datetime

from typing import Any, Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from natural.date import compress
from rest_framework.request import Request
from rest_registration.exceptions import UserNotFound
from rest_registration.signers.reset_password import ResetPasswordSigner
from rest_registration.utils.users import get_user_verification_id

from django_project_base.account.constants import RESET_USER_PASSWORD_VERIFICATION_CODE
from django_project_base.notifications.email_notification import EMailNotification
from django_project_base.notifications.models import DjangoProjectBaseMessage


def send_reset_password_verification_email(request: Request, user, send=False, first_login=False) -> Dict:
    if not send:
        return {}
    signer = ResetPasswordSigner(
        {
            "user_id": get_user_verification_id(user),
        },
        request=request,
    )

    code_ck = RESET_USER_PASSWORD_VERIFICATION_CODE + str(user.pk)
    code = get_random_string(length=6)
    cache.set(code_ck, code, timeout=settings.CONFIRMATION_CODE_TIMEOUT)

    try:
        project = request.selected_project.slug
    except:
        project = None

    if first_login:
        subject = _('First login to %s') % request.META['HTTP_HOST']
        body = _("You or someone acting as you is logging to %s for the first time.") % request.META["HTTP_HOST"]
    else:
        subject = _('Password recovery for %s') % request.META['HTTP_HOST']
        body = (
            _("You or someone acting as you requested a password reset for your account at %s.")
            % request.META["HTTP_HOST"]
        )
    body += "\n\n%s: %s \n\n%s %s.\n\n%s" % (
        _("Your verification code is"),
        code,
        _("Code is valid for"),
        compress(settings.CONFIRMATION_CODE_TIMEOUT),
        _("If this was not you or it was unintentional, you may safely ignore this message."),
    )

    EMailNotification(
        message=DjangoProjectBaseMessage(
            subject=subject,
            body=body,
            footer="",
            content_type=DjangoProjectBaseMessage.PLAIN_TEXT,
        ),
        raw_recipents=[user.pk],
        project=project,
        delay=int(datetime.datetime.now().timestamp()),
        recipients=[user.pk],
        user=request.user.pk,
    ).send()

    return signer.get_signed_data()


def find_user_by_send_reset_password_link_data(data: Dict[str, Any], **kwargs: Any):
    query = kwargs["serializer"].validated_data if kwargs.get("serializer", None) else data
    user = get_user_model().objects.filter(**query).first()
    if user:
        return user
    raise UserNotFound()
