from typing import Annotated
from livekit.agents import llm
from .base import BaseSalesAgent, SalesContext
# lazy import for DiscoveryAgent to avoid circular dependency

import logging

logger = logging.getLogger("rohan.agents.rapport")

class RapportAgent(BaseSalesAgent):
    def __init__(
        self,
        context: SalesContext,
        chat_ctx: llm.ChatContext | None = None,
        **kwargs,
    ):
        instructions = f"""
        You are in PHASE 1: RAPPORT BUILDING. 
        
        GOAL: Warm Start -> gentle Check-in -> HANDOFF.
        
        YOUR OBJECTIVES:
        1. If they confirm name: "Great. I just wanted to personally check in after the workshop on {context.workshop_date}."
        2. Soft Ask: "How did you find the session? Was it helpful?" (Intent A).
        3. Soft Check: "Were you able to stay till the end for the program details?" (Intent B).
        4. CRITICAL: Once you have Feedback + Attendance, move to Discovery.
        
        RULES:
        - SOFTEN THE TONE. No military precision. Be warm.
        - "Glad to hear that" / "No worries at all".
        - KEEP IT SHORT.
        """
        
        super().__init__(
            context=context,
            chat_ctx=chat_ctx,
            instructions=instructions,
            **kwargs
        )

    @llm.function_tool(description="Log the user's feedback about the workshop")
    async def log_feedback(
        self, 
        feedback_summary: str
    ):
        """
        Log the user's feedback about the workshop.

        Args:
            feedback_summary: Summary of the user's feedback
        """
        logger.info(f"Feedback received: {feedback_summary}")
        self.sales_context.leads_context_summary += f" | Workshop Feedback: {feedback_summary}"
        return "Feedback logged. Acknowledge it warmly and ask if they saw the end of the workshop."

    @llm.function_tool(description="Confirm if the user saw the pitch at the end of the workshop")
    async def confirm_attendance(
        self, 
        saw_pitch: bool
    ):
        """
        Confirm if the user saw the pitch at the end of the workshop.

        Args:
            saw_pitch: True if they saw the pitch, False otherwise
        """
        self.sales_context.saw_pitch = saw_pitch
        logger.info(f"Saw pitch: {saw_pitch}")
        return "Attendance confirmed. Now pivot to asking about their single biggest career challenge."

    @llm.function_tool(description="Transition to discovery phase once feedback is collected and verified")
    async def handoff_to_discovery(self):
        """
        Transition to discovery phase once feedback is collected and verified.
        
        CRITERIA FOR TRANSITION:
        1. User has provided feedback on the workshop.
        2. User has confirmed whether they saw the pitch.
        """
        from .discovery import DiscoveryAgent
        
        # Log transition to Chat Context
        self.chat_ctx.add_message(
            role="system",
            content="TRANSITION: RAPPORT -> DISCOVERY. Criteria Met: Feedback collected & Attendance confirmed."
        )
        
        logger.info("\n\n" + "="*40)
        logger.info(" TRANSITION: RAPPORT -> DISCOVERY")
        logger.info("="*40 + "\n")
        
        return DiscoveryAgent(
            context=self.sales_context,
            chat_ctx=self.chat_ctx,
        )
