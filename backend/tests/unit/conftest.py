# tests/unit/conftest.py
"""
Conftest for the unit test layer.

Unit tests must not require any external services (database, Redis, network).
This file overrides the session-scoped ``setup_test_db`` fixture from the root
conftest so that the database engine is never touched when running the unit
suite in isolation (e.g. ``pytest tests/unit/``).

The override is intentionally a no-op: unit tests do all their own mocking
and never need real I/O infrastructure.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db() -> None:  # type: ignore[override]
    """No-op override: unit tests require no database setup."""
    yield  # type: ignore[misc]
