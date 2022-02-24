from rest_framework.routers import DefaultRouter

from django_project_base.notifications.rest.maintenance_notification import UsersMaintenanceNotificationViewset
from django_project_base.rest_config import REST_API_CONFIG


class NotificationsRouter(DefaultRouter):
    pass


notifications_router: NotificationsRouter = DefaultRouter()

notifications_router.register(r'%s' % REST_API_CONFIG.MaintenanceNotification.url, UsersMaintenanceNotificationViewset,
                              basename=REST_API_CONFIG.MaintenanceNotification.basename)
