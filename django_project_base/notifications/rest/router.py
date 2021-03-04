from django_project_base.base.rest.router import Router
from django_project_base.notifications.rest.maintenance_notification import MaintenanceNotificationViewset


class NotificationsRouter(Router):
    pass


notifications_router: NotificationsRouter = NotificationsRouter()

notifications_router.register(r'maintenance-notification', MaintenanceNotificationViewset,
                              basename='maintenance-notification')
