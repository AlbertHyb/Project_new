import os
from dotenv import load_dotenv
from agent.agent import GeminiAgent, llm_call
from agent.schemas import State
from agent.triage_router import triage_router
from tools.email_tools import write_email, schedule_meeting, check_calendar_availability, Done
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
from rich.console import Console
from rich.markdown import Markdown

# Cargar variables de entorno
load_dotenv(".env")

def main():
    # Mostrar prompts en Markdown
    console = Console()
    console.print(Markdown(triage_system_prompt))
    console.print(Markdown(triage_user_prompt))
    console.print(Markdown(default_background))
    console.print(Markdown(default_triage_instructions))

    # Inicializar el agente
    agent = GeminiAgent()
    state = State(email_input={"author": "John Doe", "to": "Jane Doe", "subject": "Meeting Update", "email_thread": "Details about the meeting..."})
    
    # Llamar al router
    triage_result = triage_router(state)
    print("Triage Result:", triage_result)

    # Llamar al modelo con herramientas
    llm_result = llm_call(state)
    print("LLM Result:", llm_result)

if __name__ == "__main__":
    main()