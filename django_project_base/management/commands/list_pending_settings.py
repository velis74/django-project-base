import json

import swapper

from django.conf import settings

from django.core.management import BaseCommand

from django_project_base.notifications import send_notification, CONTENT_TYPE_HTML


class Command(BaseCommand):
    help = "Lists pending project settings. Example:  python manage.py list_pending_settings"

    def handle(self, *args, **options):
        result = dict()
        for project in swapper.load_model("django_project_base", "Project").objects.all():
            for setting in (
                swapper.load_model("django_project_base", "ProjectSettings")
                .objects.filter(project=project, pending_value__isnull=False)
                .exclude(pending_value="")
            ):
                if project.name not in result:
                    result[project.name] = {}
                result[project.name][setting.name] = {
                    "value": setting.python_value,
                    "pending_value": setting.python_pending_value,
                }

        if (to := getattr(settings, "ADMINS", getattr(settings, "MANAGERS", []))) and result:
            send_notification(
                subject="Pending settings report",
                body=json.dumps(result),
                content_type=CONTENT_TYPE_HTML,
                recipients=list(to),
            )

        self.stdout.write(self.style.WARNING(result))
