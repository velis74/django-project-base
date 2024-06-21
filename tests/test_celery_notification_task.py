from unittest.mock import patch

from django.test import TestCase

from django_project_base.celery.background_tasks.notification_tasks import SendNotificationTask


class SendNotificationTaskTest(TestCase):

    def setUp(self):
        self.task = SendNotificationTask()

    @patch('django_project_base.notifications.base.send_notification_service.SendNotificationService.make_send')
    @patch('django_project_base.celery.background_tasks.notification_tasks.SendNotificationTask.apply_async')
    def test_send_notification_task(self, mock_apply_async, mock_make_send):
        mock_make_send.result = None
        self.task.apply((None, None))
