from typing import List

from django.core.cache import cache


class PhoneNumberParser:
    @staticmethod
    def is_allowed(phone_number: str) -> bool:
        if (allowed_function := cache.get("IS_PHONE_NUMBER_ALLOWED_FUNCTION".lower(), "")) and allowed_function:
            from dill import loads as dloads

            return dloads(allowed_function)(phone_number)
        return phone_number and len(phone_number) >= 8

    @staticmethod
    def valid_phone_numbers(candidates: List[str]) -> List[str]:
        valid: List[str] = []
        for number in candidates:
            if not PhoneNumberParser.is_allowed(number):
                continue
            if number.startswith("+"):
                valid.append(number.lstrip("+"))
                continue
            if number.startswith("00"):
                valid.append(number.lstrip("00"))
                continue
            valid.append(number)
        return valid

    @staticmethod
    # TODO: SLOVENIA????????
    def ensure_country_code_slovenia(candidates: List[str]) -> List[str]:
        valid: List[str] = []
        for number in candidates:
            if number.startswith("+"):
                valid.append(number)
                continue
            if number.startswith("00"):
                nm = number.lstrip("00")
                valid.append(f"+{nm}")
                continue
            if number.startswith("0"):
                nm = number.lstrip("0")
                valid.append(f"+386{nm}")
                continue
            if number.startswith("386"):
                valid.append(f"+{number}")
                continue
            valid.append(f"+386{number}")
        return valid
