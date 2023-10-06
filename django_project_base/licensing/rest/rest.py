from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_project_base.base.exceptions import LicenseActionNotImplementedException
from django_project_base.licensing.logic import LogAccessService


class LicenseViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response(LogAccessService().report(user=request.user))

    def create(self, request):
        raise LicenseActionNotImplementedException()

    def retrieve(self, request, pk=None):
        raise LicenseActionNotImplementedException()

    def update(self, request, pk=None):
        raise LicenseActionNotImplementedException()

    def partial_update(self, request, pk=None):
        raise LicenseActionNotImplementedException()

    def destroy(self, request, pk=None):
        raise LicenseActionNotImplementedException()
