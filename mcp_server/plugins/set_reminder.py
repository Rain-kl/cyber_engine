from .ext import mcp


@mcp.tool()
async def set_reminder(
    time: str,
    message: str = "Reminder set by MCP",
):
    """Set a reminder for a specific time with a message.

    Args:
        time: The time to set the reminder (e.g. "2023-10-28 07:00")
        message: The message for the reminder (default is "Reminder set by MCP")
    """

    return f"Reminder set for {time} with message: {message}"
