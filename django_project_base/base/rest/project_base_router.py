from rest_framework import routers


class ProjectBaseRouter(routers.DefaultRouter):
    def extend(self, router):
        self.registry.extend(router.registry)
