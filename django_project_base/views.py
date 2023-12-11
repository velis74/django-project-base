import requests

from django.http import FileResponse, HttpResponse
from django.views import static


def documentation_view(request: object, path="", document_root=None) -> FileResponse:
    if not path:
        path = "index.html"
    return static.serve(request=request, path=path, document_root=document_root)


def browser_update_script(request: object) -> HttpResponse:
    # TODO: does this configurability in script name ever come into play?
    try:
        script = request.path.split("js-script")[-1].strip("/")
    except Exception:
        script = ""
    script = script or "update.min.js"
    # TODO: not sure if this proxying is useful at all? I would also suggest cache-ing.
    http_response: HttpResponse = HttpResponse(
        requests.get("https://browser-update.org/%s" % script, verify=False).content.decode(),
        content_type="application/javascript",
    )
    return http_response
