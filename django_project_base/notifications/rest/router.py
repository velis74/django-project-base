from django_project_base.base.rest.router import Router
from django_project_base.notifications.rest.maintenance_notification import UsersMaintenanceNotificationViewset


class NotificationsRouter(Router):
    pass


notifications_router: NotificationsRouter = NotificationsRouter()

notifications_router.register(r'maintenance-notification', UsersMaintenanceNotificationViewset,
                              basename='maintenance-notification')
