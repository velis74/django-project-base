from typing import List


class PhoneNumberParser:
    @staticmethod
    def is_allowed(phone_number: str, allowed_validator=None) -> bool:
        if allowed_validator:
            return allowed_validator(phone_number)
        return phone_number and len(phone_number) >= 8

    @staticmethod
    def valid_phone_numbers(candidates: List[str], allowed_validator=None) -> List[str]:
        valid: List[str] = []
        for number in candidates:
            if not PhoneNumberParser.is_allowed(number, allowed_validator):
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
