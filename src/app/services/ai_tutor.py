import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gradebook import AITutorRule
from app.schemas.ai_tutor import AITutorRequest, AITutorResponse


class AITutorService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def chat(self, user_id: uuid.UUID, offering_id: uuid.UUID, payload: AITutorRequest) -> AITutorResponse:
        """
        Processes a chat request against the offering's AI rules.
        """
        # Load rules if configured
        rule_query = await self.session.execute(
            select(AITutorRule).where(AITutorRule.offering_id == offering_id)
        )
        rule = rule_query.scalar_one_or_none()
        
        # In a real implementation:
        # 1. We would fetch the material (if context_material_id) to inject into prompt
        # 2. Append `rule.rules` as system instruction
        # 3. Request LLM completion from an external provider (OpenAI API / Local model)
        
        base_reply = f"Simulated AI Tutor response to: '{payload.message}'."
        if rule:
            base_reply += f" (Applied Lecturer Rule snippet: {rule.rules[:50]}...)"
            
        return AITutorResponse(
            reply=base_reply,
            tokens_used=42
        )

    async def update_rules(self, offering_id: uuid.UUID, rules: str) -> None:
        """
        Inserts or updates the AI Tutor rules for a specific offering.
        """
        rule_query = await self.session.execute(
            select(AITutorRule).where(AITutorRule.offering_id == offering_id)
        )
        rule = rule_query.scalar_one_or_none()
        
        if rule:
            rule.rules = rules
        else:
            rule = AITutorRule(offering_id=offering_id, rules=rules)
            self.session.add(rule)
        
        await self.session.flush()
