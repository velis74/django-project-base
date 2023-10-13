import swapper
from django.core.management.base import BaseCommand


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
        # if to := getattr(settings, "ADMINS", getattr(settings, "MANAGERS", [])):
        # # TODO: SEND THIS AS SYSTEM MSG WHEN PR IS MERGED
        # EMailNotificationWithListOfEmails(
        #     message=DjangoProjectBaseMessage(
        #         subject=_("Pending settings report"),
        #         body=json.dumps(result),
        #         footer="",
        #         content_type=DjangoProjectBaseMessage.HTML,
        #     ),
        #     recipients=to,
        #     project=None,
        #     user=None,
        # ).send()
        self.stdout.write(self.style.WARNING(result))
