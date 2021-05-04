from django.http import FileResponse
from django.views import static


def documentation_view(request: object, path='', document_root=None) -> FileResponse:
    if not path:
        path = 'index.html'
    return static.serve(request=request, path=path, document_root=document_root)
