"""EXAMPLE — canonical pattern, copy & adapt.

A DRF serializer = the validation/transport boundary.
"""
from rest_framework import serializers


class PerfectSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        # TODO: domain-specific validation.
        return value.lower()
