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
        name: str = f"manage_command_{command_name}"
        params = ""
        if args:
            params += f"args={args} "
        for param in param_names:
            params += f"{param}={options.get(param)} "

        with ProfileRequest(
            {"REQUEST_METHOD": "MANAGEMENT_COMMAND", "HTTP_HOST": "", "QUERY_STRING": params, "PATH_INFO": name},
            super().execute,
            args,
            options,
        ) as pr:
            return pr.response
