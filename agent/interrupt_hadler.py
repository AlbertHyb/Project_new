from typing import Literal
from click import Command
from agent.schemas import State
from tools.email_tools import tools_by_name
from agent.triage_router import interrupt, parse_email, format_email_markdown
from prompts.prompts import triage_system_prompt, format_for_display
from langgraph.graph import END

def interrupt_handler(state: "State") -> "Command[Literal['llm_call', '__end__']]":
    """Creates an interrupt for human review of tool calls"""
    # ...existing code...
    triage_system_prompt = triage_system_prompt  # placeholder to avoid unused variable warnings
    result = []

    goto = "llm_call"

    for tool_call in state["messages"][-1].tool_calls:
        hitl_tools = ["write_email", "schedule_meeting", "Question"]
        if tool_call["name"] not in hitl_tools:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]})
            continue

        email_input = state["email_input"]
        author, to, subject, email_thread = parse_email(email_input)
        original_email_markdown = format_email_markdown(subject, author, to, email_thread)

        tool_display = format_for_display(tool_call)
        description = original_email_markdown + tool_display

        if tool_call["name"] == "write_email":
            config = {"allow_ignore": True, "allow_respond": True, "allow_edit": True, "allow_accept": True}
        elif tool_call["name"] == "schedule_meeting":
            config = {"allow_ignore": True, "allow_respond": True, "allow_edit": True, "allow_accept": True}
        elif tool_call["name"] == "Question":
            config = {"allow_ignore": True, "allow_respond": True, "allow_edit": False, "allow_accept": False}
        else:
            raise ValueError(f"Invalid tool call: {tool_call['name']}")

        request = {
            "action_request": {"action": tool_call["name"], "args": tool_call["args"]},
            "config": config,
            "description": description,
        }

        response = interrupt([request])[0]

        if response["type"] == "accept":
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]})
        elif response["type"] == "edit":
            tool = tools_by_name[tool_call["name"]]
            edited_args = response["args"]["args"]
            ai_message = state["messages"][-1]
            current_id = tool_call["id"]
            updated_tool_calls = [tc for tc in ai_message.tool_calls if tc["id"] != current_id] + [
                {"type": "tool_call", "name": tool_call["name"], "args": edited_args, "id": current_id}
            ]
            result.append(ai_message.model_copy(update={"tool_calls": updated_tool_calls}))
            observation = tool.invoke(edited_args)
            result.append({"role": "tool", "content": observation, "tool_call_id": current_id})
        elif response["type"] == "ignore":
            if tool_call["name"] == "write_email":
                result.append({"role": "tool", "content": "User ignored this email draft. Ignore this email and end the workflow.", "tool_call_id": tool_call["id"]})
                goto = END
            elif tool_call["name"] == "schedule_meeting":
                result.append({"role": "tool", "content": "User ignored this calendar meeting draft. Ignore this email and end the workflow.", "tool_call_id": tool_call["id"]})
                goto = END
            elif tool_call["name"] == "Question":
                result.append({"role": "tool", "content": "User ignored this question. Ignore this email and end the workflow.", "tool_call_id": tool_call["id"]})
                goto = END
            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")
        elif response["type"] == "response":
            user_feedback = response["args"]
            if tool_call["name"] == "write_email":
                result.append({"role": "tool", "content": f"User gave feedback, which can we incorporate into the email. Feedback: {user_feedback}", "tool_call_id": tool_call["id"]})
            elif tool_call["name"] == "schedule_meeting":
                result.append({"role": "tool", "content": f"User gave feedback, which can we incorporate into the meeting request. Feedback: {user_feedback}", "tool_call_id": tool_call["id"]})
            elif tool_call["name"] == "Question":
                result.append({"role": "tool", "content": f"User answered the question, which can we can use for any follow up actions. Feedback: {user_feedback}", "tool_call_id": tool_call["id"]})
            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")
        else:
            raise ValueError(f"Invalid response: {response}")

    update = {"messages": result}
    return Command(name="example_command", callback=some_callback)