import functools

from django_project_base.profiling.middleware import ProfileRequest


def function_profiler(name=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            path_info = name or f"{func.__module__}.{func.__qualname__}"
            params = ""
            if args:
                params += f"args={args} "
            for key, value in kwargs.items():
                params += f"{key}={value} "
            with ProfileRequest(
                {"REQUEST_METHOD": "FUNCTION", "HTTP_HOST": "", "QUERY_STRING": params, "PATH_INFO": path_info},
                func,
                args,
                kwargs,
            ) as pr:
                return pr.response

        return wrapper

    return decorator
