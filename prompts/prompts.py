from rich.console import Console
from rich.markdown import Markdown


console = Console()


def display_tools_prompt():
    HITL_TOOLS_PROMPT = """
    # Herramientas disponibles
    Estas son las herramientas que el agente puede usar:
    - **write_email**: Escribe y envía un correo electrónico.
    - **schedule_meeting**: Programa una reunión en el calendario.
    - **check_calendar_availability**: Verifica la disponibilidad en el calendario.
    - **Question**: Realiza una pregunta al usuario.
    - **Done**: Marca una tarea como completada.
    """
    markdown_prompt = Markdown(HITL_TOOLS_PROMPT)
    console.print(markdown_prompt)


def format_for_display(tool_call):
    # Puedes personalizar el formato según lo que necesites mostrar
    return f"Tool call: {tool_call}"


triage_system_prompt = """
< Rol >
Su rol es clasificar los correos electrónicos entrantes según las instrucciones y la información de fondo a continuación.
</ Rol >

< Antecedentes >
{antecedentes}.
</ Antecedentes >

< Instrucciones >
Categorice cada correo electrónico en una de estas tres categorías:
1. IGNORAR: correos electrónicos que no vale la pena responder ni rastrear
2. NOTIFICAR: información importante que vale la pena notificar, pero que no requiere una respuesta
3. RESPONDER: correos electrónicos que requieren una respuesta directa
Clasifique el siguiente correo electrónico en una de estas categorías.
</ Instrucciones >

< Reglas >
{instrucciones_de_clasificacion}
</ Reglas >
"""
triage_user_prompt = """...tu prompt aquí..."""
default_triage_instructions = """...tus instrucciones aquí..."""
default_background = """...tu background aquí..."""
agent_system_prompt = """You are an AI assistant that helps people find information."""
agent_tools_prompt = """You have access to the following tools:"""
default_response_preferences = """...your response preferences here..."""
default_cal_preferences = """...your calendar preferences here..."""
agent_system_prompt_hitl = "Your system prompt here"
