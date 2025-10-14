from langgraph.types import Command
from langgraph.graph import END
from agent.schemas import RouterSchema, State
from prompts.prompts import triage_system_prompt, triage_user_prompt, default_triage_instructions, default_background
from tools.utils import parse_email, format_email_markdown
from langchain.chat_models import init_chat_model

llm = init_chat_model("gemini-2.5-flash", temperature=0.0)
llm_router = llm.with_structured_output(RouterSchema)

def triage_router(state: State) -> Command:
    author, to, subject, email_thread = parse_email(state["email_input"])
    system_prompt = triage_system_prompt.format(
        background=default_background,
        triage_instructions=default_triage_instructions
    )
    user_prompt = triage_user_prompt.format(
        author=author, to=to, subject=subject, email_thread=email_thread
    )
    result = llm_router.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
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