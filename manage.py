#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.setup.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    params = list(sys.argv)
    if params[1] == "makemessages":
        params.extend(("-i", "node_modules", "-i", "static", "-i", "coverage"))
        params.extend(("-i", "tests", "-i", "setup", "-i", "examples", "-i", "dist"))
        print("Modified makemessages: will process both django and djangojs domains")
        execute_from_command_line(params + ["-d", "djangojs", "-e", "js,ts,vue"])

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
