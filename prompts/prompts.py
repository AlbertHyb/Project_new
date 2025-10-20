triage_system_prompt =  """
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
agent_tools_prompt= """You have access to the following tools:"""
default_response_preferences = """...your response preferences here..."""
default_cal_preferences = """...your calendar preferences here..."""
agent_system_prompt_hitl = "Your system prompt here"
HITL_TOOLS_PROMPT = "Your tools prompt here"
format_for_display = """Format the following content for display: {content}"""