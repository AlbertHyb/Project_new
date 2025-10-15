import os
from dotenv import load_dotenv
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from tools.email_tools import write_email, schedule_meeting, check_calendar_availability, Done
from agent.schemas import State
from prompts.prompts import (
    agent_system_prompt,
    agent_tools_prompt,
    default_background,
    default_response_preferences,
    default_cal_preferences,
)


load_dotenv(".env")

class GeminiAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY no encontrada en las variables de entorno"
            )
        # Removido: project_id y su verificación, ya que no se necesita para la API directa
        
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model="gemini-2.5-flash",  # Si es un typo y querías "gemini-1.5-flash", cámbialo
        )


    def invoke(self, prompt):
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response


tools = [write_email, schedule_meeting, check_calendar_availability, Done]
tools_by_name = {tool.name: tool for tool in tools}
api_key = os.getenv("GOOGLE_API_KEY")
project_id = os.getenv("GOOGLE_PROJECT_ID")
if not project_id:
    raise ValueError(
        "GOOGLE_PROJECT_ID no encontrada en las variables de entorno"
    )
llm = ChatGoogleGenerativeAI(
    google_api_key=api_key,
    model="gemini-2.5-flash",
    project=project_id,
)
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
# credentials check via GOOGLE_APPLICATION_CREDENTIALS no longer required