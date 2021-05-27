from django_project_base.notifications.constants import NOTIFICATIONS_APP_ID

from .router import notifications_router

default_app_config = '%s.apps.DjangoProjectBaseNotifyConfig' % NOTIFICATIONS_APP_ID
