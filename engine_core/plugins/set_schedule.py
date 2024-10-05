from loguru import logger


def set_schedule(trigger_time, tasks):
    logger.info(f"Setting schedule, trigger time: {trigger_time}, tasks: {tasks}")
    return "Schedule set successfully"
    pass


schedule_tools = {
    "type": "function",
    "function": {
        "name": "set_schedule",
        "description": "Set scheduled tasks, which can be scheduled reminders or scheduled execution of operations. ",
        "parameters": {
            "type": "object",
            "properties": {
                "trigger_time": {
                    "type": "string",
                    "description": "The time to trigger the schedule, in the format of 'YYYYMMDDHHMM'，If the user does not specify a specific time, it defaults to 8am in the morning",
                },
                "tasks": {
                    "type": "string",
                    "description": "You need to write down what you need to do in the memo, and the auxiliary will remind you at the designated time",
                },
            },
            "required": ["trigger_time", "tasks"],
        },
    }
}
