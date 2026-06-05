"""EXAMPLE — canonical pattern, copy & adapt.

A pydantic schema = typed data contract at a boundary.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
