import datetime
import logging

import swapper

from django.db import transaction

from django_project_base.profiling.performance_base_command import PerformanceCommand


class Command(PerformanceCommand):
    help = "Deletes users marked for deletion"

    def handle(self, *args, **options):
        for profile in swapper.load_model("django_project_base", "Profile").objects.filter(
            delete_at__isnull=False, delete_at__lt=datetime.datetime.now()
        ):
            with transaction.atomic():
                try:
                    profile.delete()
                except Exception as e:  # pragma: no cover
                    logging.getLogger(__name__).error(e)
        return "Finished deleting users"
