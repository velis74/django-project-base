import json
import logging
from typing import Optional

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from django_project_base.licensing.rest.rest import LicenseActionNotImplementedException
from django_project_base.notifications.models import DeliveryReport


class DeliveryReportViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    authentication_classes = [TokenAuthentication, BasicAuthentication]

    _primary_key_names = ["id", "pk", "guid", "uuid"]

    def __find_dlr_id(self, params: dict) -> Optional[str]:
        id = next(filter(lambda i: i.lower() in self._primary_key_names, params.keys()), None)
        if not id:
            logger = logging.getLogger("django")
            logger.exception(
                f"Id not found for delivery report {self.request.query_params} {self.request.data} {self.request.user}"
            )
            return None
        return str(id)

    def list(self, request) -> Response:
        if (id := self.__find_dlr_id(self.request.query_params)) and (
            dlr := DeliveryReport.objects.filter(pk=id).first()
        ):
            dlr.payload = json.dumps(request.query_params)
            dlr.save(upadate_fields=["payload"])
        return Response()

    def create(self, request) -> Response:
        raise Response()

    def retrieve(self, request, pk=None):
        raise LicenseActionNotImplementedException()

    def update(self, request, pk=None):
        raise LicenseActionNotImplementedException()

    def partial_update(self, request, pk=None):
        raise LicenseActionNotImplementedException()

    def destroy(self, request, pk=None):
        raise LicenseActionNotImplementedException()
