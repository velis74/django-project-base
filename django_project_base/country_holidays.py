from typing import List, Optional

import requests

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from requests import Timeout
from rest_framework import status

holidays_api_url: str = "https://date.nager.at/Api/v3/PublicHolidays/%d/%s"


class RetrieveHolidaysException(Exception):
    pass


def get_holidays(country_alpha_2_code: str, year: int) -> List[dict]:
    try:
        assert country_alpha_2_code and isinstance(country_alpha_2_code, str) and len(country_alpha_2_code) == 2, _(
            "Not valid country alpha 2 code"
        )
        assert isinstance(year, int) and year > 1900, _("Not a valid year")
        ck: str = f"country-holidays-{year}-{country_alpha_2_code}"
        cached_data: Optional[List[dict]] = cache.get(ck)
        if cached_data is not None:
            return cached_data
        response: requests.Response = requests.get(holidays_api_url % (year, country_alpha_2_code.upper()), timeout=6)
        assert response.status_code == status.HTTP_200_OK, _("Error retrieving data")
        holidays_data: List[dict] = response.json()
        cache.set(ck, holidays_data, timeout=None)
        return holidays_data
    except (AssertionError, Timeout) as e:
        raise RetrieveHolidaysException(_("Error retrieving holidays: {}".format(e))) from None
