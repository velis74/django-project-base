from rest_framework import status
from rest_framework.exceptions import APIException


class LicenseActionNotImplementedException(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED


class InviteActionNotImplementedException(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
