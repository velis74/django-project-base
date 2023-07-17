from rest_framework.request import Request
from rest_registration.notifications import send_verification_notification
from rest_registration.signers.register_email import RegisterEmailSigner
from rest_registration.utils.users import get_user_verification_id
from rest_registration.verification_notifications import _get_email_template_config_data

from django_project_base.notifications.base.email_notification import EMailNotification
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.models import DjangoProjectBaseMessage
from django.utils.translation import gettext as __


class SendResetPasswordVerificationEmailService:
    @staticmethod
    def send_reset_password_verification_email(
        request: Request, user: "AbstractBaseUser", email: str, email_already_used: bool = False
    ) -> None:
        signer = RegisterEmailSigner(
            {
                "user_id": get_user_verification_id(user),
                "email": email,
            },
            request=request,
        )
        notification_data = {
            "params_signer": signer,
            "email_already_used": email_already_used,
        }
        template_config_data = _get_email_template_config_data(
            request, user, NotificationType.REGISTER_EMAIL_VERIFICATION
        )
        send_verification_notification(
            NotificationType.REGISTER_EMAIL_VERIFICATION,
            user,
            notification_data,
            template_config_data,
            custom_user_address=email,
        )
        EMailNotification(
            message=DjangoProjectBaseMessage(
                subject=__("Your account was created for you"),
                body="",
                footer="",
                content_type=DjangoProjectBaseMessage.HTML,
            ),
            persist=True,
            level=NotificationLevel.INFO,
            type=NotificationType.STANDARD,
            recipients=[user.pk],
        ).send()
