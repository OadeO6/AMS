# src/app/services/shared.py
from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ForbiddenError, NotFoundError
from app.models.notification import Notification
from app.models.user import User, UserRole
from app.repositories.notification import NotificationRepository
from app.repositories.material import MaterialRepository
from app.repositories.course import CourseRegistrationRepository, CourseOfferingRepository
from app.schemas.notification import NotificationResponse

class SharedService:
    """Service layer for shared endpoints (accessible by multiple roles)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repo = NotificationRepository(session)
        self.material_repo = MaterialRepository(session)
        self.registration_repo = CourseRegistrationRepository(session)
        self.offering_repo = CourseOfferingRepository(session)

    async def list_notifications(
        self, user: User, read: bool | None = None, page: int = 1, limit: int = 50
    ) -> tuple[Sequence[Notification], int]:
        return await self.notification_repo.list_for_user(
            user.id,
            unread_only=(read is False),
            offset=(page - 1) * limit,
            limit=limit,
        )

    async def list_notification_response(
        self, user: User, read: bool | None = None, page: int = 1, limit: int = 50
    ) -> dict:
        """Return the shared notification list response."""
        items, total = await self.list_notifications(user, read, page, limit)
        unread_count = await self.notification_repo.count_unread(user.id)
        return {
            "notifications": [NotificationResponse.model_validate(item) for item in items],
            "unread_count": unread_count,
            "total": total,
            "offset": (page - 1) * limit,
            "limit": limit,
        }

    async def mark_notification_read(self, user: User, notification_id: uuid.UUID) -> int:
        return await self.notification_repo.mark_read([notification_id], user.id)

    async def get_material_download_url(self, user: User, material_id: uuid.UUID) -> str:
        """Return a URL or construct logic to download a material, enforcing access."""
        material = await self.material_repo.get_by_id(material_id)
        if not material:
            raise NotFoundError("Material not found")

        offering = await self.offering_repo.get_by_id(material.offering_id)
        if not offering:
            raise NotFoundError("Course offering not found")

        # Validate access
        user_roles = {UserRole(r) for r in user.roles}
        if UserRole.LECTURER in user_roles and any(l.lecturer_id == user.id for l in offering.lecturers):
            # OK - access as lecturer
            pass
        elif UserRole.STUDENT in user_roles:
            reg = await self.registration_repo.get_by_student_and_offering(user.id, offering.id)
            if not reg or reg.status != "approved":
                raise ForbiddenError("Not registered for this course")
            if material.visibility == "ai_only":
                raise ForbiddenError("Material is restricted to AI use only")
        elif UserRole.LECTURER in user_roles:
            # Not the lecturer for this specific course offering
            raise ForbiddenError("You are not the lecturer for this course")
        else:
            raise ForbiddenError("Only students and lecturers can access materials")

        from app.services.storage import StorageService
        svc = StorageService()

        # If it's a full URL (like local mock), return it. Otherwise generate presigned URL.
        if material.file_url.startswith("http"):
            return material.file_url
        return svc.generate_presigned_url(material.file_url)
