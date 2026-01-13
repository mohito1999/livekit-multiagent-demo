from typing import Annotated, Literal
from livekit.agents import llm
import logging
from .base import BaseSalesAgent

logger = logging.getLogger("rohan.agents.rapport")

class RapportAgent(BaseSalesAgent):
    def __init__(
        self,
        **kwargs
    ):
        super().__init__(
            instructions="""
            You are in PHASE 1: RAPPORT BUILDING (The Host).
            
            GOAL: Warm Start -> Audit Workshop Experience -> Route to Correct Path.
            
            YOUR OBJECTIVES:
            1. Check In: "Hi Mohit, I'm Rohan from {context.company_name}. Calling about the '{context.workshop_topic}' workshop on Sunday. Just wanted to check—how was the experience for you?"
            2. Dig for Detail: 
               - If they liked it: "What part stood out? The tools? The strategy?"
               - If they missed it/left early: "Ah, no worries."
            3. ROUTING (CRITICAL):
               - If Missed/Left Early -> Call `check_schedule_availability`.
               - If Liked -> Say: "That's impactful. I'm curious..." -> Call `explore_profile_depth` immediately.
               - If Hated -> Apologize, get feedback, and Say Goodbye.
            
            RULES:
            - NO "TRANSFERRING/LOGGING": Do NOT say "I will log this" or "I will move you".
            - You are the same person. Just continue the thought.
            - "Life happens" attitude for missed sessions.
            - KEEP IT SHORT.
            """,
            **kwargs
        )

    @llm.function_tool(description="Log feedback and attendance details.")
    async def log_workshop_details(self,
        rating: Literal["positive", "neutral", "negative"],
        attendance: Literal["full", "partial", "missed"],
        feedback_note: str
    ):
        """
        Logs the workshop experience.
        
        Args:
            rating: How they felt about the workshop
            attendance: Did they attend the whole thing?
            feedback_note: Short summary of their feedback
        """
        self.sales_context.workshop_rating = rating
        self.sales_context.attendance_depth = attendance
        logger.info(f"WORKSHOP LOG: Rating={rating}, Attendance={attendance} | {feedback_note}")
        return "Noted regarding their experience."

    @llm.function_tool(description="Check for next available slots if they missed the workshop.")
    async def check_schedule_availability(self):
        """Routes to the Scheduler Agent."""
        from .scheduler import SchedulerAgent
        
        # Create a mutable copy of the context/history
        new_ctx = self.chat_ctx.copy()
        new_ctx.add_message(role="system", content="TRANSITION: RAPPORT -> SCHEDULER. User missed content.")
        new_ctx.add_message(role="user", content="(User is waiting for your help to reschedule.)")
        
        return SchedulerAgent(
            context=self.sales_context,
            chat_ctx=new_ctx
        )

    @llm.function_tool(description="Acknowledge feedback and pivot to understanding their background.")
    async def explore_profile_depth(self):
        """Routes to the Profiler Agent."""
        from .profiler import ProfilerAgent
        
        # Create a mutable copy of the context/history
        new_ctx = self.chat_ctx.copy()
        new_ctx.add_message(role="system", content="TRANSITION: RAPPORT -> PROFILER. User engagement confirmed.")
        # FORCE GENERATION: Add a dummy user message so the new agent speaks immediately.
        new_ctx.add_message(role="user", content="(User is listening. Please continue smoothy.)")
        
        return ProfilerAgent(
            context=self.sales_context,
            chat_ctx=new_ctx
        )
