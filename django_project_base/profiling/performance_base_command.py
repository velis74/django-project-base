import json
import logging
import time
from os import path
from typing import List, Optional

from django.core.management import BaseCommand
from django_project_base.constants import MANAGEMENT_COMMANDS_PERFORMANCE_STATS_FILES_NAME


class PerformanceCommand(BaseCommand):
    file_path: str = '/tmp/' + MANAGEMENT_COMMANDS_PERFORMANCE_STATS_FILES_NAME + '_%s.txt'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def __read_performance_data(self, filename: str) -> Optional[dict]:
        _file: str = self.file_path % filename
        if not path.exists(_file):
            return None
        with open(_file, "r") as f:
            try:
                return json.loads(f.read())
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(e)
                return None

    def __write_performance_data(self, filename: str, perf_data: dict) -> None:
        with open(self.file_path % filename, "w") as f:
            f.write(json.dumps(perf_data) + "\n")

    def execute(self, *args, **options):
        timestamp_start: float = time.time()
        output = super().execute(*args, **options)
        timestamp_end: float = time.time()
        try:
            param_names: list = list(filter(lambda o: o and o not in (
                'pythonpath', 'no_color', 'force_color', 'verbosity', 'skip_checks', 'traceback', 'settings'), options))
            command_class_data: List[str] = str(self.__class__).split('.')
            command_name: str = command_class_data[len(command_class_data) - 2]
            ck: str = '%s_%s' % ('management_command', command_name)
            command_params: str = ''
            for param in param_names:
                ck += '_%s_%s' % (param, options.get(param))
                command_params += '%s=%s ' % (param, options.get(param))
            command_data: Optional[dict] = self.__read_performance_data(ck)
            if command_data is None:
                command_data = {}
            number_of_runs: int = command_data.get('number_of_runs', 0)
            command_run_total_time: float = command_data.get('total_time', 0)
            max_run_time: float = command_data.get('max_run_time', 0)
            current_run_time: float = timestamp_end - timestamp_start
            total_number_of_runs: int = number_of_runs + 1
            total_time: float = command_run_total_time + current_run_time
            self.__write_performance_data(ck, {
                'number_of_runs': total_number_of_runs,
                'total__run_time': round(total_time, 2),
                'max_run_time': round(max_run_time if current_run_time < max_run_time else current_run_time, 2),
                'avg_run_time': round(total_time / total_number_of_runs, 2),
                'name': command_name,
                'params': command_params,
            })
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(e)
        return output
