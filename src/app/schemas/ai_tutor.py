"""
Schemas for AI Tutor Module.
"""

from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AITutorRequest(BaseModel):
    """Request payload sent by a student to the AI Tutor."""
    message: str = Field(..., max_length=2000, description="The student's question or prompt.")
    context_material_id: UUID | None = Field(None, description="Optional ID of specific material to constrain the Q/A context.")


class AITutorResponse(BaseModel):
    """Response returned by the AI Tutor."""
    reply: str
    tokens_used: int = 0


class AITutorRuleUpdate(BaseModel):
    """Payload for a lecturer updating the AI Tutor's guiding rules."""
    rules: str = Field(..., max_length=5000, description="System instructions/rules for the AI to follow (e.g., 'don't give direct answers').")
