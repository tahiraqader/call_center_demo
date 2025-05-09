from typing import TypedDict
from datetime import datetime

class Call(TypedDict, total=False):
    date: datetime
    dialog: str
    summary: str
    action_items: str
    caller_sentiment: str
    agent_sentiment: str