# LiveKit Multi-Agent Sales Demo

A proof-of-concept demonstrating a **State-Based Multi-Agent Voice System** built with [LiveKit Agents](https://docs.livekit.io/agents). 

This project implements a sophisticated conversational AI that moves a lead through a structured sales funnel: **Rapport -> Discovery -> Pitch -> Closing**.

## 🚀 Why Multi-Agent?

Single-prompt AI agents often fail at complex conversations because they try to do everything at once. They tend to rush to the "sale" immediately, ignoring the subtle social dynamics required to build trust.

**The Multi-Agent Advantage:**
*   **Patience & Pacing**: Each agent has a *specific* limited goal. The "Rapport Agent" *cannot* pitch; it forces the conversation to slow down and build a connection first.
*   **State Management**: We define explicit "Exit Criteria" (e.g., "Must confirm pain point X before moving to Pitch"). This prevents the AI from Hallucinating progress.
*   **Specialized Prompts**: Instead of one massive system prompt, we have smaller, hyper-focused experts. The "Discovery Agent" is an expert at asking probing questions; the "Closing Agent" is an expert at handling objections.
*   **Human-Like Flow**: This mimics how top sales professionals break down a conversation, earning the right to ask for the sale step-by-step.

## 🏗 Architecture

The system uses a **Handoff Pattern**. All agents share a common `SalesContext` (data layer), but the `logic` switches entirely at each phase.

1.  **Phase 1: Rapport Agent** (`rapport.py`)
    *   *Goal*: Verify identity, get feedback on the previous interactions, and confirm attendance.
    *   *Transition*: Only moves forward once specific data points are collected.
    
2.  **Phase 2: Discovery Agent** (`discovery.py`)
    *   *Goal*: "The Doctor". Uncover the user's specific "Pain Point" (e.g., career stagnation, low pay).
    *   *Transition*: Only moves forward once the user admits the problem is urgent.

3.  **Phase 3: Pitch Agent** (`pitch.py`)
    *   *Goal*: "The Solution". Link the specific pain point to the product (AI Accelerator Program).
    *   *Transition*: Moves forward once interest is confirmed.

4.  **Phase 4: Closing Agent** (`closing.py`)
    *   *Goal*: Secure the booking deposit. Handles objections (Time, Money, Spousal approval).

## 🛠️ Setup & Installation

### Prerequisites
*   Python 3.10+
*   LiveKit Cloud Account (URL & API Key)
*   API Keys for: OpenAI, Deepgram, Cartesia

### 1. Clone & Install
```bash
git clone https://github.com/mohito1999/livekit-multiagent-demo.git
cd livekit-multiagent-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory:
```bash
LIVEKIT_URL=wss://...
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
OPENAI_API_KEY=...
DEEPGRAM_API_KEY=...
CARTESIA_API_KEY=...
```

### 3. Run the Agent
```bash
python src/main.py dev
```

### 4. Trigger a Call (SIP)
To simulate an outbound call (requires configured SIP Trunk in LiveKit):
```bash
python src/trigger_call.py <PHONE_NUMBER> <SIP_TRUNK_ID>
```
*Example: `python src/trigger_call.py +15550000000 ST_...`*

## 📁 Key Files
*   `src/main.py`: Entry point. Configures the AgentSession, STT (Deepgram/Hindi), TTS (Cartesia/Hindi), and LLM.
*   `src/agents/base.py`: Defines the `SalesContext` data structure and global rules (conciseness, tone).
*   `src/agents/*.py`: The specialized agent implementations.
