from typing import List, Optional


CONTENT_TYPE_PLAIN_TEXT = "text/plain"
CONTENT_TYPE_HTML = "text/html"


def _noop_send_notification(
    subject: str,
    body: str,
    recipients: List,
    content_type: str = CONTENT_TYPE_PLAIN_TEXT,
    footer: str = "",
    project: Optional[str] = None,
    user: Optional[int] = None,
    delay: Optional[int] = None,
) -> None:
    pass


def send_notification(
    subject: str,
    body: str,
    recipients: List,
    content_type: str = CONTENT_TYPE_PLAIN_TEXT,
    footer: str = "",
    project: Optional[str] = None,
    user: Optional[int] = None,
    delay: Optional[int] = None,
) -> None:
    from django.conf import settings
    from django.utils.module_loading import import_string

    func_path = getattr(
        settings,
        "DPB_SEND_NOTIFICATION",
        "django_project_base.notifications._noop_send_notification",
    )
    import_string(func_path)(
        subject=subject,
        body=body,
        recipients=recipients,
        content_type=content_type,
        footer=footer,
        project=project,
        user=user,
        delay=delay,
    )
