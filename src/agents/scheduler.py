
from typing import Annotated
from livekit.agents import llm
import logging
from datetime import datetime, timedelta
from .base import BaseSalesAgent

import asyncio

logger = logging.getLogger("rohan.agents.scheduler")

class SchedulerAgent(BaseSalesAgent):
    def __init__(
        self,
        **kwargs
    ):
        super().__init__(
            instructions="""
            You are the SCHEDULER AGENT (The Rescuer).
            
            GOAL: Re-engage the user who missed the workshop.
            
            Key Information:
            - Next Workshops: Sundays at 11 AM & 7 PM. Wednesdays at 7 PM.
            
            YOUR OBJECTIVES:
            1. Empathize: "Oh, life happens! No worries at all."
            2. Offer Option: "We have another live session coming up this Sunday at 11 AM. Does that work for you?"
            3. Confirm & Book: Call `confirm_reschedule` if they say yes.
            
            RULES:
            - Be very forgiving.
            - Do not ask "Why". Just solve it.
            """,
            **kwargs
        )
        # Kickstart generation to solve silence on handoff
        if self.sales_context.session:
            asyncio.create_task(self.kickstart_generation())

    @llm.function_tool(description="Confirm the user wants to attend the next session.")
    async def confirm_reschedule(self, 
        accepted: bool,
        next_date: str
    ):
        """
        Logs the reschedule and ends the call positively.
        
        Args:
            accepted: Did user accept the new time?
            next_date: The date/time they agreed to
        """
        if accepted:
            self.sales_context.next_session_proposed = next_date
            logger.info(f"RESCHEDULED: User booked for {next_date}")
            # self.chat_ctx.add_message(...) # Removing to avoid ReadOnly error
            return "Great! I've locked that in. You'll get an email shortly. Thanks for picking up, looking forward to seeing you then!"
        else:
            logger.info("RESCHEDULED: User declined.")
            return "No problem. We'll keep you on the email list for future updates. Have a wonderful day!"
