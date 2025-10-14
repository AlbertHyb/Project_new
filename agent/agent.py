import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from tools.email_tools import write_email, schedule_meeting, check_calendar_availability, Done
from agent.schemas import State
from agent.triage_router import triage_router
from prompts.prompts import (
    triage_system_prompt,
    triage_user_prompt,
    default_triage_instructions,
    default_background,
    agent_system_prompt,
    agent_tools_prompt,
    default_response_preferences,
    default_cal_preferences,
)

# Cargar variables de entorno
load_dotenv(".env")

class GeminiAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada en las variables de entorno")
        self.llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-2.5-flash")

    def invoke(self, prompt):
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response

# Inicializar herramientas y modelo con herramientas
tools = [write_email, schedule_meeting, check_calendar_availability, Done]
tools_by_name = {tool.name: tool for tool in tools}

api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-2.5-flash")
llm_with_tools = llm.bind_tools(tools, tool_choice="any")

def llm_call(state: State):
    """LLM decides whether to call a tool or not"""
    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    {"role": "system", "content": agent_system_prompt.format(
                        tools_prompt=agent_tools_prompt,
                        background=default_background,
                        response_preferences=default_response_preferences,
                        cal_preferences=default_cal_preferences,
                    )}
                ] + state["messages"]
            )
        ]
    }