from rest_framework.routers import DefaultRouter

from django_project_base.notifications.rest.maintenance_notification import UsersMaintenanceNotificationViewset


class NotificationsRouter(DefaultRouter):
    pass


notifications_router: NotificationsRouter = DefaultRouter()

notifications_router.register(r'maintenance-notification', UsersMaintenanceNotificationViewset,
                              basename='maintenance-notification')
