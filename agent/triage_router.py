import os
from langgraph.types import Command
from langgraph.graph import END
from agent.schemas import RouterSchema, State  # Asumo que RouterSchema es para la salida; si no, ajusta
from prompts.prompts import triage_system_prompt, triage_user_prompt, default_triage_instructions, default_background
from tools.utils import parse_email, format_email_markdown
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field  # Para salida estructurada
from agent.schemas import State
from typing import Literal



# Define el schema de salida para classification
class RouterOutput(BaseModel):
    """Salida estructurada del router."""
    classification: str = Field(..., description="Clasificación: 'respond', 'ignore' o 'notify'")

def triage_router(state: State):
    # Inicialización del LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # Extrae datos del email del state (corregido: no estaban definidos)
    email_input = state.get("email_input", {})
    author = email_input.get("author", "")
    to = email_input.get("to", "")
    subject = email_input.get("subject", "")
    email_thread = email_input.get("email_thread", "")

    # Define system_prompt combinando los prompts del sistema (ajusta si es diferente)
    system_prompt = (
        triage_system_prompt
        + "\n\n" + default_background
        + "\n\n" + default_triage_instructions
    )

    # Formatea el user prompt
    system_prompt = triage_system_prompt.format(
        antecedentes=default_background,  # Asumiendo que {antecedentes} es para background
        instrucciones_de_clasificación=default_triage_instructions  # Asumiendo que {instrucciones_de_clasificación} es para instructions
    )

    # Formatea el user prompt (igual)
    user_prompt = triage_user_prompt.format(
        author=author, to=to, subject=subject, email_thread=email_thread
    )

    # Crea el chain: prompt con mensajes + LLM con salida estructurada
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),  # Placeholder para user_prompt
    ])
    llm_router = prompt | llm.with_structured_output(RouterOutput)

    # Invoke corregido: usa BaseMessage objects
    result = llm_router.invoke({"input": user_prompt})  # Pasa como dict para el placeholder

    # Lógica de clasificación (igual, pero ahora result es RouterOutput)
    if result.classification == "respond":
        goto = "response_agent"
        update = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Respond to the email: \n\n{format_email_markdown(subject, author, to, email_thread)}",
                }
            ],
            "classification_decision": result.classification,
        }
    elif result.classification == "ignore":
        goto = END
        update = {"classification_decision": result.classification}
    elif result.classification == "notify":
        goto = END
        update = {"classification_decision": result.classification}
    else:
        raise ValueError(f"Invalid classification: {result.classification}")
    
    return Command(goto=goto, update=update)



   




