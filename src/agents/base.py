from dataclasses import dataclass, field
from typing import Optional, List, Literal
from livekit import agents
from livekit.agents import llm
import logging

logger = logging.getLogger("rohan.agents")

@dataclass
class SalesContext:
    # Lead Static Info
    lead_name: str = "Mohit"
    workshop_date: str = "Sunday, November 30th"
    leads_context_summary: str = "Fresh Lead"
    today_date: str = "Friday, December 5th, 2025"
    
    # Company & Product Info
    company_name: str = "bee-ten-ex (Be10X)"
    company_mission: str = "Helping professionals master AI tools to future-proof their careers."
    workshop_topic: str = "Mastering AI Agents with LLMs"
    
    # Pricing Configuration
    retail_price: str = "Forty-five thousand two hundred rupees"
    price_level_1_discount: str = "Thirty-eight thousand rupees"
    price_floor_target: str = "Thirty-two thousand nine hundred ninety-nine rupees"
    booking_amount: str = "Five thousand rupees"
    full_payment_discount_rate: str = "10 percent"

    # Session State
    persona: Optional[Literal["Student", "Professional", "Business Owner", "Homemaker"]] = None
    identified_pain_point: Optional[str] = None
    saw_pitch: bool = False
    
    # Adaptive Flow State
    workshop_rating: Optional[str] = None # 'positive', 'neutral', 'negative'
    attendance_depth: Optional[str] = None # 'missed', 'partial', 'full'
    motivation: Optional[str] = None
    career_goal: Optional[str] = None
    next_session_proposed: Optional[str] = None
    
    current_price_revealed: Optional[Literal["retail", "scholarship", "floor"]] = None
    objections_log: List[str] = field(default_factory=list)
    active_agent: Optional[object] = None # Track the currently running agent
    session: Optional[object] = None # Reference to the main AgentSession
    

class BaseSalesAgent(agents.Agent):
    def __init__(
        self,
        context: SalesContext,
        chat_ctx: Optional[llm.ChatContext] = None,
        **kwargs,
    ):
        self.sales_context = context
        # Register self as the active agent for transcript logging
        self.sales_context.active_agent = self
        
        # Base instructions that apply to ALL agents
        base_instructions = f"""
        You are Rohan, an extremely patient, dedicated, and professional AI Sales Consultant at bee-ten-ex.
        
        CONTEXT VARIABLES:
        - Lead Name: {context.lead_name}
        - Company: {context.company_name}
        - Mission: {context.company_mission}
        - Workshop Date: {context.workshop_date}
        - Workshop Topic: {context.workshop_topic}
        - Lead Summary: {context.leads_context_summary}
        - Today's Date: {context.today_date}
        
        GLOBAL RULES:
        1. Tone: Conversational, empathetic, professional. Use "Hinglish" naturally (e.g., "sahi baat hai", "bilkul", "tension mat lo"), but avoid overly informal slang like "yaar".
        2. Patience: Do NOT rush. Earn the right to pitch.
        3. Formatting: NEVER use markdown, bullets, or numbered lists in spoken output.
        4. Voicemail: If you detect voicemail, say strictly: "Have a great day, goodbye."
        5. Numbers: Generate numbers as text (e.g., "two hundred percent" instead of "200%").
        6. LENGTH: ABSOLUTE LIMIT of 1-2 sentences. Keep it punchy. Speak like a busy but helpful human.
        
        See your specific role instructions below.
        """
        
        # Combine with any specific instructions passed
        specific_instructions = kwargs.pop("instructions", "")
        full_instructions = f"{base_instructions}\n\n{specific_instructions}".strip()

        super().__init__(
            instructions=full_instructions,
            chat_ctx=chat_ctx,
            **kwargs
        )
        
        # Prepend base instructions to any specific instructions passed in kwargs
        if self.chat_ctx and len(self.chat_ctx.items) > 0 and self.chat_ctx.items[0].role == "system":
             # Prepend to existing system prompt if present
             first_message = self.chat_ctx.items[0]
             if isinstance(first_message.content, list):
                 if first_message.content and isinstance(first_message.content[0], str):
                     first_message.content[0] = base_instructions + "\n\n" + first_message.content[0]
                 else:
                     first_message.content.insert(0, base_instructions + "\n\n")

    def get_context_description(self) -> str:
        """Returns a string description of the current context for the LLM."""
        return f"""
        Current State:
        - Persona: {self.sales_context.persona or 'Unknown'}
        - Motivation: {self.sales_context.motivation or 'Unknown'}
        - Attendance: {self.sales_context.attendance_depth or 'Unknown'}
        - Pain Point: {self.sales_context.identified_pain_point or 'Unknown'}
        - Saw Pitch: {self.sales_context.saw_pitch}
        - Price Revealed: {self.sales_context.current_price_revealed or 'None'}
        """
