import logging
import os
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm, AgentSession
from livekit.agents import inference

from agents.base import SalesContext
from agents.rapport import RapportAgent

load_dotenv()

logger = logging.getLogger("rohan")

async def entrypoint(ctx: JobContext):
    # Connect to the room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant (optional, but good for 1:1)
    participant = await ctx.wait_for_participant()
    
    logger.info(f"Participant connected: {participant.identity}")

    # Initialize Sales Context
    sales_context = SalesContext()

    # Configure LiveKit Cloud Inference Components
    # CHANGE MODELS HERE
    # STT options: deepgram/nova-2, deepgram/nova-2-medical, google/uss-chirp
    # LLM options: openai/gpt-4o, anthropic/claude-3-5-sonnet, meta/llama-3.1-70b
    # TTS options: cartesia/sonic, openai/tts-1, deepgram/aura
    
    # STT: Deepgram Nova-2 (Hindi)
    stt = inference.stt.STT(
        model="deepgram/nova-2", 
        language="hi"
    )

    llm_plugin = inference.llm.LLM(model="openai/gpt-4o-mini")

    # TTS: Cartesia Sonic-3 (Hindi Voice)
    tts = inference.tts.TTS(
        model="cartesia/sonic-3",
        voice="6303e5fb-a0a7-48f9-bb1a-dd42c216dc5d",
        language="hi"
    )

    # Initialize ChatContext
    initial_ctx = llm.ChatContext()
    initial_ctx.add_message(role="system", content="You are a helpful AI sales assistant.")

    # Initialize the Agent (Logic/Persona)
    agent = RapportAgent(
        context=sales_context,
        chat_ctx=initial_ctx,
    )

    # Initialize the Session (Media Pipeline)
    session = AgentSession(
        stt=stt,
        llm=llm_plugin,
        tts=tts,
    )

    # Start the session with the agent
    await session.start(room=ctx.room, agent=agent)
    
    # Trigger the initial greeting
    await session.generate_reply(instructions=f"Say exactly: 'Hi, this is Rohan calling from bee ten ex. Am I speaking to {sales_context.lead_name}?'")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
