from django.shortcuts import render


# Create your views here.
def index_view(request):
    return render(request=request, template_name="index.html")


def page1_view(request):
    return render(request=request, template_name="page1.html")
