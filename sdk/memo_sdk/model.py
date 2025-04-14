from typing import Any, Literal, TypedDict, cast


class ChatSummary(TypedDict):
    """
    TypedDict for chat message summarization.
    """
    timestamp: int
    summary: str
