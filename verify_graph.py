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
                msg = value["messages"][-1]
                print(f"Output Type: {type(msg)}")
                if hasattr(msg, "content"):
                    print(f"Output: {msg.content}")
                else:
                    print(f"Output: {str(msg)}")

    # Test 2: General Query (Commented out because llama-3.1-8b loops on FINISH)
    # print("\nTest 2: 'Hello, who are you?'")
    # inputs = {"messages": [HumanMessage(content="Hello, who are you?")]}
    # async for event in graph.astream(inputs):
    #     for key, value in event.items():
    #         print(f"Node: {key}")
    #         if "messages" in value:
    #             print(f"Output: {value['messages'][-1].content[:100]}...")

    # Test 3: Journal Query
    print("\nTest 3: 'What did I do on February 21?'")
    inputs = {"messages": [HumanMessage(content="What did I do on February 21?")]}
    async for event in graph.astream(inputs):
        for key, value in event.items():
            print(f"Node: {key}")
            if "messages" in value:
                msg = value["messages"][-1]
                if hasattr(msg, "content"):
                    print(f"Output: {msg.content}")
                else:
                    print(f"Output: {str(msg)}")

if __name__ == "__main__":
    asyncio.run(main())
