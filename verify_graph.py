import asyncio
from app.graph.graph import graph
from langchain_core.messages import HumanMessage

async def main():
    print("--- Verifying Cortex Agent Routing ---")
    
    # Test 1: System Query
    print("\nTest 1: 'Check my system stats'")
    inputs = {"messages": [HumanMessage(content="Check my system stats")]}
    async for event in graph.astream(inputs):
        for key, value in event.items():
            print(f"Node: {key}")
            if "messages" in value:
                print(f"Output: {value['messages'][-1].content[:100]}...")

    # Test 2: General Query
    print("\nTest 2: 'Hello, who are you?'")
    inputs = {"messages": [HumanMessage(content="Hello, who are you?")]}
    async for event in graph.astream(inputs):
        for key, value in event.items():
            print(f"Node: {key}")
            if "messages" in value:
                print(f"Output: {value['messages'][-1].content[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
