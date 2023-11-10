import datetime

from django.core.cache import cache

from django_project_base.celery.celery import app
from django_project_base.notifications.base.send_notification_mixin import SendNotificationMixin
from django_project_base.notifications.models import DjangoProjectBaseNotification


class BeatTask(app.Task):
    name = "background_tasks.notification_tasks.beat_task.beat_task"

    max_retries = 0
    time_limit = 1800

    run_ck = "run-scheduled-send-notifications-send-at"

    def _clear_in_progress_status(self):
        cache.set(self.run_ck, False)

    def run(self):
        with open("/tmp/beat.txt", "a") as f:
            f.write(f"\n RUN \n")
        if cache.get(self.run_ck):
            return
        with open("/tmp/beat.txt", "a") as f:
            f.write(f"\n IN RUN \n")
        cache.set(self.run_ck, True, timeout=None)
        now_ts = datetime.datetime.now().timestamp() + 300
        for notification in DjangoProjectBaseNotification.objects.filter(
            send_at__isnull=False, sent_at__isnull=True, send_at__lte=now_ts
        ):
            with open("/tmp/beat.txt", "a") as f:
                f.write(f"\n {notification} \n")
            notification.email_fallback = notification.extra_data["mail-fallback"]
            notification.user = notification.extra_data["user"]
            notification.recipients_list = notification.extra_data["recipients-list"]
            notification.sender = notification.extra_data["sender"]
            SendNotificationMixin().make_send(notification, notification.extra_data or {}, resend=False)
        self._clear_in_progress_status()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self._clear_in_progress_status()
        import logging

        logger = logging.getLogger("django")
        msg = f"""

                CELERY DEVICE TASK FAILURE
                Exception: {str(exc)}
                Task id: {str(task_id)}
                Args: {str(args)}
                Kwargs: {str(kwargs)}
                EInfo: {str(einfo)}
                """
        with open("/tmp/beat.txt", "a") as f:
            f.write(f"\n msg \n")
        logger.exception(msg)


beat_task = app.register_task(BeatTask())
