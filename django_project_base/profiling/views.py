import json
import random

from datetime import datetime

from django.core.cache import cache
from django.shortcuts import render
from dynamicforms.struct import Struct

from django_project_base.caching.cache_queue import CacheQueue
from django_project_base.settings import PROFILER_LOG_LONG_REQUESTS_COUNT


def app_debug_view(request):
    # if not getattr(request, 'user', None) or request.user.pk not in POWER_USERS:
    if not getattr(request, "user", None):
        raise PermissionError
    return render(request, "app-debug/main.html", __get_debug_data())


def __get_debug_data():
    import time

    result_data = []
    requests = []

    for cache_ptr in range(PROFILER_LOG_LONG_REQUESTS_COUNT):
        item = cache.get("long_running_cmds_data%d" % cache_ptr)
        if item:
            requests.append(item)

    totals = {}
    min_timestamp = time.time()

    for req in requests:
        queries_executed: list = req.get("queries", []) or []

        num_of_queries: int = len(queries_executed)
        num_of_distinct_queries: int = len(
            set(map(lambda d: d["sql"], filter(lambda e: isinstance(e, dict), queries_executed)))
        )
        r = lambda: random.randint(0, 255)  # noqa: E731
        item = dict(
            r_data=dict(
                num_of_duplicate_queries=num_of_queries - num_of_distinct_queries,
                num_of_queries=num_of_queries,
                duration=req.get("duration"),
                path_info=req.get("PATH_INFO"),
                host=req.get("HTTP_HOST"),
                method=req.get("REQUEST_METHOD"),
                timestamp=datetime.utcfromtimestamp(req["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                if req.get("timestamp")
                else None,
                query_string=req.get("QUERY_STRING"),
            ),
            db_queries=queries_executed,
            color="rgba(%d, %d, %d, 0.3)" % (r(), r(), r()),
        )
        item_data = item["r_data"]
        totals.setdefault(item_data["path_info"], Struct(count=0, time=0, path=""))
        total = totals[item_data["path_info"]]
        total.count += 1
        total.time += item_data["duration"]
        total.path = item_data["path_info"]
        min_timestamp = min(req["timestamp"], min_timestamp)
        result_data.append(item)

    result_data.sort(key=lambda f: f.get("r_data", {}).get("duration", 0) or 0, reverse=True)
    spenders = list(sorted(totals.values(), key=lambda x: x.time, reverse=True))

    totals = {}
    for interval in range(int((time.time()) - 3600) // 10, int(time.time()) // 10 + 1):
        last_hour_running_cmds_key = f"last_hour_running_cmds{interval}"
        last_hour_running_cmds_queue = CacheQueue.get_cache_queue(last_hour_running_cmds_key, timeout=3600)

        cache_ptr = last_hour_running_cmds_queue.lrange()
        for item in [json.loads(item) for item in cache_ptr]:
            totals.setdefault(item[0], Struct(count=0, wall_time=0, path="", user_time=0, sys_time=0, cpu_time=0))
            total = totals[item[0]]
            total.count += 1
            total.wall_time += item[1]
            total.user_time += item[2]
            total.sys_time += item[3]
            total.cpu_time += item[2] + item[3]
            total.path = item[0]
    for total in totals.values():
        total.wall_avg = int(total.wall_time / total.count)
        total.cpu_avg = int(total.cpu_time / total.count)
        total.core_usage = int(total.cpu_time / 3600.0) / 1000.0

    all_requests = list(sorted(totals.values(), key=lambda x: x.wall_time, reverse=True))

    return dict(
        debug_data=result_data,
        spenders=spenders,
        long_running_time=int(time.time() - min_timestamp),
        all_requests=all_requests,
    )
