from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        tool_name = request.tool_call.get("name", "未知工具")
        return ToolMessage(
            content=f"{tool_name} 工具暂时不可用 ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )