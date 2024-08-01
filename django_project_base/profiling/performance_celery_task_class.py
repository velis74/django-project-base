import celery

from django_project_base.profiling.performance_function_decorator import function_profiler


class PerformanceCeleryTask(celery.Task):
    def get_profiler_params(self):
        return dict()

    def __getattribute__(self, name):
        # Get the original attribute
        attr = super().__getattribute__(name)

        # If the attribute is a callable (i.e., a method), wrap it with the custom behavior
        if name == "run" and callable(attr):
            return function_profiler(**self.get_profiler_params())(attr)
        return attr
