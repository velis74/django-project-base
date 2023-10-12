import swapper
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from django_project_base.base.event import ProjectSettingConfirmedEvent


class Command(BaseCommand):
    help = "Lists pending project settings. Example:  python manage.py list_pending_settings 2"

    def add_arguments(self, parser) -> None:
        parser.add_argument("project-id", type=str, help="Project identifier")

    def handle(self, *args, **options):
        project = get_object_or_404(swapper.load_model("django_project_base", "Project"), pk=str(options["project-id"]))
        setting = get_object_or_404(
            swapper.load_model("django_project_base", "ProjectSettings"),
            project=project,
            name=str(options["setting-name"]),
        )
        ProjectSettingConfirmedEvent(user=None).trigger(payload=setting)
        # TODO: send email when owner is known
        # SystemEMailNotification(
        #     message=DjangoProjectBaseMessage(
        #         subject=f"{__('Project setting confirmed')}",
        #         body=f"{__('Setting')} {setting.name} {__('in project')} "
        #         f"{project.name} {__('has been confirmed and is now active.')}",
        #         footer="",
        #         content_type=DjangoProjectBaseMessage.PLAIN_TEXT,
        #     ),
        #     recipients=[],  # TODO: find project owner
        #     user=None,  # TODO: find project owner
        # ).send()
        return "ok"
