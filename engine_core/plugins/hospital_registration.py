async def hospital_registration(
        department: str,
):
    return f"Registering to the {department} department"


hospital_registration_tools = {
    "type": "function",
    "function": {
        "name": "hospital_registration",
        "description": "Register to a hospital department",
        "parameters": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "The department to register to (e.g. Cardiology, Neurology)",
                },
            },
            "required": ["department"],
        },
    }
}
