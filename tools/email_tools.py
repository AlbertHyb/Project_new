from langchain_core.tools import tool
from datetime import datetime
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.schemas import RouterSchema




@tool
def write_email(to: str, subject: str, content: str) -> str:
    """Write and send an email."""
    return f"Email sent to {to} with subject '{subject}' and content: {content}"

@tool
def schedule_meeting(attendees: list[str], subject: str, duration_minutes: int, preferred_day: datetime, start_time: int) -> str:
    """Schedule a calendar meeting."""
    date_str = preferred_day.strftime("%A, %B %d, %Y")
    return f"Meeting '{subject}' scheduled on {date_str} at {start_time} for {duration_minutes} minutes with {len(attendees)} attendees"

@tool
def check_calendar_availability(day: str) -> str:
    """Check calendar availability for a given day."""
    return f"Available times on {day}: 9:00 AM, 2:00 PM, 4:00 PM"


@tool
# This is new! 
class Question(BaseModel):
      """Question to ask user."""
      content: str

@tool
class Done(BaseModel):
    """E-mail has been sent."""
    done: bool

# All tools available to the agent
tools = [
    write_email, 
    schedule_meeting, 
    check_calendar_availability, 
    Question, 
    Done,
]

tools_by_name = {tool.name: tool for tool in tools}

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)  # Usa 'gemini-pro' si prefieres la versión básica
llm_router = llm.with_structured_output(RouterSchema)

# Inicializar el LLM, forzando el uso de herramientas (de cualquier herramienta disponible) para el agente
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
llm_with_tools = llm.bind_tools(tools, tool_choice="required")     