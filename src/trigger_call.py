import asyncio
import os
import sys
import random
import string
from dotenv import load_dotenv
from livekit import api
from livekit.protocol.sip import CreateSIPParticipantRequest

load_dotenv()

async def main():
    if len(sys.argv) < 3:
        print("Usage: python src/trigger_call.py <phone_number> <sip_trunk_id>")
        print("Example: python src/trigger_call.py +15550001234 ST_abcdef123456")
        return

    phone_number = sys.argv[1]
    sip_trunk_id = sys.argv[2]
    sip_number = sys.argv[3] if len(sys.argv) > 3 else None

    # Initialize LiveKit API
    lkapi = api.LiveKitAPI(
        os.getenv("LIVEKIT_URL"),
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET"),
    )

    try:
        # Create a unique room name
        room_name = f"call-{(''.join(random.choices(string.ascii_lowercase + string.digits, k=6)))}"
        print(f"Creating room: {room_name}")
        
        # Create the room
        await lkapi.room.create_room(api.CreateRoomRequest(name=room_name))
        print(f"Room created. Dialing {phone_number} using Trunk ID {sip_trunk_id}...")

        # Create SIP Participant (Dial Out)
        request = CreateSIPParticipantRequest(
            sip_trunk_id=sip_trunk_id,
            sip_call_to=phone_number,
            room_name=room_name,
            participant_identity=f"sip_{phone_number}",
            sip_number=sip_number, # Caller ID
        )
        
        participant = await lkapi.sip.create_sip_participant(request)
        print(f"Call initiated!")
        print(f"Participant Info: {participant}")
        print(f"Make sure your agent is running: python src/main.py dev")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(main())
