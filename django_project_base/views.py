import requests
from django.http import FileResponse, HttpResponse
from django.views import static


def documentation_view(request: object, path='', document_root=None) -> FileResponse:
    if not path:
        path = 'index.html'
    return static.serve(request=request, path=path, document_root=document_root)


def browser_update_script(request: object) -> HttpResponse:
    try:
        script: str = request.path.split('js-script')[-1].strip('/')
    except Exception:
        script: str = ''
    script = script or 'update.min.js'
    http_response: HttpResponse = HttpResponse(
        requests.get('https://browser-update.org/%s' % script, verify=False).content.decode(),
        content_type='application/javascript',
    )
    return http_response
