import functools

from celery import shared_task

from django_project_base.profiling.performance_function_decorator import function_profiler


def shared_task_profiler(*args, **kwargs):
    profiler_name = kwargs.pop("profiler_name", None)

    def decorator(func):
        profiled_func = function_profiler(name=profiler_name)(func)

        # Then, define a new function that applies shared_task to the wrapped function
        @shared_task(*args, **kwargs)
        @functools.wraps(profiled_func)
        def task_wrapper(*_args, **_kwargs):
            return profiled_func(*_args, **_kwargs)

        return task_wrapper

    return decorator
