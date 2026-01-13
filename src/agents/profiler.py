from typing import Annotated, Literal
from livekit.agents import llm
import logging
from .base import BaseSalesAgent

import asyncio

logger = logging.getLogger("rohan.agents.profiler")

class ProfilerAgent(BaseSalesAgent):
    def __init__(
        self,
        **kwargs
    ):
        super().__init__(
            instructions="""
            You are the PROFILER AGENT (The Researcher).
            
            GOAL: You are NOT selling. You are interviewing to understand WHO the lead is.
            
            CONTEXT: 
            - User attended the workshop and liked it (or at least stayed).
            
            YOUR OBJECTIVES:
            1. IMMEDIATE ACTION: Acknowledge the transition seamlessly. "That's exactly why we focus on tools. To help me recommend the right ones for you..."
            2. Identify Persona: Are they a Student, Working Professional, Business Owner, or Homemaker?
            3. Identify Motivation: WHY did they join? (Curiosity, Crisis, Fear of Missing Out?)
               - **SPECIAL RULE**: If they seem to be a Homemaker/on a career break, ask explicitly: "Are you looking to restart your corporate career, or start something of your own from home?"
            4. Identify Goal: Where do they want to be in 6 months?
            
            TRANSITION:
            - Once you have clear answers for Persona, Motivation, and Goal, call `submit_profile_and_handoff`.
            
            RULES:
            - Be curious, not interrogation-style. "That's interesting, tell me more..."
            - Use "Menu Options" to make it easier: "Is it more about finding a job or just upskilling in your current role?"
            - DO NOT PITCH the product yet. Just listen and categorize.
            - KEEP IT SHORT.
            """,
            **kwargs
        )

    @llm.function_tool(description="Save user profile and move to Strategy phase.")
    async def submit_profile_and_handoff(self,
        persona: Literal["Student", "Professional", "Business Owner", "Homemaker"],
        motivation: str,
        career_goal: str
    ):
        """
        Saves the user persona and hands off to the Strategist.
        
        Args:
            persona: The category of the user
            motivation: Why they are interested in AI
            career_goal: What they want to achieve in 6 months
        """
        from .strategist import StrategistAgent
        
        # Update Context
        self.sales_context.persona = persona
        self.sales_context.motivation = motivation
        self.sales_context.career_goal = career_goal
        
        logger.info(f"PROFILE CAPTURED: {persona} | {motivation} | {career_goal}")
        
        # Log transition
        new_ctx = self.chat_ctx.copy()
        new_ctx.add_message(
            role="system",
            content=f"TRANSITION: PROFILER -> STRATEGIST. Profile: {persona}, Goal: {career_goal}"
        )
        new_ctx.add_message(role="user", content="(User is listening. Present the strategy now.)")

        return StrategistAgent(
            context=self.sales_context,
            chat_ctx=new_ctx
        )
