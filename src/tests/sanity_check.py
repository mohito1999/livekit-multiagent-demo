import inspect
import asyncio
import logging
from agents.rapport import RapportAgent
from agents.profiler import ProfilerAgent
from agents.scheduler import SchedulerAgent
from agents.strategist import StrategistAgent
from agents.base import SalesContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sanity_check")

def check_async(cls, method_name):
    method = getattr(cls, method_name)
    is_async = inspect.iscoroutinefunction(method)
    status = "✅ ASYNC" if is_async else "❌ SYNC (FAIL)"
    logger.info(f"{cls.__name__}.{method_name}: {status}")
    if not is_async:
        raise ValueError(f"{cls.__name__}.{method_name} must be async def!")

def main():
    logger.info("Verifying Tool Definitions...")
    
    # Check RapportAgent
    check_async(RapportAgent, "log_workshop_details")
    check_async(RapportAgent, "handoff_to_scheduler")
    check_async(RapportAgent, "handoff_to_profiler")
    
    # Check ProfilerAgent
    check_async(ProfilerAgent, "submit_profile_and_handoff")
    
    # Check SchedulerAgent
    check_async(SchedulerAgent, "confirm_reschedule")
    
    # Check StrategistAgent
    check_async(StrategistAgent, "handoff_to_closing")
    
    logger.info("ALL CHECKS PASSED. Agents are ready.")

if __name__ == "__main__":
    main()
