from typing import List, Optional

import requests
from django.conf import settings
from django.core.cache.backends.filebased import FileBasedCache
from rest_framework import status

country_holidays_storage: FileBasedCache = FileBasedCache(settings.DJANGO_PROJECT_BASE_COUNTRY_HOLIDAYS_CACHE_FOLDER, {
    'max_entries': 1000,
    'timeout': None,
})

holidays_api_url: str = 'https://date.nager.at/Api/v2/PublicHolidays/%d/%s'


def get_holidays(country_alpha_2_code: str, year: int) -> List[dict]:
    assert country_alpha_2_code and isinstance(country_alpha_2_code, str) and len(
        country_alpha_2_code) == 2, ValueError("Not valid country alpha 2 code")
    assert isinstance(year, int) and year > 1900, ValueError("Not a valid year")
    ck: str = f'country-holidays-{year}-{country_alpha_2_code}'
    cached_data: Optional[List[dict]] = country_holidays_storage.get(ck)
    if cached_data is not None:
        return cached_data
    response: requests.Response = requests.get(holidays_api_url % (year, country_alpha_2_code.upper()), timeout=6)
    assert response.status_code == status.HTTP_200_OK, "Error retrieving data"
    holidays_data: List[dict] = response.json()
    country_holidays_storage.set(ck, holidays_data, timeout=None)
    return holidays_data
