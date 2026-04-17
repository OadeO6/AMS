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
    ) -> tuple[int, Sequence[Notification]]:
        return await self.notification_repo.list_by_user(user.id, read, page, limit)

    async def mark_notification_read(self, user: User, notification_id: uuid.UUID) -> Notification:
        notification = await self.notification_repo.get_by_id(user.id, notification_id)
        if not notification:
            raise NotFoundError("Notification not found")
        return await self.notification_repo.mark_read(notification)

    async def get_material_download_url(self, user: User, material_id: uuid.UUID) -> str:
        """Return a URL or construct logic to download a material, enforcing access."""
        material = await self.material_repo.get_by_id(material_id)
        if not material:
            raise NotFoundError("Material not found")

        offering = await self.offering_repo.get_by_id(material.offering_id)
        if not offering:
            raise NotFoundError("Course offering not found")

        # Validate access
        if user.role == UserRole.STUDENT:
            reg = await self.registration_repo.get_by_student_and_offering(user.id, offering.id)
            if not reg or reg.status != "approved":
                raise ForbiddenError("Not registered for this course")
            if material.visibility == "ai_only":
                raise ForbiddenError("Material is restricted to AI use only")
        elif user.role == UserRole.LECTURER:
            if offering.lecturer_id != user.id:
                raise ForbiddenError("You are not the lecturer for this course")
        else:
            raise ForbiddenError("Only students and lecturers can access materials")

        from app.services.storage import StorageService
        svc = StorageService()

        # If it's a full URL (like local mock), return it. Otherwise generate presigned URL.
        if material.file_url.startswith("http"):
            return material.file_url
        return svc.generate_presigned_url(material.file_url)
