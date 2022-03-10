from typing import Optional

import swapper
from django.contrib.auth.models import Group
from dynamicforms import fields
from dynamicforms.serializers import ModelSerializer
from dynamicforms.viewsets import ModelViewSet
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ProjectRole:
    delimiter = '§'


class ProjectRoleSerializer(ModelSerializer):

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        if self.instance:
            project = self.instance.name.split(ProjectRole.delimiter)[0]
            internal_value['name'] = f'{project}{ProjectRole.delimiter}{internal_value["name"]}'
        else:
            if not internal_value.get("project"):
                raise ValidationError(dict(project=[_('required')]))
            internal_value['name'] = f'{internal_value["project"]}{ProjectRole.delimiter}{internal_value["name"]}'
        internal_value.pop('project', None)
        return internal_value

    def to_representation(self, instance, row_data=None):
        project_role = super().to_representation(instance, row_data)
        project_role['name'] = project_role['name'].split(ProjectRole.delimiter)[1]
        return project_role

    project = fields.CharField(max_length=512, write_only=True, required=False)

    class Meta:
        model = Group
        exclude = ()


class ProjectRoleViewSet(ModelViewSet):
    serializer_class = ProjectRoleSerializer

    def __get_project(self) -> Optional[str]:
        request_project_attr: str = settings.DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES.get('project', {}).get(
            'value_name')
        project_model = swapper.load_model('django_project_base', 'Project')
        if request_project_attr:
            project = getattr(self.request, request_project_attr, None)
            if project:
                try:
                    project_obj: Optional['Model'] = project_model.objects.get(slug=project)
                    return str(project_obj.pk)
                except:
                    pass
        project = self.request.GET.get('project', '')
        if project:
            try:
                project_obj: Optional['Model'] = project_model.objects.get(pk=project)
                return str(project_obj.pk)
            except:
                pass
        return None

    def get_queryset(self):
        project: Optional[str] = self.__get_project()
        if project:
            return self.serializer_class.Meta.model.objects.filter(name__startswith=f'{project}{ProjectRole.delimiter}')
        return self.serializer_class.Meta.model.objects.all()
