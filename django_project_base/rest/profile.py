from django_project_base.base.rest.project_base_serializer import ProjectBaseSerializer
from django_project_base.base.rest.project_base_viewset import ProjectBaseViewSet
from django.apps import apps


class ProfileSerializer(ProjectBaseSerializer):
    class Meta:
        model = None
        exclude = ()


class ProfileViewSet(ProjectBaseViewSet):
    def get_queryset(self):
        return apps.get_model(
            self._get_application_name('DJANGO_PROJECT_BASE_PROFILE_MODEL'),
            self._get_model('DJANGO_PROJECT_BASE_PROFILE_MODEL')
        ).objects.all()

    def get_serializer_class(self):
        ProfileSerializer.Meta.model = apps.get_model(
            self._get_application_name('DJANGO_PROJECT_BASE_PROFILE_MODEL'),
            self._get_model('DJANGO_PROJECT_BASE_PROFILE_MODEL'))
        return ProfileSerializer
