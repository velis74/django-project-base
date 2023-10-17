from typing import List

from django.core.management import BaseCommand

from django_project_base.profiling.middleware import ProfileRequest


class PerformanceCommand(BaseCommand):
    def execute(self, *args, **options):
        param_names: list = list(
            filter(
                lambda o: o
                and o
                not in ("pythonpath", "no_color", "force_color", "verbosity", "skip_checks", "traceback", "settings"),
                options,
            )
        )
        command_class_data: List[str] = str(self.__class__).split(".")
        command_name: str = command_class_data[len(command_class_data) - 2]
        name: str = "%s_%s " % ("manage_command", command_name)
        for param in param_names:
            name += "%s=%s " % (param, options.get(param))

        with ProfileRequest(
            {"REQUEST_METHOD": "GET", "HTTP_HOST": "", "QUERY_STRING": "", "PATH_INFO": name},
            super().execute,
            args,
            options,
        ) as pr:
            return pr.response
