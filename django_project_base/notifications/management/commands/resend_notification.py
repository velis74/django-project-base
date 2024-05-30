from django.shortcuts import get_object_or_404

from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import DjangoProjectBaseNotification
from django_project_base.profiling.performance_base_command import PerformanceCommand


class Command(PerformanceCommand):
    help = 'Resends notification. Example:  python manage.py resend_notification "178a46c2-2aa3-4a33-bad6-9af2d76f6891" 2'  # noqa: E501

    def add_arguments(self, parser) -> None:
        parser.add_argument("notification", type=str, help="Notification identifier (uuid string).")
        parser.add_argument("user", type=str, help="User identifier (user sending notification).", nargs="?")

    def handle(self, *args, **options):
        Notification.resend(
            get_object_or_404(DjangoProjectBaseNotification, pk=str(options["notification"])), str(options["user"])
        )
        return "ok"
