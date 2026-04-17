# tests/unit/test_health_coverage.py
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.api.v1.health import readiness
from fastapi.responses import JSONResponse

@pytest.mark.asyncio
async def test_readiness_db_failure() -> None:
    # Mock AsyncSessionFactory context manager to raise exception
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__.side_effect = Exception("DB Connection Refused")
    
    with patch("app.api.v1.health.AsyncSessionFactory", mock_session_factory):
        # Also mock redis to avoid real redis connection
        with patch("app.core.redis.redis_pool.ping", new_callable=AsyncMock) as mock_ping:
            response = await readiness()
            assert isinstance(response, JSONResponse)
            assert response.status_code == 503
            # data = response.init_subclass  # This is not how to get data from JSONResponse in tests easily without more boilerplate
            # # Let's just check status_code for now or use .body
            import json
            body = json.loads(response.body.decode())
            assert body["status"] == "degraded"
            assert "database" in body["failures"]

@pytest.mark.asyncio
async def test_readiness_redis_failure() -> None:
    # Mock DB to succeed
    mock_session = AsyncMock()
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session
    
    # Mock redis to fail
    with patch("app.api.v1.health.AsyncSessionFactory", mock_session_factory):
        with patch("app.core.redis.redis_pool.ping", side_effect=Exception("Redis Timeout")):
            response = await readiness()
            assert response.status_code == 503
            import json
            body = json.loads(response.body.decode())
            assert body["status"] == "degraded"
            assert "redis" in body["failures"]
