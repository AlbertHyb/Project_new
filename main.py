from dotenv import load_dotenv
from agent.agent import  llm_call
from agent.schemas import State
from agent.triage_router import triage_router
from prompts.prompts import (
    triage_system_prompt,
    triage_user_prompt,
    default_triage_instructions,
    default_background,
    
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
    #agent = GeminiAgent()

    state_maintenance = State(
    email_input={
        "author": "System Admin <sysadmin@company.com>",
        "to": "Development Team <dev@company.com>",
        "subject": "Scheduled maintenance - database downtime",
        "email_thread": "Hi team,\n\nThis is a reminder that we'll be performing scheduled maintenance on the production database tonight from 2AM to 4AM EST. During this time, all database services will be unavailable.\n\nPlease plan your work accordingly and ensure no critical deployments are scheduled during this window.\n\nThanks,\nSystem Admin Team"
    },
    messages=[]
)

# Caso 2: Pregunta sobre documentación de API
    state_api_question = State(
       email_input={
        "author": "Alice Smith <alice.smith@company.com>",
        "to": "John Doe <john.doe@company.com>",
        "subject": "Quick question about API documentation",
        "email_thread": "Hi John,\nI was reviewing the API documentation for the new authentication service and noticed a few endpoints seem to be missing from the specs. Could you help clarify if this was intentional or if we should update the docs?\nSpecifically, I'm looking at:\n- /auth/refresh\n- /auth/validate\nThanks!\nAlice"
    },
    messages=[]
)
       
    # Ejecutar el flujo para ambos casos
    for state in [state_maintenance, state_api_question]:
        triage_result = triage_router(state)
        print("Triage Result:", triage_result)

        if triage_result.goto == "response_agent":
            llm_result = llm_call(state)
            print("LLM Result:", llm_result)
        else:
            print("Flujo terminado: No se necesita respuesta (clasificación:", triage_result.update.get("classification_decision"), ")")
        
    # Llamar al router
    triage_result = triage_router(state)
    print("Triage Result:", triage_result)

    # Llamar al modelo con herramientas
    if triage_result.goto == "response_agent":
        llm_result = llm_call(state)
        print("LLM Result:", llm_result)
    else:
        print("Flujo terminado: No se necesita respuesta (clasificación:", triage_result.update.get("classification_decision"), ")")


if __name__ == "__main__":
    main()