# tests/unit/test_middleware_coverage.py
import pytest
import uuid
from app.middleware.active_semester import require_active_semester
from app.middleware.session_owner import require_session_owner
from app.exceptions import ForbiddenError

@pytest.mark.asyncio
async def test_require_active_semester_stub(db_session) -> None:
    # With no active semester in the DB, middleware raises ForbiddenError
    with pytest.raises(ForbiddenError) as excinfo:
        await require_active_semester(session=db_session)
    assert excinfo.value.error_code == "NO_ACTIVE_SEMESTER"

@pytest.mark.asyncio
async def test_require_session_owner_stub() -> None:
    # This stub currently always raises ForbiddenError
    fake_id = uuid.uuid4()
    with pytest.raises(ForbiddenError) as excinfo:
        await require_session_owner(session_id=fake_id, current_user=None)  # type: ignore
    assert excinfo.value.error_code == "FORBIDDEN"
