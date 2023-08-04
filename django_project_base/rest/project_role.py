from typing import Optional

import swapper
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from dynamicforms import fields
from dynamicforms.serializers import ModelSerializer
from dynamicforms.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError

from django_project_base.base.models import BaseProject


class ProjectRole:
    delimiter = "§"


class ProjectRoleSerializer(ModelSerializer):
    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        if self.instance:
            project = self.instance.name.split(ProjectRole.delimiter)[0]
            internal_value["name"] = f'{project}{ProjectRole.delimiter}{internal_value["name"]}'
        else:
            if not internal_value.get("project"):
                raise ValidationError(dict(project=[_("Project is required")]))
            internal_value["name"] = f'{internal_value["project"]}{ProjectRole.delimiter}{internal_value["name"]}'
        internal_value.pop("project", None)
        return internal_value

    def to_representation(self, instance, row_data=None):
        project_role = super().to_representation(instance, row_data)
        project_role["name"] = project_role["name"].split(ProjectRole.delimiter)[1]
        return project_role

    project = fields.CharField(max_length=512, write_only=True, required=False)

    class Meta:
        model = Group
        exclude = ()


class ProjectRoleViewSet(ModelViewSet):
    serializer_class = ProjectRoleSerializer

    def __get_project(self) -> Optional[BaseProject]:
        request_project_attr: str = settings.DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES.get("project", {}).get(
            "value_name"
        )
        project_model = swapper.load_model("django_project_base", "Project")
        if request_project_attr:
            project = getattr(self.request, request_project_attr, None)
            if project:
                try:
                    return project_model.objects.prefetch_related("owner").get(slug=project)
                except project_model.DoesNotExist:
                    pass

        project = self.request.GET.get("project", "")
        if project:
            try:
                return project_model.objects.prefetch_related("owner").get(pk=project)
            except Model.DoesNotExist:
                pass

        return None

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.serializer_class.Meta.model.objects.all()
        if self.action == "list":
            project: BaseProject = self.__get_project()
            if project and project.owner_id == self.request.user.id:
                return self.serializer_class.Meta.model.objects.filter(
                    name__startswith=f"{project.pk}{ProjectRole.delimiter}"
                )
            return self.serializer_class.Meta.model.objects.none()

        try:
            role: Group = get_object_or_404(
                Group, **{self.lookup_field: self.kwargs[self.lookup_url_kwarg or self.lookup_field]}
            )
            if ProjectRole.delimiter in role.name:
                project_pk: str = role.name.split(ProjectRole.delimiter)[0]
                project: BaseProject = (
                    swapper.load_model("django_project_base", "Project").objects.filter(pk=project_pk).first()
                )
                if project and project.owner_id == self.request.user.userprofile.pk:
                    return self.serializer_class.Meta.model.objects.filter(
                        name__startswith=f"{project_pk}{ProjectRole.delimiter}"
                    )
        except:
            pass

        return self.serializer_class.Meta.model.objects.none()
