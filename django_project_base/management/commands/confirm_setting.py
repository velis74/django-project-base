from gettext import gettext

import swapper

from django.shortcuts import get_object_or_404

from django_project_base.base.event import ProjectSettingConfirmedEvent
from django_project_base.notifications.email_notification import SystemEMailNotification
from django_project_base.notifications.models import DjangoProjectBaseMessage
from django_project_base.profiling.performance_base_command import PerformanceCommand


class Command(PerformanceCommand):
    help = "Confirms project setting. Example:  python manage.py confirm_setting 2 email-sender-id"

    def add_arguments(self, parser) -> None:
        parser.add_argument("project-id", type=str, help="Project identifier")
        parser.add_argument("setting-name", type=str, help="Setting name")

    def handle(self, *args, **options):
        project = get_object_or_404(swapper.load_model("django_project_base", "Project"), pk=str(options["project-id"]))
        setting = get_object_or_404(
            swapper.load_model("django_project_base", "ProjectSettings"),
            project=project,
            name=str(options["setting-name"]),
        )
        ProjectSettingConfirmedEvent(user=None).trigger(payload=setting)
        SystemEMailNotification(
            message=DjangoProjectBaseMessage(
                subject=f"{gettext('Project setting confirmed')}",
                body=f"{gettext('Setting')} {setting.name} {gettext('in project')} "
                f"{project.name} {gettext('has been confirmed and is now active.')}",
                footer="",
                content_type=DjangoProjectBaseMessage.PLAIN_TEXT,
            ),
            recipients=[],  # TODO: find project owner and send, when project owner is found use EmailNotification
            user=None,  # TODO: find project owner and send -> add .send()
        )
        return "ok"
