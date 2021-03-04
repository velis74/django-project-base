from rest_framework import routers


class Router(routers.DefaultRouter):
    def extend(self, router):
        self.registry.extend(router.registry)
