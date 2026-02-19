from langchain_core.messages import SystemMessage
from app.core.llm import get_llm
from app.tools.system import get_system_stats, get_process_list

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
        "To use a tool, output valid JSON with keys 'cortex_tool' (name) and 'args' (dict).\n"
        "Example: {\"cortex_tool\": \"get_system_stats\", \"args\": {}}\n"
        "If no tool is needed, just output your answer as text."
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
        if "{" in content and "cortex_tool" in content:
            # Extract JSON substring
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            data = json.loads(json_str)
            tool_name = data.get("cortex_tool")
            tool_args = data.get("args", {})
    except Exception:
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
            SystemMessage(content=f"Tool Output: {tool_output}")
        ]
        final_response = llm.invoke(follow_up_messages)
        return {"messages": [final_response]}
        
    return {"messages": [response]}

# --- Journal Worker ---
def journal_worker_node(state):
    llm = get_llm()
    # TODO: Add RAG tools here
    tools = [] 
    agent = create_agent(
        llm,
        tools,
        "You are the Journal Worker. You have access to the user's personal journal and notes. "
        "Use RAG tools to search for past entries or add new ones. "
        "For now, just say 'Journal tools are not yet implemented'."
    )
    return agent(state)

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
