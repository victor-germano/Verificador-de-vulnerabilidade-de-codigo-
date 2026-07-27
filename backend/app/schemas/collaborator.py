import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.enums import ProjectRole


class AddCollaboratorRequest(BaseModel):
    email: EmailStr
    role: ProjectRole


class UpdateCollaboratorRoleRequest(BaseModel):
    role: ProjectRole


class CollaboratorResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    role: str
    added_at: datetime
