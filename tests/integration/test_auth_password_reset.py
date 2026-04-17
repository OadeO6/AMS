import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

@pytest.mark.asyncio
async def test_forgot_password(async_client: AsyncClient, setup_lecturer_data, redis_client, db_session: AsyncSession):
    student_user = setup_lecturer_data["student"]
    # 1. Invalid email
    resp = await async_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "not.found@example.com"}
    )
    assert resp.status_code == 200  # Never enumerate
    assert "reset link was sent" in resp.json()["message"]

    # 2. Valid email
    resp = await async_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": student_user.email}
    )
    assert resp.status_code == 200

    # 3. Check Redis for token
    keys = await redis_client.keys("reset_token:*")
    assert len(keys) > 0
    token = keys[0].decode("utf-8").split("reset_token:")[1] if isinstance(keys[0], bytes) else keys[0].split("reset_token:")[1]
    
    # 4. Use token to reset password
    reset_resp = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "NewSecurePassword123!"}
    )
    assert reset_resp.status_code == 200

    # 5. Invalid token (should return 401 since token is consumed)
    reset_resp2 = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "NewSecurePassword123!"}
    )
    assert reset_resp2.status_code == 401

    # 6. Try to login with new password
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": student_user.email, "password": "NewSecurePassword123!"}
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()
