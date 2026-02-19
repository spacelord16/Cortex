from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """The state of the agentic system."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
