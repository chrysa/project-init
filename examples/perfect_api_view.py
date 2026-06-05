"""EXAMPLE — canonical pattern, copy & adapt.

A thin DRF view: validate via serializer, delegate to a service.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from perfect_serializer import PerfectSerializer


class PerfectAPIView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = PerfectSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # TODO: delegate to a service; no business logic inline.
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
