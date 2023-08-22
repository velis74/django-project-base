import re

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from requests.auth import HTTPBasicAuth
from rest_framework import status

from django_project_base.celery.settings import NOTIFICATION_QUEABLE_HARD_TIME_LIMIT
from django_project_base.notifications.models import DjangoProjectBaseNotification

# -*- coding: utf8 -*-
"""
Created on Jul 10, 2016
@author: Dayo
"""
from math import ceil


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


class T2:
    sms_from_number: str
    username: str
    password: str

    endpoint_one = "send_sms"
    endpoint_multi = "send_multiple_sms"

    url = ""

    def __init__(self) -> None:
        super().__init__()

    def __ensure_credentials(self, extra_data):
        self.sms_from_number = getattr(settings, "SMS_SENDER", None)
        self.username = getattr(settings, "T2_USERNAME", None)
        self.password = getattr(settings, "T2_PASSWORD", None)
        self.url = getattr(settings, "SMS_API_URL", None)
        if stgs := extra_data.get("SETTINGS"):
            self.sms_from_number = getattr(stgs, "SMS_SENDER", None)
            self.username = getattr(stgs, "T2_USERNAME", None)
            self.password = getattr(stgs, "T2_PASSWORD", None)
            self.url = getattr(stgs, "SMS_API_URL", None)
        assert self.sms_from_number, "SMS_SENDER is required"
        assert self.username, "T2_USERNAME is required"
        assert self.password, "T2_PASSWORD is required"
        assert len(self.url) > 0, "T2_PASSWORD is required"

    def send(self, notification: DjangoProjectBaseNotification, **kwargs):
        self.__ensure_credentials(extra_data=kwargs.get("extra_data"))

        to = (
            [get_user_model().objects.get(pk=u).userprofile.phone_number for u in notification.recipients.split(",")]
            if not notification.recipients_list
            else [u.userprofile.phone_number for u in notification.recipients_list]
        )

        multi = len(to) > 1

        endpoint = self.endpoint_multi if multi else self.endpoint_one

        message = f"{notification.message.subject or ''}"

        if notification.message.subject:
            message += "\n\n"

        message += notification.message.body

        text_only = re.sub("[ \t]+", " ", strip_tags(message))
        # Strip single spaces in the beginning of each line
        message = text_only.replace("\n ", "\n").replace("\n", "\r\n").strip()

        basic_auth = HTTPBasicAuth(self.username, self.password)
        response = requests.post(
            f"{self.url}{endpoint}",
            auth=basic_auth,
            json={
                "from_number": self.sms_from_number,
                f"to_number{'s' if multi else ''}": to if multi else to[0],
                "message": message,
            },
            verify=False,
            headers={"Content-Type": "application/json"},
            timeout=int(0.8 * NOTIFICATION_QUEABLE_HARD_TIME_LIMIT),
        )
        # todo: what is t2 response code 200 or 201
        # todo: handle messages longer than 160 chars - same as on mars???
        if response.status_code != status.HTTP_200_OK:
            import logging

            logger = logging.getLogger("django")
            exc = Exception(f"Failed sms sending for notification {notification.pk}")
            logger.exception(exc)
            raise exc

        response_data = response.json()

        if str(response_data["error_code"]) != "0":
            import logging

            logger = logging.getLogger("django")
            exc = Exception(f"Faild sms sending for notification {notification.pk} \n\n {str(response_data)}")
            logger.exception(exc)
            raise exc
        return SMSCounter.count(message)["messages"]
