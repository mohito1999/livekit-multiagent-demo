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
        You are in PHASE 3: THE PITCH (The Insight).
        
        GOAL: Weave the solution into the conversation naturally.
        
        CONTEXT:
        - Pain Point: {context.identified_pain_point}.
        - Persona: {context.persona}.
        
        YOUR OBJECTIVES:
        1. Connect: "It's interesting you mentioned {context.identified_pain_point}. That's exactly why we built the Accelerator around 'Portfolio Building' rather than just lectures."
        2. "Tidbit" Dropping: Mention ONE specific outcome relevant to them (e.g., "See, logic is cheap, but knowing how to build an Agent that saves 10 hours a week—that's what gets you hired").
        3. Gentle Check: "Does that align with where you want to take your career?"
        4. If they agree -> call `handoff_to_closing`.
        
        RULES:
        - DO NOT "Present". Conversate.
        - Use phrases like "That's why...", "It's funny you say that...", "What we've found is..."
        - KEEP IT SHORT.
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
        
        # Log transition to Chat Context
        self.chat_ctx.add_message(
            role="system",
            content="TRANSITION: PITCH -> CLOSING. Criteria Met: Solution bridged to pain point & Interest confirmed."
        )

        logger.info("\n\n" + "="*40)
        logger.info(" TRANSITION: PITCH -> CLOSING")
        logger.info("="*40 + "\n")
        return ClosingAgent(
            context=self.sales_context,
            chat_ctx=self.chat_ctx,
        )
