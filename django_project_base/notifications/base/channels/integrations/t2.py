import json

from math import ceil
from typing import Optional, Union

import requests
import swapper

from django.conf import Settings
from django.contrib.auth import get_user_model
from requests.auth import HTTPBasicAuth
from rest_framework.status import is_success

from django_project_base.celery.settings import NOTIFICATION_QUEABLE_HARD_TIME_LIMIT
from django_project_base.notifications.base.channels.channel import Recipient
from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.models import DeliveryReport, DjangoProjectBaseNotification

# -*- coding: utf8 -*-
"""
Created on Jul 10, 2016
@author: Dayo
"""


class SMSCounter(object):
    # https: // raw.githubusercontent.com / dedayoa / sms - counter - python / master / sms_counter / main.py
    GSM_7BIT = "GSM_7BIT"
    GSM_7BIT_EX = "GSM_7BIT_EX"
    UTF16 = "UTF16"
    GSM_7BIT_LEN = GSM_7BIT_EX_LEN = 160
    UTF16_LEN = 70
    GSM_7BIT_LEN_MULTIPART = GSM_7BIT_EX_LEN_MULTIPART = 153
    UTF16_LEN_MULTIPART = 67

    @classmethod
    def _get_gsm_7bit_map(cls):
        gsm_7bit_map = [
            10,
            12,
            13,
            32,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79,
            80,
            81,
            82,
            83,
            84,
            85,
            86,
            87,
            88,
            89,
            90,
            92,
            95,
            97,
            98,
            99,
            100,
            101,
            102,
            103,
            104,
            105,
            106,
            107,
            108,
            109,
            110,
            111,
            112,
            113,
            114,
            115,
            116,
            117,
            118,
            119,
            120,
            121,
            122,
            161,
            163,
            164,
            165,
            191,
            196,
            197,
            198,
            199,
            201,
            209,
            214,
            216,
            220,
            223,
            224,
            228,
            229,
            230,
            232,
            233,
            236,
            241,
            242,
            246,
            248,
            249,
            252,
            915,
            916,
            920,
            923,
            926,
            928,
            931,
            934,
            936,
            937,
        ]
        return gsm_7bit_map

    @classmethod
    def _get_added_gsm_7bit_ex_map(cls):
        added_gsm_7bit_ex_map = [12, 91, 92, 93, 94, 123, 124, 125, 126, 8364]
        return added_gsm_7bit_ex_map

    @classmethod
    def _text_to_unicode_pointcode_list(cls, plaintext):
        textlist = []
        for stg in plaintext:
            textlist.append(ord(stg))
        return textlist

    @classmethod
    def _detect_encoding(cls, plaintext):
        rf = cls._text_to_unicode_pointcode_list(plaintext)

        non_gsm_7bit_chars = set(rf) - set(cls._get_gsm_7bit_map())
        if not non_gsm_7bit_chars:
            return cls.GSM_7BIT

        non_gsm_7bit_ex_chars = non_gsm_7bit_chars - set(cls._get_added_gsm_7bit_ex_map())
        if not non_gsm_7bit_ex_chars:
            return cls.GSM_7BIT_EX

        return cls.UTF16

    @classmethod
    def count(cls, plaintext):
        textlist = cls._text_to_unicode_pointcode_list(plaintext)

        encoding = cls._detect_encoding(plaintext)
        length = len(textlist)

        if encoding == cls.GSM_7BIT_EX:
            exchars = [c for c in textlist if c in cls._get_added_gsm_7bit_ex_map()]
            lengthexchars = len(exchars)
            length += lengthexchars

        if encoding == cls.GSM_7BIT:
            permessage = cls.GSM_7BIT_LEN
            if length > cls.GSM_7BIT_LEN:
                permessage = cls.GSM_7BIT_LEN_MULTIPART
        elif encoding == cls.GSM_7BIT_EX:
            permessage = cls.GSM_7BIT_EX_LEN
            if length > cls.GSM_7BIT_EX_LEN:
                permessage = cls.GSM_7BIT_EX_LEN_MULTIPART
        else:
            permessage = cls.UTF16_LEN
            if length > cls.UTF16_LEN:
                permessage = cls.UTF16_LEN_MULTIPART

        # Convert the dividend to fload so the division will be a float number
        # and then convert the ceil result to int
        # since python 2.7 return a float
        messages = int(ceil(length / float(permessage)))
        remaining = (permessage * messages) - length

        returnset = {
            "encoding": encoding,
            "length": length,
            "per_message": permessage,
            "remaining": remaining,
            "messages": messages,
        }

        return returnset

    @classmethod
    def truncate(cls, plaintext, limitsms):
        count = cls.count(plaintext)

        if count.messages <= limitsms:
            return plaintext

        if count.encoding == "UTF16":
            limit = cls.UTF16_LEN

            if limitsms > 2:
                limit = cls.UTF16_LEN_MULTIPART

        if count.encoding != "UTF16":
            limit = cls.GSM_7BIT_LEN

            if limitsms > 2:
                limit = cls.GSM_7BIT_LEN_MULTIPART

        while True:
            text = plaintext[0 : limit * limitsms]  # noqa:  E203
            count = cls.count(plaintext)

            limit = limit - 1

            if count.messages < limitsms:
                break

        return text


class T2(ProviderIntegration):
    sms_from_number: dict
    username: str
    password: str

    endpoint_one = "send_sms"
    endpoint_multi = "send_multiple_sms"
    settings: object

    url = ""

    def __init__(self) -> None:
        super().__init__(settings=object())

    def ensure_credentials(self, settings: Optional[Settings] = None):
        if settings and getattr(settings, "TESTING", False):
            return
        self.username = getattr(settings, "NOTIFICATIONS_T2_USERNAME", None)
        self.password = getattr(settings, "NOTIFICATIONS_T2_PASSWORD", None)
        self.url = getattr(settings, "NOTIFICATIONS_SMS_API_URL", None)
        self.settings = settings
        assert self.username, "NOTIFICATIONS_T2_USERNAME is required"
        assert self.password, "NOTIFICATIONS_T2_PASSWORD is required"
        assert len(self.url) > 0, "NOTIFICATIONS_T2_PASSWORD is required"

    def client_send(self, sender: str, recipient: Recipient, msg: str, dlr_id: str):
        if not recipient.phone_number:
            return
        basic_auth = HTTPBasicAuth(self.username, self.password)
        response = requests.post(
            f"{self.url}{self.endpoint_one}",
            auth=basic_auth,
            json={"from_number": sender, "to_number": recipient.phone_number, "message": msg, "guid": dlr_id},
            verify=False,
            headers={"Content-Type": "application/json"},
            timeout=int(0.8 * NOTIFICATION_QUEABLE_HARD_TIME_LIMIT),
        )

        self.validate_send(response)

    def validate_send(self, response: object):
        assert response
        is_success(response.status_code)
        response_data = response.json()
        assert str(response_data["error_code"]) == "0"

    def parse_delivery_report(self, dlr: DeliveryReport):
        payload = json.loads(getattr(dlr, "payload", "{}"))
        dlr.status = (
            DeliveryReport.Status.DELIVERED
            if str(payload.get("status", "-1")) == str(DeliveryReport.Status.DELIVERED.value)
            else DeliveryReport.Status.NOT_DELIVERED
        )
        dlr.save(update_fields=["status"])

    @property
    def delivery_report_username_setting_name(self) -> str:
        return "t2-sms-dlr-user"

    @property
    def delivery_report_password_setting_name(self) -> str:
        return "t2-sms-dlr-password"

    def ensure_dlr_user(self, project_slug: str):
        if project_slug and (
            project := swapper.load_model("django_project_base", "Project").objects.filter(slug=project_slug).first()
        ):
            project_settings_model = swapper.load_model("django_project_base", "ProjectSettings")

            username_setting = project_settings_model.objects.filter(
                name=self.delivery_report_username_setting_name, project=project
            ).first()

            password_setting = project_settings_model.objects.filter(
                name=self.delivery_report_password_setting_name, project=project
            ).first()

            assert username_setting
            assert password_setting

            user, user_created = get_user_model().objects.get_or_create(
                username=username_setting.python_value,
                email="klemen.spruk@velis.si",
                first_name=username_setting.python_value,
                last_name=username_setting.python_value,
            )
            if user_created:
                user.set_password(password_setting.python_value)
                user.save()

            ProjectMember = swapper.load_model("django_project_base", "ProjectMember")
            ProjectMember.objects.get_or_create(member=user.userprofile, project=project)

    def enqueue_dlr_request(self, pk: str):
        pass

    def get_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return self._get_sms_message(notification)

    def _get_sms_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return super()._get_sms_message(notification)
