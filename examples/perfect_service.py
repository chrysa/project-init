"""EXAMPLE — canonical pattern, copy & adapt.

A service: pure business logic, framework-agnostic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from perfect_repository import UserRepository


class NotFoundError(Exception):
    pass


@dataclass(frozen=True)
class User:
    id: str
    email: str


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def get_user(self, user_id: str) -> User:
        user = self._repo.find_by_id(user_id)
        if user is None:
            raise NotFoundError(user_id)
        return user
