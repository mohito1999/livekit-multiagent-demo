from typing import Annotated, Literal
from livekit.agents import llm
from .base import BaseSalesAgent, SalesContext
import logging

logger = logging.getLogger("rohan.agents.closing")

class ClosingAgent(BaseSalesAgent):
    def __init__(
        self,
        context: SalesContext,
        chat_ctx: llm.ChatContext | None = None,
        **kwargs,
    ):
        instructions = f"""
        You are in PHASE 4: CLOSING.
        
        GOAL: Secure the Deposit or Define Next Steps.
        
        PRICING:
        - Retail: {context.retail_price}.
        - Discount: {context.price_level_1_discount} (If they act now).
        - Booking: {context.booking_amount} to lock the seat.
        
        YOUR OBJECTIVES:
        1. Reveal Price confidently: "Normally it's {context.retail_price}, but for workshop attendees, it's {context.price_level_1_discount}."
        2. Ask for the close: "Can I send you the link to lock your seat with {context.booking_amount}?"
        3. Handle Objections: Empathize -> Isolate -> Overcome.
        
        RULES:
        - Be direct about money. No hesitation.
        - KEEP IT SHORT.
        """
        
        super().__init__(
            context=context,
            chat_ctx=chat_ctx,
            instructions=instructions,
            **kwargs,
        )

    @llm.function_tool(description="Log that a specific price tier has been revealed to the user.")
    async def reveal_price(
        self, 
        price_tier: Literal["retail", "scholarship", "floor"]
    ):
        """
        Log that a specific price tier has been revealed to the user.

        Args:
            price_tier: The price tier revealed
        """
        logger.info(f"Price revealed: {price_tier}")
        self.sales_context.current_price_revealed = price_tier
        return f"Price tier '{price_tier}' revealed. Wait for their reaction."

    @llm.function_tool(description="Log an objection raised by the user.")
    async def handle_objection(
        self,
        objection_type: Literal["time", "money", "trust", "other"],
        summary: str
    ):
        """
        Log an objection raised by the user.

        Args:
            objection_type: Category of objection
            summary: Summary of the objection
        """
        logger.info(f"Objection: {objection_type} - {summary}")
        self.sales_context.objections_log.append(f"{objection_type}: {summary}")
        return "Objection logged. Address it using the Deep Knowledge Base (e.g. lifetime access, EMI options)."

    @llm.function_tool(description="Send the payment link to the user to finalize the deal.")
    async def send_payment_link(
        self,
        amount: str
    ):
        """
        Send the payment link to the user to finalize the deal.

        Args:
            amount: The amount to be paid (e.g. 'Five thousand rupees')
        """
        logger.info(f"Sending payment link for: {amount}")
        # In a real app, this would trigger an SMS/Email
        return f"Link sent for {amount}. Say: 'I have sent the link to your WhatsApp. Please confirm once you receive it.'"

    @llm.function_tool(description="End the call gracefully if the user is not interested or the deal is closed.")
    async def end_session(
        self,
        outcome: Literal["closed", "not_interested", "follow_up"]
    ):
        """
        End the call gracefully if the user is not interested or the deal is closed.

        Args:
            outcome: Outcome of the session
        """
        logger.info(f"Session ended: {outcome}")
        return "Say goodbye appropriately based on the outcome."
