from .ext import mcp


@mcp.tool()
async def hospital_registration(
    department: str,
):
    """Register to a hospital department

    Args:
        department: The department to register to (e.g. Cardiology, Neurology)
    """

    return f"Registering to the {department} department"
