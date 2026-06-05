"""EXAMPLE — canonical pattern, copy & adapt.

A repository: the only place that touches the ORM/storage.
"""
from __future__ import annotations


class UserRepository:
    def find_by_id(self, user_id: str):
        # TODO: real ORM query, e.g. User.objects.filter(pk=user_id).first()
        raise NotImplementedError
