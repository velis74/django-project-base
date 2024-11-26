import datetime
from datetime import timedelta

import swapper
from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import make_aware


class MgmtCmdDeleteUsersTest(TestCase):
    def test_call_command(self):
        profile = swapper.load_model("django_project_base", "Profile").objects
        no_delete = profile.create(first_name="John", last_name="Doe", username="JohnDoe")
        delete_in_future = profile.create(
            first_name="John",
            last_name="Pitt",
            username="JohnPitt",
            delete_at=make_aware(datetime.datetime.now()) + timedelta(days=1),
        )
        delete_in_past = profile.create(
            first_name="Johanna",
            last_name="Pitt",
            username="JohannaPitt",
            delete_at=make_aware(datetime.datetime.now()) - timedelta(minutes=1),
        )
        call_command("delete_users")
        profiles = swapper.load_model("django_project_base", "Profile").objects.values_list("id", flat=True)
        self.assertIn(no_delete.id, profiles)
        self.assertIn(delete_in_future.id, profiles)
        self.assertNotIn(delete_in_past.id, profiles)
