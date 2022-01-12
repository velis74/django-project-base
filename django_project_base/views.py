import requests
from django.http import FileResponse, HttpResponse
from django.views import static


def documentation_view(request: object, path='', document_root=None) -> FileResponse:
    if not path:
        path = 'index.html'
    return static.serve(request=request, path=path, document_root=document_root)

def browser_update_script(request: object) -> HttpResponse:
    return HttpResponse(requests.get('https://browser-update.org/update.min.js', verify=False).content.decode(),
                        content_type='application/javascript')