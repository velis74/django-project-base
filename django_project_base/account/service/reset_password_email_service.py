from typing import Any, Dict

from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_registration.exceptions import UserNotFound
from rest_registration.notifications import send_verification_notification, create_verification_notification
from rest_registration.notifications.enums import NotificationType
from rest_registration.signers.reset_password import ResetPasswordSigner
from rest_registration.utils.users import get_user_verification_id
from rest_registration.verification_notifications import _get_email_template_config_data

from django_project_base.notifications.base.email_notification import EMailNotification
from django_project_base.notifications.base.enums import NotificationLevel
from django_project_base.notifications.base.enums import NotificationType as NotificationTypeDPB
from django_project_base.notifications.models import DjangoProjectBaseMessage
from django.utils.translation import gettext as __


def send_reset_password_verification_email(request: Request, user: "AbstractBaseUser") -> None:
    signer = ResetPasswordSigner(
        {
            "user_id": get_user_verification_id(user),
        },
        request=request,
    )

    template_config_data = _get_email_template_config_data(request, user, NotificationType.RESET_PASSWORD_VERIFICATION)
    notification_data = {
        "params_signer": signer,
    }

    notification = create_verification_notification(
        NotificationType.RESET_PASSWORD_VERIFICATION, user, user.email, notification_data, template_config_data
    )

    EMailNotification(
        message=DjangoProjectBaseMessage(
            subject=notification.subject,
            body=notification.body,
            footer="",
            content_type=DjangoProjectBaseMessage.HTML
            if notification.content_subtype != "plain"
            else DjangoProjectBaseMessage.PLAIN_TEXT,
        ),
        persist=True,
        level=NotificationLevel.INFO,
        type=NotificationTypeDPB.STANDARD,
        recipients=[user.pk],
    ).send()


def find_user_by_send_reset_password_link_data(data: Dict[str, Any], **kwargs: Any) -> "AbstractBaseUser":
    user = get_user_model().objects.filter(**kwargs["serializer"].validated_data).first()
    if user:
        return user
    raise UserNotFound()
