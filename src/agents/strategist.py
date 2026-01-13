from typing import Annotated
from livekit.agents import llm
import logging
from .base import BaseSalesAgent

import asyncio

logger = logging.getLogger("rohan.agents.strategist")

class StrategistAgent(BaseSalesAgent):
    def __init__(
        self,
        **kwargs
    ):
        # Adaptive Logic for Prompt Injection
        persona = kwargs.get("context").persona if kwargs.get("context") else "Unknown"
        
        strategy_prompt = ""
        if persona == "Student":
            strategy_prompt = """
            STRATEGY: FOCUS ON JOBS & PORTFOLIO.
            - "Degrees are common, Portfolios are rare."
            - Talk about: The ' AI Residency' where they build real apps.
            - Case Study: Mention a student who got hired because they showed a working Agent, not a certificate.
            """
        elif persona == "Professional":
            strategy_prompt = """
            STRATEGY: FOCUS ON TIME & LEVERAGE.
            - "You don't need to become a coder; you need to become an Architect."
            - Talk about: Automating drudge work (reports, emails) to focus on strategy.
            - Value: "This is your 'Second Brain'."
            """
        elif persona == "Business Owner":
            strategy_prompt = """
            STRATEGY: FOCUS ON MARGINS & SCALE.
            - "Employees sleep, Agents don't."
            - Talk about: Customer Support bots that handle 80% of queries.
            - Value: "Cutting costs while improving speed."
            """
        elif persona == "Homemaker":
            strategy_prompt = """
            STRATEGY: FOCUS ON FLEXIBILITY & INDEPENDENCE.
            - "The world has changed. You can build a global business from your living room."
            - Talk about: Freelancing, starting a content agency, or just getting back into the workforce with a superpower.
            - Value: "Future-proofing yourself."
            """

        super().__init__(
            instructions=f"""
            You are the STRATEGIST AGENT (The Consultant).
            
            GOAL: Connect the user's specific PERSONA to our solution. Do not use a generic pitch.
            
            CONTEXT:
            - Persona: {persona}
            - Goal: {{context.career_goal}}
            
            {strategy_prompt}
            
            YOUR OBJECTIVES:
            1. Validate their Goal: "Given that you want to {{{{context.career_goal or 'grow'}}}}, the generic path won't work."
            2. Present the 'New Way': Explain how our AI Accelerator specifically helps *THEM* (using the Strategy above).
            3. Check Alignment: "Does this approach of building {{{{context.career_goal}}}} sound like the right path for you?"
            4. If they agree -> call `handoff_to_closing`.
            
            RULES:
            - WEAVE insights. Don't lecture.
            - Use the specific angles defined in your STRATEGY section.
            - KEEP IT SHORT.
            """,
            **kwargs
        )
        # Kickstart generation to solve silence on handoff
        if self.sales_context.session:
            asyncio.create_task(self.sales_context.session.generate_reply())

    @llm.function_tool(description="User buys into the vision. Move to closing.")
    async def handoff_to_closing(self):
        """Moves to the closing phase."""
        from .closing import ClosingAgent
        
        new_ctx = self.chat_ctx.copy()
        new_ctx.add_message(
            role="system",
            content="TRANSITION: STRATEGIST -> CLOSING. Vision aligned."
        )
        new_ctx.add_message(role="user", content="(User is ready. Move to closing details/price.)")
        
        return ClosingAgent(
            context=self.sales_context,
            chat_ctx=new_ctx
        )
