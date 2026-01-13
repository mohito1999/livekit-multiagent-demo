from typing import Annotated, Literal
from livekit.agents import llm
from .base import BaseSalesAgent, SalesContext
import logging

logger = logging.getLogger("rohan.agents.discovery")

class DiscoveryAgent(BaseSalesAgent):
    def __init__(
        self,
        context: SalesContext,
        chat_ctx: llm.ChatContext | None = None,
        **kwargs,
    ):
        instructions = f"""
        You are in PHASE 2: DISCOVERY (The Guide).
        
        GOAL: Gently uncover their career status by offering "Menu Options" rather than interrogation.
        
        CONTEXT: 
        - They attended the workshop (Interest is there).
        - We know if they saw the pitch: {context.saw_pitch}.
        
        YOUR OBJECTIVES:
        1. Acknowledge & Pivot: "A lot of people I talk to loved the workshop but feel a bit overwhelmed by how fast AI is moving. Is that how you're feeling, or is it something else?"
        2. Categorical Questioning: Instead of "What's your problem?", ask: "Are you looking to switch jobs, or maybe just automate your current work?"
        3. Validate & Weave: Whatever they say, validate it ("That makes total sense"). Then drop a tiny "crumb" about the program ("That's actually a huge part of what we focus on—making it practical").
        4. Once you have a sense of their direction, call `handoff_to_pitch`.
        
        RULES:
        - NO "Interview Mode". Do not ask open-ended "Why?" questions.
        - Suggest answers. "Is it X or Y?"
        - Be empathetic. "I hear that a lot."
        - KEEP IT SHORT.
        """
        
        super().__init__(
            context=context,
            chat_ctx=chat_ctx,
            instructions=instructions,
            **kwargs,
        )

    @llm.function_tool(description="Capture the user's primary career pain point or challenge")
    async def capture_pain_point(
        self,
        challenge: str
    ):
        """
        Capture the user's primary career pain point or challenge.

        Args:
            challenge: The specific career challenge (e.g., 'stuck in support role', 'low salary')
        """
        self.sales_context.identified_pain_point = challenge
        logger.info(f"Pain point identified: {challenge}")
        return "Pain point captured. Now differentiate between casual learning vs structured learning."

    @llm.function_tool(description="Classify the user's intent as Student or Working Professional, and Casual vs Structured")
    async def classify_intent(
        self,
        persona: Literal["Student", "Professional"],
        intent_type: Literal["Casual", "Structured"]
    ):
        """
        Classify the user's intent as Student or Working Professional, and Casual vs Structured.

        Args:
            persona: User's current role
            intent_type: Whether they want free content or a structured path
        """
        self.sales_context.persona = persona
        logger.info(f"Classified intent: {persona}, {intent_type}")
        
        if intent_type == "Structured":
            return "Intent is structured. You have earned the right to pitch. HANDOFF to Pitch Agent immediately."
        else:
            return "Intent is casual. Gently challenge them: 'Do you believe random videos will solve [pain point]?'"

    @llm.function_tool(description="Transition to pitch phase once pain point is identified and magnified.")
    async def handoff_to_pitch(self):
        """
        Transition to pitch phase once pain point is identified and magnified.
        
        CRITERIA FOR TRANSITION:
        1. A specific pain point (e.g. 'stagnation', 'low pay') has been identified.
        2. You have asked at least one follow-up question to 'twist the knife' (magnify the pain).
        """
        from .pitch import PitchAgent
        
        # Log transition to Chat Context
        self.chat_ctx.add_message(
            role="system",
            content=f"TRANSITION: DISCOVERY -> PITCH. Criteria Met: Pain point identified ({self.sales_context.identified_pain_point or 'General'}) & magnified."
        )

        logger.info("\n\n" + "="*40)
        logger.info(" TRANSITION: DISCOVERY -> PITCH")
        logger.info("="*40 + "\n")
        logger.info(f"Handing off to PitchAgent (Persona: {self.sales_context.persona})")
        return PitchAgent(
            context=self.sales_context,
            chat_ctx=self.chat_ctx,
        )
