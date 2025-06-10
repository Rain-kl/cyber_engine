from loguru import logger

from .ext import mcp


@mcp.tool()
async def retrieve_contact_list(contact_name):
    """Query user contact information, return: contact's phone number, QQ number, and other related contact information.
    Args:
        contact_name: The name of the contact to retrieve information for.

    """
    try:
        contact_info = {
            "name": "张三",
            "phone": "1234567890",
            "qq": "2595449660",
        }
        return f"{contact_info}"
    except Exception as e:
        logger.error(f"Error retrieving contact list: {e}")
        return []
