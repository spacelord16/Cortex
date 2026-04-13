from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.core.llm import get_llm
from app.graph.state import AgentState

# The Supervisor is responsible for routing to the correct worker
members = ["SystemWorker", "JournalWorker", "CalendarWorker", "GeneralWorker"]

class RouteSchema(BaseModel):
    next: Literal["SystemWorker", "JournalWorker", "CalendarWorker", "GeneralWorker", "FINISH"] = Field(
        description="The next role to act."
    )

parser = JsonOutputParser(pydantic_object=RouteSchema)

system_prompt = (
    "You are the Supervisor of Cortex, an advanced personal operating system.\n"
    "Your ONLY job is to output a JSON routing decision. Do not answer the user yourself.\n"
    " - SystemWorker: CPU, RAM, battery, disk, processes, system stats.\n"
    " - JournalWorker: Journal entries, notes, memories, past events.\n"
    " - CalendarWorker: Schedule, calendar, availability.\n"
    " - GeneralWorker: Greetings, small talk, or anything not covered above.\n"
    " - FINISH: The user's request has already been answered. Choose this if the last message\n"
    "   in the conversation is from a worker (not the user).\n"
    "\n"
    "CRITICAL RULE: If there is already a worker response in the conversation, output FINISH.\n"
    "Never route to a worker twice for the same user request.\n"
    "\n"
    "Return ONLY valid JSON: {{\"next\": \"<choice>\"}}\n"
    "Options: {options}\n"
    "{format_instructions}"
)

options = members + ["FINISH"]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Who should act next? Reply with JSON only.",
        ),
    ]
).partial(options=str(options), format_instructions=parser.get_format_instructions())

# Short acknowledgments that don't need any worker — route to FINISH instantly
_FINISH_KEYWORDS = {"thanks", "thank you", "ok", "okay", "got it", "bye", "goodbye",
                    "great", "perfect", "awesome", "nice", "cool", "noted", "sure"}

def supervisor_node(state: AgentState):
    # Fast-path: skip the LLM call for simple acknowledgments
    messages = state.get("messages", [])
    if messages:
        last_content = messages[-1].content.strip().lower().rstrip("!.,")
        if last_content in _FINISH_KEYWORDS or len(last_content.split()) <= 3 and any(
            kw in last_content for kw in _FINISH_KEYWORDS
        ):
            return {"next": "FINISH"}

    llm = get_llm()
    supervisor_chain = prompt | llm | parser
    result = supervisor_chain.invoke(state)
    return result

