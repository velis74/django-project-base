import json

from typing import Optional

import social_core.backends.facebook
import social_core.backends.google
import social_core.backends.microsoft

from django.db import connection
from social_django.models import UserSocialAuth

from django_project_base.profiling.performance_base_command import PerformanceCommand


# This is not tested because there is no socialaccount model anymore
class Command(PerformanceCommand):  # pragma: no cover
    help = "Migrate social login data from allauth to social_core"

    provider_mapping: dict = {
        "google": social_core.backends.google.GoogleOAuth2.name,
        "facebook": social_core.backends.facebook.FacebookOAuth2.name,
        "azure": social_core.backends.microsoft.MicrosoftOAuth2.name,
    }

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("select user_id, provider, extra_data from socialaccount_socialaccount;")
            rows: list = cursor.fetchall()
            for row in rows:
                user_id: int = row[0]
                provider: str = row[1]
                extra_data: dict = json.loads(row[2]) if row[2] else {}
                user_email: Optional[str] = extra_data.get("email") or extra_data.get("mail")
                if user_email:
                    new_provider: str = self.provider_mapping.get(provider)
                    assert new_provider, "New social auth provider for %s is not defined" % provider
                    payload = {
                        "user_id": user_id,
                        "provider": new_provider,
                    }
                    social_auth_records_exists: bool = UserSocialAuth.objects.filter(**payload).exists()
                    if not social_auth_records_exists:
                        payload["uid"] = user_email
                        payload["extra_data"] = None
                        UserSocialAuth.objects.create(**payload)
        return "ok"
