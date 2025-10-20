import os
from dotenv import load_dotenv
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from tools.email_tools import write_email, schedule_meeting, check_calendar_availability, Done
from agent.schemas import State
from typing import Literal
from langgraph.graph import END
from langgraph.graph import StateGraph, START, END
from tools.email_assistant_utils import show_graph
from prompts.prompts import triage_system_prompt
from rich.markdown import Markdown
Markdown(triage_system_prompt)


load_dotenv(".env")
class GeminiAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada en las variables de entorno")
        
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model="gemini-2.5-flash",
        )

    def invoke(self, prompt):
        return self.llm.invoke(prompt)

tools = [write_email, schedule_meeting, check_calendar_availability, Done]
tools_by_name = {tool.name: tool for tool in tools}
api_key = os.getenv("GOOGLE_API_KEY")
project_id = os.getenv("GOOGLE_PROJECT_ID")
if not project_id:
    raise ValueError("GOOGLE_PROJECT_ID no encontrada en las variables de entorno")

llm = ChatGoogleGenerativeAI(
    google_api_key=api_key,
    model="gemini-2.5-flash",
    project=project_id,
)
llm_with_tools = llm.bind_tools(tools, tool_choice="any")

def llm_call(state: State):
    # Llama al LLM con herramientas
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_handler(state: State):
    """Performs the tool call."""
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]})
    return {"messages": result}

def should_continue(state: State) -> Literal["tool_handler", "__end__"]:
    """Route to tool handler, or end if Done tool called."""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "Done":
                return "__end__"
            else:
                return "tool_handler"
    return "__end__"

# Build workflow
overall_workflow = StateGraph(State)

# Add nodes
overall_workflow.add_node("llm_call", llm_call)
overall_workflow.add_node("tool_handler", tool_handler)

# Add edges
overall_workflow.add_edge(START, "llm_call")
overall_workflow.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "tool_handler": "tool_handler",
        END: END,
    },
)
overall_workflow.add_edge("tool_handler", "llm_call")

# Compile the agent
agent = overall_workflow.compile()

# View
show_graph(agent)