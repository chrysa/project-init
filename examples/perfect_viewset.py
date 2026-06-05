"""EXAMPLE — canonical pattern, copy & adapt.

A DRF ViewSet wiring serializer + queryset; logic stays in services.
"""
from rest_framework import viewsets


class PerfectViewSet(viewsets.ModelViewSet):
    serializer_class = None  # TODO: PerfectSerializer
    queryset = None          # TODO: Model.objects.all()
