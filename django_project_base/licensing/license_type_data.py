from enum import Enum


class LicenseType(Enum):
    EMAIL = "email"
    SMS = "sms"


class LicenseTypeData:
    price: float

    def __init__(self, price: float) -> None:
        self.price = price
