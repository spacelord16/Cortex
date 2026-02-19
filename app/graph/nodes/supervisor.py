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
    "Your role is to route the user's request to the appropriate worker agent.\n"
    " - SystemWorker: For computer stats, CPU, RAM, battery, process management.\n"
    " - JournalWorker: For writing to or reading from the daily journal/notes.\n"
    " - CalendarWorker: For scheduling, checking availability, or calendar events.\n"
    " - GeneralWorker: For general chitchat (hello, hi), greetings, or questions not covered by others.\n"
    "\n"
    "Given the conversation below, which agent should act next?"
    " Return a JSON object with a single key 'next' matching one of the options below.\n"
    "Options: {options}\n"
    "\n"
    "{format_instructions}"
)

# options = ["FINISH"] + members
options = members + ["FINISH"] # Order matters little

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Who should act next?",
        ),
    ]
).partial(options=str(options), format_instructions=parser.get_format_instructions())

def supervisor_node(state: AgentState):
    llm = get_llm()
    supervisor_chain = prompt | llm | parser
    result = supervisor_chain.invoke(state)
    return result
