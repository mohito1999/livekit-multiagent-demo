from typing import Annotated
from livekit.agents import llm
from .base import BaseSalesAgent, SalesContext
import logging

logger = logging.getLogger("rohan.agents.pitch")

class PitchAgent(BaseSalesAgent):
    def __init__(
        self,
        context: SalesContext,
        chat_ctx: llm.ChatContext | None = None,
        **kwargs,
    ):
        instructions = f"""
        You are in PHASE 3: THE PITCH (The Solution).
        
        GOAL: Link their Pain to Our Solution.
        
        CONTEXT:
        - Pain Point: {context.identified_pain_point}.
        - Persona: {context.persona}.
        
        YOUR OBJECTIVES:
        1. Bridge: "That's exactly what our Accelerator solves. We don't just teach theory; we build your portfolio."
        2. Explain ONE key benefit relevant to their pain (e.g., "We have a dedicated placement team" for job seekers).
        3. Check Interest: "Does that sound like the direction you want to go?"
        4. If Positive -> call `handoff_to_closing`.
        
        RULES:
        - KEEP IT SHORT. Punchy sentences.
        - Focus on OUTCOMES (Salary, Jobs), not features (hours of video).
        """
        
        super().__init__(
            context=context,
            chat_ctx=chat_ctx,
            instructions=instructions,
            **kwargs,
        )

    @llm.function_tool(description="Validate the user's interest level in the pitched solution.")
    async def validate_interest(
        self,
        score: int,
        commitment: str
    ):
        """
        Validate the user's interest level in the pitched solution.

        Args:
            score: Interest score from 1-10
            commitment: User's verbal commitment (e.g. 'I definitely need this')
        """
        logger.info(f"Interest validation: {score}/10 - {commitment}")
        if score >= 7:
            return "High interest confirmed. You can now move to the Closing phase."
        else:
            return "Interest is low. Ask what specific part of the program they are unsure about."

    @llm.function_tool(description="Transition to closing phase once user shows interest in the solution.")
    async def handoff_to_closing(self):
        """
        Transition to closing phase once user shows interest in the solution.
        
        CRITERIA FOR TRANSITION:
        1. You have presented the solution linked to their pain point.
        2. User has expressed positive interest or asked about price/details.
        """
        from .closing import ClosingAgent
        logger.info("\n\n" + "="*40)
        logger.info(" TRANSITION: PITCH -> CLOSING")
        logger.info("="*40 + "\n")
        return ClosingAgent(
            context=self.sales_context,
            chat_ctx=self.chat_ctx,
        )
