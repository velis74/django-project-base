"""
query_tracker

this submodule allows for tracking SQL queries and outputting them to logs

activate by setting database ENGINE to "django_project_base.query_tracker"

it will also check for these additional parameters:

"TRACKED_ENGINE": mandatory. what was "ENGINE" before. tracker will instantiate this engine with the rest of options

"TRACKER_LOGGER_NAME": default None. name of logger to use for logging SQL requests.
  See https://docs.djangoproject.com/en/dev/topics/logging/

"TRACKER_LOGGER_LEVEL": default logging.WARNING. if a falsy value is given, it is reset to DEBUG. Needs to be int.
  Also see django logging docs or python logging module docs
  Note: when manage.py test has been run, the default becomes logging.DEBUG. Default logger will ignore the logging

"TRACKER_FILTER_STACK": default ("site-packages", "query_tracker", "/python3", "JetBrains").
  Whether we should filter the stack to only show "relevant" stack code points, i.e. "our own" code.
  set to empty tuple to NOT filter the stack or specify a tuple of strings that should not be in code path


Example DATABASES configuration from settings.py:
DATABASES = {
    "default": {
        "ENGINE": "django_project_base.query_tracker",
        "TRACKED_ENGINE": "django.db.backends.sqlite3",
        "TRACKER_LOGGER_LEVEL": logging.INFO,
        "TRACKER_FILTER_STACK", ("site-packages", "query_tracker", "/python3", "JetBrains"),
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

Output for each query consists of:
* request path (if it could be found, requires "django_project_base.base.UrlVarsMiddleware" to be installed
* query itself, prefixed by execution time in ms
* stack trace that led to the query
"""

import importlib
import logging
import sys
import time
import traceback

from typing import Optional, Tuple

from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.utils import CursorWrapper

from django_project_base.base.middleware import get_current_request


def filter_stack(filter_stack: Tuple[str] = tuple()):
    # Get the current stack trace
    stack = traceback.extract_stack()

    # Filter out the entries containing ".venv"
    if filter_stack:
        filtered_stack = filter(
            lambda entry: not any(s in entry.filename for s in filter_stack),
            stack,
        )
    else:
        filtered_stack = stack

    # Format the filtered stack trace
    formatted_stack = traceback.format_list(filtered_stack)

    return "".join(formatted_stack)


def quote_strings(val):
    if isinstance(val, str):
        return f"'{val}'"
    return val


class StackTraceCursorWrapper(CursorWrapper):
    def __init__(self, logger_name: Optional[str], logger_level: int, filter_stack: Tuple[str], *args, **kwds):
        self.logger = logging.getLogger(logger_name)
        self.logger_level = logger_level
        self.filter_stack = filter_stack
        super().__init__(*args, **kwds)

    def execute(self, sql, params=None):
        log_lines = []
        try:
            request = get_current_request()
            log_lines.append(" ".join(["request path", request.path]))
        except:
            pass
        log_lines.append(" ".join(["sql", sql % tuple(map(quote_strings, params)) if params else sql]))
        log_lines.append(filter_stack(self.filter_stack))
        tim = time.time()
        res = super().execute(sql, params)
        tim = (time.time() - tim) * 1000
        log_lines.append(" ".join(["sql", f"{tim:.2f}ms", sql % tuple(map(quote_strings, params)) if params else sql]))
        self.logger.log(self.logger_level, "\n".join(log_lines))
        return res

    def executemany(self, sql, param_list):
        log_lines = []
        try:
            request = get_current_request()
            log_lines.append(" ".join(["request path", request.path]))
        except:
            pass
        log_lines.append(" ".join(["sql", sql]))
        log_lines.append(filter_stack())
        self.logger.log(self.logger_level, "\n".join(log_lines))
        return super().executemany(sql, param_list)


class DatabaseWrapper(BaseDatabaseWrapper):
    def __new__(cls, settings_dict, *args, **kwargs):
        assert "TRACKED_ENGINE" in settings_dict
        testing = len(sys.argv) > 1 and sys.argv[1] == "test" and "manage.py" in sys.argv[0]
        default_level = logging.DEBUG if testing else logging.WARNING

        tracked_engine = settings_dict["TRACKED_ENGINE"] + ".base"
        logger_name = settings_dict.get("TRACKER_LOGGER_NAME", None)
        logger_level = settings_dict.get("TRACKER_LOGGER_LEVEL", default_level) or logging.DEBUG
        filter_stack = settings_dict.get(
            "TRACKER_FILTER_STACK", ("site-packages", "query_tracker", "/python3", "JetBrains")
        )
        assert isinstance(logger_level, int)

        module = importlib.import_module(tracked_engine)
        DBW = getattr(module, "DatabaseWrapper")

        class CDBW(DBW):
            def create_cursor(self, name=None):
                cursor = super().create_cursor(name)
                return StackTraceCursorWrapper(logger_name, logger_level, filter_stack, cursor, self)

        return CDBW(settings_dict, *args, **kwargs)
