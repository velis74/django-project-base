import datetime
import logging
import uuid

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from django.conf import Settings, settings
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from django.utils.translation import gettext

from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.base.phone_number_parser import PhoneNumberParser
from django_project_base.notifications.models import (
    DeliveryReport,
    DjangoProjectBaseMessage,
    DjangoProjectBaseNotification,
)
from django_project_base.utils import get_pk_name


class Recipient:
    identifier: str
    phone_number: str
    email: str
    unique_attribute: str

    def __init__(
        self,
        identifier: str,
        phone_number: str,
        email: str,
        unique_attribute: str = "identifier",
        phone_number_validator=None,
    ) -> None:
        super().__init__()
        self.identifier = identifier
        self.phone_number = (
            next(
                iter(
                    PhoneNumberParser.valid_phone_numbers([phone_number], phone_number_validator)
                    if phone_number and len(phone_number)
                    else ""
                ),
                None,
            )
            or ""
        )
        self.email = email
        self.unique_attribute = unique_attribute

    def __eq__(self, __o: "Recipient") -> bool:
        return str(getattr(self, self.unique_attribute)) == str(getattr(__o, self.unique_attribute))

    def __hash__(self) -> int:
        return getattr(self, self.unique_attribute).__hash__()


class Channel(ABC):
    id = None

    name = ""

    notification_price = 0

    provider_setting_name = ""

    _provider: ProviderIntegration

    def _get_provider(self):
        return self._provider

    def _set_provider(self, val: ProviderIntegration):
        self._provider = val

    provider = property(_get_provider, _set_provider)

    def sender(self, notification: DjangoProjectBaseNotification) -> str:
        _sender = getattr(notification, "sender", {}).get(self.name)
        if not getattr(settings, "TESTING", False):
            assert _sender, "Notification sender is required"
        return _sender

    def _find_provider(
        self, settings: Optional[Settings], setting_name: str, exclude: Optional[List[str]] = None
    ) -> Optional[ProviderIntegration]:
        if exclude is None:
            exclude = []

        def get_first_provider(val: Union[str, List]):
            if val and isinstance(val, (list, tuple)):
                prov = next(filter(lambda i: i not in exclude, val), None)

                return import_string(prov)() if prov else None

            return import_string(val)() if val not in exclude and val else None

        if settings and getattr(settings, setting_name, None):
            return get_first_provider(getattr(settings, setting_name))
        return get_first_provider(getattr(settings or object(), setting_name, ""))

    def clean_recipients(self, recipients: List[Recipient]) -> List[Recipient]:
        return list(set(recipients))

    def create_delivery_report(
        self,
        notification: DjangoProjectBaseNotification,
        recipient: Recipient,
        pk: str,
        channel: Optional[str] = None,
        provider: Optional[str] = None,
        auxiliary_notification: Optional[uuid.UUID] = None,
    ) -> Union[DeliveryReport, None]:
        if notification._state.adding:
            # Če notification ni persisted, ni mogoče narediti delivery report
            return None

        return next(
            iter(
                DeliveryReport.objects.get_or_create(
                    notification=notification,
                    user_id=recipient.identifier,
                    channel=f"{self.__module__}.{self.__class__.__name__}" if not channel else channel,
                    provider=f"{self.provider.__module__}.{self.provider.__class__.__name__}"
                    if not provider
                    else provider,
                    pk=pk,
                    auxiliary_notification=auxiliary_notification,
                )
            ),
            None,
        )

    @abstractmethod
    def get_recipients(
        self, notification: DjangoProjectBaseNotification, unique_identifier="email", phone_number_validator=None
    ) -> List[Recipient]:
        rec_obj = notification.email_list
        if not rec_obj:
            rec_obj = notification.recipients_list
        if not rec_obj:
            att = ("email", "phone_number", get_pk_name(get_user_model()))
            rec_obj = [
                {k: v for k, v in profile.__dict__.items() if not k.startswith("_") and k in att}
                for profile in [
                    get_user_model().objects.get(pk=u).userprofile for u in notification.recipients.split(",")
                ]
            ]
        return [
            Recipient(
                identifier=u.get("id", "") or "",
                email=u.get("email", "") or "",
                phone_number=u.get("phone_number", "") or "",
                unique_attribute=unique_identifier,
                phone_number_validator=phone_number_validator,
            )
            for u in rec_obj
        ]

    def _make_send(self, notification_obj, rec_obj, message_str, dlr_pk) -> Tuple[Optional[DeliveryReport], bool]:
        do_send = True
        sent = False
        logger = logging.getLogger("django")
        try:
            dlr_exists = list(
                DeliveryReport.objects.filter(
                    notification=notification_obj,
                    user_id=rec_obj.identifier,
                    channel=f"{self.__module__}.{self.__class__.__name__}",
                    provider=f"{self.provider.__module__}.{self.provider.__class__.__name__}",
                )
            )
            if len(dlr_exists) > 1:
                raise Exception(f"{gettext('To many DLR exist.')} {notification_obj} {rec_obj}")
            if dlr_notification := next(iter(dlr_exists), None):
                dlr_pk = str(dlr_notification.pk)
                if dlr_notification.status == DeliveryReport.Status.DELIVERED:
                    do_send = False

            if getattr(settings, "TESTING", False):
                sent = True
            elif do_send:
                self.provider.client_send(self.sender(notification_obj), rec_obj, message_str, dlr_pk)
                sent = True
        except Exception as te:
            logger.exception(te)
            sent = False
        dlr_obj = None
        try:
            if sent and do_send:
                dlr_obj = self.create_delivery_report(notification_obj, rec_obj, dlr_pk)
            return dlr_obj, (sent and do_send)
        except Exception as de:
            logger.exception(de)
            return dlr_obj, (sent and do_send)

    def send(self, notification: DjangoProjectBaseNotification, extra_data, settings: Settings, **kwargs) -> int:
        logger = logging.getLogger("django")
        try:
            message = self.provider.get_message(notification)

            recipients = self.get_recipients(
                notification, phone_number_validator=getattr(settings, "IS_PHONE_NUMBER_ALLOWED_FUNCTION", None)
            )

            if not recipients:
                raise ValueError("No valid recipients")

            exclude_providers: List[str] = []
            sent_no = 0

            from django_project_base.notifications.base.channels.mail_channel import MailChannel

            mail_fallback = (
                MailChannel.name not in (notification.required_channels or "").split(",")
                and notification.email_fallback
            )

            from django_project_base.notifications.email_notification import EMailNotification

            for recipient in recipients:  # noqa: E203
                dlr__uuid = str(uuid.uuid4())
                was_sent = False
                try:
                    if (
                        self.provider.is_sms_provider
                        and not recipient.phone_number
                        and mail_fallback
                        and not notification.send_notification_sms
                    ):
                        try:
                            a_notification = EMailNotification(
                                message=DjangoProjectBaseMessage(
                                    subject=notification.message.subject,
                                    body=notification.message.body,
                                    footer=notification.message.footer,
                                    content_type=notification.message.content_type,
                                ),
                                raw_recipents=[
                                    recipient.identifier,
                                ],
                                project=notification.project_slug if notification.project_slug else None,
                                recipients=[
                                    recipient.identifier,
                                ],
                                a_sender=notification.sender,
                                a_extra_data=extra_data,
                                a_recipients_list=notification.recipients_list,
                                a_settings=settings,
                                delay=int(datetime.datetime.now().timestamp()),
                                user=extra_data["user"],
                            ).send()
                            self.create_delivery_report(
                                notification, recipient, dlr__uuid, auxiliary_notification=a_notification.pk
                            )
                            continue
                        except Exception as e:
                            logger.exception(e)
                            continue

                    while True:
                        _make_send = self._make_send(
                            notification_obj=notification, message_str=message, rec_obj=recipient, dlr_pk=dlr__uuid
                        )
                        if _make_send[1]:
                            dlr__uuid = str(_make_send[0].pk)
                            was_sent = True
                            break
                        else:
                            exclude_providers.append(f"{self.provider.__module__}.{self.provider.__class__.__name__}")
                            if next_provider := self._find_provider(
                                settings=settings,
                                setting_name=self.provider_setting_name,
                                exclude=exclude_providers,
                            ):
                                self.provider = next_provider
                            else:
                                break
                    if was_sent:
                        self.provider.enqueue_dlr_request(pk=dlr__uuid)
                        sent_no += 1
                except Exception as ge:
                    logger.exception(ge)

            if self.provider.is_sms_provider:
                from django_project_base.notifications.base.channels.integrations.t2 import SMSCounter

                sent_no = sent_no * SMSCounter.count(message)["messages"]
            return sent_no
        except Exception as e:
            logger.exception(e)
            raise e
