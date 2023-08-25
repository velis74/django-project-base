from typing import List


class PhoneNumberParser:
    @staticmethod
    def valid_phone_numbers(candidates: List[str]) -> List[str]:
        valid: List[str] = []
        for number in candidates:
            if number.startswith("+"):
                valid.append(number.lstrip("+"))
            if number.startswith("00"):
                valid.append(number.lstrip("00"))
                continue
            valid.append(number)
        return valid
