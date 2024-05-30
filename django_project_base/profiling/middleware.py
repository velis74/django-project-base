import glob
import importlib
import json
import os
import re
import socket
import threading
import time

from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.db import connections

from django_project_base.caching import CacheCounter
from django_project_base.caching.cache_queue import CacheQueue

DEFAULT_MAX_LOG_FILE_SIZE = 10000000
MAX_DATA_LOGGING_FILE_SIZE = 3000000

MATCH_DETAIL_QUERIES = re.compile(
    r"(rest/\w+)/((?:[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})|" r"(?:(?:[0-9a-f]{2}:){5}[0-9a-f]{2})|\d+)(/.*)?"
)


class ProfileRequest(object):
    response: object
    _start_time: tuple
    _end_time: tuple
    _process_function: callable
    _process_function_args: tuple
    _process_function_kwargs: dict
    _settings: dict
    _profile_path: str

    def __init__(
        self,
        settings: dict,
        process_function: callable,
        process_function_args: tuple,
        process_function_kwargs: dict,
    ):
        assert "REQUEST_METHOD" in settings
        assert "PATH_INFO" in settings
        settings.setdefault("QUERY_STRING", "")
        settings.setdefault("HTTP_HOST", socket.gethostname())
        self._settings = settings
        self._process_function = process_function
        self._process_function_args = process_function_args
        self._process_function_kwargs = process_function_kwargs

    def __enter__(self):
        # # Code to be executed for each request before
        # # the view (and later middleware) are called.
        tms = os.times()
        self._start_time = (int(time.time() * 1000), int(tms.user * 1000), int(tms.system * 1000))
        self._set_profiling_path(None, None)
        # # Get the response itself
        self.response = self._process_function(*self._process_function_args, **self._process_function_kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # # Code to be executed for each request/response after
        # # the view is called.
        tms = os.times()
        self._end_time = (int(time.time() * 1000), int(tms.user * 1000), int(tms.system * 1000))
        self._do_profile(self.response, self._start_time, self._end_time)

    def _set_profiling_path(self, path_info, query_string):
        threading.current_thread().profiling_path = (path_info, query_string)

    def _get_profiling_path(self) -> tuple:
        return threading.current_thread().profiling_path

    def _get_path_info(self, path: str, params: Optional[str] = None):
        original_path = path
        path = path.strip("/")
        if "robots.txt" in path:
            return "other"
        if any(x in path for x in (".php", ".map")):
            return "other"

        if MATCH_DETAIL_QUERIES.match(path):
            return MATCH_DETAIL_QUERIES.sub("\\1\\3", path)

        if path.startswith("configure_site") and "&type=" in (params or ""):
            pos = params.find("&type=")
            return path + "/" + params[pos + 6 : pos + 9]

        if getattr(settings, "PROFILER_PATH_TRANSFORM", None):
            split_module_path: list = settings.PROFILER_PATH_TRANSFORM.split(".")
            module: str = ".".join(split_module_path[: (len(split_module_path) - 1)])
            method: str = split_module_path[-1]
            path = getattr(importlib.import_module(module), method)(
                path, {"original_path": original_path, "params": params}
            )

        return path

    def _get_queries(self, response):
        try:
            query_list = []
            for c in connections:
                con = connections[c]
                con.force_debug_cursor = True
                query_list.append(con.queries)
            _queries = filter(lambda x: x, query_list)
            return [q for sublist in _queries for q in sublist]
        except Exception as e:
            return ["exception getting queries: " + str(e)]

    def _do_profile(self, response, start_time, end_time):
        try:
            locs = locals()
            if "PATH_INFO" in self._settings:
                _profiling_path: tuple = next(iter(self._get_profiling_path()), None)
                path_info = _profiling_path or self._get_path_info(
                    str(self._settings["PATH_INFO"]), str(self._settings["QUERY_STRING"])
                )
                if path_info:
                    duration = (end_time[0] - start_time[0], end_time[1] - start_time[1], end_time[2] - start_time[2])
                    if hasattr(settings, "PROFILER_LONG_RUNNING_TASK_THRESHOLD"):
                        if duration[0] > settings.PROFILER_LONG_RUNNING_TASK_THRESHOLD:
                            queries = self._get_queries(response)
                            r_data = {
                                "timestamp": end_time[0] / 1000,
                                "duration": duration[0],
                                "queries": queries,
                                "PATH_INFO": path_info,
                            }
                            r_data.update(
                                {i: str(self._settings[i]) for i in ("HTTP_HOST", "REQUEST_METHOD", "QUERY_STRING")}
                            )
                            cache_ptr = CacheCounter("long_running_cmds_pointer", timeout=86400).incr(start=-1) % 50

                            cache.set("long_running_cmds_data%d" % cache_ptr, r_data, timeout=86400)

                        r_data = [path_info, duration[0], duration[1], duration[2]]
                        last_hour_running_cmds_key = f"last_hour_running_cmds{int(time.time()) // 10}"
                        last_hour_running_cmds_queue = CacheQueue.get_cache_queue(
                            last_hour_running_cmds_key, timeout=3600
                        )
                        last_hour_running_cmds_queue.rpush(json.dumps(r_data))

                    req_data = dict(
                        code=getattr(response, "status_code", None),
                        method=self._settings["REQUEST_METHOD"],
                        duration=duration[0],
                        timestamp=end_time[0] / 1000,
                        path_info=path_info,
                        pid=os.getpid(),
                        raw_path_info=self._settings.get("PATH_INFO", None),
                    )
                    files = glob.glob("/tmp/wsgi_performance.txt.*")
                    if not files:
                        with open("/tmp/wsgi_performance.txt.1", "a") as f:
                            f.write(json.dumps(req_data) + "\n")
                        files = ["/tmp/wsgi_performance.txt.1"]
                    file_num_array = list(map(lambda r: int(r.split(".")[-1]), files))
                    max_file = max(file_num_array)
                    min_file = min(file_num_array)
                    if max_file > 3:
                        if os.path.exists("/tmp/wsgi_performance.txt.1"):
                            os.remove("/tmp/wsgi_performance.txt.1")
                        if os.path.exists("/tmp/wsgi_performance.txt.2"):
                            os.remove("/tmp/wsgi_performance.txt.2")
                        os.rename("/tmp/wsgi_performance.txt.%d" % max_file, "/tmp/wsgi_performance.txt.1")
                        os.rename("/tmp/wsgi_performance.txt.%d" % (max_file - 1), "/tmp/wsgi_performance.txt.2")
                        for ff in filter(lambda f: f and int(f.split(".")[-1]) not in [1, 2], files):
                            if os.path.exists(ff):
                                os.remove(ff)
                        files = glob.glob("/tmp/wsgi_performance.txt.*")
                    if not files:
                        with open("/tmp/wsgi_performance.txt.1", "a") as f:
                            f.write(json.dumps(req_data) + "\n")
                    else:
                        if os.path.getsize("/tmp/wsgi_performance.txt.%d" % max_file) > MAX_DATA_LOGGING_FILE_SIZE:
                            with open("/tmp/wsgi_performance.txt.%d" % (max_file + 1), "a") as f:
                                f.write(json.dumps(req_data) + "\n")
                        else:
                            with open("/tmp/wsgi_performance.txt.%d" % max_file, "a") as f:
                                f.write(json.dumps(req_data) + "\n")
        except Exception as exc:
            try:
                error_file = "/tmp/wsgi_performance_error.txt"
                if os.path.exists(error_file) and os.path.getsize(error_file) > MAX_DATA_LOGGING_FILE_SIZE:
                    os.remove(error_file)
                with open(error_file, "a") as fe:
                    fe.write(str(exc) + "\n")
            except Exception:
                pass


def profile_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        with ProfileRequest(request.META, get_response, (request,), {}) as pr:
            return pr.response

    return middleware
