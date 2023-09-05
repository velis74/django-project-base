from typing import List, Optional, Union

from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import OperandHolder
from rest_framework.routers import DefaultRouter

from django_project_base.rest.project import ProjectSettingsViewSet, ProjectViewSet
from django_project_base.rest.project_role import ProjectRoleViewSet


def filter_rest_documentation_endpoints(endpoints: list) -> list:
    _endpoints: list = []
    for path_, path_regex, method, callback in endpoints:
        module: str = getattr(getattr(callback, "view_class", object()), "__module__", "")
        exclude: bool = "profile" in path_ and "rest_registration" in module
        if not exclude:
            _endpoints.append((path_, path_regex, method, callback))
    return _endpoints


def postprocess_rest_documentation(result, generator, request, public):
    def get_endpoint_view_function(method: str, name: str) -> Optional[object]:
        return next(
            filter(lambda e: len(e) > 3 and name in e[0] and method.lower() == e[2].lower(), generator.endpoints), None
        )

    def parse_operand_holder(holder: Union[OperandHolder, str]) -> str:
        # parse permissions like permission_classes=[IsAuthenticated | ReadOnly | ReadOnlyX]
        perm = []
        if isinstance(holder, str):
            return holder
        if isinstance(holder, OperandHolder):
            oper = ""
            p_list = []
            for op in filter(lambda o: o.endswith("_class"), dir(holder)):
                _cl = getattr(holder, op, None)
                if _cl:
                    if isinstance(_cl, OperandHolder):
                        p_list.append(parse_operand_holder(_cl))
                    else:
                        name = _cl.__name__
                        if "operator" in op:
                            oper = name
                        else:
                            p_list.append(name)
            if len(p_list) == 2 and oper:
                perm.append(f"({p_list[0]} {oper} {p_list[1]})")
            else:
                perm.append(next(iter(p_list), ""))
        return ", ".join(perm).rstrip(", ")

    def format_permission_classes(classes: List[object]) -> str:
        _classes: List[str] = []
        for cl in classes:
            if getattr(cl, "__name__", None) and cl.__name__ != "AllowAny":
                _classes.append(cl.__name__)
            elif isinstance(cl, OperandHolder):
                _classes.append(parse_operand_holder(cl))
        if not _classes:
            return ""
        return f'{_("Special permissions")}: {", ".join(_classes).rstrip(", ")}'

    for path_name, path in result.get("paths", {}).items():
        for method, data in path.items():
            try:
                view: Optional[tuple] = get_endpoint_view_function(method=method, name=path_name)
                if view:
                    _view = view[3]
                    txt: str = format_permission_classes(
                        getattr(_view, "initkwargs", {}).get("permission_classes", [])
                    ) or format_permission_classes(getattr(getattr(_view, "cls", object()), "permission_classes", []))
                    if not txt:
                        continue
                    description: str = data.get("description", "")
                    description = f"{description}\n\n{txt}"
                    data["description"] = description
            except:
                pass
    return result


class RestRouter(DefaultRouter):
    pass


# TODO: this is wrong, the location of this router. Obviously, this is a project router, so it belongs
#  to the project submodule. same goes for the rest submodule: it contains project-related stuff
django_project_base_router = RestRouter(trailing_slash=False)
django_project_base_router.register(r"project", ProjectViewSet, basename="project-base-project")
django_project_base_router.register(r"project-role", ProjectRoleViewSet, basename="project-role")
django_project_base_router.register(r"project-settings", ProjectSettingsViewSet, basename="project-settings")
