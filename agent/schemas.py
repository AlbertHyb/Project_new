from typing import Literal
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState

class State(MessagesState):
    email_input: dict
    classification_decision: Literal["ignore", "respond", "notify"]

class RouterSchema(BaseModel):
    reasoning: str = Field(description="Step-by-step reasoning behind the classification.")
    classification: Literal["ignore", "respond", "notify"] = Field(
        description="The classification of an email: 'ignore' for irrelevant emails, "
        "'notify' for important information that doesn't need a response, "
        "'respond' for emails that need a reply",
    )