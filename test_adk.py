import asyncio
import os
from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

async def main():
    if "GEMINI_API_KEY" not in os.environ:
         print("Missing GEMINI_API_KEY")
         # We'll just assume it works if we get to this point
    agent = Agent(name="wiki_agent", instruction="You summarize text into 3 bullet points.", model="gemini-2.5-flash")
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="session1")

    runner = Runner(agent=agent, app_name="test_app", session_service=session_service)
    msg = Content(role="user", parts=[Part.from_text(text="Here is a long text: The agentic framework uses DDD to build memory graphs.")])
    events = runner.run_async(
        user_id="test_user", 
        session_id="session1", 
        new_message=msg
    )
    async for e in events:
        if e.type == "LLM_RESPONSE":
            print("Response:", e.message)
        elif e.type == "RUN_COMPLETED":
            pass

if __name__ == "__main__":
    asyncio.run(main())
