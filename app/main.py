from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cortex")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load agents, connect to DB
    logger.info("Cortex System Initializing...")
    yield
    # Shutdown
    logger.info("Cortex System Shutting Down...")

app = FastAPI(
    title="Cortex API",
    description="Agentic Personal Operating System",
    version="0.1.0",
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.graph.graph import graph
from langchain_core.messages import HumanMessage
from fastapi.responses import StreamingResponse
import json

@app.post("/chat")
async def chat(message: str):
    """
    Chat with Cortex.
    """
    inputs = {"messages": [HumanMessage(content=message)]}
    
    async def event_generator():
        try:
            # recursion_limit=6: Supervisor can route at most 2 worker calls before stopping
            config = {"recursion_limit": 6}
            async for event in graph.astream(inputs, config=config):
                for key, value in event.items():
                    if key == "Supervisor":
                        continue
                    if "messages" in value:
                        last_msg = value["messages"][-1]
                        content = last_msg.content if isinstance(last_msg.content, str) else str(last_msg.content)
                        # Filter out raw internal tool-call JSON blobs (not meant for the user)
                        if content.strip().startswith("```json") and "cortex_tool" in content:
                            continue
                        if not content.strip():
                            continue
                        yield json.dumps({"sender": key, "content": content}) + "\n"
        except Exception as e:
            logger.error(f"Graph execution error: {e}", exc_info=True)
            yield json.dumps({"sender": "Cortex", "content": f"⚠️ Error: {str(e)}"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.get("/stats")
async def stats():
    """
    Get current system statistics.
    """
    from app.tools.system import get_system_stats
    # get_system_stats returns a JSON string, we should parse it to return valid JSON
    stats_json = get_system_stats.invoke({})
    return json.loads(stats_json)

@app.get("/")
async def root():
    return {"status": "online", "system": "Cortex"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
