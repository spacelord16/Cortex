from langchain_core.messages import SystemMessage
from app.core.llm import get_llm
from app.tools.system import get_system_stats, get_process_list
from app.tools.journal import search_journal

def create_agent(llm, tools, system_prompt: str):
    """Helper to create an agent node."""
    if tools:
        llm = llm.bind_tools(tools)
        
    prompt = SystemMessage(content=system_prompt)
    
    def agent_node(state):
        messages = [prompt] + state["messages"]
        result = llm.invoke(messages)
        return {"messages": [result]}
        
    return agent_node

# --- System Worker (Manual ReAct) ---
def system_worker_node(state):
    llm = get_llm()
    
    # Define Tools Description
    tools_desc = """
    1. get_system_stats(): Returns CPU, RAM, Battery, Disk usage.
    2. get_process_list(limit=5): Returns top processes by memory.
    """
    
    system_prompt = (
        "You are the System Worker. You have access to the following tools:\n" + tools_desc + "\n"
        "To check system status, you MUST output valid JSON with keys 'cortex_tool' and 'args' inside a code block.\n"
        "Example:\n"
        "```json\n"
        "{\"cortex_tool\": \"get_system_stats\", \"args\": {}}\n"
        "```\n"
        "Refuse to answer if it's not about system stats."
    )
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    # 1. Call LLM
    response = llm.invoke(messages)
    content = response.content.strip()
    
    # 2. Check for Tool Call (Naive parsing for robustness)
    tool_name = None
    tool_args = {}
    
    try:
        import json
        import re
        # Find JSON inside code block or raw
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if not json_match:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
        if json_match:
            json_str = json_match.group(1) if '```' in json_match.group(0) else json_match.group(0)
            data = json.loads(json_str)
            tool_name = data.get("cortex_tool")
            tool_args = data.get("args", {})
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        pass
        
    # 3. Execute Tool if found
    if tool_name:
        tool_output = f"Tool {tool_name} failed or not found."
        
        if tool_name == "get_system_stats":
            tool_output = get_system_stats.invoke(tool_args)
        elif tool_name == "get_process_list":
            tool_output = get_process_list.invoke(tool_args)
            
        # 4. Feed back to LLM
        from langchain_core.messages import AIMessage
        follow_up_messages = messages + [
            AIMessage(content=content),
            SystemMessage(content=f"Tool Output: {tool_output}\n\nBased on this output, provide a concise human-readable answer to the user.")
        ]
        final_response = llm.invoke(follow_up_messages)
        return {"messages": [final_response]}
        
    return {"messages": [response]}

# --- Journal Worker ---
def journal_worker_node(state):
    llm = get_llm()
    
    tools_desc = "1. search_journal(query: str): Searches the user's private Markdown journal entries for past memories, work updates, thoughts, and plans."
    system_prompt = (
        "You are the Journal Worker. You have access to the following RAG tool:\n" + tools_desc + "\n"
        "To search memories or notes, you MUST output valid JSON with keys 'cortex_tool' and 'args' inside a code block.\n"
        "Example:\n"
        "```json\n"
        "{\"cortex_tool\": \"search_journal\", \"args\": {\"query\": \"what did I do today?\"}}\n"
        "```\n"
        "If you don't need to search, just answer normally based on your persona."
    )
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    response = llm.invoke(messages)
    content = response.content.strip()
    
    tool_name = None
    tool_args = {}
    
    try:
        import json
        import re
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if not json_match:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
        if json_match:
            json_str = json_match.group(1) if '```' in json_match.group(0) else json_match.group(0)
            data = json.loads(json_str)
            tool_name = data.get("cortex_tool")
            tool_args = data.get("args", {})
    except Exception as e:
        print(f"Journal JSON Parsing Error: {e}")
        pass
        
    if tool_name == "search_journal":
        try:
            tool_output = search_journal.invoke(tool_args)
        except Exception as e:
            tool_output = f"Tool search_journal failed: {e}"
            
        from langchain_core.messages import AIMessage
        follow_up_messages = messages + [
            AIMessage(content=content),
            SystemMessage(content=f"Tool Output (Retrieved Context): {tool_output}\n\nBased on this retrieved memory, provide a concise human-readable answer to the user.")
        ]
        final_response = llm.invoke(follow_up_messages)
        return {"messages": [final_response]}
        
    return {"messages": [response]}

# --- Calendar Worker ---
def calendar_worker_node(state):
    llm = get_llm()
    # TODO: Add Calendar tools here
    tools = []
    agent = create_agent(
        llm,
        tools,
        "You are the Calendar Worker. You manage the user's schedule. "
        "For now, just say 'Calendar tools are not yet implemented'."
    )
    return agent(state)

# --- General Worker ---
def general_worker_node(state):
    llm = get_llm()
    tools = []
    agent = create_agent(
        llm,
        tools,
        "You are a helpful assistant within the Cortex operating system. "
        "Handle loose ends, small talk, and general queries that don't fit into System, Journal, or Calendar contexts."
    )
    return agent(state)
